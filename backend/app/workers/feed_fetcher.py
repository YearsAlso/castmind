"""
Feed Fetcher Worker - 订阅源抓取 Worker

负责从外部订阅源获取最新内容，支持 RSS/Atom 格式。
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.database import SessionLocal
from app.models.database import Feed, Article
from app.services.rss_service import RSSService

logger = logging.getLogger(__name__)


class FeedFetcher:
    """订阅源抓取 Worker"""

    def __init__(self):
        self.rss_service = RSSService()
        self.name = "feed_fetcher"
        logger.info(f"{self.name} Worker 初始化完成")

    def fetch_feed(self, feed_id: int) -> Dict[str, Any]:
        """
        抓取单个订阅源

        Args:
            feed_id: 订阅源 ID

        Returns:
            抓取结果
        """
        logger.info(f"[{self.name}] 开始抓取订阅源 ID: {feed_id}")

        db = SessionLocal()
        try:
            feed = db.query(Feed).filter(Feed.id == feed_id).first()
            if not feed:
                return {
                    "success": False,
                    "error": f"订阅源不存在: {feed_id}",
                    "feed_id": feed_id,
                }

            # 解析订阅源
            feed_info = self.rss_service.parse_feed(feed.url)
            if not feed_info:
                feed.status = "error"
                db.commit()
                return {
                    "success": False,
                    "error": "RSS 解析失败",
                    "feed_id": feed_id,
                }

            # 提取文章
            articles = self.rss_service.extract_articles(feed_info)

            # 保存新文章
            new_count = 0
            for article_data in articles:
                existing = (
                    db.query(Article)
                    .filter(Article.url == article_data["url"])
                    .first()
                )
                if existing:
                    continue

                article = Article(
                    feed_id=feed.id,
                    title=article_data["title"],
                    url=article_data["url"],
                    content=article_data["content"],
                    summary=article_data["summary"],
                    published_at=article_data["published_at"],
                    is_podcast=article_data.get("is_podcast", False),
                    status="pending",  # 待解析
                )
                db.add(article)
                new_count += 1

            db.commit()

            result = {
                "success": True,
                "feed_id": feed_id,
                "feed_name": feed.name,
                "total_articles": len(articles),
                "new_articles": new_count,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"[{self.name}] 抓取完成: {result}")
            return result

        except Exception as e:
            logger.error(f"[{self.name}] 抓取失败 (ID: {feed_id}): {e}")
            return {
                "success": False,
                "error": str(e),
                "feed_id": feed_id,
            }
        finally:
            db.close()

    def fetch_all_active(self) -> Dict[str, Any]:
        """
        抓取所有活跃订阅源

        Returns:
            抓取结果统计
        """
        logger.info(f"[{self.name}] 开始抓取所有活跃订阅源")

        db = SessionLocal()
        try:
            feeds = db.query(Feed).filter(Feed.status == "active").all()
            total = len(feeds)
            success = 0
            error = 0
            total_new = 0

            for feed in feeds:
                result = self.fetch_feed(feed.id)
                if result.get("success"):
                    success += 1
                    total_new += result.get("new_articles", 0)
                else:
                    error += 1

            summary = {
                "success": True,
                "total_feeds": total,
                "success_count": success,
                "error_count": error,
                "total_new_articles": total_new,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"[{self.name}] 批量抓取完成: {summary}")
            return summary

        finally:
            db.close()

    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务（Zoo Framework 入口）

        Args:
            task_data: 任务数据

        Returns:
            处理结果
        """
        task_type = task_data.get("type")

        if task_type == "fetch_single":
            feed_id = task_data.get("feed_id")
            return self.fetch_feed(feed_id)
        elif task_type == "fetch_all":
            return self.fetch_all_active()
        else:
            return {
                "success": False,
                "error": f"未知任务类型: {task_type}",
            }
