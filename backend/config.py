from pathlib import Path

MODEL_DISPLAY_NAME = "LexAI-Qwen3 1.7B"
MAX_NEW_TOKENS = 8192
TEMPERATURE = 0
TOP_P = 0.4
SEED = 42


BASELINE_MODEL = "Qwen/Qwen3-1.7B"
FINETUNED_MODEL = "Qwen/Qwen3-1.7B"
FINETUNED_WEIGHTS_PATH = Path("local_model/")
DEFAULT_MODEL_VARIANT = "finetuned"
COMPARISON_VARIANTS = ("finetuned", "baseline")

MODEL_VARIANTS = {
    "baseline": {
        "display_name": "Qwen3-1.7B (Baseline)",
        "base_model": BASELINE_MODEL,
        "weights_path": None,
        "device_ids": "0,1",
        "tensor_parallel_size": 2,
        "gpu_memory_utilization": 0.85,
    },
    "finetuned": {
        "display_name": MODEL_DISPLAY_NAME,
        "base_model": FINETUNED_MODEL,
        "weights_path": FINETUNED_WEIGHTS_PATH,
        "device_ids": "2,3",
        "tensor_parallel_size": 2,
        "gpu_memory_utilization": 0.85,
    },
}

LOCAL_BASE_MODEL = FINETUNED_MODEL
LOCAL_WEIGHTS_PATH = FINETUNED_WEIGHTS_PATH
TENSOR_PARALLEL_SIZE = 2
GPU_MEMORY_UTILIZATION = 0.85

SYSTEM_PROMPT = (
    "당신은 'Lexi'라는 이름의 한국 법률 전문가입니다. "
    "당신에게 물어보는 질문에 대해서 천천히 단계별로 심도있게 생각하고 답변해주세요."
    "설명할 때 법 조항에 대한 내용을 담지 마세요. "
    "만약 모르는 내용이라면 모르다고 답변하세요. 만약 없는 내용을 만들어서 제시하면 penalty를 부과하겠습니다."
    "모든 답변은 한글로 대답하세요."
    "법률 질문에 대한 답변을 완료한 뒤에는 마지막에 '더 정확한 정보를 원하신다면 변호사와 상담하세요.' 라는 문구를 말해주세요."
)
DISCLAIMER = (
    "Lexi is an AI legal assistant based on the Qwen3-1.7B model. "
    "It does not replace professional legal counsel. Verify critical "
    "information with a qualified attorney."
)
