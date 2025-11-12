import asyncio
import logging
import re
from pathlib import Path

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

from .. import config
from ..schemas import UsageReport

logger = logging.getLogger(__name__)

_LOCAL_ENGINE = None
THINK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_think_tag(text):
    cleaned = THINK_PATTERN.sub("", text)
    return cleaned.strip()


def _maybe_resolve_local_path(path_like):
    if path_like is None:
        return None
    candidate = Path(path_like).expanduser()
    if candidate.exists():
        return str(candidate.resolve())
    return str(path_like)


class LocalVLLMEngine:
    def __init__(self):
        self.lora_request: LoRARequest | None = None

        base_model = _maybe_resolve_local_path(config.LOCAL_BASE_MODEL)
        tokenizer_source = base_model

        adapter_path = config.LOCAL_WEIGHTS_PATH
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

        self.llm = LLM(
            model=base_model,
            tokenizer=tokenizer_source,
            tensor_parallel_size=config.TENSOR_PARALLEL_SIZE,
            trust_remote_code=True,
            gpu_memory_utilization=config.GPU_MEMORY_UTILIZATION,
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

    async def generate(self, history, user_message):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, history, user_message
        )

## 서버 키자마자 vLLM Engine 초기화 & 모델 로드 바로 해
## vLLM 엔진 초기화 한번만 할 수 있도록 체크하는 역할도 함
def _ensure_local_engine():
    global _LOCAL_ENGINE
    if _LOCAL_ENGINE is None:
        logger.info("Bootstrapping local vLLM engine with model %s", config.LOCAL_BASE_MODEL)
        _LOCAL_ENGINE = LocalVLLMEngine()
    return _LOCAL_ENGINE


def warm_up_local_engine():
    """Eagerly initialize the local vLLM engine so chat requests don't block."""

    _ensure_local_engine()


async def generate_reply(history, user_message):
    """Generate a reply via the locally hosted vLLM."""

    engine = _ensure_local_engine()
    return await engine.generate(history, user_message)
