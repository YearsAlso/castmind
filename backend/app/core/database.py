"""
数据库连接和模型管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

from .config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

def get_db():
    """
    获取数据库会话依赖
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化数据库，创建所有表
    """
    try:
        # 导入所有模型以确保它们被注册
        from app.models.database import Feed, Article
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise