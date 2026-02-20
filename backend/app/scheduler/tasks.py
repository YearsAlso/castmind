"""
定时任务定义
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.database import Feed, Article
from app.services.rss_service import RSSService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.rss_service = RSSService()
        self.ai_service = AIService()
        logger.info("任务调度器初始化完成")
    
    def fetch_all_feeds(self) -> dict:
        """
        抓取所有订阅源
        
        Returns:
            抓取结果统计
        """
        logger.info("开始抓取所有订阅源...")
        
        db = SessionLocal()
        try:
            feeds = db.query(Feed).filter(Feed.status == "active").all()
            total_feeds = len(feeds)
            success_count = 0
            error_count = 0
            
            for feed in feeds:
                try:
                    self._fetch_single_feed(db, feed)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"抓取订阅源失败 (ID: {feed.id}, URL: {feed.url}): {e}")
                    feed.status = "error"
                    db.commit()
                    error_count += 1
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "total_feeds": total_feeds,
                "success": success_count,
                "error": error_count,
                "skipped": total_feeds - success_count - error_count
            }
            
            logger.info(f"订阅源抓取完成: {result}")
            return result
            
        finally:
            db.close()
    
    def _fetch_single_feed(self, db: Session, feed: Feed):
        """抓取单个订阅源"""
        logger.info(f"抓取订阅源: {feed.name} (ID: {feed.id})")
        
        # 解析 RSS 订阅源
        feed_info = self.rss_service.parse_feed(feed.url)
        if not feed_info:
            raise ValueError("RSS 解析失败")
        
        # 提取文章
        articles = self.rss_service.extract_articles(feed_info)
        
        # 保存文章到数据库
        new_articles = 0
        for article_data in articles:
            # 检查文章是否已存在
            existing = db.query(Article).filter(Article.url == article_data["url"]).first()
            if existing:
                continue
            
            # 创建新文章
            article = Article(
                feed_id=feed.id,
                title=article_data["title"],
                url=article_data["url"],
                content=article_data["content"],
                summary=article_data["summary"],
                published_at=article_data["published_at"]
            )
            
            db.add(article)
            new_articles += 1
        
        # 更新订阅源信息
        feed.last_fetch = datetime.now()
        feed.article_count = db.query(Article).filter(Article.feed_id == feed.id).count()
        feed.status = "active"
        
        db.commit()
        
        logger.info(f"订阅源抓取完成: {feed.name}, 新增 {new_articles} 篇文章")
    
    def cleanup_old_data(self, days: int = 30) -> dict:
        """
        清理旧数据
        
        Args:
            days: 保留天数
            
        Returns:
            清理结果统计
        """
        logger.info(f"开始清理 {days} 天前的数据...")
        
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 清理旧文章
            old_articles = db.query(Article).filter(
                Article.created_at < cutoff_date,
                Article.read_status == True,
                Article.processed_status == True
            ).all()
            
            deleted_count = 0
            for article in old_articles:
                db.delete(article)
                deleted_count += 1
            
            db.commit()
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_articles": deleted_count,
                "retention_days": days
            }
            
            logger.info(f"数据清理完成: {result}")
            return result
            
        finally:
            db.close()
    
    def update_feed_status(self) -> dict:
        """
        更新订阅源状态
        
        Returns:
            状态更新结果
        """
        logger.info("开始更新订阅源状态...")
        
        db = SessionLocal()
        try:
            feeds = db.query(Feed).all()
            updated_count = 0
            
            for feed in feeds:
                # 检查是否需要更新状态
                if feed.status == "error":
                    # 尝试重新验证
                    if self.rss_service.validate_feed_url(feed.url):
                        feed.status = "active"
                        updated_count += 1
                
                # 更新文章计数
                current_count = db.query(Article).filter(Article.feed_id == feed.id).count()
                if current_count != feed.article_count:
                    feed.article_count = current_count
                    updated_count += 1
            
            db.commit()
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "total_feeds": len(feeds),
                "updated": updated_count
            }
            
            logger.info(f"订阅源状态更新完成: {result}")
            return result
            
        finally:
            db.close()
    
    def process_unprocessed_articles(self, limit: int = 100) -> dict:
        """
        处理未处理的文章
        
        Args:
            limit: 处理数量限制
            
        Returns:
            处理结果统计
        """
        logger.info(f"开始处理未处理的文章 (限制: {limit})...")
        
        db = SessionLocal()
        try:
            # 获取未处理的文章
            unprocessed = db.query(Article).filter(
                Article.processed_status == False
            ).limit(limit).all()
            
            if not unprocessed:
                logger.info("没有未处理的文章")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "processed": 0,
                    "total": 0
                }
            
            # 准备分析数据
            articles_data = []
            for article in unprocessed:
                articles_data.append({
                    "id": article.id,
                    "title": article.title,
                    "content": article.content or "",
                })
            
            # 批量分析
            analysis_results = self.ai_service.batch_analyze(articles_data)
            
            # 更新文章
            processed_count = 0
            for result in analysis_results:
                article = db.query(Article).filter(Article.id == result["id"]).first()
                if article:
                    article.summary = result.get("summary", article.summary)
                    article.keywords = ", ".join(result.get("keywords", []))
                    article.sentiment = result.get("sentiment", "neutral")
                    article.processed_status = True
                    processed_count += 1
            
            db.commit()
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "total": len(unprocessed),
                "processed": processed_count,
                "failed": len(unprocessed) - processed_count
            }
            
            logger.info(f"文章处理完成: {result}")
            return result
            
        finally:
            db.close()
    
    def run_all_tasks(self) -> dict:
        """
        运行所有任务
        
        Returns:
            所有任务的结果
        """
        logger.info("开始运行所有定时任务...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {}
        }
        
        try:
            # 1. 抓取订阅源
            results["tasks"]["fetch_feeds"] = self.fetch_all_feeds()
            
            # 2. 处理文章
            results["tasks"]["process_articles"] = self.process_unprocessed_articles()
            
            # 3. 更新状态
            results["tasks"]["update_status"] = self.update_feed_status()
            
            # 4. 清理数据（每天运行一次）
            if datetime.now().hour == 2:  # 凌晨2点运行
                results["tasks"]["cleanup"] = self.cleanup_old_data()
            
            logger.info("所有定时任务运行完成")
            return results
            
        except Exception as e:
            logger.error(f"运行定时任务失败: {e}")
            results["error"] = str(e)
            return results