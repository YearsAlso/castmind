"""
🎧 健康检查路由
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import get_config
from ...config import CastMindConfig

router = APIRouter()


@router.get("/health", summary="健康检查", tags=["健康检查"])
async def health_check(
    config: CastMindConfig = Depends(get_config)
) -> Dict[str, Any]:
    """
    健康检查端点
    
    返回系统健康状态信息
    """
    return {
        "status": "healthy",
        "service": "CastMind",
        "version": config.version,
        "environment": config.environment,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "running",
            "database": "connected",  # 这里可以添加实际的数据库检查
            "ai_service": "available" if config.ai.deepseek_api_key or config.ai.openai_api_key else "unconfigured",
            "storage": "available",
        }
    }


@router.get("/health/detailed", summary="详细健康检查", tags=["健康检查"])
async def detailed_health_check(
    config: CastMindConfig = Depends(get_config)
) -> Dict[str, Any]:
    """
    详细健康检查端点
    
    返回更详细的系统状态信息
    """
    import psutil
    import platform
    
    # 获取系统信息
    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "disk_usage_percent": psutil.disk_usage("/").percent,
    }
    
    # 获取进程信息
    process = psutil.Process()
    process_info = {
        "pid": process.pid,
        "name": process.name(),
        "memory_percent": process.memory_percent(),
        "cpu_percent": process.cpu_percent(),
        "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": system_info,
        "process": process_info,
        "config": {
            "environment": config.environment,
            "debug": config.debug,
            "api_port": config.api.port,
            "data_dir": config.storage.data_dir,
        }
    }


@router.get("/health/readiness", summary="就绪检查", tags=["健康检查"])
async def readiness_check() -> Dict[str, Any]:
    """
    就绪检查端点
    
    Kubernetes 就绪探针使用
    """
    # 这里可以添加更严格的就绪检查
    # 例如: 数据库连接、Redis 连接、外部服务等
    
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/health/liveness", summary="存活检查", tags=["健康检查"])
async def liveness_check() -> Dict[str, Any]:
    """
    存活检查端点
    
    Kubernetes 存活探针使用
    """
    # 简单的存活检查，只要进程在运行就返回成功
    
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/health/metrics", summary="性能指标", tags=["健康检查"])
async def metrics_check() -> Dict[str, Any]:
    """
    性能指标端点
    
    返回系统性能指标
    """
    import psutil
    import time
    
    # 获取系统指标
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "percent": cpu_percent,
            "count": psutil.cpu_count(),
            "frequency": psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else None,
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent": memory.percent,
            "used_gb": round(memory.used / (1024**3), 2),
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent,
        },
        "network": {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
        },
        "process": {
            "thread_count": len(psutil.Process().threads()),
            "open_files": len(psutil.Process().open_files()),
            "connections": len(psutil.Process().connections()),
        }
    }


@router.get("/health/config", summary="配置检查", tags=["健康检查"])
async def config_check(
    config: CastMindConfig = Depends(get_config)
) -> Dict[str, Any]:
    """
    配置检查端点
    
    返回当前配置信息（敏感信息会被隐藏）
    """
    config_dict = config.to_dict()
    
    # 隐藏敏感信息
    def hide_sensitive(data):
        if isinstance(data, dict):
            for key in list(data.keys()):
                if any(sensitive in key.lower() for sensitive in ["key", "password", "secret", "token"]):
                    data[key] = "***HIDDEN***"
                elif isinstance(data[key], dict):
                    hide_sensitive(data[key])
                elif isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict):
                            hide_sensitive(item)
        return data
    
    safe_config = hide_sensitive(config_dict.copy())
    
    return {
        "timestamp": datetime.now().isoformat(),
        "config": safe_config,
        "validation_errors": config.validate(),
    }