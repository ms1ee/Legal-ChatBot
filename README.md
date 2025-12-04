# LexAI Legal Chatbot
   Note: This guide is optimized for Linux environments. For more information or original configurations (macOS), please check the macos branch.
   
## Setup
1. Clone Repository
```bash
git clone -b main https://github.com/ms1ee/Legal-ChatBot
cd Legal-Chatbot
```
2. Install Dependency
Note: On Linux (especially if using NVIDIA GPUs), it is recommended to ensure PyTorch is installed with the correct CUDA version.

```bash
conda create --name lexai python==3.10
conda activate lexai

# (Optional) If using an NVIDIA GPU, install the CUDA version of PyTorch first
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

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

###