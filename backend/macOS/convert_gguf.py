import os
import subprocess
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnquantizedConverter:
    def __init__(self, llama_cpp_path: str = "./llama.cpp"):
        self.base_path = Path(llama_cpp_path).resolve()
        self.convert_script = self.base_path / "convert_hf_to_gguf.py"
        
        if not self.convert_script.exists():
            raise FileNotFoundError(f"변환 스크립트 없음: {self.convert_script}\nllama.cpp 폴더 경로를 확인하세요.")

    def convert_fp16(self, input_dir: str, output_dir: str, model_name: str):
        input_path = Path(input_dir).resolve()
        output_path = Path(output_dir).resolve()
        
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{model_name}.fp16.gguf"
        
        logger.info(f"🚀 Starting conversion (No Quantization, FP16)...")
        logger.info(f"   Input: {input_path}")
        logger.info(f"   Output: {output_file}")

        command = [
            "python", str(self.convert_script),
            str(input_path),
            "--outfile", str(output_file),
            "--outtype", "f16" 
        ]
        
        try:
            subprocess.run(command, check=True)
            return output_file
        except subprocess.CalledProcessError as e:
            raise e

if __name__ == "__main__":
    LLAMA_CPP_DIR = "backend/macOS/llama.cpp" 
    OUTPUT_DIR = "local_model/gguf"

    converter = UnquantizedConverter(llama_cpp_path=LLAMA_CPP_DIR)
    
    try:
        INPUT_MODEL_DIR = "local_model/Qwen3-1.7B/"
        MODEL_NAME = "baseline"
        final_path = converter.convert_fp16(
            input_dir=INPUT_MODEL_DIR,
            output_dir=OUTPUT_DIR,
            model_name=MODEL_NAME
        )
        INPUT_MODEL_DIR = "local_model/sft_rlvr/checkpoint-3500/"
        MODEL_NAME = "sft_rlvr" 
        final_path = converter.convert_fp16(
            input_dir=INPUT_MODEL_DIR,
            output_dir=OUTPUT_DIR,
            model_name=MODEL_NAME
        )
    except Exception as e:
        print(f"\n Conver Error :  {e}")   