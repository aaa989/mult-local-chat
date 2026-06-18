import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")

class OllamaClient:
    def __init__(self, host: str = None, model: str = None):
        self.host = host or OLLAMA_HOST
        self.model = model or DEFAULT_MODEL
        self.client = httpx.AsyncClient(base_url=self.host, timeout=120.0)

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 2048
            }
        }

        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama API 错误: {e.response.text}")
        except Exception as e:
            raise Exception(f"Ollama 请求失败: {str(e)}")

    async def generate_with_image(self, prompt: str, image_base64: str, system_prompt: str = "", model: str = None) -> str:
        use_model = model or self.model
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({
            "role": "user",
            "content": prompt,
            "images": [image_base64]
        })

        payload = {
            "model": use_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_tokens": 2048
            }
        }

        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama 视觉模型 API 错误: {e.response.text}")
        except Exception as e:
            raise Exception(f"Ollama 视觉模型请求失败: {str(e)}")

    async def generate_stream(self, prompt: str, system_prompt: str = ""):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "max_tokens": 2048
            }
        }

        try:
            async with self.client.post("/api/chat", json=payload) as response:
                response.raise_for_status()
                async for chunk in response.aiter_lines():
                    if chunk:
                        data = json.loads(chunk)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        if data.get("done", False):
                            break
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama API 错误: {e.response.text}")
        except Exception as e:
            raise Exception(f"Ollama 请求失败: {str(e)}")

    async def list_models(self) -> list:
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            raise Exception(f"获取模型列表失败: {str(e)}")

    async def close(self):
        await self.client.aclose()

ollama_client = OllamaClient()
