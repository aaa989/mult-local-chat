# AI Agent 中台系统

一个基于 FastAPI + React 的智能 Agent 中台系统，支持**全本地部署**，集成多种 AI 能力模块。

## 项目概览

本系统提供以下核心功能：

- **综合问答终端**：多模式智能聊天，支持附件上传
- **自动编程控制台**：代码生成，支持多种编程语言
- **深度研究枢纽**：智能研究报告生成与深度分析
- **视觉 OCR**：本地图像文字识别，支持纯识别和分析模式
- **语音语义分析**：本地语音转文字，支持纯识别和语义分析模式

## 技术栈

### 前端

- React 19 + Vite 8
- Tailwind CSS 3
- Lucide React

### 后端

- FastAPI + Python 3.10+
- httpx、PyPDF2、python-docx
- faster-whisper（本地语音识别）

### AI 模型（全本地部署）

- **聊天/编程/研究**：Ollama + DeepSeek R1 1.5B
- **OCR 视觉识别**：Ollama + minicpm-v
- **语音识别**：faster-whisper（small 模型）

## 快速开始

### 环境要求

- Node.js >= 20.x
- Python >= 3.10
- Ollama（用于本地模型）

### 1. 启动 Ollama 并下载模型

```powershell
# 检查 Ollama 状态
Invoke-RestMethod -Uri http://localhost:11434/api/tags -UseBasicParsing

# 如果未运行，启动 Ollama
ollama serve

# 下载所需模型
ollama pull deepseek-r1:1.5b
ollama pull minicpm-v
```

### 2. 配置后端

```powershell
cd backend
```

编辑 `.env` 配置文件：

```env
HOST=0.0.0.0
PORT=8000

USE_LOCAL_MODEL=true

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:1.5b

VISION_MODEL=minicpm-v

ASR_MODEL=small
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8
```

### 3. 安装依赖并启动

**后端（激活虚拟环境）：**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python backend/main.py
```

**前端（另一个终端）：**

```powershell
cd frontend
npm install
npm run dev
```

### 访问地址

- **前端应用**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 项目结构

```
mult_llm/
├── backend/                          # 后端服务
│   ├── main.py                       # FastAPI 主应用入口
│   ├── ollama_client.py              # Ollama 本地模型客户端
│   ├── ocr_service.py                # 本地 OCR 识别服务
│   ├── speech_service.py             # 本地语音识别服务
│   ├── test_asr.py                   # 语音识别测试脚本
│   ├── test_sample.wav               # 测试音频文件
│   ├── .env                          # 环境配置文件
│   ├── .env.example                  # 环境配置模板
│   └── requirements.txt              # Python 依赖列表
├── frontend/                         # 前端应用
│   ├── src/                          # React 源代码
│   │   ├── App.jsx                   # 主应用组件（核心业务逻辑）
│   │   ├── main.jsx                  # 应用入口
│   │   ├── index.css                 # Tailwind CSS 入口
│   │   ├── App.css                   # 应用样式
│   │   └── assets/                   # 静态资源
│   │       ├── hero.png              # Hero 图片
│   │       ├── react.svg             # React Logo
│   │       └── vite.svg              # Vite Logo
│   ├── public/                       # 公共静态文件
│   │   ├── favicon.svg               # 网站图标
│   │   └── icons.svg                 # 图标资源
│   ├── vite.config.js                # Vite 构建配置
│   ├── tailwind.config.js            # Tailwind CSS 配置
│   ├── postcss.config.js             # PostCSS 配置
│   ├── eslint.config.js              # ESLint 配置
│   ├── .env.example                  # 环境变量模板
│   ├── .env.production               # 生产环境配置
│   └── package.json                  # 前端依赖配置
├── docs/                             # 文档
│   ├── DEPLOYMENT.md                 # 模型部署流程
│   ├── DEPLOYMENT_STRATEGY.md        # 部署策略说明
└── .venv/                            # Python 虚拟环境（已忽略）
```

## API 接口

| 接口                 | 方法         | 功能                                   |
| -------------------- | ------------ | -------------------------------------- |
| `GET /`              | 健康检查     | 返回服务状态                           |
| `GET /api/models`    | 获取模型列表 | 查看本地可用模型                       |
| `POST /api/chat`     | POST         | 综合智能聊天对话                       |
| `POST /api/coder`    | POST         | 自动编程代码生成                       |
| `POST /api/research` | POST         | 深度研究报告生成                       |
| `POST /api/ocr`      | POST         | 图片/文档 OCR 识别（支持 prompt 参数） |
| `POST /api/speech`   | POST         | 语音转写与分析（支持 prompt 参数）     |

## 功能模块

### 综合问答终端

- 多模式切换：聊天、编程、研究、OCR、语音
- 附件支持：图片、文档、音频文件
- 附加指令：可附带具体问题或分析要求

### 视觉 OCR

- **纯识别模式**：直接返回图像中的文字内容
- **分析模式**：附带 prompt 进行深度分析
- 支持图片格式（JPG、PNG 等）

### 语音语义分析

- **纯识别模式**：直接返回语音转写文本
- **分析模式**：附带 prompt 进行语义分析
- 麦克风实时录制 + 音频文件上传
- 支持中文识别

## 核心特性

### 全本地部署

- 无需云端 API Key
- 所有模型运行在本地
- 数据隐私安全

### 双模式识别

- OCR 和语音识别均支持**纯识别模式**和**分析模式**
- 纯识别模式：仅输出识别结果，无额外修饰
- 分析模式：可进行多样化的 AI 分析和修饰

## 开发命令

```bash
# 激活虚拟环境 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 后端启动
python backend/main.py

# 前端开发
cd frontend && npm run dev

# 前端构建
npm run build

# 代码检查
npm run lint
```

## 文档

- **部署流程**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **部署策略**: [docs/DEPLOYMENT_STRATEGY.md](docs/DEPLOYMENT_STRATEGY.md)

## 许可证

MIT License
