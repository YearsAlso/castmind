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
    connect_args={"check_same_thread": False, "timeout": 30} if "sqlite" in settings.DATABASE_URL else {}
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
        # 确保数据目录存在
        import os
        from pathlib import Path
        
        # 从数据库 URL 中提取路径
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite:///"):
            # 提取相对路径
            db_path = db_url.replace("sqlite:///", "")
            db_dir = Path(db_path).parent
            
            if db_dir and not db_dir.exists():
                logger.info(f"创建数据库目录: {db_dir}")
                db_dir.mkdir(parents=True, exist_ok=True)
        
        # 导入所有模型以确保它们被注册
        from app.models.database import Feed, Article
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
        
        # 验证表是否创建成功
        with engine.connect() as conn:
            # SQLAlchemy 2.0 语法
            from sqlalchemy import text
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            logger.info(f"数据库中的表: {tables}")
            
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        
        # 尝试使用更简单的方法创建表
        try:
            logger.info("尝试使用备用方法创建表...")
            import sqlite3
            
            # 直接使用 SQLite 创建表
            if db_url.startswith("sqlite:///"):
                db_path = db_url.replace("sqlite:///", "")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 创建 feeds 表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feeds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        category TEXT DEFAULT '未分类',
                        interval INTEGER DEFAULT 3600,
                        status TEXT DEFAULT 'active',
                        last_fetch TIMESTAMP,
                        article_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建 articles 表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        feed_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        content TEXT,
                        summary TEXT,
                        published_at TIMESTAMP,
                        read_status BOOLEAN DEFAULT 0,
                        processed_status BOOLEAN DEFAULT 0,
                        keywords TEXT,
                        sentiment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE
                    )
                """)
                
                conn.commit()
                cursor.close()
                conn.close()
                
                logger.info("使用备用方法成功创建数据库表")
                return True
                
        except Exception as e2:
            logger.error(f"备用方法也失败: {e2}")
        
        # 返回 False 但不抛出异常，让应用可以继续启动
        return False