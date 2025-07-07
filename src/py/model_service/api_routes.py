"""
API 路由定义
"""

import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .model_manager import model_manager
from utils.log_util import default_logger as logger

router = APIRouter()

# 请求/响应模型
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

class ModelInfoResponse(BaseModel):
    model_name: str
    device: str
    is_loaded: bool
    model_size: Optional[int] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """普通聊天接口"""
    try:
        logger.info(f"收到聊天请求: {request.message}")
        
        # 转换历史记录格式
        history = []
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # 生成响应
        response = model_manager.generate_response(request.message, history)
        logger.info(f"生成响应完成")
        
        return ChatResponse(
            response=response,
            success=True
        )
        
    except Exception as e:
        logger.error(f"聊天请求处理失败: {e}")
        return ChatResponse(
            response="",
            success=False,
            error=str(e)
        )

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    try:
        logger.info(f"收到流式聊天请求: {request.message}")
        
        # 转换历史记录格式
        history = []
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        def generate():
            try:
                # 发送开始标记
                yield f"data: {json.dumps({'type': 'start', 'content': ''})}\n\n"
                
                # 流式生成响应
                for chunk in model_manager.generate_response_stream(request.message, history):
                    # 发送文本块
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # 发送结束标记
                yield f"data: {json.dumps({'type': 'end', 'content': ''})}\n\n"
                
            except Exception as e:
                logger.error(f"流式生成失败: {e}")
                # 发送错误信息
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
            }
        )
        
    except Exception as e:
        logger.error(f"流式聊天请求处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    try:
        is_healthy, message = model_manager.health_check()
        
        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            message=message
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return HealthResponse(
            status="error",
            message=str(e)
        )

@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """获取模型信息"""
    try:
        info = model_manager.get_model_info()
        
        return ModelInfoResponse(
            model_name=info["model_name"],
            device=info["device"],
            is_loaded=info["is_loaded"],
            model_size=info["model_size"]
        )
        
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/model/load")
async def load_model():
    """加载模型"""
    try:
        if model_manager.is_loaded:
            return {"status": "already_loaded", "message": "模型已加载"}
        
        model_manager.load_model()
        return {"status": "loaded", "message": "模型加载完成"}
        
    except Exception as e:
        logger.error(f"加载模型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))