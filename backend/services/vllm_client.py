import asyncio
import logging
import os
import re
from collections.abc import Iterator
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.entrypoints.utils import _validate_truncation_size
from vllm.lora.request import LoRARequest
from vllm.sampling_params import RequestOutputKind

from .. import config
from ..schemas import UsageReport

logger = logging.getLogger(__name__)

THINK_OPEN = "<think>"
THINK_CLOSE = "</think>"


@dataclass
class StreamChunk:
    delta: str
    text: str
    finished: bool
    usage: UsageReport | None = None
    think_text: str | None = None
    thinking: bool = False
    finish_reason: str | None = None


def _split_think_and_answer(text: str) -> tuple[str, str, bool]:
    """Return (think_text, answer_text, thinking_active)."""

    lowered = text.lower()
    start = lowered.find(THINK_OPEN)
    if start == -1:
        return "", text.strip(), False

    start_idx = start + len(THINK_OPEN)
    end = lowered.find(THINK_CLOSE, start_idx)

    prefixed = text[:start]
    if end == -1:
        think_section = text[start_idx:]
        answer_text = prefixed.strip()
        return think_section.strip(), answer_text, True

    think_section = text[start_idx:end]
    suffix = text[end + len(THINK_CLOSE) :]
    answer_text = (prefixed + suffix).strip()
    return think_section.strip(), answer_text, False


def _strip_think_tag(text):
    _, answer_text, _ = _split_think_and_answer(text)
    return answer_text


def _maybe_resolve_local_path(path_like):
    if path_like is None:
        return None
    candidate = Path(path_like).expanduser()
    if candidate.exists():
        return str(candidate.resolve())
    return str(path_like)


class LocalVLLMEngine:
    def __init__(self, variant_name: str, profile: dict):
        self.lora_request: LoRARequest | None = None
        self.variant = variant_name
        self.display_name = profile.get("display_name", variant_name)

        base_model = _maybe_resolve_local_path(profile.get("base_model"))
        tokenizer_source = base_model

        adapter_path = profile.get("weights_path")
        adapter_path = _maybe_resolve_local_path(adapter_path)
        if adapter_path:
            adapter_path = Path(adapter_path).expanduser()
            adapter_cfg = adapter_path / "adapter_config.json"
            if adapter_cfg.exists():
                adapter_name = adapter_path.name
                adapter_root = str(adapter_path.resolve())
                self.lora_request = LoRARequest(
                    adapter_name, 1, adapter_root
                )
            else:
                resolved = str(adapter_path.resolve())
                base_model = resolved
                tokenizer_source = resolved

        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_source,
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        tensor_parallel = int(
            profile.get("tensor_parallel_size", config.TENSOR_PARALLEL_SIZE)
        )
        gpu_utilization = float(
            profile.get("gpu_memory_utilization", config.GPU_MEMORY_UTILIZATION)
        )

        self.llm = LLM(
            model=base_model,
            tokenizer=tokenizer_source,
            tensor_parallel_size=tensor_parallel,
            trust_remote_code=True,
            gpu_memory_utilization=gpu_utilization,
            enable_lora=self.lora_request is not None,
        )

        self.sampling_params = SamplingParams(
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
            max_tokens=config.MAX_NEW_TOKENS,
            seed=config.SEED
        )

    def _prepare_prompt(self, history, user_message):
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend([msg.dict() for msg in history])
        messages.append({"role": "user", "content": user_message})
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    def _generate_sync(self, history, user_message):
        prompt = self._prepare_prompt(history, user_message)
        outputs = self.llm.generate(
            [prompt],
            sampling_params=self.sampling_params,
            lora_request=self.lora_request,
        )
        if not outputs or not outputs[0].outputs:
            raise RuntimeError("vLLM returned an empty response.")

        first = outputs[0]
        ## <think> 부분은 굳이 안 보여줘도 될 듯
        text = _strip_think_tag(first.outputs[0].text.strip())
        prompt_tokens = len(first.prompt_token_ids or [])
        completion_tokens = len(first.outputs[0].token_ids or [])
        usage = UsageReport(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        return text, usage

    def stream_generate(self, history, user_message) -> Iterator[StreamChunk]:
        prompt = self._prepare_prompt(history, user_message)

        sampling_params = deepcopy(self.sampling_params)
        sampling_params.output_kind = RequestOutputKind.CUMULATIVE

        request_id = str(next(self.llm.request_counter))
        model_config = self.llm.llm_engine.model_config
        tokenization_kwargs: dict[str, Any] = {}
        _validate_truncation_size(
            model_config.max_model_len,
            sampling_params.truncate_prompt_tokens,
            tokenization_kwargs,
        )

        self.llm.llm_engine.add_request(
            request_id,
            prompt,
            sampling_params,
            lora_request=self.lora_request,
            tokenization_kwargs=tokenization_kwargs,
        )

        last_clean_text = ""
        finished = False
        while self.llm.llm_engine.has_unfinished_requests() and not finished:
            step_outputs = self.llm.llm_engine.step()
            for output in step_outputs:
                if output.request_id != request_id or not output.outputs:
                    continue

                raw_text = output.outputs[0].text or ""
                think_text, clean_text, think_active = _split_think_and_answer(
                    raw_text
                )
                if clean_text.startswith(last_clean_text):
                    delta = clean_text[len(last_clean_text) :]
                else:
                    delta = clean_text
                last_clean_text = clean_text

                usage = None
                finish_reason = None
                finished = output.finished and output.outputs[0].finished()
                if finished:
                    prompt_tokens = len(output.prompt_token_ids or [])
                    completion_tokens = len(output.outputs[0].token_ids or [])
                    finish_reason_raw = getattr(
                        output.outputs[0], "finish_reason", None
                    )
                    if finish_reason_raw is not None:
                        finish_reason = getattr(
                            finish_reason_raw, "value", None
                        ) or str(finish_reason_raw)
                    usage = UsageReport(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    )

                think_payload = think_text if think_text else None

                yield StreamChunk(
                    delta=delta,
                    text=clean_text,
                    finished=finished,
                    usage=usage,
                    think_text=think_payload,
                    thinking=think_active,
                    finish_reason=finish_reason,
                )

    async def generate(self, history, user_message):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, history, user_message
        )

_ENGINES: dict[str, LocalVLLMEngine] = {}

def _get_variant_profile(variant: str) -> dict:
    try:
        return config.MODEL_VARIANTS[variant]
    except KeyError as exc:
        raise ValueError(f"Unknown model variant '{variant}'") from exc

def _ensure_local_engine(variant: str):
    engine = _ENGINES.get(variant)
    if engine is None:
        profile = _get_variant_profile(variant)
        device_scope = profile.get("device_ids")
        logger.info(
            "Bootstrapping vLLM engine for variant '%s' with base model %s (devices=%s)",
            variant,
            profile.get("base_model"),
            device_scope or "all",
        )
        previous_devices = os.environ.get("CUDA_VISIBLE_DEVICES")
        try:
            if device_scope:
                os.environ["CUDA_VISIBLE_DEVICES"] = device_scope
            engine = LocalVLLMEngine(variant, profile)
        finally:
            if device_scope:
                if previous_devices is None:
                    os.environ.pop("CUDA_VISIBLE_DEVICES", None)
                else:
                    os.environ["CUDA_VISIBLE_DEVICES"] = previous_devices

        _ENGINES[variant] = engine
    return engine

def warm_up_local_engine():
    """Eagerly initialize the local vLLM engine so chat requests don't block."""

    for variant_key in config.MODEL_VARIANTS.keys():
        try:
            _ensure_local_engine(variant_key)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to warm up variant: %s", variant_key)


async def generate_reply(history, user_message, model_variant):
    """Generate a reply via the locally hosted vLLM."""

    engine = _ensure_local_engine(model_variant)
    return await engine.generate(history, user_message), engine.display_name


def stream_reply_chunks(history, user_message, model_variant):
    """Return display name and streaming iterator."""

    engine = _ensure_local_engine(model_variant)
    return engine.display_name, engine.stream_generate(history, user_message)
