"""
SQLAlchemy 数据库模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Feed(Base):
    """订阅源模型"""

    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    category = Column(String(100), default="未分类")
    interval = Column(Integer, default=3600)  # 抓取间隔（秒）
    status = Column(String(50), default="active")  # active, paused, error
    feed_type = Column(String(50), default="rss")  # rss, podcast, atom
    author = Column(String(255), nullable=True)  # 播客主持人/网站作者
    image_url = Column(String(500), nullable=True)  # 播客封面图
    description = Column(Text, nullable=True)  # 订阅源描述
    last_fetch = Column(DateTime, nullable=True)
    article_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    articles = relationship(
        "Article", back_populates="feed", cascade="all, delete-orphan"
    )


class Article(Base):
    """文章/播客剧集模型"""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id", ondelete="CASCADE"))
    title = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    author = Column(String(255), nullable=True)  # 文章作者/播客嘉宾
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    read_status = Column(Boolean, default=False)
    processed_status = Column(Boolean, default=False)
    keywords = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    key_points = Column(Text, nullable=True)
    business_insights = Column(Text, nullable=True)
    technical_points = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)

    # 播客相关字段
    is_podcast = Column(Boolean, default=False)  # 是否为播客
    audio_url = Column(String(500), nullable=True)  # 音频文件URL
    audio_type = Column(String(50), nullable=True)  # 音频类型 (mp3, m4a, etc)
    audio_duration = Column(Integer, nullable=True)  # 时长（秒）
    audio_size = Column(Integer, nullable=True)  # 文件大小（字节）
    audio_local_path = Column(String(500), nullable=True)  # 本地音频文件路径
    podcast_description = Column(Text, nullable=True)  # 播客描述/笔记
    transcript = Column(Text, nullable=True)  # 转录文本
    podcast_summary = Column(Text, nullable=True)  # AI生成的播客摘要
    chapters = Column(Text, nullable=True)  # 章节信息 (JSON)

    # 转录和分析状态
    transcription_status = Column(
        String(50), default="pending"
    )  # pending, running, completed, failed
    analysis_status = Column(
        String(50), default="pending"
    )  # pending, running, completed, failed

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    feed = relationship("Feed", back_populates="articles")


class Task(Base):
    """任务模型"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(
        Integer, ForeignKey("feeds.id", ondelete="SET NULL"), nullable=True
    )
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="SET NULL"), nullable=True
    )
    task_type = Column(
        String(50), nullable=False
    )  # fetch, transcription, analysis, cleanup
    task_name = Column(String(100), nullable=True)  # 任务名称
    status = Column(
        String(20), default="pending"
    )  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 进度百分比
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result_data = Column(Text, nullable=True)  # JSON 存储结果
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
