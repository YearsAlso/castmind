"""
订阅源服务
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.database import Feed, Article

logger = logging.getLogger(__name__)

class FeedService:
    """订阅源服务类"""
    
    @staticmethod
    def get_feed(db: Session, feed_id: int) -> Optional[Feed]:
        """获取订阅源"""
        return db.query(Feed).filter(Feed.id == feed_id).first()
    
    @staticmethod
    def get_feeds(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Feed]:
        """获取订阅源列表"""
        query = db.query(Feed)
        
        if status:
            query = query.filter(Feed.status == status)
        if category:
            query = query.filter(Feed.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_feed(db: Session, feed_data: dict) -> Feed:
        """创建订阅源"""
        feed = Feed(**feed_data)
        db.add(feed)
        db.commit()
        db.refresh(feed)
        return feed
    
    @staticmethod
    def update_feed(db: Session, feed_id: int, feed_data: dict) -> Optional[Feed]:
        """更新订阅源"""
        feed = db.query(Feed).filter(Feed.id == feed_id).first()
        if not feed:
            return None
        
        for key, value in feed_data.items():
            if value is not None:
                setattr(feed, key, value)
        
        db.commit()
        db.refresh(feed)
        return feed
    
    @staticmethod
    def delete_feed(db: Session, feed_id: int) -> bool:
        """删除订阅源"""
        feed = db.query(Feed).filter(Feed.id == feed_id).first()
        if not feed:
            return False
        
        db.delete(feed)
        db.commit()
        return True
    
    @staticmethod
    def fetch_feed(db: Session, feed_id: int) -> Optional[Feed]:
        """抓取订阅源内容"""
        feed = db.query(Feed).filter(Feed.id == feed_id).first()
        if not feed:
            return None
        
        # 这里应该实现实际的 RSS 抓取逻辑
        # 暂时只是更新最后抓取时间
        from datetime import datetime
        feed.last_fetch = datetime.now()
        db.commit()
        db.refresh(feed)
        
        logger.info(f"已抓取订阅源: {feed.name} (ID: {feed_id})")
        return feed
    
    @staticmethod
    def get_feed_stats(db: Session) -> dict:
        """获取订阅源统计"""
        total = db.query(Feed).count()
        active = db.query(Feed).filter(Feed.status == "active").count()
        error = db.query(Feed).filter(Feed.status == "error").count()
        
        return {
            "total": total,
            "active": active,
            "error": error,
            "paused": total - active - error
        }