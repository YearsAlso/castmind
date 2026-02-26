"""
AI Analyzer Worker - AI 分析 Worker

负责使用 AI 分析文章内容，提取摘要、标签、情感等。
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.core.database import SessionLocal
from app.models.database import Article
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI 分析 Worker"""

    def __init__(self):
        self.ai_service = AIService()
        self.name = "ai_analyzer"
        logger.info(f"{self.name} Worker 初始化完成")

    def analyze_article(self, article_id: int) -> Dict[str, Any]:
        """
        分析单个文章

        Args:
            article_id: 文章 ID

        Returns:
            分析结果
        """
        logger.info(f"[{self.name}] 开始分析文章 ID: {article_id}")

        db = SessionLocal()
        try:
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                return {
                    "success": False,
                    "error": f"文章不存在: {article_id}",
                    "article_id": article_id,
                }

            # 检查内容是否足够分析
            if not article.content or len(article.content) < 50:
                return {
                    "success": False,
                    "error": "内容不足，无法分析",
                    "article_id": article_id,
                }

            # 使用 AI 分析
            try:
                analysis_result = self.ai_service.analyze_article(
                    title=article.title,
                    content=article.content,
                    url=article.url,
                )

                if analysis_result:
                    # 更新文章分析结果
                    article.summary = analysis_result.get("summary", article.summary)
                    article.tags = analysis_result.get("tags", article.tags)
                    article.sentiment = analysis_result.get("sentiment")
                    article.category = analysis_result.get("category", article.category)
                    article.status = "analyzed"
                    article.updated_at = datetime.now()

                    # 如果有摘要，更新摘要
                    if analysis_result.get("summary"):
                        article.summary = analysis_result["summary"]

                    db.commit()

                    result = {
                        "success": True,
                        "article_id": article_id,
                        "title": article.title,
                        "analysis": analysis_result,
                        "timestamp": datetime.now().isoformat(),
                    }

                    logger.info(f"[{self.name}] 分析完成: {article_id}")
                    return result
                else:
                    article.status = "analyze_failed"
                    db.commit()
                    return {
                        "success": False,
                        "error": "AI 分析返回为空",
                        "article_id": article_id,
                    }

            except Exception as e:
                logger.error(f"[{self.name}] AI 分析失败 (ID: {article_id}): {e}")
                article.status = "analyze_failed"
                db.commit()
                return {
                    "success": False,
                    "error": str(e),
                    "article_id": article_id,
                }

        finally:
            db.close()

    def analyze_batch(self, article_ids: List[int]) -> Dict[str, Any]:
        """
        批量分析文章

        Args:
            article_ids: 文章 ID 列表

        Returns:
            分析结果统计
        """
        logger.info(f"[{self.name}] 批量分析文章: {len(article_ids)} 篇")

        success = 0
        error = 0
        results = []

        for article_id in article_ids:
            result = self.analyze_article(article_id)
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

        logger.info(f"[{self.name}] 批量分析完成: {summary}")
        return summary

    def analyze_pending(self, limit: int = 20) -> Dict[str, Any]:
        """
        分析所有待分析文章

        Args:
            limit: 每次处理数量

        Returns:
            处理结果统计
        """
        logger.info(f"[{self.name}] 开始分析待处理文章 (限制: {limit})")

        db = SessionLocal()
        try:
            articles = (
                db.query(Article)
                .filter(Article.status == "parsed")
                .filter(Article.content.isnot(None))
                .filter(Article.content != "")
                .limit(limit)
                .all()
            )

            article_ids = [a.id for a in articles]
            logger.info(f"[{self.name}] 找到 {len(article_ids)} 篇待分析文章")

            if not article_ids:
                return {
                    "success": True,
                    "total": 0,
                    "message": "没有待分析的文章",
                    "timestamp": datetime.now().isoformat(),
                }

            return self.analyze_batch(article_ids)

        finally:
            db.close()

    def re_analyze(
        self, article_ids: List[int], force: bool = False
    ) -> Dict[str, Any]:
        """
        重新分析文章

        Args:
            article_ids: 文章 ID 列表
            force: 是否强制重新分析

        Returns:
            分析结果
        """
        logger.info(
            f"[{self.name}] 重新分析文章: {len(article_ids)}, force={force}"
        )

        if not force:
            # 只分析已分析的文章
            db = SessionLocal()
            try:
                articles = (
                    db.query(Article)
                    .filter(Article.id.in_(article_ids))
                    .filter(Article.status == "analyzed")
                    .all()
                )
                article_ids = [a.id for a in articles]
            finally:
                db.close()

        return self.analyze_batch(article_ids)

    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务（Zoo Framework 入口）

        Args:
            task_data: 任务数据

        Returns:
            处理结果
        """
        task_type = task_data.get("type")

        if task_type == "analyze_single":
            article_id = task_data.get("article_id")
            return self.analyze_article(article_id)
        elif task_type == "analyze_batch":
            article_ids = task_data.get("article_ids", [])
            return self.analyze_batch(article_ids)
        elif task_type == "analyze_pending":
            limit = task_data.get("limit", 20)
            return self.analyze_pending(limit)
        elif task_type == "re_analyze":
            article_ids = task_data.get("article_ids", [])
            force = task_data.get("force", False)
            return self.re_analyze(article_ids, force)
        else:
            return {
                "success": False,
                "error": f"未知任务类型: {task_type}",
            }
