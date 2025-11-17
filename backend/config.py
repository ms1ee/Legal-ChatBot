from pathlib import Path

MODEL_DISPLAY_NAME = "LexAI-Qwen3 1.7B"
MAX_NEW_TOKENS = 8192
TEMPERATURE = 0
TOP_P = 0.1

LOCAL_BASE_MODEL = Path("local_model/Qwen3-1.7B")
LOCAL_WEIGHTS_PATH = Path("local_model/LoRA")
LOCAL_MODEL_OUT = Path("local_model/merged")

TENSOR_PARALLEL_SIZE = 4
GPU_MEMORY_UTILIZATION = 0.85
RUNTIME_BACKEND="hf-mps" # or "vllm"
SYSTEM_PROMPT = (
    "당신은 'Lexi'라는 이름의 한국 법률 전문가입니다. "
    "핵심 요약만 전달하고 불필요한 사족은 덧붙이지 않습니다. "
    "설명할 때 법 조항에 대한 내용을 담지 마세요. "
    "근거가 부족하면 추측하지 말고 명확히 한계를 밝혀 주세요."
    "만약 모르는 내용이라면 모르다고 답변하세요. 만약 없는 내용을 만들어서 제시하면 penalty를 부과하겠습니다. "
    "모든 답변은 한글로 대답하세요."
)
DISCLAIMER = (
    "Lexi is an AI legal assistant based on the Qwen3-1.7B model. "
    "It does not replace professional legal counsel. Verify critical "
    "information with a qualified attorney."
)
