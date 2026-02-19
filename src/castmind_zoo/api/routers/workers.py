"""
🎧 Worker 管理路由
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from ..dependencies import get_config, verify_api_key, get_pagination_params
from ...config import CastMindConfig

router = APIRouter()


@router.get("/workers", summary="获取 Worker 列表", tags=["Worker 管理"])
async def list_workers(
    config: CastMindConfig = Depends(get_config),
    api_key: str = Depends(verify_api_key),
    pagination: Dict = Depends(get_pagination_params)
) -> Dict[str, Any]:
    """
    获取所有 Worker 的列表
    
    返回系统中所有 Worker 的状态和信息
    """
    # 这里应该从 Zoo Framework 获取实际的 Worker 信息
    # 暂时返回模拟数据
    
    workers = [
        {
            "id": "rss_parser_1",
            "name": "RSS 解析器",
            "type": "rss_parser",
            "status": "running",
            "metrics": {
                "processed_items": 152,
                "errors": 3,
                "last_activity": "2026-02-19T15:30:00Z"
            },
            "config": {
                "timeout": config.podcast.rss_timeout,
                "cache_ttl": config.podcast.rss_cache_ttl
            }
        },
        {
            "id": "audio_downloader_1",
            "name": "音频下载器",
            "type": "audio_downloader",
            "status": "running",
            "metrics": {
                "downloaded_files": 89,
                "total_size_gb": 12.5,
                "last_activity": "2026-02-19T15:25:00Z"
            },
            "config": {
                "timeout": config.podcast.audio_download_timeout,
                "max_size_mb": config.podcast.audio_max_size_mb
            }
        },
        {
            "id": "transcription_worker_1",
            "name": "转录 Worker",
            "type": "transcription",
            "status": "idle",
            "metrics": {
                "transcribed_minutes": 245,
                "accuracy": 0.92,
                "last_activity": "2026-02-19T14:45:00Z"
            },
            "config": {
                "language": config.podcast.transcription_language,
                "model": config.podcast.transcription_model
            }
        },
        {
            "id": "ai_processor_1",
            "name": "AI 处理器",
            "type": "ai_processor",
            "status": "running",
            "metrics": {
                "processed_tasks": 312,
                "tokens_used": 125000,
                "last_activity": "2026-02-19T15:28:00Z"
            },
            "config": {
                "model": config.ai.deepseek_model if config.ai.deepseek_api_key else config.ai.openai_model,
                "max_tokens": config.ai.max_tokens
            }
        }
    ]
    
    # 应用分页
    skip = pagination["skip"]
    limit = pagination["limit"]
    paginated_workers = workers[skip:skip + limit]
    
    return {
        "total": len(workers),
        "count": len(paginated_workers),
        "skip": skip,
        "limit": limit,
        "workers": paginated_workers,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/workers/{worker_id}", summary="获取 Worker 详情", tags=["Worker 管理"])
async def get_worker(
    worker_id: str,
    config: CastMindConfig = Depends(get_config),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    获取指定 Worker 的详细信息
    """
    # 这里应该从 Zoo Framework 获取实际的 Worker 信息
    # 暂时返回模拟数据
    
    worker_data = {
        "rss_parser_1": {
            "id": "rss_parser_1",
            "name": "RSS 解析器 #1",
            "type": "rss_parser",
            "status": "running",
            "started_at": "2026-02-19T08:00:00Z",
            "metrics": {
                "processed_items": 152,
                "errors": 3,
                "success_rate": 0.98,
                "average_processing_time": 2.5,
                "last_error": None,
                "last_success": "2026-02-19T15:30:00Z"
            },
            "config": {
                "timeout": config.podcast.rss_timeout,
                "cache_ttl": config.podcast.rss_cache_ttl,
                "max_items": config.podcast.rss_max_items,
                "user_agent": "CastMind/1.0"
            },
            "performance": {
                "cpu_usage": 15.2,
                "memory_usage_mb": 128.5,
                "thread_count": 3
            }
        },
        "audio_downloader_1": {
            "id": "audio_downloader_1",
            "name": "音频下载器 #1",
            "type": "audio_downloader",
            "status": "running",
            "started_at": "2026-02-19T08:00:00Z",
            "metrics": {
                "downloaded_files": 89,
                "total_size_gb": 12.5,
                "average_speed_mbps": 5.2,
                "failed_downloads": 2,
                "last_download": "2026-02-19T15:25:00Z"
            },
            "config": {
                "timeout": config.podcast.audio_download_timeout,
                "max_size_mb": config.podcast.audio_max_size_mb,
                "supported_formats": config.podcast.audio_supported_formats,
                "concurrent_downloads": 3
            },
            "performance": {
                "cpu_usage": 8.7,
                "memory_usage_mb": 85.3,
                "network_usage_mbps": 2.1
            }
        }
    }
    
    if worker_id not in worker_data:
        raise HTTPException(
            status_code=404,
            detail=f"Worker '{worker_id}' 未找到"
        )
    
    return {
        "worker": worker_data[worker_id],
        "timestamp": datetime.now().isoformat()
    }


@router.post("/workers/{worker_id}/restart", summary="重启 Worker", tags=["Worker 管理"])
async def restart_worker(
    worker_id: str,
    config: CastMindConfig = Depends(get_config),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    重启指定的 Worker
    """
    # 这里应该调用 Zoo Framework 的 Worker 重启逻辑
    # 暂时返回模拟响应
    
    valid_workers = ["rss_parser_1", "audio_downloader_1", "transcription_worker_1", "ai_processor_1"]
    
    if worker_id not in valid_workers:
        raise HTTPException(
            status_code=404,
            detail=f"Worker '{worker_id}' 未找到"
        )
    
    return {
        "status": "success",
        "message": f"Worker '{worker_id}' 重启命令已发送",
        "worker_id": worker_id,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/workers/{worker_id}/metrics", summary="获取 Worker 指标", tags=["Worker 管理"])
async def get_worker_metrics(
    worker_id: str,
    timeframe: str = Query("1h", description="时间范围: 1h, 24h, 7d, 30d"),
    config: CastMindConfig = Depends(get_config),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    获取 Worker 的性能指标历史
    """
    # 这里应该从监控系统获取实际的指标数据
    # 暂时返回模拟数据
    
    # 生成模拟时间序列数据
    import random
    from datetime import timedelta
    
    now = datetime.now()
    data_points = []
    
    # 根据时间范围确定数据点数量
    if timeframe == "1h":
        points = 60  # 每分钟一个点
        delta = timedelta(minutes=1)
    elif timeframe == "24h":
        points = 24  # 每小时一个点
        delta = timedelta(hours=1)
    elif timeframe == "7d":
        points = 7  # 每天一个点
        delta = timedelta(days=1)
    else:  # 30d
        points = 30  # 每天一个点
        delta = timedelta(days=1)
    
    for i in range(points):
        timestamp = now - (delta * (points - i - 1))
        data_points.append({
            "timestamp": timestamp.isoformat(),
            "cpu_usage": random.uniform(5, 25),
            "memory_usage_mb": random.uniform(50, 150),
            "processed_items": random.randint(0, 10),
            "error_count": random.randint(0, 2)
        })
    
    return {
        "worker_id": worker_id,
        "timeframe": timeframe,
        "metrics": data_points,
        "summary": {
            "avg_cpu_usage": sum(p["cpu_usage"] for p in data_points) / len(data_points),
            "avg_memory_usage_mb": sum(p["memory_usage_mb"] for p in data_points) / len(data_points),
            "total_processed": sum(p["processed_items"] for p in data_points),
            "total_errors": sum(p["error_count"] for p in data_points)
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/workers/stats", summary="Worker 统计", tags=["Worker 管理"])
async def get_worker_stats(
    config: CastMindConfig = Depends(get_config),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    获取 Worker 的统计信息
    """
    # 这里应该从 Zoo Framework 获取实际的统计信息
    # 暂时返回模拟数据
    
    stats = {
        "total_workers": config.worker.get_worker_count(),
        "active_workers": 4,
        "idle_workers": 1,
        "worker_types": {
            "rss_parser": config.worker.rss_parser_count,
            "audio_downloader": config.worker.audio_downloader_count,
            "transcription": config.worker.transcription_worker_count,
            "ai_processor": config.worker.ai_processor_count,
            "file_generator": config.worker.file_generator_count
        },
        "performance": {
            "total_processed_tasks": 1258,
            "success_rate": 0.97,
            "avg_processing_time": 3.2,
            "peak_concurrent_tasks": 12
        },
        "resource_usage": {
            "total_cpu_percent": 45.3,
            "total_memory_mb": 512.7,
            "avg_cpu_per_worker": 11.3,
            "avg_memory_per_worker_mb": 128.2
        }
    }
    
    return {
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/workers/scale", summary="调整 Worker 数量", tags=["Worker 管理"])
async def scale_workers(
    worker_type: str = Query(..., description="Worker 类型: rss_parser, audio_downloader, transcription, ai_processor, file_generator"),
    count: int = Query(..., ge=1, le=20, description="目标数量"),
    config: CastMindConfig = Depends(get_config),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    调整指定类型 Worker 的数量
    """
    # 这里应该调用 Zoo Framework 的 Worker 缩放逻辑
    # 暂时返回模拟响应
    
    valid_types = ["rss_parser", "audio_downloader", "transcription", "ai_processor", "file_generator"]
    
    if worker_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的 Worker 类型。必须是: {', '.join(valid_types)}"
        )
    
    # 检查数量限制
    max_workers = 20
    if count > max_workers:
        raise HTTPException(
            status_code=400,
            detail=f"Worker 数量不能超过 {max_workers}"
        )
    
    return {
        "status": "success",
        "message": f"{worker_type} Worker 数量已调整为 {count}",
        "worker_type": worker_type,
        "target_count": count,
        "timestamp": datetime.now().isoformat()
    }