from pathlib import Path

MODEL_DISPLAY_NAME = "Lexi-Qwen3 1.7B"
MAX_NEW_TOKENS = 8192
TEMPERATURE = 0.15
TOP_P = 0.95

LOCAL_BASE_MODEL = "Qwen/Qwen3-1.7B"
LOCAL_WEIGHTS_PATH = Path("local_model/")
TENSOR_PARALLEL_SIZE = 4
GPU_MEMORY_UTILIZATION = 0.85

SYSTEM_PROMPT = (
    "당신은 'Lexi'라는 이름의 한국 법률 전문가입니다. "
    "정확한 판례·조문·절차 정보를 근거와 함께 제시하되, 핵심 요약만 전달하고 불필요한 사족은 덧붙이지 않습니다. "
    "근거가 부족하면 추측하지 말고 명확히 한계를 밝혀 주세요."
)
DISCLAIMER = (
    "Lexi is an AI legal assistant based on the Qwen3-1.7B model. "
    "It does not replace professional legal counsel. Verify critical "
    "information with a qualified attorney."
)
