import asyncio
import logging
import os
import re
from collections.abc import Iterator
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transformers import AutoModelForCausalLM, AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.entrypoints.utils import _validate_truncation_size
from vllm.lora.request import LoRARequest
from vllm.sampling_params import RequestOutputKind
import torch
from peft import PeftModel

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


def _strip_think_tag(text):
    lowered = text.lower()
    result = []
    idx = 0
    while idx < len(text):
        start = lowered.find(THINK_OPEN, idx)
        if start == -1:
            result.append(text[idx:])
            break
        result.append(text[idx:start])
        end = lowered.find(THINK_CLOSE, start)
        if end == -1:
            # Drop everything after an opening tag with no closing tag yet.
            break
        idx = end + len(THINK_CLOSE)
    cleaned = "".join(result)
    return cleaned.strip()


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
                clean_text = _strip_think_tag(raw_text)
                if clean_text.startswith(last_clean_text):
                    delta = clean_text[len(last_clean_text) :]
                else:
                    delta = clean_text
                last_clean_text = clean_text

                usage = None
                finished = output.finished and output.outputs[0].finished()
                if finished:
                    prompt_tokens = len(output.prompt_token_ids or [])
                    completion_tokens = len(output.outputs[0].token_ids or [])
                    usage = UsageReport(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    )

                yield StreamChunk(
                    delta=delta,
                    text=clean_text,
                    finished=finished,
                    usage=usage,
                )

    async def generate(self, history, user_message):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, history, user_message
        )


import threading
from transformers import TextIteratorStreamer

_GENERATE_LOCK = threading.Lock()

class LocalHFEngine:
    def __init__(self, variant_name: str, profile: dict):
        self.variant = variant_name
        self.display_name = profile.get("display_name", variant_name)
        
        base_model = _maybe_resolve_local_path(profile.get("base_model"))
        tokenizer_source = base_model

        adapter_path = profile.get("weights_path")

        self.lora_path = None
        if adapter_path:
             adapter_path = _maybe_resolve_local_path(adapter_path)
             if adapter_path:
                adapter_path = Path(adapter_path).expanduser()
                adapter_cfg = adapter_path / "adapter_config.json"
                if adapter_cfg.exists():
                    self.lora_path = str(adapter_path.resolve())

        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_source,
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
            logger.warning("MPS is not available. Falling back to CPU for LocalHFEngine.")

        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            trust_remote_code=True,
            torch_dtype=torch.float16,
        ).to(self.device)
        self.model.eval()

        if self.lora_path is not None:
            logger.info("Loading HF LoRA weights from %s", self.lora_path)
            self.model = PeftModel.from_pretrained(
                self.model,
                self.lora_path,
                torch_dtype=torch.float16,
            ).to(self.device)
            self.model.eval()

        self.temperature = config.TEMPERATURE
        self.top_p = config.TOP_P
        self.max_new_tokens = config.MAX_NEW_TOKENS
   
    def _prepare_prompt(self, history, user_message):
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend([msg.dict() for msg in history])
        messages.append({"role": "user", "content": user_message})
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    @torch.no_grad()
    def _generate_sync(self, history, user_message):
        prompt = self._prepare_prompt(history, user_message)

        encoded = self.tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=False,
        ).to(self.device)

        input_ids = encoded["input_ids"]
        attention_mask = encoded.get("attention_mask")

        with _GENERATE_LOCK:
            generated_ids = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                do_sample=True if self.temperature > 0 else False,
                temperature=float(self.temperature),
                top_p=float(self.top_p),
                max_new_tokens=int(self.max_new_tokens),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated_only_ids = generated_ids[:, input_ids.shape[1]:]

        full_text = self.tokenizer.decode(
            generated_only_ids[0],
            skip_special_tokens=True,
        )
        text = _strip_think_tag(full_text.strip())

        prompt_tokens = int(input_ids.shape[1])
        completion_tokens = int(generated_only_ids.shape[1])

        usage = UsageReport(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        return text, usage

    @torch.no_grad()
    def stream_generate(self, history, user_message) -> Iterator[StreamChunk]:
        prompt = self._prepare_prompt(history, user_message)

        encoded = self.tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=False,
        ).to(self.device)

        input_ids = encoded["input_ids"]
        attention_mask = encoded.get("attention_mask")

        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True
        )

        generation_kwargs = dict(
            input_ids=input_ids,
            attention_mask=attention_mask,
            streamer=streamer,
            do_sample=True if self.temperature > 0 else False,
            temperature=float(self.temperature),
            top_p=float(self.top_p),
            max_new_tokens=int(self.max_new_tokens),
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        def thread_target():
            with _GENERATE_LOCK:
                self.model.generate(**generation_kwargs)

        thread = threading.Thread(target=thread_target)
        thread.start()

        full_text = ""
        for new_text in streamer:
            full_text += new_text
            clean_text = _strip_think_tag(full_text)
            yield StreamChunk(
                delta=new_text,
                text=clean_text,
                finished=False,
                usage=None,
            )
        
        thread.join()
        
        prompt_tokens = int(input_ids.shape[1])
        completion_tokens = len(self.tokenizer.encode(full_text))

        usage = UsageReport(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

        yield StreamChunk(
            delta="",
            text=_strip_think_tag(full_text),
            finished=True,
            usage=usage,
        )
    
    async def generate(self, history, user_message):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, history, user_message
        )


class LocalMLXEngine:
    def __init__(self, variant_name: str, profile: dict):
        self.variant = variant_name
        self.display_name = profile.get("display_name", variant_name)
        
        from mlx_lm import load as mlx_load, generate as mlx_generate, stream_generate as mlx_stream_generate
        from mlx_lm.sample_utils import make_sampler
        self._mlx_generate = mlx_generate
        self._mlx_stream_generate = mlx_stream_generate
        
        model_id = _maybe_resolve_local_path(profile.get("base_model"))
        logger.info("Loading MLX model from %s", model_id)
        self.model, self.tokenizer = mlx_load(model_id)
        if getattr(self.tokenizer, "pad_token", None) is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        self.sampler = make_sampler(
            temp=config.TEMPERATURE,
            top_p=config.TOP_P,
        )
        self.max_new_tokens = config.MAX_NEW_TOKENS

    def _prepare_prompt(self, history, user_message):
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend([msg.dict() for msg in history])
        messages.append({"role": "user", "content": user_message})
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    def _count_tokens(self, text: str) -> int:
        ids = self.tokenizer.encode(text)
        return len(ids)

    def _generate_sync(self, history, user_message):
        prompt = self._prepare_prompt(history, user_message)

        with _GENERATE_LOCK:
            result = self._mlx_generate(
                self.model,
                self.tokenizer,
                prompt,
                max_tokens=int(self.max_new_tokens),
                sampler=self.sampler,
            )

        if isinstance(result, dict):
            text = result.get("text", "")
        else:
            text = str(result)

        text = _strip_think_tag(text.strip())

        prompt_tokens = self._count_tokens(prompt)
        completion_tokens = self._count_tokens(text)

        usage = UsageReport(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        return text, usage

    def stream_generate(self, history, user_message) -> Iterator[StreamChunk]:
        prompt = self._prepare_prompt(history, user_message)
        prompt_tokens = self._count_tokens(prompt)
        full_text = ""
        with _GENERATE_LOCK:
            generation_stream = self._mlx_stream_generate(
                self.model,
                self.tokenizer,
                prompt,
                max_tokens=int(self.max_new_tokens),
                sampler=self.sampler,
            )
            
            for response in generation_stream:
                if hasattr(response, "text"):
                    delta = response.text
                else:
                    delta = str(response) # Fallback
                
                full_text += delta
                clean_text = _strip_think_tag(full_text)
                
                yield StreamChunk(
                    delta=delta,
                    text=clean_text,
                    finished=False,
                    usage=None,
                )

        completion_tokens = self._count_tokens(full_text)
        usage = UsageReport(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        
        yield StreamChunk(
            delta="",
            text=_strip_think_tag(full_text),
            finished=True,
            usage=usage,
        )

    async def generate(self, history, user_message):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, history, user_message
        )

import ollama
class LocalOllamaEngine:
    def __init__(self, variant_name: str, profile: dict):
        self.variant = variant_name
        self.display_name = profile.get("display_name", variant_name)
        self.model_id = profile.get("ollama_model_name")

    def _prepare_messages(self, history, user_message):
        messages = [msg.dict() for msg in history]
        messages.append({"role": "user", "content": user_message})
        return messages

    def _generate_sync(self, history, user_message):
        messages = self._prepare_messages(history, user_message)
        response = ollama.chat(
            model=self.model_id,
            messages=messages,
            stream=False,
        )
        text = response.get("message", {}).get("content", "")
        text = _strip_think_tag(text.strip())

        prompt_tokens = response.get("prompt_eval_count", 0)
        completion_tokens = response.get("eval_count", 0)

        usage = UsageReport(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        return text, usage

    def stream_generate(self, history, user_message) -> Iterator[StreamChunk]:
        messages = self._prepare_messages(history, user_message)
        full_text = ""
        
        final_prompt_tokens = 0
        final_eval_tokens = 0
        
        stream = ollama.chat(
            model=self.model_id,
            messages=messages,
            stream=True,
        )
        
        for chunk in stream:
            delta = chunk.get("message", {}).get("content", "")
            full_text += delta
            clean_text = _strip_think_tag(full_text)
            
            yield StreamChunk(
                delta=delta,
                text=clean_text,
                finished=False,
                usage=None,
            )
            
            if chunk.get("done", False):
                final_prompt_tokens = chunk.get("prompt_eval_count", 0)
                final_eval_tokens = chunk.get("eval_count", 0)

        usage = UsageReport(
            prompt_tokens=final_prompt_tokens,
            completion_tokens=final_eval_tokens,
            total_tokens=final_prompt_tokens + final_eval_tokens,
        )
        
        yield StreamChunk(
            delta="",
            text=_strip_think_tag(full_text),
            finished=True,
            usage=usage,
        )

    async def generate(self, history, user_message):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, history, user_message
        )
_ENGINES: dict[str, LocalVLLMEngine | LocalHFEngine | LocalMLXEngine | LocalOllamaEngine] = {}


def _get_variant_profile(variant: str) -> dict:
    try:
        return config.MODEL_VARIANTS[variant]
    except KeyError as exc:
        raise ValueError(f"Unknown model variant '{variant}'") from exc


def _ensure_local_engine(variant: str):
    engine = _ENGINES.get(variant)
    if engine is None:
        profile = _get_variant_profile(variant)
        framework = profile.get("framework")

        if framework == "hf-mps":
            logger.info("Bootstrapping HF engine for variant '%s'", variant)
            engine = LocalHFEngine(variant, profile)
        elif framework == "mlx":
            logger.info("Bootstrapping MLX engine for variant '%s'", variant)
            engine = LocalMLXEngine(variant, profile)
        elif framework == "ollama":
            logger.info("Bootstrapping Ollama engine for variant '%s'", variant)
            engine = LocalOllamaEngine(variant, profile)
        else:
            raise ValueError(f"Unknown framework '{framework}' for variant '{variant}'")
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
    display_name = getattr(engine, "display_name", model_variant)
    return await engine.generate(history, user_message), display_name


def stream_reply_chunks(history, user_message, model_variant):
    """Return display name and streaming iterator."""

    engine = _ensure_local_engine(model_variant)
    display_name = getattr(engine, "display_name", model_variant)
    return display_name, engine.stream_generate(history, user_message)
