"""
Pydantic 数据模式
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class FeedBase(BaseModel):
    """订阅源基础模式"""

    name: str
    url: str
    category: Optional[str] = "未分类"
    interval: Optional[int] = 3600
    author: Optional[str] = None
    description: Optional[str] = None


class FeedCreate(FeedBase):
    """创建订阅源模式"""

    pass


class FeedUpdate(BaseModel):
    """更新订阅源模式"""

    name: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    interval: Optional[int] = None
    status: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class FeedResponse(FeedBase):
    """订阅源响应模式"""

    id: int
    status: str
    feed_type: str = "rss"
    image_url: Optional[str] = None
    last_fetch: Optional[datetime]
    article_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleBase(BaseModel):
    """文章基础模式"""

    title: str
    url: str
    content: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None


class ArticleCreate(ArticleBase):
    """创建文章模式"""

    feed_id: int


class ArticleUpdate(BaseModel):
    """更新文章模式"""

    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    read_status: Optional[bool] = None
    processed_status: Optional[bool] = None
    keywords: Optional[str] = None
    sentiment: Optional[str] = None
    author: Optional[str] = None


class ArticleResponse(BaseModel):
    """文章响应模式"""

    id: int
    feed_id: int
    feed_name: Optional[str] = None
    title: str
    url: str
    author: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    read_status: bool
    processed_status: bool
    keywords: Optional[str] = None
    sentiment: Optional[str] = None
    key_points: Optional[str] = None
    business_insights: Optional[str] = None
    technical_points: Optional[str] = None
    action_items: Optional[str] = None
    is_podcast: bool = False
    audio_url: Optional[str] = None
    audio_type: Optional[str] = None
    audio_duration: Optional[int] = None
    audio_size: Optional[int] = None
    audio_local_path: Optional[str] = None
    podcast_description: Optional[str] = None
    transcript: Optional[str] = None
    podcast_summary: Optional[str] = None
    chapters: Optional[str] = None
    transcription_status: str = "pending"
    analysis_status: str = "pending"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PodcastAnalysisRequest(BaseModel):
    """播客分析请求"""

    article_id: int
    generate_summary: bool = True
    extract_chapters: bool = True


class PodcastAnalysisResponse(BaseModel):
    """播客分析响应"""

    article_id: int
    title: str
    audio_url: Optional[str] = None
    audio_duration: Optional[int] = None
    podcast_summary: Optional[str] = None
    key_topics: Optional[List[str]] = None
    chapters: Optional[List[dict]] = None
    action_items: Optional[str] = None
    timestamp: str


class TaskBase(BaseModel):
    """任务基础模式"""

    task_type: str
    task_name: Optional[str] = None


class TaskCreate(TaskBase):
    """创建任务模式"""

    feed_id: Optional[int] = None
    article_id: Optional[int] = None


class TaskResponse(TaskBase):
    """任务响应模式"""

    id: int
    feed_id: Optional[int] = None
    article_id: Optional[int] = None
    status: str
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""

    total: int
    tasks: List[TaskResponse]


class StatsResponse(BaseModel):
    """统计响应模式"""

    feeds: dict
    articles: dict
    system: dict
    tasks: dict


class HealthResponse(BaseModel):
    """健康检查响应模式"""

    status: str
    app: str
    version: str
    database: str
    timestamp: str
    scheduler: Optional[dict] = None
    ai_service: Optional[str] = None


class TrendsResponse(BaseModel):
    """趋势统计响应模式"""

    feeds: dict
    articles: dict
    unread_articles: dict
    tasks: dict
