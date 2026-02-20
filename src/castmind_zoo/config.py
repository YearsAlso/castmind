"""
🎧 CastMind 配置模块

管理 CastMind 的所有配置
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class DatabaseConfig:
    """数据库配置"""
    
    # SQLite 配置
    sqlite_path: str = "data/castmind.db"
    
    # PostgreSQL 配置 (可选)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "castmind"
    postgres_user: str = "castmind"
    postgres_password: str = "castmind123"
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    
    # 连接池配置
    pool_size: int = 10
    pool_recycle: int = 3600
    pool_timeout: int = 30


@dataclass
class AIConfig:
    """AI 服务配置"""
    
    # DeepSeek 配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    
    # OpenAI 配置 (备用)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # 本地模型配置
    local_model_path: str = ""
    local_model_device: str = "cpu"
    
    # 通用配置
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retry_count: int = 3


@dataclass
class PodcastConfig:
    """播客处理配置"""
    
    # RSS 配置
    rss_timeout: int = 30
    rss_cache_ttl: int = 3600
    rss_max_items: int = 50
    
    # 音频处理配置
    audio_download_timeout: int = 300
    audio_max_size_mb: int = 100
    audio_supported_formats: List[str] = field(default_factory=lambda: [
        "mp3", "m4a", "wav", "flac", "ogg"
    ])
    
    # 转录配置
    transcription_language: str = "auto"
    transcription_model: str = "base"
    transcription_device: str = "cpu"
    
    # 总结配置
    summary_prompt_template: str = """
请总结以下播客内容：

{transcript}

请提供:
1. 3-5个关键观点
2. 主要内容摘要
3. 听众可能感兴趣的点
4. 使用{language}回复
"""
    
    # 文件输出配置
    output_dir: str = "data/output"
    keep_original_audio: bool = False
    max_output_files: int = 1000


@dataclass
class APIConfig:
    """API 配置"""
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # 安全配置
    api_key: str = ""
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60
    
    # 文档配置
    enable_docs: bool = True
    docs_path: str = "/api/docs"
    
    # 日志配置
    log_level: str = "info"
    access_log: bool = True
    
    # WebSocket 配置
    enable_websocket: bool = True
    websocket_ping_interval: int = 30


@dataclass
class WorkerConfig:
    """Worker 配置"""
    
    # Worker 数量配置
    rss_parser_count: int = 2
    audio_downloader_count: int = 3
    transcription_worker_count: int = 2
    ai_processor_count: int = 2
    file_generator_count: int = 2
    
    # 任务队列配置
    max_queue_size: int = 1000
    queue_timeout: int = 300
    
    # 重试配置
    max_retries: int = 3
    retry_delay: int = 60
    
    # 监控配置
    monitor_interval: int = 30
    health_check_interval: int = 60


@dataclass
class StorageConfig:
    """存储配置"""
    
    # 数据目录
    data_dir: str = "data"
    
    # 备份配置
    backup_dir: str = "data/backups"
    backup_retention_days: int = 7
    backup_schedule: str = "0 3 * * *"  # 每天凌晨3点
    
    # 清理配置
    cleanup_enabled: bool = True
    cleanup_max_age_days: int = 30
    cleanup_schedule: str = "0 4 * * *"  # 每天凌晨4点
    
    # 缓存配置
    cache_dir: str = "data/cache"
    cache_max_size_mb: int = 1024
    cache_ttl: int = 86400  # 24小时


@dataclass
class MonitoringConfig:
    """监控配置"""
    
    # Prometheus 配置
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    
    # 日志配置
    log_file: str = "logs/castmind.log"
    log_max_size_mb: int = 100
    log_backup_count: int = 5
    
    # 告警配置
    enable_alerts: bool = False
    alert_email: str = ""
    alert_webhook: str = ""
    
    # 性能监控
    monitor_cpu: bool = True
    monitor_memory: bool = True
    monitor_disk: bool = True
    monitor_network: bool = True


@dataclass
class CastMindConfig:
    """CastMind 总配置"""
    
    # 基础配置
    version: str = "1.0.0"
    environment: str = "development"  # development, testing, production
    debug: bool = False
    timezone: str = "Asia/Shanghai"
    
    # 子配置
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    podcast: PodcastConfig = field(default_factory=PodcastConfig)
    api: APIConfig = field(default_factory=APIConfig)
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # 元数据
    config_path: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保数据目录存在
        data_dir = Path(self.storage.data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 确保日志目录存在
        log_dir = Path(self.monitoring.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_file(cls, config_path: str) -> "CastMindConfig":
        """
        从配置文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            CastMindConfig 实例
        """
        config_path_obj = Path(config_path)
        
        if not config_path_obj.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        # 创建配置实例
        config = cls._from_dict(config_data)
        config.config_path = config_path
        
        return config
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "CastMindConfig":
        """从字典创建配置"""
        
        # 处理嵌套配置
        database_data = data.get("database", {})
        ai_data = data.get("ai", {})
        podcast_data = data.get("podcast", {})
        api_data = data.get("api", {})
        worker_data = data.get("worker", {})
        storage_data = data.get("storage", {})
        monitoring_data = data.get("monitoring", {})
        
        # 创建配置实例
        return cls(
            version=data.get("version", "1.0.0"),
            environment=data.get("environment", "development"),
            debug=data.get("debug", False),
            timezone=data.get("timezone", "Asia/Shanghai"),
            
            database=DatabaseConfig(**database_data),
            ai=AIConfig(**ai_data),
            podcast=PodcastConfig(**podcast_data),
            api=APIConfig(**api_data),
            worker=WorkerConfig(**worker_data),
            storage=StorageConfig(**storage_data),
            monitoring=MonitoringConfig(**monitoring_data),
            
            config_path=data.get("config_path"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=datetime.now().isoformat(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        
        # 更新更新时间
        data["updated_at"] = datetime.now().isoformat()
        
        return data
    
    def save(self, config_path: Optional[str] = None):
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用当前路径
        """
        if config_path is None:
            if self.config_path is None:
                raise ValueError("未指定配置文件路径")
            config_path = self.config_path
        
        config_path_obj = Path(config_path)
        config_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.config_path = config_path
    
    def validate(self) -> List[str]:
        """
        验证配置
        
        Returns:
            错误消息列表，如果为空则表示配置有效
        """
        errors = []
        
        # 验证必要配置
        if not self.ai.deepseek_api_key and not self.ai.openai_api_key:
            errors.append("必须配置至少一个 AI API Key (DeepSeek 或 OpenAI)")
        
        # 验证端口范围
        if not (1 <= self.api.port <= 65535):
            errors.append(f"API 端口必须在 1-65535 范围内: {self.api.port}")
        
        # 验证数据目录可写
        data_dir = Path(self.storage.data_dir)
        try:
            test_file = data_dir / ".test_write"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            errors.append(f"数据目录不可写: {data_dir} - {e}")
        
        # 验证环境变量
        if self.environment not in ["development", "testing", "production"]:
            errors.append(f"环境必须是 development/testing/production: {self.environment}")
        
        return errors
    
    def get_worker_count(self) -> int:
        """获取总 Worker 数量"""
        return (
            self.worker.rss_parser_count +
            self.worker.audio_downloader_count +
            self.worker.transcription_worker_count +
            self.worker.ai_processor_count +
            self.worker.file_generator_count
        )
    
    def get_api_url(self) -> str:
        """获取 API URL"""
        return f"http://{self.api.host}:{self.api.port}"
    
    def get_database_url(self) -> str:
        """获取数据库 URL"""
        # 这里可以根据配置返回 SQLite 或 PostgreSQL URL
        # 暂时返回 SQLite
        return f"sqlite:///{self.database.sqlite_path}"


# 默认配置
DEFAULT_CONFIG = CastMindConfig()

# 环境变量配置加载
def load_config_from_env() -> CastMindConfig:
    """
    从环境变量加载配置
    
    Returns:
        CastMindConfig 实例
    """
    config = CastMindConfig()
    
    # 从环境变量更新配置
    # AI 配置
    config.ai.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", config.ai.deepseek_api_key)
    config.ai.openai_api_key = os.getenv("OPENAI_API_KEY", config.ai.openai_api_key)
    
    # API 配置
    config.api.host = os.getenv("API_HOST", config.api.host)
    config.api.port = int(os.getenv("API_PORT", config.api.port))
    config.api.api_key = os.getenv("API_KEY", config.api.api_key)
    
    # 环境配置
    config.environment = os.getenv("ENVIRONMENT", config.environment)
    config.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # 数据目录
    config.storage.data_dir = os.getenv("DATA_DIR", config.storage.data_dir)
    
    return config


# 配置工厂
def create_config(
    config_path: Optional[str] = None,
    from_env: bool = True
) -> CastMindConfig:
    """
    创建配置
    
    Args:
        config_path: 配置文件路径
        from_env: 是否从环境变量加载
        
    Returns:
        CastMindConfig 实例
    """
    config = None
    
    # 1. 从配置文件加载
    if config_path and Path(config_path).exists():
        try:
            config = CastMindConfig.from_file(config_path)
        except Exception as e:
            print(f"⚠️ 配置文件加载失败: {e}")
    
    # 2. 从环境变量加载
    if config is None and from_env:
        try:
            config = load_config_from_env()
        except Exception as e:
            print(f"⚠️ 环境变量配置加载失败: {e}")
    
    # 3. 使用默认配置
    if config is None:
        config = CastMindConfig()
    
    # 验证配置
    errors = config.validate()
    if errors:
        print("⚠️ 配置验证警告:")
        for error in errors:
            print(f"   • {error}")
    
    return config