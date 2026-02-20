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
        """抓取订阅源内容并保存文章"""
        from datetime import datetime
        from app.services.rss_service import RSSService
        
        feed = db.query(Feed).filter(Feed.id == feed_id).first()
        if not feed:
            return None
        
        try:
            logger.info(f"开始抓取订阅源: {feed.name} (URL: {feed.url})")
            
            # 解析 RSS 订阅源
            feed_info = RSSService.parse_feed(feed.url)
            if not feed_info:
                logger.error(f"无法解析订阅源: {feed.url}")
                feed.status = "error"
                db.commit()
                return None
            
            # 提取文章信息
            articles_data = RSSService.extract_articles(feed_info)
            
            # 保存文章到数据库
            new_articles_count = 0
            from app.services.ai_service import AIService
            ai_service = AIService()
            
            for article_data in articles_data:
                # 检查文章是否已存在（通过 URL）
                existing_article = db.query(Article).filter(
                    Article.url == article_data["url"]
                ).first()
                
                if not existing_article:
                    # 创建新文章
                    article = Article(
                        feed_id=feed.id,
                        title=article_data["title"],
                        url=article_data["url"],
                        content=article_data["content"],
                        summary=article_data.get("summary", ""),
                        published_at=article_data["published_at"],
                        author=article_data.get("author", ""),
                        keywords=article_data.get("categories", ""),
                    )
                    db.add(article)
                    db.flush()  # 获取 article.id
                    
                    # 进行 AI 分析
                    try:
                        analysis_result = ai_service.analyze_article(
                            title=article.title,
                            content=article.content
                        )
                        
                        # 更新文章的分析结果
                        if analysis_result:
                            article.summary = analysis_result.get("summary", article.summary)
                            article.keywords = analysis_result.get("keywords", article.keywords)
                            article.sentiment = analysis_result.get("sentiment", "")
                            article.key_points = analysis_result.get("key_points", "")
                            article.business_insights = analysis_result.get("business_insights", "")
                            article.technical_points = analysis_result.get("technical_points", "")
                            article.action_items = analysis_result.get("action_items", "")
                            
                            logger.info(f"文章 AI 分析完成: {article.title}")
                        
                    except Exception as e:
                        logger.warning(f"文章 AI 分析失败 (ID: {article.id}): {e}")
                        # 继续处理其他文章
                    
                    new_articles_count += 1
            
            # 更新订阅源信息
            feed.last_fetch = datetime.now()
            feed.article_count = db.query(Article).filter(Article.feed_id == feed.id).count()
            feed.status = "active"
            db.commit()
            db.refresh(feed)
            
            logger.info(f"成功抓取订阅源: {feed.name}, 新增 {new_articles_count} 篇文章, 总计 {feed.article_count} 篇")
            return feed
            
        except Exception as e:
            logger.error(f"抓取订阅源失败 (ID: {feed_id}): {e}")
            feed.status = "error"
            db.commit()
            return None
    
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