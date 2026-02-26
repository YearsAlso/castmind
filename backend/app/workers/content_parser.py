"""
Content Parser Worker - 内容解析 Worker

负责解析和提取文章详细内容，清理 HTML，提取关键信息。
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.core.database import SessionLocal
from app.models.database import Article
from app.services.rss_service import RSSService

logger = logging.getLogger(__name__)


class ContentParser:
    """内容解析 Worker"""

    def __init__(self):
        self.rss_service = RSSService()
        self.name = "content_parser"
        logger.info(f"{self.name} Worker 初始化完成")

    def parse_article(self, article_id: int) -> Dict[str, Any]:
        """
        解析单个文章内容

        Args:
            article_id: 文章 ID

        Returns:
            解析结果
        """
        logger.info(f"[{self.name}] 开始解析文章 ID: {article_id}")

        db = SessionLocal()
        try:
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                return {
                    "success": False,
                    "error": f"文章不存在: {article_id}",
                    "article_id": article_id,
                }

            # 如果已有完整内容，跳过解析
            if article.content and len(article.content) > 500:
                return {
                    "success": True,
                    "skipped": True,
                    "article_id": article_id,
                    "message": "内容已完整",
                }

            # 从原始 URL 获取内容
            if article.url:
                parsed_content = self._extract_content(article.url)
                if parsed_content:
                    article.content = parsed_content.get("content", article.content)
                    article.summary = parsed_content.get(
                        "summary", article.summary
                    ) or article.summary

            # 更新状态
            article.status = "parsed"
            article.updated_at = datetime.now()
            db.commit()

            result = {
                "success": True,
                "article_id": article_id,
                "title": article.title,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"[{self.name}] 解析完成: {result}")
            return result

        except Exception as e:
            logger.error(f"[{self.name}] 解析失败 (ID: {article_id}): {e}")
            return {
                "success": False,
                "error": str(e),
                "article_id": article_id,
            }
        finally:
            db.close()

    def _extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """
        从 URL 提取内容

        Args:
            url: 文章 URL

        Returns:
            提取的内容
        """
        try:
            # 使用 RSS 服务提取内容
            return self.rss_service.fetch_article_content(url)
        except Exception as e:
            logger.warning(f"内容提取失败 ({url}): {e}")
            return None

    def parse_pending(self, limit: int = 50) -> Dict[str, Any]:
        """
        解析所有待处理文章

        Args:
            limit: 每次处理数量

        Returns:
            处理结果统计
        """
        logger.info(f"[{self.name}] 开始解析待处理文章 (限制: {limit})")

        db = SessionLocal()
        try:
            articles = (
                db.query(Article)
                .filter(Article.status == "pending")
                .limit(limit)
                .all()
            )

            total = len(articles)
            success = 0
            error = 0

            for article in articles:
                result = self.parse_article(article.id)
                if result.get("success"):
                    success += 1
                else:
                    error += 1

            summary = {
                "success": True,
                "total": total,
                "success_count": success,
                "error_count": error,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"[{self.name}] 批量解析完成: {summary}")
            return summary

        finally:
            db.close()

    def batch_parse(
        self, article_ids: List[int]
    ) -> Dict[str, Any]:
        """
        批量解析指定文章

        Args:
            article_ids: 文章 ID 列表

        Returns:
            处理结果
        """
        logger.info(f"[{self.name}] 批量解析文章: {len(article_ids)} 篇")

        success = 0
        error = 0
        results = []

        for article_id in article_ids:
            result = self.parse_article(article_id)
            if result.get("success"):
                success += 1
            else:
                error += 1
            results.append(result)

        summary = {
            "success": True,
            "total": len(article_ids),
            "success_count": success,
            "error_count": error,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"[{self.name}] 批量解析完成: {summary}")
        return summary

    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务（Zoo Framework 入口）

        Args:
            task_data: 任务数据

        Returns:
            处理结果
        """
        task_type = task_data.get("type")

        if task_type == "parse_single":
            article_id = task_data.get("article_id")
            return self.parse_article(article_id)
        elif task_type == "parse_pending":
            limit = task_data.get("limit", 50)
            return self.parse_pending(limit)
        elif task_type == "batch_parse":
            article_ids = task_data.get("article_ids", [])
            return self.batch_parse(article_ids)
        else:
            return {
                "success": False,
                "error": f"未知任务类型: {task_type}",
            }
