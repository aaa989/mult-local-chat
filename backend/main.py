import os
import time
import httpx
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import io
import PyPDF2
import docx
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("agent-hub")

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

app = FastAPI(title="Agent Hub Backend")

USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
DASHSCOPE_API_URL = os.getenv("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
LLM_MODEL_TEXT = os.getenv("LLM_MODEL_TEXT", "qwen-plus")
LLM_MODEL_VISION = os.getenv("LLM_MODEL_VISION", "qwen-vl-plus")
ASR_MODEL_NAME = os.getenv("ASR_MODEL_NAME", "qwen3-asr-flash")

from ollama_client import ollama_client
from ocr_service import ocr_service
from speech_service import speech_service

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    prompt: str
    system_prompt: str = ""

async def call_llm_gateway(prompt: str, system_prompt: str = "", image_base64: str = None) -> str:
    api_url = DASHSCOPE_API_URL
    if not DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY 环境变量未配置")
    api_key = DASHSCOPE_API_KEY

    model_name = LLM_MODEL_VISION if image_base64 else LLM_MODEL_TEXT

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if image_base64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(api_url, json=payload, headers=headers, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            err_text = e.response.text
            try:
                err_msg = e.response.json().get("error", {}).get("message", err_text)
            except:
                err_msg = err_text
            raise HTTPException(status_code=e.response.status_code, detail=f"大模型报错: {err_msg}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"模型请求失败: {str(e)}")

async def transcribe_audio(audio_bytes: bytes, filename: str, content_type: str) -> str:
    api_url = DASHSCOPE_API_URL
    if not DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY 环境变量未配置")
    api_key = DASHSCOPE_API_KEY

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    audio_data_uri = f"data:{content_type};base64,{audio_base64}"

    payload = {
        "model": ASR_MODEL_NAME,
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

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(api_url, json=payload, headers=headers, timeout=120.0)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            err_text = e.response.text
            try:
                err_msg = e.response.json().get("error", {}).get("message", err_text)
            except:
                err_msg = err_text
            raise HTTPException(status_code=e.response.status_code, detail=err_msg)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    mode = "本地 Ollama" if USE_LOCAL_MODEL else "阿里云通义千问"
    return {"status": "running", "mode": mode, "model": OLLAMA_MODEL if USE_LOCAL_MODEL else "qwen-plus"}

@app.get("/api/models")
async def get_models():
    if USE_LOCAL_MODEL:
        try:
            models = await ollama_client.list_models()
            return {"status": "success", "data": models}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        return {"status": "success", "data": [{"name": "qwen-plus"}, {"name": "qwen-vl-plus"}]}

@app.post("/api/chat")
async def api_chat(req: AgentRequest):
    logger.info(f"[CHAT] 收到请求 | prompt长度={len(req.prompt)} | 内容预览: {req.prompt[:80]!r}")
    sys_prompt = "你是一个智能、友善、全能的AI助手。请自然、准确地回答用户的问题，并提供有帮助的信息。"
    if USE_LOCAL_MODEL:
        logger.info(f"[CHAT] -> 调用本地 Ollama 模型: {OLLAMA_MODEL}")
        try:
            t0 = time.time()
            result = await ollama_client.generate(req.prompt, sys_prompt)
            logger.info(f"[CHAT] <- Ollama 返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"[CHAT] Ollama 调用失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.info(f"[CHAT] -> 调用阿里云 DashScope (qwen-plus)")
        try:
            t0 = time.time()
            result = await call_llm_gateway(req.prompt, sys_prompt)
            logger.info(f"[CHAT] <- 阿里云返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"[CHAT] 阿里云调用失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coder")
async def api_auto_coder(req: AgentRequest):
    logger.info(f"[CODER] 收到请求 | prompt长度={len(req.prompt)} | 内容预览: {req.prompt[:80]!r}")
    sys_prompt = "你是一个顶尖的全栈软件架构师。请根据用户需求输出高质量代码。务必在回答最后使用 Markdown 代码块包裹代码，并准确标注编程语言（如 ```javascript, ```python 等）。"
    if USE_LOCAL_MODEL:
        logger.info(f"[CODER] -> 调用本地 Ollama 模型: {OLLAMA_MODEL}")
        try:
            t0 = time.time()
            result = await ollama_client.generate(req.prompt, sys_prompt)
            logger.info(f"[CODER] <- Ollama 返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"[CODER] Ollama 调用失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.info(f"[CODER] -> 调用阿里云 DashScope (qwen-plus)")
        try:
            t0 = time.time()
            result = await call_llm_gateway(req.prompt, sys_prompt)
            logger.info(f"[CODER] <- 阿里云返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"[CODER] 阿里云调用失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research")
async def api_deep_research(req: AgentRequest):
    logger.info(f"[RESEARCH] 收到请求 | prompt长度={len(req.prompt)} | 内容预览: {req.prompt[:80]!r}")
    sys_prompt = "你是一个严谨的资深行业研究员。请对给定主题进行深度剖析。直接输出排版干净、优雅的自然语言或Markdown排版。绝对不要包含任何JSON格式、特殊符号或复杂的代码包裹。"
    if USE_LOCAL_MODEL:
        logger.info(f"[RESEARCH] -> 调用本地 Ollama 模型: {OLLAMA_MODEL}")
        try:
            t0 = time.time()
            result = await ollama_client.generate(req.prompt, sys_prompt)
            logger.info(f"[RESEARCH] <- Ollama 返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"[RESEARCH] Ollama 调用失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        logger.info(f"[RESEARCH] -> 调用阿里云 DashScope (qwen-plus)")
        try:
            t0 = time.time()
            result = await call_llm_gateway(req.prompt, sys_prompt)
            logger.info(f"[RESEARCH] <- 阿里云返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"[RESEARCH] 阿里云调用失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr")
async def api_ocr(file: UploadFile = File(...), prompt: str = Form(None)):
    logger.info(f"[OCR] ========== 收到新请求 ==========")
    logger.info(f"[OCR] 文件名: {file.filename} | content_type: {file.content_type} | 附加 prompt: {prompt!r}")

    content = await file.read()
    filename = file.filename.lower()
    extracted_text = ""
    image_base64 = None
    logger.info(f"[OCR] 文件大小: {len(content)} bytes")

    try:
        if filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            logger.info(f"[OCR] PDF 解析完成 | 提取文本长度: {len(extracted_text)}")
            if not extracted_text.strip():
                return {"status": "error", "data": "未能从 PDF 中提取到文本。若是纯图片扫描件，请尝试上传图片格式。"}

        elif filename.endswith('.docx'):
            try:
                doc = docx.Document(io.BytesIO(content))
                extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text])
                logger.info(f"[OCR] DOCX 解析完成 | 提取文本长度: {len(extracted_text)}")
                if not extracted_text.strip():
                    return {"status": "error", "data": "未能从 Word 文档中提取到文字，可能是纯图片Word。"}
            except Exception as e:
                return {"status": "error", "data": f"Word 文档解析异常: {str(e)}"}

        elif filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            image_base64 = base64.b64encode(content).decode('utf-8')
            logger.info(f"[OCR] 图片 base64 长度: {len(image_base64)}")
            is_pure_ocr = (not prompt)
            
            if prompt:
                logger.info(f"[OCR] -> 调用 ocr_service.recognize_image (传图+prompt | 问答模式)")
                try:
                    t0 = time.time()
                    ocr_result = await ocr_service.recognize_image(image_base64, prompt, is_pure_ocr=False)
                    logger.info(f"[OCR] <- 返回成功 | 耗时 {time.time()-t0:.2f}s | 长度 {len(ocr_result)}")
                    return {"status": "success", "data": ocr_result}
                except Exception as e:
                    logger.error(f"[OCR] OCR 失败: {e}")
                    return {"status": "error", "data": f"OCR识别失败: {str(e)}"}
            else:
                logger.info(f"[OCR] -> 调用 ocr_service.recognize_image (纯 OCR 识别模式)")
                try:
                    t0 = time.time()
                    ocr_result = await ocr_service.recognize_image(image_base64, "", is_pure_ocr=True)
                    logger.info(f"[OCR] <- 返回成功 | 耗时 {time.time()-t0:.2f}s | 长度 {len(ocr_result)}")
                    return {"status": "success", "data": ocr_result}
                except Exception as e:
                    logger.error(f"[OCR] OCR 失败: {e}")
                    return {"status": "error", "data": f"OCR识别失败: {str(e)}"}

        elif filename.endswith(('.txt', '.md', '.csv')):
            extracted_text = content.decode('utf-8', errors='ignore')
            logger.info(f"[OCR] 纯文本读取完成 | 长度: {len(extracted_text)}")
        else:
            return {"status": "error", "data": f"暂不支持解析该文件格式: {filename}"}
    except Exception as e:
        return {"status": "error", "data": f"文件解析失败: {str(e)}"}

    if prompt and not filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        extracted_text += f"\n\n--- 用户的具体问题/要求 ---\n{prompt}"

    sys_prompt = """你是一个高级多模态文档分析专家。
请对提取出的文档文本或图片内容进行自然语言总结和重组。
要求：
1. 绝对不要输出 JSON 格式。
2. 用流畅的自然语言、清晰的段落结构来汇报。
3. 如果用户有具体的附加问题，请优先解答用户的问题。"""

    try:
        if USE_LOCAL_MODEL:
            logger.info(f"[OCR] -> 调用本地 Ollama 模型: {OLLAMA_MODEL} | 输入文本长度 {len(extracted_text)}")
            t0 = time.time()
            result = await ollama_client.generate(extracted_text, sys_prompt)
            logger.info(f"[OCR] <- Ollama 返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
        else:
            logger.info(f"[OCR] -> 调用阿里云 qwen-vl-plus (含图片) | 输入文本长度 {len(extracted_text)}")
            t0 = time.time()
            result = await call_llm_gateway(extracted_text, sys_prompt, image_base64)
            logger.info(f"[OCR] <- 阿里云返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[OCR] 模型分析失败: {e}")
        return {"status": "error", "data": f"分析失败: {str(e)}"}

@app.post("/api/speech")
async def api_speech_analysis(file: UploadFile = File(...), prompt: str = Form(None)):
    logger.info(f"[SPEECH] ========== 收到新请求 ==========")
    logger.info(f"[SPEECH] 文件名: {file.filename} | content_type: {file.content_type} | 附加 prompt: {prompt!r}")

    content = await file.read()
    logger.info(f"[SPEECH] 文件大小: {len(content)} bytes")

    filename = file.filename or "audio_record.webm"
    content_type = file.content_type or "audio/webm"

    if "." not in filename:
        if "wav" in content_type:
            filename += ".wav"
        elif "mp3" in content_type:
            filename += ".mp3"
        else:
            filename += ".webm"

    try:
        logger.info(f"[SPEECH] -> 调用 speech_service.transcribe (阿里云 qwen3-asr-flash)")
        t0 = time.time()
        transcript = await speech_service.transcribe(content, content_type)
        logger.info(f"[SPEECH] <- 阿里云 ASR 返回 | 耗时 {time.time()-t0:.2f}s | 转写长度 {len(transcript)}")
        if not transcript:
            return {"status": "error", "data": "未能识别出语音内容，音频可能为空或全为噪音。"}
    except HTTPException as he:
        logger.error(f"[SPEECH] 阿里云语音接口 HTTP 错误: {he.detail}")
        return {"status": "error", "data": f"阿里云语音接口报错: {he.detail}"}
    except Exception as e:
        logger.error(f"[SPEECH] 音频发送异常: {e}")
        return {"status": "error", "data": f"音频发送异常: {str(e)}"}

    if prompt:
        prompt_text = f"以下是语音转写结果：\n\n{transcript}\n\n--- 用户的附加问题/要求 ---\n{prompt}"
        sys_prompt = """你是一个全能的智能语音语义分析专家。
请对用户的语音转写文本进行深度理解。
请输出排版优雅的自然语言，包含：
1. 语音转写原文（引用格式）。
2. 如果用户有附加提问，请优先解答提问。
3. 分析说话者的深层语义与意图。"""
    else:
        logger.info(f"[SPEECH] 纯语音识别模式，直接返回原始转写结果")
        return {"status": "success", "data": transcript}

    try:
        if USE_LOCAL_MODEL:
            logger.info(f"[SPEECH] -> 调用本地 Ollama 模型: {OLLAMA_MODEL} | 转写文本长度 {len(transcript)}")
            t0 = time.time()
            result = await ollama_client.generate(prompt_text, sys_prompt)
            logger.info(f"[SPEECH] <- Ollama 返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
        else:
            logger.info(f"[SPEECH] -> 调用阿里云 qwen-plus 整理转写文本")
            t0 = time.time()
            result = await call_llm_gateway(prompt_text, sys_prompt)
            logger.info(f"[SPEECH] <- 阿里云返回成功 | 耗时 {time.time()-t0:.2f}s | 返回长度 {len(result)}")
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[SPEECH] 语义模型调用失败: {e}")
        return {"status": "error", "data": f"语义模型报错: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    logger.info(f"========== Agent Hub Backend 启动 ==========")
    logger.info(f"  HOST: {host}")
    logger.info(f"  PORT: {port}")
    logger.info(f"  USE_LOCAL_MODEL: {USE_LOCAL_MODEL}")
    logger.info(f"  OLLAMA_MODEL: {OLLAMA_MODEL}")
    logger.info(f"  DASHSCOPE_API_KEY: {'已配置 (***' + DASHSCOPE_API_KEY[-6:] + ')' if DASHSCOPE_API_KEY else '未配置'}")
    logger.info(f"===========================================")
    uvicorn.run(app, host=host, port=port)
