# merge_lora.py

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import config

BASE = config.LOCAL_BASE_MODEL
LORA = config.LOCAL_WEIGHTS_PATH
OUT  = config.LOCAL_MODEL_OUT

def main():
    base = AutoModelForCausalLM.from_pretrained(
        BASE,
        torch_dtype=torch.float16,
        device_map="mps",
    )
    tokenizer = AutoTokenizer.from_pretrained(
        BASE,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(
        base,
        LORA,
        torch_dtype=torch.float16,
    )
    model = model.merge_and_unload()
    model.save_pretrained(OUT)
    tokenizer.save_pretrained(OUT)
    print(f"Saved merged model + tokenizer to: {OUT}")

if __name__ == "__main__":
    main()