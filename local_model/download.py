#!/usr/bin/env python3
from huggingface_hub import snapshot_download

def main():
    repo_id = "ms1ee/sft-grpo-onlyLegalKo"
    local_dir = "local_model/sft_rlvr"
    include = ["checkpoint-3500/*"]
    exclude = [
        "*/optimizer.pt",
        "*/scheduler.pt",
        "*/rng_state_*.pth",
        "*/trainer_state.json",
        "*/training_args.bin",
    ]
    snapshot_download(
        repo_id=repo_id,
        revision=None,
        local_dir=local_dir,
        local_dir_use_symlinks=False,   
        allow_patterns=include,    
        ignore_patterns=exclude,   
        resume_download=True,
    )

if __name__ == "__main__":
    main()
