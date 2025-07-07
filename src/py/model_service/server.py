"""
FastAPI 服务器主程序
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api_routes import router
from .model_manager import model_manager
from utils.log_util import default_logger as logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时加载模型
    logger.info("正在启动服务，加载模型...")
    try:
        model_manager.load_model()
        logger.info("模型加载完成，服务准备就绪")
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        raise
    
    yield
    
    # 关闭时的清理工作
    logger.info("服务正在关闭...")

# 创建 FastAPI 应用
app = FastAPI(
    title="Qwen3 模型服务",
    description="基于 FastAPI 的 Qwen3 模型服务，支持普通聊天和流式聊天",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(router, prefix="/api/v1")

# 根路径
@app.get("/")
async def root():
    return {
        "message": "Qwen3 模型服务",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# 健康检查（根路径版本）
@app.get("/health")
async def health():
    return {"status": "ok", "service": "qwen3-model-service"}

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=19100,
        reload=False,  # 生产环境关闭热重载
        log_level="info"
    )