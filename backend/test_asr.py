from faster_whisper import WhisperModel
import os
from dotenv import load_dotenv

load_dotenv()

ASR_MODEL = os.getenv("ASR_MODEL", "base")
ASR_DEVICE = os.getenv("ASR_DEVICE", "cpu")
ASR_COMPUTE_TYPE = os.getenv("ASR_COMPUTE_TYPE", "int8")

model = WhisperModel(ASR_MODEL, device=ASR_DEVICE, compute_type=ASR_COMPUTE_TYPE)
print(f"模型 {ASR_MODEL} 加载成功")