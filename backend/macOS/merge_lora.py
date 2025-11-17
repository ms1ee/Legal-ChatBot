# merge_lora.py

import torch
from transformers import AutoModelForCausalLM
from peft import PeftModel
from ..backend.config import *

BASE = LOCAL_BASE_MODEL
LORA = LOCAL_WEIGHTS_PATH
OUT  = LOCAL_MODEL_OUT

def main():
    base = AutoModelForCausalLM.from_pretrained(
        BASE,
        torch_dtype=torch.float16,
        device_map="mps",
    )

    model = PeftModel.from_pretrained(
        base,
        LORA,
        torch_dtype=torch.float16,
    )

    model = model.merge_and_unload()

    model.save_pretrained(OUT)
    print(f"Saved merged model to: {OUT}")

if __name__ == "__main__":
    main()
