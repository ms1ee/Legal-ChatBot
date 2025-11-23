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
python3 local_model/download.py
```
4. Run Backend
```bash
./open_server.sh
```
5. Run Frontend
```bash
./run_app.sh
```
