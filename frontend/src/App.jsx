import React, { useState, useRef, useEffect } from "react";
import {
  Terminal,
  Code2,
  FileText,
  Mic,
  Cpu,
  Play,
  StopCircle,
  UploadCloud,
  Search,
  Send,
  FileCode2,
  Copy,
  AlignLeft,
  Sparkles,
  Zap,
  Loader2,
  HardDrive,
  CheckCircle2,
  Activity,
  FileAudio,
  MessageSquare,
  Paperclip,
  Trash2,
  User,
} from "lucide-react";

const API_BASE_URL = "http://localhost:8000";

const Button = ({
  children,
  variant = "default",
  className = "",
  ...props
}) => {
  const baseStyle =
    "inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-[13px] font-medium transition-all duration-300 focus:outline-none active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    default:
      "bg-white text-zinc-700 border border-zinc-200 hover:bg-zinc-50 hover:border-zinc-300 shadow-sm",
    primary:
      "bg-zinc-900 text-white shadow-md hover:bg-zinc-800 hover:shadow-lg",
    danger: "bg-red-500 text-white shadow-md hover:bg-red-600",
  };
  return (
    <button
      className={`${baseStyle} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

const DeepResearchView = () => {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState("");

  const handleStartResearch = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setReport("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: topic }),
      });
      const resData = await response.json();
      setReport(resData.data);
    } catch (error) {
      setReport(`请求失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col space-y-6 animate-in fade-in duration-700">
      <div className="bg-white rounded-2xl p-8 border border-zinc-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
        <h2 className="text-lg font-semibold text-zinc-900 flex items-center gap-2 mb-6 tracking-tight">
          <Search className="w-5 h-5 text-zinc-900" /> 全网深度挖掘与研究
        </h2>
        <div className="flex space-x-4">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
            placeholder="输入复杂命题，例如：固态电池商业化落地的最新技术进展与瓶颈..."
            className="w-full bg-zinc-50 border border-zinc-200 rounded-xl px-5 py-3.5 text-sm focus:outline-none focus:ring-1 focus:ring-zinc-900 focus:border-zinc-900 transition-all text-zinc-800"
          />
          <Button
            variant="primary"
            onClick={handleStartResearch}
            disabled={loading}
            className="px-8 whitespace-nowrap"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Sparkles className="w-4 h-4 mr-2" />
            )}{" "}
            开始研究
          </Button>
        </div>
      </div>
      <div className="flex-1 bg-white border border-zinc-100 rounded-2xl flex flex-col shadow-[0_2px_10px_rgba(0,0,0,0.02)] overflow-hidden min-h-0">
        <div className="border-b border-zinc-100 px-8 py-5 flex items-center bg-zinc-50/50">
          <AlignLeft className="w-4 h-4 text-zinc-400 mr-2" />{" "}
          <span className="text-[13px] font-semibold text-zinc-700 tracking-wide">
            研究报告总览
          </span>
        </div>
        <div className="p-10 overflow-y-auto flex-1 text-[15px] text-zinc-700 leading-loose whitespace-pre-wrap font-sans">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center text-zinc-400">
              <Loader2 className="w-8 h-8 animate-spin mb-4 text-zinc-800" />
              <p className="text-sm">引擎正在深度检索...</p>
            </div>
          ) : report ? (
            report
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-zinc-300">
              <FileText className="w-10 h-10 mb-4 opacity-50" />
              <p className="text-sm">暂无数据</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const AutoCoderView = () => {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [codeContent, setCodeContent] = useState("// 等待指令...\n");
  const [fileExt, setFileExt] = useState("code");
  const messagesEndRef = useRef(null);

  useEffect(
    () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }),
    [messages],
  );

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/coder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMsg }),
      });
      const resData = await response.json();
      const aiResponse = resData.data;

      let textPart = aiResponse;
      let codePart = "";
      const extMatch = aiResponse.match(/```([a-zA-Z0-9+#]+)/);
      if (extMatch) {
        const ext = extMatch[1].toLowerCase();
        const extMap = {
          python: "py",
          javascript: "js",
          typescript: "ts",
          java: "java",
          cpp: "cpp",
          c: "c",
          html: "html",
          css: "css",
        };
        setFileExt(extMap[ext] || ext);
      }

      if (aiResponse.includes("```")) {
        const parts = aiResponse.split("```");
        textPart = parts[0];
        const rawCode = parts[1];
        codePart = rawCode.substring(rawCode.indexOf("\n") + 1).trim();
        setCodeContent(codePart);
      }
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: textPart || "代码已生成。" },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `[错误] ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex gap-6 animate-in fade-in duration-700">
      <div className="w-[40%] min-w-[350px] border border-zinc-200/80 rounded-2xl flex flex-col bg-white shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-zinc-100 font-semibold text-[13px] text-zinc-900 flex items-center gap-2 bg-zinc-50/50">
          <Zap className="w-4 h-4 text-zinc-900" /> 架构构思与逻辑对话
        </div>
        <div className="flex-1 p-6 overflow-y-auto space-y-6 text-[14px] bg-white">
          {messages.map((msg, idx) => (
            <div key={idx} className="flex gap-4 items-start">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-[11px] font-bold tracking-tighter ${msg.role === "user" ? "bg-zinc-100 text-zinc-600" : "bg-zinc-900 text-white shadow-md"}`}
              >
                {msg.role === "user" ? "USR" : <Cpu className="w-4 h-4" />}
              </div>
              <div className="bg-zinc-50 border border-zinc-100 rounded-2xl rounded-tl-sm p-4 text-zinc-700 flex-1 whitespace-pre-wrap">
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-4 items-start animate-pulse">
              <div className="w-8 h-8 rounded-full bg-zinc-900 text-white flex items-center justify-center flex-shrink-0">
                <Loader2 className="w-4 h-4 animate-spin" />
              </div>
              <div className="text-zinc-400 text-sm py-1.5">
                思考代码结构...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="p-5 bg-white border-t border-zinc-100">
          <div className="relative border border-zinc-200 rounded-xl bg-zinc-50 focus-within:ring-1 focus-within:ring-zinc-900 focus-within:border-zinc-900 transition-all">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="描述业务需求..."
              className="w-full bg-transparent pl-4 pr-12 py-4 text-sm focus:outline-none resize-none h-24 text-zinc-800"
            ></textarea>
            <button
              onClick={handleSend}
              disabled={loading}
              className="absolute right-3 bottom-3 p-2 bg-zinc-900 text-white rounded-lg hover:bg-zinc-800 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      <div className="flex-1 border border-zinc-800 rounded-2xl flex flex-col bg-[#18181B] shadow-xl overflow-hidden relative">
        <div className="px-6 py-4 border-b border-zinc-800/80 flex justify-between items-center">
          <div className="text-[13px] text-zinc-400 font-mono flex items-center gap-2">
            <FileCode2 className="w-4 h-4 text-zinc-500" /> workspace.{fileExt}
          </div>
          <button
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-white bg-zinc-800 rounded-lg"
            onClick={() => navigator.clipboard.writeText(codeContent)}
          >
            <Copy className="w-3.5 h-3.5" /> 复制
          </button>
        </div>
        <div className="flex-1 overflow-y-auto font-mono text-[14px] text-[#D4D4D8] flex">
          <div className="w-14 bg-[#18181B] border-r border-zinc-800/50 flex flex-col py-6 items-end pr-4 text-zinc-600 select-none text-[12px] leading-[1.625rem]">
            {[...Array(60)].map((_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>
          <pre className="flex-1 py-6 px-6 whitespace-pre-wrap">
            {codeContent}
          </pre>
        </div>
      </div>
    </div>
  );
};

const VisionOCRView = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState("");
  const fileInputRef = useRef(null);
  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      if (selected.type.startsWith("image/"))
        setPreview(URL.createObjectURL(selected));
      else setPreview("document");
      setResult("");
    }
  };
  const startOCR = async () => {
    if (!file) return;
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE_URL}/api/ocr`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setResult(data.data);
    } catch (error) {
      setResult(`处理失败：${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-full flex flex-col space-y-6 animate-in fade-in duration-700">
      <div
        className="border border-dashed border-zinc-300 rounded-2xl p-10 flex flex-col items-center justify-center bg-white hover:bg-zinc-50 cursor-pointer group"
        onClick={() => fileInputRef.current.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept="image/*,.pdf,.txt,.doc,.docx"
        />
        {!file ? (
          <>
            {" "}
            <div className="bg-zinc-100 p-4 rounded-2xl mb-4 group-hover:scale-105 transition-transform">
              <UploadCloud className="w-8 h-8 text-zinc-700" />
            </div>
            <p className="font-semibold text-zinc-900 text-[15px]">
              点击或拖拽上传文档图像
            </p>
          </>
        ) : (
          <div className="flex flex-col items-center">
            <CheckCircle2 className="w-10 h-10 text-zinc-900 mb-3" />
            <p className="font-semibold">{file.name}</p>
          </div>
        )}
      </div>
      <div className="grid grid-cols-2 gap-6 flex-1 min-h-0">
        <div className="border border-zinc-100 rounded-2xl bg-white flex flex-col overflow-hidden">
          <div className="border-b border-zinc-100 px-8 py-5 flex justify-between items-center bg-zinc-50/50">
            <span className="text-[13px] font-semibold text-zinc-700">
              源文件预览区
            </span>
            {file && (
              <Button
                variant="primary"
                onClick={startOCR}
                disabled={isProcessing}
                className="py-2 text-[12px]"
              >
                {isProcessing ? "读取与分析中..." : "开始重组分析"}
              </Button>
            )}
          </div>
          <div className="flex-1 flex items-center justify-center p-8 bg-zinc-50/30">
            {preview === "document" ? (
              <div className="text-zinc-400">
                <FileText className="w-12 h-12 mb-4" />
                文档格式
              </div>
            ) : preview ? (
              <img
                src={preview}
                alt="preview"
                className="max-h-[300px] object-contain rounded-xl border border-zinc-200"
              />
            ) : (
              <span className="text-zinc-400 text-sm">等待文件加载</span>
            )}
          </div>
        </div>
        <div className="border border-zinc-100 rounded-2xl bg-white flex flex-col overflow-hidden">
          <div className="border-b border-zinc-100 px-8 py-5 text-[13px] font-semibold text-zinc-700 bg-zinc-50/50">
            自然语言重组结果
          </div>
          <div className="flex-1 p-10 overflow-y-auto text-[15px] text-zinc-700 leading-loose whitespace-pre-wrap">
            {isProcessing ? (
              <div className="flex flex-col items-center text-zinc-400">
                <Loader2 className="w-8 h-8 animate-spin mb-4 text-zinc-800" />
                深度阅读中...
              </div>
            ) : result ? (
              result
            ) : (
              <div className="flex flex-col items-center text-zinc-300">
                <AlignLeft className="w-10 h-10 mb-4 opacity-50" />
                暂无结果
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const SpeechAnalyticsView = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);
  const handleAudioUpload = async (e) => {
    if (e.target.files[0]) await sendAudioToBackend(e.target.files[0]);
  };
  const toggleRecording = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];
        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunksRef.current.push(event.data);
        };
        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm",
          });
          const file = new File([audioBlob], "recorded_audio.webm", {
            type: "audio/webm",
          });
          await sendAudioToBackend(file);
        };
        mediaRecorderRef.current.start();
        setIsRecording(true);
        setResult("");
      } catch (err) {
        alert("无法访问麦克风");
      }
    } else {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };
  const sendAudioToBackend = async (audioFile) => {
    setIsProcessing(true);
    const formData = new FormData();
    formData.append("file", audioFile);
    try {
      const response = await fetch(`${API_BASE_URL}/api/speech`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setResult(data.data);
    } catch (error) {
      setResult(`分析失败: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };
  return (
    <div className="h-full flex flex-col space-y-6 animate-in fade-in duration-700">
      <div className="border border-zinc-100 rounded-2xl bg-white p-10 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-zinc-900 mb-2">
            智能语音语义剖析
          </h2>
          <p className="text-[14px] text-zinc-500 max-w-lg">
            支持实时录音或上传音频文件。
          </p>
        </div>
        <div className="flex gap-4 items-center">
          <input
            type="file"
            accept="audio/*"
            ref={fileInputRef}
            onChange={handleAudioUpload}
            className="hidden"
          />
          <Button
            variant="default"
            onClick={() => fileInputRef.current.click()}
            disabled={isRecording || isProcessing}
            className="px-6 h-12 rounded-xl"
          >
            <FileAudio className="w-4 h-4 mr-2" />
            上传音频
          </Button>
          <Button
            variant={isRecording ? "danger" : "primary"}
            onClick={toggleRecording}
            disabled={isProcessing}
            className={`px-6 h-12 rounded-xl ${isRecording ? "animate-pulse" : ""}`}
          >
            {isRecording ? (
              <StopCircle className="w-4 h-4 mr-2" />
            ) : (
              <Mic className="w-4 h-4 mr-2" />
            )}
            {isRecording ? "结束录制并分析" : "开始麦克风录音"}
          </Button>
        </div>
      </div>
      <div className="border border-zinc-100 rounded-2xl bg-white flex-1 min-h-0 flex flex-col">
        <div className="border-b border-zinc-100 px-8 py-5 font-semibold text-zinc-700 text-[13px] bg-zinc-50/50">
          语义剖析看板
        </div>
        <div className="p-10 flex-1 overflow-y-auto text-[15px] text-zinc-700 leading-loose whitespace-pre-wrap">
          {isProcessing ? (
            <div className="flex flex-col items-center text-zinc-400">
              <Loader2 className="w-8 h-8 animate-spin mb-4 text-zinc-800" />
              提取中...
            </div>
          ) : result ? (
            result
          ) : (
            <div className="flex flex-col items-center text-zinc-300">
              <Activity className="w-10 h-10 mb-4 opacity-50" />
              等待分析
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const UnifiedChatView = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("chat"); // 'chat' | 'research' | 'coder' | 'ocr' | 'speech'
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(
    () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }),
    [messages],
  );

  // 处理文件附件
  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // 处理麦克风录音附件
  const toggleRecording = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];
        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunksRef.current.push(event.data);
        };
        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm",
          });
          const audioFile = new File([audioBlob], "录音文件_record.webm", {
            type: "audio/webm",
          });
          setFile(audioFile); // 录完音直接变成附件，等待用户点击发送
        };
        mediaRecorderRef.current.start();
        setIsRecording(true);
      } catch (err) {
        alert("无法访问麦克风，请检查权限。");
      }
    } else {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() && !file) return;

    // 构建用户消息 UI
    const userMsg = {
      role: "user",
      content: input,
      fileName: file ? file.name : null,
      modeTag: mode,
    };

    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input;
    const currentFile = file;

    setInput("");
    setFile(null); // 发送后清空附件
    setLoading(true);

    try {
      let resData;

      // 分发请求逻辑
      if (["chat", "research", "coder"].includes(mode)) {
        // 纯文本 API 调用
        const response = await fetch(`${API_BASE_URL}/api/${mode}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: currentInput }),
        });
        resData = await response.json();
      } else {
        // 文件/多模态 API 调用 (ocr, speech)
        if (!currentFile) {
          throw new Error("此模式下需要附带文件或录音才能进行分析哦。");
        }
        const formData = new FormData();
        formData.append("file", currentFile);
        if (currentInput) {
          formData.append("prompt", currentInput);
        }
        const response = await fetch(`${API_BASE_URL}/api/${mode}`, {
          method: "POST",
          body: formData,
        });
        resData = await response.json();
      }

      if (resData.status === "success") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: resData.data },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `[请求拒绝] ${resData.data}` },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `[系统错误] ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 映射模式名称
  const getModeLabel = (m) => {
    const map = {
      chat: "综合聊天",
      research: "深度研究",
      coder: "自动编程",
      ocr: "视觉与文档",
      speech: "语音分析",
    };
    return map[m] || "AI";
  };

  return (
    <div className="h-full flex flex-col bg-white border border-zinc-200/80 rounded-2xl shadow-sm overflow-hidden animate-in fade-in duration-700 relative">
      {/* 聊天记录展示区 */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-zinc-50/30">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-zinc-400 space-y-4">
            <Sparkles className="w-12 h-12 text-zinc-300" />
            <p className="text-[15px] font-medium text-zinc-500">
              欢迎使用全能 AI 问答终端
            </p>
            <p className="text-[13px] max-w-sm text-center">
              在下方选择你需要的特定能力，发送文本、图片、PDF
              或语音，获取定制化分析解答。
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "assistant" && (
              <div className="w-9 h-9 rounded-full bg-zinc-900 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                <Cpu className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-[75%] rounded-2xl p-5 text-[15px] leading-relaxed whitespace-pre-wrap shadow-sm
              ${msg.role === "user" ? "bg-zinc-100 text-zinc-800 rounded-tr-sm" : "bg-white border border-zinc-100 text-zinc-700 rounded-tl-sm"}
            `}
            >
              {msg.role === "user" && (
                <div className="flex items-center gap-2 mb-2 text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
                  <span>{getModeLabel(msg.modeTag)} Mode</span>
                </div>
              )}
              {msg.fileName && (
                <div className="flex items-center gap-2 mb-3 p-2.5 bg-white border border-zinc-200 rounded-lg text-sm text-zinc-600 w-fit">
                  <FileText className="w-4 h-4 text-emerald-600" />
                  <span className="truncate max-w-[200px]">{msg.fileName}</span>
                </div>
              )}
              {msg.content}
            </div>

            {msg.role === "user" && (
              <div className="w-9 h-9 rounded-full bg-zinc-200 text-zinc-600 flex items-center justify-center flex-shrink-0">
                <User className="w-4.5 h-4.5" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-4 items-start animate-pulse">
            <div className="w-9 h-9 rounded-full bg-zinc-900 text-white flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-white border border-zinc-100 rounded-2xl rounded-tl-sm px-6 py-4 text-zinc-400 text-sm">
              正在处理您的请求...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 底部功能栏与输入区 */}
      <div className="p-6 bg-white border-t border-zinc-100">
        <div className="max-w-4xl mx-auto relative border border-zinc-200 rounded-2xl bg-zinc-50 focus-within:ring-1 focus-within:ring-zinc-900 focus-within:border-zinc-900 transition-all shadow-sm">
          {/* 模式选择器与附件预览条 */}
          <div className="flex items-center justify-between px-4 pt-3 pb-1 border-b border-zinc-100/50">
            <div className="flex items-center gap-3">
              <select
                value={mode}
                onChange={(e) => {
                  setMode(e.target.value);
                  setFile(null);
                }}
                className="bg-white border border-zinc-200 text-zinc-700 text-[13px] font-medium rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-zinc-400 cursor-pointer shadow-sm"
              >
                <option value="chat">综合聊天</option>
                <option value="research">深度研究</option>
                <option value="coder">自动编程</option>
                <option value="ocr">视觉与文档分析</option>
                <option value="speech">语音语义分析</option>
              </select>

              {/* 动态显示附件提示 */}
              {file && (
                <div className="flex items-center gap-2 bg-emerald-50 text-emerald-700 border border-emerald-100 px-3 py-1 rounded-md text-[12px] font-medium animate-in zoom-in-95 duration-200">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span className="truncate max-w-[150px]">{file.name}</span>
                  <button
                    onClick={() => setFile(null)}
                    className="ml-1 hover:text-emerald-900"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>
          </div>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder={
              mode === "ocr"
                ? "请在左下方上传图片或文档，并在此输入您的要求..."
                : mode === "speech"
                  ? "请上传音频或使用麦克风录音，并输入附加分析要求..."
                  : "输入指令，与 AI 对话 (Shift + Enter 换行)..."
            }
            className="w-full bg-transparent px-5 py-4 text-[15px] focus:outline-none resize-none h-28 text-zinc-800 placeholder:text-zinc-400"
          ></textarea>

          <div className="absolute left-4 bottom-4 flex gap-2 items-center">
            {/* 根据模式动态显示功能按钮 */}
            {["ocr", "speech"].includes(mode) && (
              <>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept={
                    mode === "ocr" ? "image/*,.pdf,.doc,.docx,.txt" : "audio/*"
                  }
                />
                <button
                  onClick={() => fileInputRef.current.click()}
                  className="p-2 bg-white border border-zinc-200 rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 transition-colors shadow-sm"
                  title="上传本地文件"
                >
                  <Paperclip className="w-4.5 h-4.5" />
                </button>
              </>
            )}

            {mode === "speech" && (
              <button
                onClick={toggleRecording}
                className={`p-2 border rounded-lg transition-all shadow-sm flex items-center gap-2 px-3
                  ${isRecording ? "bg-red-50 border-red-200 text-red-600 animate-pulse" : "bg-white border-zinc-200 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900"}
                `}
              >
                {isRecording ? (
                  <StopCircle className="w-4.5 h-4.5" />
                ) : (
                  <Mic className="w-4.5 h-4.5" />
                )}
                <span className="text-xs font-medium">
                  {isRecording ? "点击结束录音" : "录制语音"}
                </span>
              </button>
            )}
          </div>

          <button
            onClick={handleSend}
            disabled={loading || (!input.trim() && !file)}
            className="absolute right-4 bottom-4 p-2.5 bg-zinc-900 text-white rounded-xl shadow-md hover:bg-zinc-800 transition-colors disabled:opacity-40 flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <div className="text-center mt-3 text-[12px] text-zinc-400">
          AI
          生成的内容可能存在偏差，请按需选择最匹配的智能体模式以获得最佳效果。
        </div>
      </div>
    </div>
  );
};

// --- 全局根容器 ---
export default function App() {
  const [activeTab, setActiveTab] = useState("unified");

  const tabs = [
    { id: "unified", label: "综合问答", icon: MessageSquare },
    { id: "research", label: "深度研究", icon: Terminal },
    { id: "coder", label: "自动编程", icon: Code2 },
    { id: "ocr", label: "视觉 OCR", icon: FileText },
    { id: "speech", label: "语音分析", icon: Mic },
  ];

  return (
    <div className="min-h-screen bg-zinc-100 p-4 lg:p-8 flex items-center justify-center font-sans text-zinc-900 selection:bg-zinc-200">
      <div className="w-full max-w-[1600px] h-[90vh] bg-white rounded-[2rem] shadow-2xl overflow-hidden flex border border-zinc-200/60 relative">
        {/* 高级侧边栏 */}
        <div className="w-[260px] bg-zinc-50/80 backdrop-blur-3xl border-r border-zinc-200/80 flex flex-col z-10 shrink-0">
          <div className="h-20 flex items-center px-8 border-b border-zinc-200/80">
            <div className="flex items-center gap-3 font-bold text-zinc-900 text-[16px] tracking-tight">
              <div className="bg-zinc-900 p-2 rounded-xl shadow-md">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              专业综合实践
            </div>
          </div>
          <div className="px-8 pt-8 pb-3 text-[11px] font-bold text-zinc-400 uppercase tracking-widest">
            系统核心模块
          </div>
          <nav className="flex-1 px-4 space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl text-[14px] transition-all duration-300 
                  ${activeTab === tab.id ? "text-zinc-900 font-semibold bg-white shadow-sm ring-1 ring-zinc-200/50" : "text-zinc-500 hover:bg-zinc-100/50 hover:text-zinc-900"}
                `}
              >
                <tab.icon
                  className={`w-[18px] h-[18px] ${activeTab === tab.id ? "text-zinc-900" : "text-zinc-400"}`}
                />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* 主体内容区 */}
        <div className="flex-1 flex flex-col min-w-0 bg-white relative">
          <header className="h-20 border-b border-zinc-100 flex items-center justify-between px-10 bg-white/80 backdrop-blur-md sticky top-0 z-20">
            <span className="text-xl font-bold text-zinc-800 tracking-tight">
              {tabs.find((t) => t.id === activeTab)?.label}
            </span>
            <div className="flex items-center">
              <div className="flex items-center text-[12px] border border-zinc-200 rounded-full bg-white shadow-sm px-4 py-2 font-semibold text-zinc-700">
                <HardDrive className="w-3.5 h-3.5 text-emerald-500 mr-2" />
                deepseek-r1
              </div>
            </div>
          </header>

          <main className="flex-1 p-8 overflow-y-auto bg-zinc-50/30">
            <div className="h-full">
              {activeTab === "unified" && <UnifiedChatView />}
              {activeTab === "research" && <DeepResearchView />}
              {activeTab === "coder" && <AutoCoderView />}
              {activeTab === "ocr" && <VisionOCRView />}
              {activeTab === "speech" && <SpeechAnalyticsView />}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
