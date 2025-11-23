# LexAI Legal Chatbot

## Setup (For Mac)
1. Clone Repository
```bash
git clone -b macOS https://github.com/ms1ee/Legal-ChatBot
cd Legal-ChatBot
```
2. Install Dependency
```bash
conda create --name lexai python==3.10
conda activate lexai
pip install -r requirements.txt
```
3. Download Model
```bash
# Download basline model
huggingface-cli download Qwen/Qwen3-1.7B \
   --local-dir local_model/Qwen3-1.7B \
   --local-dir-use-symlinks False

# Download fine-tuned model (ours)
huggingface-cli download ms1ee/sft-grpo-onlyLegalKo \
  --include "checkpoint-3500/*" \
  --exclude "*/optimizer.pt" \
  --exclude "*/scheduler.pt" \
  --exclude "*/rng_state_*.pth" \
  --exclude "*/trainer_state.json" \
  --exclude "*/training_args.bin" \
  --local-dir local_model/sft_rlvr \
  --local-dir-use-symlinks False
```
4. Run Backend
```bash
./open_server.sh
```
5. Run Frontend
```bash
./run_app.sh
```
