import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("agent-hub")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"
VISION_MODEL = os.getenv("VISION_MODEL", "minicpm-v")


class OCRService:
    def __init__(self):
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        from ollama_client import ollama_client
        self.ollama_client = ollama_client

    async def recognize_image(self, image_base64: str, prompt: str = "", is_pure_ocr: bool = True) -> str:
        if USE_LOCAL_MODEL:
            logger.info(f"[OCR-Service] -> 本地视觉模型 {VISION_MODEL} | is_pure_ocr={is_pure_ocr}")
            try:
                if is_pure_ocr:
                    use_prompt = "请仔细识别图片中的所有文字内容，严格按照原文逐字逐句输出，只输出识别到的文字，不要做任何解释、总结、格式修饰或添加其他内容。"
                else:
                    use_prompt = prompt or "请描述这张图片的内容。"

                result = await self.ollama_client.generate_with_image(
                    prompt=use_prompt,
                    image_base64=image_base64,
                    model=VISION_MODEL
                )
                return result
            except Exception as e:
                logger.error(f"[OCR-Service] 本地视觉模型调用失败: {e}")
                raise Exception(f"本地 OCR 识别失败: {str(e)}")
        else:
            if not DASHSCOPE_API_KEY:
                raise Exception("未配置 DASHSCOPE_API_KEY 环境变量")

            import httpx
            headers = {
                "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
                "Content-Type": "application/json"
            }

            content = [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]

            if is_pure_ocr:
                use_prompt = "请仔细识别图片中的所有文字内容，严格按照原文逐字逐句输出，只输出识别到的文字，不要做任何解释、总结、格式修饰或添加其他内容。"
                content.insert(0, {"type": "text", "text": use_prompt})
            elif prompt:
                content.insert(0, {"type": "text", "text": prompt})

            payload = {
                "model": "qwen-vl-plus",
                "messages": [
                    {"role": "user", "content": content}
                ],
                "temperature": 0.3,
            }

            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(self.api_url, json=payload, headers=headers, timeout=60.0)
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                err_text = e.response.text
                try:
                    err_msg = e.response.json().get("error", {}).get("message", err_text)
                except Exception:
                    err_msg = err_text
                raise Exception(f"OCR 识别失败: {err_msg}")
            except Exception as e:
                raise Exception(f"OCR 请求失败: {str(e)}")


ocr_service = OCRService()
