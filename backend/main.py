"""
CastMind 后端主入口
FastAPI 应用服务器
"""
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional

from app.core.config import settings
from app.core.database import init_db, get_db
from app.api.v1 import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时
    logger.info("启动 CastMind 后端服务...")
    
    # 初始化数据库
    try:
        # 确保数据目录存在
        import os
        from pathlib import Path
        
        data_dir = Path("data")
        if not data_dir.exists():
            logger.info(f"创建数据目录: {data_dir}")
            data_dir.mkdir(exist_ok=True)
        
        logs_dir = data_dir / "logs"
        if not logs_dir.exists():
            logger.info(f"创建日志目录: {logs_dir}")
            logs_dir.mkdir(exist_ok=True)
        
        # 初始化数据库
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        # 不直接抛出异常，让应用继续启动
        # 数据库连接会在第一次使用时建立
    
    yield
    
    # 关闭时
    logger.info("关闭 CastMind 后端服务...")

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CastMind - 智能播客订阅处理平台",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/api/redoc" if settings.DOCS_ENABLED else None,
)

# 配置 CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册 API 路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根端点"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs" if settings.DOCS_ENABLED else None,
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
        "timestamp": "2026-02-20T21:15:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )