# merge_lora.py

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import config

def main():
    base = AutoModelForCausalLM.from_pretrained(
        config.LOCAL_BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="mps",
    )
    tokenizer = AutoTokenizer.from_pretrained(
        config.LOCAL_BASE_MODEL,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(
        base,
        config.LOCAL_LORA_MODEL,
        torch_dtype=torch.float16,
    )
    model = model.merge_and_unload()
    model.save_pretrained(config.LOCAL_MERGED_MODEL)
    tokenizer.save_pretrained(config.LOCAL_MERGED_MODEL)
    print(f"Saved merged model + tokenizer to: {config.LOCAL_MERGED_MODEL}")

if __name__ == "__main__":
    main()