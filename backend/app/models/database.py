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
    last_fetch = Column(DateTime, nullable=True)
    article_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    articles = relationship("Article", back_populates="feed", cascade="all, delete-orphan")

class Article(Base):
    """文章模型"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id", ondelete="CASCADE"))
    title = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    read_status = Column(Boolean, default=False)
    processed_status = Column(Boolean, default=False)
    keywords = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    feed = relationship("Feed", back_populates="articles")