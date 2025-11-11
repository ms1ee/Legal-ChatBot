# Lexi Legal Chatbot

Streamlit 프런트엔드와 FastAPI 백엔드를 이용해, vLLM 위에 올라간 사내 파인튜닝 모델(Qwen3-1.7B)을 그대로 응답 엔진으로 쓰는 챗봇입니다. 외부 데이터셋에 의존하지 않고, vLLM 서버가 제공하는 OpenAI 호환 API만 활용합니다.

## Project layout

```
chatbot/
  backend/    FastAPI 앱, 설정, vLLM 클라이언트
  frontend/   Streamlit UI (모델/세션 정보 + 대화/로그 뷰)
  chat_logs/  대화 기록(JSON)
eval/         기존 평가 스크립트 및 체크포인트
requirements.txt   공통 파이썬 의존성
```

## Configuration

`chatbot/backend/config.py`에서 읽는 주요 환경 변수:

| Variable | Default | Description |
| --- | --- | --- |
| `VLLM_API_URL` | `http://127.0.0.1:8000/v1/chat/completions` | vLLM OpenAI 엔드포인트 |
| `VLLM_MODEL_NAME` | `qwen3-1.7B-lexi` | vLLM 실행 시 `--served-model-name` 값 |
| `MODEL_DISPLAY_NAME` | `Lexi · Qwen3 1.7B` | 프런트엔드에 노출되는 모델 표시 이름 |
| `MAX_NEW_TOKENS` | `512` | 응답 토큰 최대치 |
| `TEMPERATURE` | `0.15` | 샘플링 온도 |
| `TOP_P` | `0.95` | Nucleus sampling 값 |
| `USE_LOCAL_VLLM` | `false` | `true`면 FastAPI 프로세스 안에서 vLLM 실행 |
| `LOCAL_BASE_MODEL` | `Qwen/Qwen3-1.7B` | 내장 모드에서 사용할 베이스 모델 |
| `LOCAL_WEIGHTS_PATH` | `eval/checkpoints/grpo_checkpoints/only_grpo` | 파인튜닝 가중치/LoRA 경로 |
| `TENSOR_PARALLEL_SIZE` | `1` | vLLM 텐서 병렬 크기 |
| `GPU_MEMORY_UTILIZATION` | `0.9` | GPU 메모리 사용률 힌트 |

`.env` 파일은 `chatbot/` 디렉토리에 두고, 필요 시 `export VAR=value` 로 덮어쓸 수 있습니다.

## Setup and execution

1. **의존성 설치 (Conda)**

   ```bash
   cd /home/xailaw
   conda env create -f environment.yml
   conda activate lexi-chatbot
   ```

   이미 환경이 있다면 `conda env update -f environment.yml --prune` 로 동기화하세요.

2. **LLM 실행 방식 선택**

   - **옵션 A · 외부 vLLM 서버** (기존 방식)

     ```bash
     python -m vllm.entrypoints.openai.api_server \
       --model eval/checkpoints/grpo_checkpoints/only_grpo \
       --served-model-name qwen3-1.7B-lexi \
       --tensor-parallel-size 1 \
       --host 0.0.0.0 --port 8000
     ```

     모델 경로가 바뀌면 `--model` 인자만 업데이트하면 됩니다.

   - **옵션 B · FastAPI 프로세스 안에서 vLLM 직접 실행**

     `.env` 혹은 환경 변수로 아래 값을 지정하면 `eval/scripts/llm.py` 와 동일한 방식으로 LLM을 애플리케이션이 직접 로딩합니다.

     ```bash
     export USE_LOCAL_VLLM=true
     export LOCAL_BASE_MODEL="Qwen/Qwen3-1.7B"
     export LOCAL_WEIGHTS_PATH="eval/checkpoints/grpo_checkpoints/only_grpo"
     export TENSOR_PARALLEL_SIZE=1
     export GPU_MEMORY_UTILIZATION=0.9
     ```

     `LOCAL_WEIGHTS_PATH` 안에 `adapter_config.json` 이 있으면 LoRARequest 를 자동으로 붙이고, 없으면 완전한 모델 가중치로 간주합니다.

3. **FastAPI 백엔드 실행**

   ```bash
   cd /home/xailaw/chatbot
   export VLLM_API_URL="http://127.0.0.1:8000/v1/chat/completions"
   export VLLM_MODEL_NAME="qwen3-1.7B-lexi"
   uvicorn backend.main:app --port 9000 --reload
   ```

4. **Streamlit 프런트엔드 실행**

   ```bash
   cd /home/xailaw/chatbot
   export LEXI_BACKEND_URL="http://127.0.0.1:9000"
   streamlit run frontend/streamlit_app.py
   ```

   기본 주소 `http://localhost:8501` 에서 좌측에는 모델/세션 정보 카드, 우측에는 대화창이 표시됩니다. “Reset chat” 버튼으로 컨텍스트를 초기화할 수 있습니다.

## Notes

- 백엔드는 `/health`, `/chat`, `/conversations`, `/conversations/{id}` 엔드포인트를 노출하며, 모든 답변은 로컬 vLLM에서 생성됩니다.
- 시스템 프롬프트/면책 문구는 `backend/config.py`에서 한 곳에 관리합니다.
- 좌측 UI에 노출되는 채팅 로그는 `chatbot/chat_logs/` 디렉터리에 JSON 파일로 저장됩니다.
