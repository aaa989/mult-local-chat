import os
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_OFFLINE", "0")
import logging
import tempfile
import shutil
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("agent-hub")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"
ASR_MODEL = os.getenv("ASR_MODEL", "base")
ASR_DEVICE = os.getenv("ASR_DEVICE", "cpu")
ASR_COMPUTE_TYPE = os.getenv("ASR_COMPUTE_TYPE", "int8")

MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "whisper")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)


class SpeechService:
    def __init__(self):
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.whisper_model = None

    def _ensure_model_files(self):
        model_dir = os.path.join(MODEL_CACHE_DIR, f"models--Systran--faster-whisper-{ASR_MODEL}")
        snapshots_dir = os.path.join(model_dir, "snapshots")
        blobs_dir = os.path.join(model_dir, "blobs")
        os.makedirs(snapshots_dir, exist_ok=True)
        os.makedirs(blobs_dir, exist_ok=True)

        if os.path.exists(snapshots_dir) and os.listdir(snapshots_dir):
            return os.path.join(snapshots_dir, os.listdir(snapshots_dir)[0])

        logger.info(f"[Speech-Service] 开始下载 Whisper 模型: {ASR_MODEL}")
        logger.info(f"[Speech-Service] 目标目录: {model_dir}")

        download_urls = [
            f"https://hf-mirror.com/Systran/faster-whisper-{ASR_MODEL}/resolve/main/",
            f"https://huggingface.co/Systran/faster-whisper-{ASR_MODEL}/resolve/main/",
        ]

        files_to_download = [
            "config.json",
            "model.bin",
            "tokenizer.json",
            "vocabulary.txt",
        ]

        for base_url in download_urls:
            try:
                logger.info(f"[Speech-Service] 尝试源: {base_url}")
                import urllib.request
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                success = True
                for fname in files_to_download:
                    url = base_url + fname
                    target = os.path.join(snapshots_dir, fname)
                    if os.path.exists(target) and os.path.getsize(target) > 0:
                        continue
                    try:
                        logger.info(f"[Speech-Service] 下载: {fname}")
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                            with open(target, 'wb') as f:
                                shutil.copyfileobj(resp, f)
                        size = os.path.getsize(target)
                        logger.info(f"[Speech-Service] {fname} 下载完成 | {size} bytes")
                    except Exception as fe:
                        logger.warning(f"[Speech-Service] {fname} 下载失败: {fe}")
                        success = False
                        break

                if success and all(os.path.exists(os.path.join(snapshots_dir, f)) for f in files_to_download):
                    logger.info(f"[Speech-Service] 模型下载完成: {snapshots_dir}")
                    return snapshots_dir
            except Exception as e:
                logger.warning(f"[Speech-Service] 源 {base_url} 失败: {e}")
                continue

        return None

    def _load_whisper(self):
        if self.whisper_model is None:
            from faster_whisper import WhisperModel
            logger.info(f"[Speech-Service] 加载本地 Whisper 模型: {ASR_MODEL}")
            logger.info(f"[Speech-Service] 设备: {ASR_DEVICE} | 精度: {ASR_COMPUTE_TYPE}")

            self.whisper_model = WhisperModel(
                ASR_MODEL,
                device=ASR_DEVICE,
                compute_type=ASR_COMPUTE_TYPE
            )
            logger.info(f"[Speech-Service] Whisper 模型加载成功！")
        return self.whisper_model

    async def transcribe(self, audio_bytes: bytes, content_type: str = "audio/webm") -> str:
        if USE_LOCAL_MODEL:
            logger.info(f"[Speech-Service] -> 本地 Whisper ASR")
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._transcribe_local,
                    audio_bytes,
                    content_type
                )
                return result
            except Exception as e:
                import traceback
                logger.error(f"[Speech-Service] 本地 ASR 失败: {e}")
                logger.error(f"[Speech-Service] 完整堆栈:\n{traceback.format_exc()}")
                raise Exception(f"本地语音识别失败: {str(e)}")
        else:
            return await self._transcribe_dashscope(audio_bytes, content_type)

    def _transcribe_local(self, audio_bytes: bytes, content_type: str = "audio/webm") -> str:
        import os as os_module
        model = self._load_whisper()

        ext_map = {
            "audio/webm": ".webm",
            "audio/wav": ".wav",
            "audio/x-wav": ".wav",
            "audio/wave": ".wav",
            "audio/mp3": ".mp3",
            "audio/mpeg": ".mp3",
            "audio/ogg": ".ogg",
            "audio/m4a": ".m4a",
            "audio/mp4": ".mp4",
            "audio/x-m4a": ".m4a",
        }
        ext = ext_map.get(content_type, ".webm")

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            logger.info(f"[Speech-Service] 临时文件: {tmp_path} | 大小: {len(audio_bytes)} bytes")
            segments, info = model.transcribe(
                tmp_path,
                language="zh",
                beam_size=5,
                vad_filter=True
            )
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            full_text = "".join(text_parts).strip()
            logger.info(f"[Speech-Service] 识别完成 | 语言: {info.language} | 文本长度: {len(full_text)}")
            return full_text
        finally:
            try:
                os_module.unlink(tmp_path)
            except Exception:
                pass

    async def _transcribe_dashscope(self, audio_bytes: bytes, content_type: str = "audio/webm") -> str:
        if not DASHSCOPE_API_KEY:
            raise Exception("未配置 DASHSCOPE_API_KEY 环境变量")

        import httpx
        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_data_uri = f"data:{content_type};base64,{audio_base64}"

        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen3-asr-flash",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {"data": audio_data_uri}
                        }
                    ]
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=120.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            err_text = e.response.text
            try:
                err_msg = e.response.json().get("error", {}).get("message", err_text)
            except:
                err_msg = err_text
            raise Exception(f"语音识别失败: {err_msg}")
        except Exception as e:
            raise Exception(f"语音请求失败: {str(e)}")


speech_service = SpeechService()
