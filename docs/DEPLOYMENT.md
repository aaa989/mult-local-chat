# AI Agent 中台系统 - 模型部署流程

## 一、技术选型说明

### 1.1 整体架构设计

| 层级 | 技术选型 | 选型理由 |
|------|----------|----------|
| 前端框架 | React 19 + Vite 8 | React 生态成熟，社区活跃；Vite 构建速度快，开发体验好 |
| 后端框架 | FastAPI | 高性能异步框架，自动生成 API 文档，类型提示完善 |
| 模型部署 | Ollama | 轻量级本地模型管理工具，支持一键下载和运行多种模型 |
| 模型推理 | Python | 丰富的 AI 库支持，与 Ollama 客户端无缝对接 |

### 1.2 AI 模型选型

#### 1.2.1 大语言模型（LLM）

| 模型名称 | 版本 | 参数规模 | 选型理由 |
|----------|------|----------|----------|
| DeepSeek R1 | 1.5B | 15 亿 | 开源免费，推理速度快，支持中文，适合本地部署 |

**选型对比：**

| 模型 | 参数 | 本地部署难度 | 中文支持 | 推理速度 |
|------|------|-------------|----------|----------|
| Llama 3 | 8B/70B | 高（需大量显存） | 较差 | 中 |
| Qwen 2 | 1.8B/7B | 中 | 优秀 | 快 |
| DeepSeek R1 | 1.5B | 低 | 优秀 | 快 |

**选型决策：** DeepSeek R1 1.5B 以其轻量化、中文支持好、推理速度快的特点，成为本地部署的最佳选择。

#### 1.2.2 视觉 OCR 模型

| 模型名称 | 选型理由 |
|----------|----------|
| minicpm-v | 轻量级视觉语言模型，支持中文OCR，可通过Ollama一键部署 |

**选型决策：** minicpm-v 是目前唯一可通过 Ollama 部署的视觉模型，无需额外安装复杂依赖。

#### 1.2.3 语音识别模型

| 模型名称 | 版本 | 选型理由 |
|----------|------|----------|
| faster-whisper | small | 基于 OpenAI Whisper，推理速度快，支持中文，可本地运行 |

**选型对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| FunASR | 中文优化好 | 依赖复杂，模型注册问题多 |
| Whisper (官方) | 功能完善 | 推理速度慢 |
| faster-whisper | 速度快，支持INT8量化 | 模型下载需手动处理 |

**选型决策：** faster-whisper small 模型在速度和准确性之间取得平衡，适合本地部署。

---

## 二、环境准备

### 2.1 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4核 | 8核及以上 |
| 内存 | 16GB | 32GB |
| 显存 | 4GB（无GPU可用CPU） | 8GB+ |
| 存储 | 50GB 可用空间 | 100GB+ |

### 2.2 软件依赖安装

#### 2.2.1 安装 Ollama

**Windows 系统：**

```powershell
# 下载并安装 Ollama
# 下载地址：https://ollama.com/download/windows

# 验证安装
ollama --version

# 启动 Ollama 服务（首次运行会自动启动）
ollama serve
```

#### 2.2.2 安装 Python 环境

```powershell
# 检查 Python 版本（要求 >= 3.10）
python --version

# 创建虚拟环境
cd agent-hub-backend
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

#### 2.2.3 安装 Node.js 环境

```powershell
# 检查 Node.js 版本（要求 >= 20.x）
node --version
npm --version

# 安装前端依赖
cd agent-hub-frontend
npm install
```

---

## 三、模型下载与配置

### 3.1 下载 LLM 模型（DeepSeek R1）

```powershell
# 查看已下载的模型
ollama list

# 下载 DeepSeek R1 1.5B 模型
ollama pull deepseek-r1:1.5b

# 验证模型
ollama run deepseek-r1:1.5b "Hello!"
```

### 3.2 下载 OCR 模型（minicpm-v）

```powershell
# 下载 minicpm-v 视觉模型
ollama pull minicpm-v

# 验证模型（需要图片输入）
# 可通过 API 测试
```

### 3.3 下载语音识别模型（faster-whisper）

**方式一：自动下载（首次运行时）**

```powershell
# 运行测试脚本，触发模型自动下载
python test_asr.py
```

**方式二：手动下载（推荐，避免网络问题）**

```powershell
# 创建模型目录
mkdir -p $env:USERPROFILE\.cache\huggingface\hub

# 从国内镜像下载模型
# 访问：https://hf-mirror.com/Systran/faster-whisper-small
# 下载以下文件：
# - config.json
# - model.bin
# - vocab.json
# - tokenizer.json
# - special_tokens_map.json

# 放置路径示例：
# C:\Users\[用户名]\.cache\huggingface\hub\models--Systran--faster-whisper-small\snapshots\[版本号]\
```

### 3.4 配置环境变量

创建/编辑 `agent-hub-backend/.env` 文件：

```env
# 服务配置
HOST=0.0.0.0
PORT=8000

# 模型配置
USE_LOCAL_MODEL=true

# Ollama 配置
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:1.5b

# 视觉模型配置
VISION_MODEL=minicpm-v

# 语音识别配置
ASR_MODEL=small
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8
```

**配置说明：**

| 参数 | 说明 | 可选值 |
|------|------|--------|
| USE_LOCAL_MODEL | 是否使用本地模型 | true/false |
| OLLAMA_HOST | Ollama 服务地址 | http://localhost:11434 |
| OLLAMA_MODEL | 聊天模型名称 | deepseek-r1:1.5b |
| VISION_MODEL | OCR 模型名称 | minicpm-v |
| ASR_MODEL | 语音模型大小 | tiny/base/small/medium/large |
| ASR_DEVICE | 运行设备 | cpu/cuda |
| ASR_COMPUTE_TYPE | 计算精度 | int8/int16/float16 |

---

## 四、后端部署

### 4.1 启动后端服务

```powershell
# 确保已激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 启动 FastAPI 服务
python main.py
```

**预期输出：**

```
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4.2 验证后端服务

```powershell
# 健康检查
Invoke-RestMethod http://localhost:8000/ -UseBasicParsing

# 获取模型列表
Invoke-RestMethod http://localhost:8000/api/models -UseBasicParsing

# 测试聊天功能
$body = @{
    message = "你好"
} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/api/chat -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
```

### 4.3 测试 OCR 功能

```powershell
# 测试 OCR（纯识别模式）
curl -X POST http://localhost:8000/api/ocr `
  -F "file=@test_image.png"

# 测试 OCR（分析模式）
curl -X POST http://localhost:8000/api/ocr `
  -F "file=@test_image.png" `
  -F "prompt=请分析这张图片的内容"
```

### 4.4 测试语音识别功能

```powershell
# 测试语音识别（纯识别模式）
curl -X POST http://localhost:8000/api/speech `
  -F "file=@test_audio.wav"

# 测试语音识别（分析模式）
curl -X POST http://localhost:8000/api/speech `
  -F "file=@test_audio.wav" `
  -F "prompt=请总结这段语音的内容"
```

---

## 五、前端部署

### 5.1 开发模式运行

```powershell
cd agent-hub-frontend
npm run dev
```

**访问地址：** http://localhost:5173

### 5.2 生产构建

```powershell
cd agent-hub-frontend
npm run build
```

### 5.3 生产环境部署

```powershell
# 安装静态文件服务（可选）
npm install -g serve

# 启动生产服务器
serve -s dist -l 5173
```

---

## 六、功能模块说明

### 6.1 综合问答终端

**功能描述：**
- 支持文本输入和附件上传
- 多模式切换：聊天、编程、研究

**调用方式：**
```bash
POST /api/chat
POST /api/coder
POST /api/research
```

### 6.2 视觉 OCR

**功能描述：**
- **纯识别模式**：直接返回图像中的文字内容
- **分析模式**：附带 prompt 进行深度分析

**调用方式：**
```bash
# 纯识别模式（无 prompt 参数）
POST /api/ocr -F "file=@image.png"

# 分析模式（带 prompt 参数）
POST /api/ocr -F "file=@image.png" -F "prompt=请分析图片内容"
```

### 6.3 语音语义分析

**功能描述：**
- **纯识别模式**：直接返回语音转写文本
- **分析模式**：附带 prompt 进行语义分析

**调用方式：**
```bash
# 纯识别模式（无 prompt 参数）
POST /api/speech -F "file=@audio.wav"

# 分析模式（带 prompt 参数）
POST /api/speech -F "file=@audio.wav" -F "prompt=请总结语音内容"
```

---

## 七、常见问题及解决方案

### 7.1 Ollama 连接失败

**问题描述：**
```
ConnectionError: [WinError 10061] 无法连接到目标计算机
```

**解决方案：**
```powershell
# 确保 Ollama 服务正在运行
ollama serve

# 检查端口是否被占用
netstat -ano | findstr :11434
```

### 7.2 语音识别模型下载失败

**问题描述：**
```
An error happened while trying to locate the files on the Hub
```

**解决方案：**
1. 手动从 [Hugging Face Mirror](https://hf-mirror.com/) 下载模型
2. 将模型文件放置到正确的缓存目录
3. 确保目录结构正确：
   ```
   models--Systran--faster-whisper-small/
   └── snapshots/
       └── [版本号]/
           ├── config.json
           ├── model.bin
           ├── vocab.json
           └── ...
   ```

### 7.3 模型文件路径错误（WinError 14007）

**问题描述：**
```
[WinError 14007] 在活动的激活上下文中找不到任何查找密钥
```

**解决方案：**
```powershell
# 将模型文件复制到所有可能的 snapshot 目录
# 查找所有 snapshot 目录
Get-ChildItem -Path "$env:USERPROFILE\.cache\huggingface\hub\models--Systran--faster-whisper-small\snapshots" -Directory

# 将模型文件复制到每个目录
```

### 7.4 前端构建失败

**问题描述：**
```
npm run build 失败，提示依赖缺失
```

**解决方案：**
```powershell
# 删除 node_modules 和 package-lock.json
rm -Recurse -Force node_modules
rm package-lock.json

# 重新安装依赖
npm install

# 再次构建
npm run build
```

---

## 八、性能优化建议

### 8.1 模型优化

| 优化项 | 说明 |
|--------|------|
| 使用 INT8 量化 | ASR_COMPUTE_TYPE=int8，减少内存占用 |
| 选择合适的模型大小 | 根据硬件配置选择 tiny/small/medium |
| 关闭不必要的功能 | 如 VAD 过滤可根据需求关闭 |

### 8.2 服务优化

```powershell
# 使用多进程模式启动（生产环境）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 8.3 资源监控

```powershell
# 查看 CPU 和内存使用
Get-Process -Name python | Select-Object CPU, WorkingSet

# 查看显存使用（需要安装 nvidia-smi）
nvidia-smi
```

---

## 九、部署清单

| 步骤 | 检查项 | 状态 |
|------|--------|------|
| 1 | Ollama 服务已启动 | [ ] |
| 2 | DeepSeek R1 模型已下载 | [ ] |
| 3 | minicpm-v 模型已下载 | [ ] |
| 4 | faster-whisper 模型已下载 | [ ] |
| 5 | .env 配置文件已正确配置 | [ ] |
| 6 | 后端服务已启动 | [ ] |
| 7 | 前端服务已启动 | [ ] |
| 8 | API 健康检查通过 | [ ] |
| 9 | OCR 功能测试通过 | [ ] |
| 10 | 语音识别功能测试通过 | [ ] |

---

## 十、附录

### 10.1 模型下载命令汇总

```powershell
# Ollama 模型
ollama pull deepseek-r1:1.5b
ollama pull minicpm-v

# faster-whisper 模型（自动下载）
python test_asr.py
```

### 10.2 服务启动命令汇总

```powershell
# 启动 Ollama（如需手动启动）
ollama serve

# 启动后端
cd agent-hub-backend
.\.venv\Scripts\Activate.ps1
python main.py

# 启动前端（开发模式）
cd agent-hub-frontend
npm run dev
```

### 10.3 常用端口

| 服务 | 端口 |
|------|------|
| 后端 API | 8000 |
| 前端应用 | 5173 |
| Ollama | 11434 |

---

**文档版本：** v1.0  
**创建日期：** 2026年6月  
**适用项目：** AI Agent 中台系统
