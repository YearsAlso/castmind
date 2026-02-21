"""
应用配置管理
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    # 应用信息
    APP_NAME: str = "CastMind"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "sqlite:///data/castmind.db"
    DATABASE_ECHO: bool = False

    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # 文档配置
    DOCS_ENABLED: bool = True

    # AI 服务配置
    AI_SERVICE_ENABLED: bool = True
    AI_MODEL: str = "gpt-3.5-turbo"
    AI_MAX_TOKENS: int = 1000

    # 任务调度配置
    SCHEDULER_ENABLED: bool = True
    FETCH_INTERVAL_MINUTES: int = 10
    CLEANUP_DAYS: int = 30
    PROCESS_ARTICLES_MINUTES: int = 15
    UPDATE_STATUS_HOURS: int = 1
    CLEANUP_HOUR: int = 2
    SCHEDULER_TIMEZONE: str = "Asia/Shanghai"
    SCHEDULER_MAX_INSTANCES: int = 1
    SCHEDULER_MISFIRE_GRACE_TIME: int = 30

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "data/logs/castmind.log"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 允许额外的环境变量


# 全局配置实例
settings = Settings()
