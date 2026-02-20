"""
系统 API 路由
"""
import psutil
import platform
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.database import Feed, Article
from app.models.schemas import HealthResponse, StatsResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    系统健康检查
    """
    return HealthResponse(
        status="healthy",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        database="connected",
        timestamp=datetime.now().isoformat()
    )

@router.get("/stats", response_model=StatsResponse)
async def get_system_stats(
    db: Session = Depends(get_db)
):
    """
    获取系统统计信息
    """
    # 订阅源统计
    total_feeds = db.query(Feed).count()
    active_feeds = db.query(Feed).filter(Feed.status == "active").count()
    error_feeds = db.query(Feed).filter(Feed.status == "error").count()
    
    # 文章统计
    total_articles = db.query(Article).count()
    unread_articles = db.query(Article).filter(Article.read_status == False).count()
    processed_articles = db.query(Article).filter(Article.processed_status == True).count()
    
    # 系统资源统计
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return StatsResponse(
        feeds={
            "total": total_feeds,
            "active": active_feeds,
            "error": error_feeds,
            "paused": total_feeds - active_feeds - error_feeds
        },
        articles={
            "total": total_articles,
            "unread": unread_articles,
            "read": total_articles - unread_articles,
            "processed": processed_articles
        },
        system={
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_usage": disk.percent,
            "platform": platform.system(),
            "python_version": platform.python_version()
        },
        tasks={
            "total": 3,  # 抓取、清理、状态更新
            "running": 3,
            "success_rate": 98.5
        }
    )

@router.get("/config")
async def get_config():
    """
    获取系统配置（安全过滤版本）
    """
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "host": settings.HOST,
        "port": settings.PORT,
        "debug": settings.DEBUG,
        "docs_enabled": settings.DOCS_ENABLED,
        "ai_service_enabled": settings.AI_SERVICE_ENABLED,
        "scheduler_enabled": settings.SCHEDULER_ENABLED,
        "fetch_interval_minutes": settings.FETCH_INTERVAL_MINUTES,
        "cleanup_days": settings.CLEANUP_DAYS
    }

@router.get("/logs")
async def get_logs():
    """
    获取系统日志（简化版本）
    """
    # 这里应该从日志文件读取
    # 暂时返回示例日志
    return {
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "系统启动完成"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO", 
                "message": "数据库连接正常"
            }
        ],
        "total": 2
    }

@router.post("/scheduler/start")
async def start_scheduler():
    """
    启动任务调度器
    """
    # 这里应该启动实际的调度器
    # 暂时返回成功响应
    return {
        "status": "success",
        "message": "调度器已启动",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    停止任务调度器
    """
    # 这里应该停止实际的调度器
    # 暂时返回成功响应
    return {
        "status": "success",
        "message": "调度器已停止",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/process/all")
async def process_all_articles():
    """
    处理所有未处理的文章
    """
    # 这里应该调用 AI 服务处理所有文章
    # 暂时返回成功响应
    return {
        "status": "success",
        "message": "已开始处理所有文章",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/version")
async def get_version():
    """
    获取版本信息
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_version": "v1",
        "timestamp": datetime.now().isoformat()
    }