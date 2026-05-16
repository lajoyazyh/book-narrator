# src/api/server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import time
import uuid
from datetime import datetime
import os
from pydantic import BaseModel
from src.tools.narrator import NarratorTool
from src.agents.langchain_agent import LangChainNarratorAgent
from src.config.path import PathConfig

app = FastAPI(title="Book Narrator Agent API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 Agent 实例（保持上下文）
agent = LangChainNarratorAgent()

# ============ 请求/响应模型 ============#

class AgentRequest(BaseModel):
    user_request: str = Field(description="用户请求内容")
    reset_context: bool = Field(default=False, description="是否重置上下文")

class ToolCallRecord(BaseModel):
    tool_name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: str

class AgentResponse(BaseModel):
    task_id: str
    success: bool
    result: str
    context_summary: Dict[str, Any]
    tool_calls: List[ToolCallRecord]
    duration_seconds: float
    timestamp: str
    error: Optional[str] = None

class ContextResponse(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    total_chapters: int
    total_narrations: int
    total_audio_files: int

# ============ API 端点 ============#

@app.post("/api/v1/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """
    运行 Agent 并返回完整执行数据
    
    评估平台调用此接口，传入用户请求，获取：
    - 执行结果
    - 上下文状态
    - 工具调用记录
    - 耗时统计
    """
    task_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # 按需重置上下文
        if request.reset_context:
            agent.reset_context()
        
        # 执行 Agent
        result = agent.run(request.user_request)
        
        duration = time.time() - start_time
        
        # 提取工具调用记录
        tool_calls = _extract_tool_calls(result.get("context", {}))
        
        # 构建上下文摘要（避免返回过大数据）
        context_summary = _build_context_summary(result.get("context", {}))
        
        return AgentResponse(
            task_id=task_id,
            success=result.get("success", False),
            result=result.get("result", ""),
            context_summary=context_summary,
            tool_calls=tool_calls,
            duration_seconds=round(duration, 2),
            timestamp=datetime.now().isoformat(),
            error=result.get("error")
        )
    
    except Exception as e:
        return AgentResponse(
            task_id=task_id,
            success=False,
            result="",
            context_summary={},
            tool_calls=[],
            duration_seconds=round(time.time() - start_time, 2),
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

@app.get("/api/v1/agent/context", response_model=ContextResponse)
async def get_context():
    """获取当前 Agent 上下文状态"""
    context = agent.context
    
    return ContextResponse(
        metadata=context.get("metadata"),
        total_chapters=len(context.get("chapters", [])),
        total_narrations=len(context.get("narrations", {})),
        total_audio_files=len(context.get("audio_files", {}))
    )

@app.post("/api/v1/agent/reset")
async def reset_context():
    """重置 Agent 上下文"""
    agent.reset_context()
    return {"message": "上下文已重置"}

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    import os
    return {
        "status": "ok",
        "message": "Agent API is running",
        "model": os.getenv("MODEL_NAME", "unknown")
    }

@app.get("/api/v1/audio/list")
async def list_audio_files():
    """列出所有生成的音频文件"""
    audio_dir = PathConfig.AUDIO_DIR
    
    if not audio_dir.exists():
        return {"files": []}
    
    files = []
    for f in audio_dir.glob("*.mp3"):
        stat = f.stat()
        files.append({
            "filename": f.name,
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "url": f"/api/v1/audio/{f.name}"
        })
    
    return {"files": sorted(files, key=lambda x: x["created_at"], reverse=True)}

@app.get("/api/v1/audio/{filename}")
async def get_audio(filename: str):
    """获取生成的音频文件"""
    audio_path = PathConfig.get_audio_path(filename)
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail=f"音频文件不存在: {filename}")
    
    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=filename
    )

# ============ 辅助函数 ============#

def _extract_tool_calls(context: dict) -> List[dict]:
    """从上下文中提取工具调用记录"""
    tool_calls = context.get("tool_calls", [])
    # 将 ToolCallRecord 对象转换为字典
    return [tc.model_dump() if hasattr(tc, 'model_dump') else tc for tc in tool_calls]

def _build_context_summary(context: dict) -> Dict[str, Any]:
    """构建上下文摘要"""
    return {
        "metadata": context.get("metadata"),
        "total_chapters": len(context.get("chapters", [])),
        "chapter_titles": [ch.get("title") for ch in context.get("chapters", [])],
        "narrations": {str(k): f"[{len(v)} 字符]" for k, v in context.get("narrations", {}).items()},
        "audio_files": {str(k): v for k, v in context.get("audio_files", {}).items()}
    }