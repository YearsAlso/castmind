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

class FeedResponse(FeedBase):
    """订阅源响应模式"""
    id: int
    status: str
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

class ArticleResponse(ArticleBase):
    """文章响应模式"""
    id: int
    feed_id: int
    feed_name: Optional[str] = None
    read_status: bool
    processed_status: bool
    keywords: Optional[str] = None
    sentiment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

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