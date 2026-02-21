"""
AI 分析服务
"""

import logging
import json
from typing import Dict, Optional, List
import re

logger = logging.getLogger(__name__)


class AIService:
    """AI 分析服务类"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        logger.info(f"AI 服务初始化: {'已启用' if enabled else '已禁用'}")

    def analyze_article(self, content: str, title: str = "") -> Dict:
        """
        分析文章内容

        Args:
            content: 文章内容
            title: 文章标题

        Returns:
            分析结果
        """
        if not self.enabled:
            logger.warning("AI 服务已禁用，返回默认分析结果")
            return self._get_default_analysis(content, title)

        try:
            # 这里应该调用实际的 AI 服务
            # 暂时使用基于规则的分析

            summary = self._generate_summary(content)
            keywords = self._extract_keywords(content)
            sentiment = self._analyze_sentiment(content)

            analysis = {
                "summary": summary,
                "keywords": keywords
                if isinstance(keywords, str)
                else ", ".join(keywords),
                "sentiment": sentiment,
                "key_points": self._extract_key_points(content),
                "business_insights": self._extract_business_insights(content),
                "technical_points": self._extract_technical_points(content),
                "action_items": self._extract_action_items(content),
                "length": len(content),
                "read_time_minutes": self._calculate_read_time(content),
                "has_code": self._check_has_code(content),
                "has_links": self._check_has_links(content),
                "topic": self._identify_topic(content, title),
            }

            logger.info(f"文章分析完成: {title}, 长度: {len(content)} 字符")
            return analysis

        except Exception as e:
            logger.error(f"文章分析失败: {e}")
            return self._get_default_analysis(content, title)

    def _generate_summary(self, content: str, max_length: int = 300) -> str:
        """生成文章摘要"""
        if not content:
            return "无内容"

        # 简单摘要生成：取前 N 个字符
        summary = content[:max_length].strip()

        # 如果被截断，添加省略号
        if len(content) > max_length:
            summary = summary.rsplit(" ", 1)[0] + "..."

        return summary

    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        if not content:
            return []

        # 简单的关键词提取：按频率排序的单词
        words = re.findall(r"\b\w{3,}\b", content.lower())

        # 过滤常见停用词
        stop_words = {
            "the",
            "and",
            "for",
            "that",
            "with",
            "this",
            "from",
            "have",
            "what",
            "when",
        }
        filtered_words = [word for word in words if word not in stop_words]

        # 统计词频
        from collections import Counter

        word_counts = Counter(filtered_words)

        # 返回最常见的词
        keywords = [word for word, _ in word_counts.most_common(max_keywords)]
        return keywords

    def _extract_key_points(self, content: str) -> str:
        """提取关键要点"""
        if not content:
            return ""

        sentences = content.split(".")
        key_points = []

        important_indicators = [
            "important",
            "key",
            "main",
            "critical",
            "essential",
            "关键",
            "重要",
            "核心",
            "主要",
            "必须",
        ]

        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                if any(
                    indicator in sentence.lower() for indicator in important_indicators
                ):
                    key_points.append(sentence)

        if not key_points and sentences:
            key_points = [s.strip() for s in sentences[:3] if 20 < len(s.strip()) < 200]

        return "; ".join(key_points[:3])

    def _extract_business_insights(self, content: str) -> str:
        """提取商业洞察"""
        if not content:
            return ""

        business_keywords = [
            "business",
            "market",
            "revenue",
            "profit",
            "growth",
            "customer",
            "商业",
            "市场",
            "收入",
            "增长",
            "客户",
            "投资",
            "融资",
        ]

        content_lower = content.lower()
        insights = []

        if any(kw in content_lower for kw in business_keywords):
            sentences = content.split(".")
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in business_keywords):
                    sentence = sentence.strip()
                    if 20 < len(sentence) < 150:
                        insights.append(sentence)

        return "; ".join(insights[:2]) if insights else "暂无商业洞察"

    def _extract_technical_points(self, content: str) -> str:
        """提取技术要点"""
        if not content:
            return ""

        tech_keywords = [
            "python",
            "javascript",
            "api",
            "database",
            "code",
            "software",
            "algorithm",
            "function",
            "class",
            "编程",
            "代码",
            "算法",
            "技术",
        ]

        content_lower = content.lower()
        tech_points = []

        if any(kw in content_lower for kw in tech_keywords):
            sentences = content.split(".")
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in tech_keywords):
                    sentence = sentence.strip()
                    if 20 < len(sentence) < 150:
                        tech_points.append(sentence)

        return "; ".join(tech_points[:2]) if tech_points else "暂无技术要点"

    def _extract_action_items(self, content: str) -> str:
        """提取行动项"""
        if not content:
            return ""

        action_keywords = [
            "should",
            "must",
            "need to",
            "recommend",
            "action",
            "todo",
            "需要",
            "建议",
            "应该",
            "必须",
            "行动",
        ]

        content_lower = content.lower()
        actions = []

        sentences = content.split(".")
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in action_keywords):
                sentence = sentence.strip()
                if 10 < len(sentence) < 100:
                    actions.append(sentence)

        return "; ".join(actions[:2]) if actions else "暂无行动项"

    def _analyze_sentiment(self, content: str) -> str:
        """分析情感倾向"""
        if not content:
            return "neutral"

        # 简单的情感分析：基于关键词
        positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "best",
            "love",
            "happy",
        }
        negative_words = {
            "bad",
            "terrible",
            "awful",
            "worst",
            "hate",
            "sad",
            "angry",
            "problem",
        }

        content_lower = content.lower()

        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _calculate_read_time(self, content: str, words_per_minute: int = 200) -> int:
        """计算阅读时间（分钟）"""
        if not content:
            return 0

        word_count = len(content.split())
        read_time = max(1, word_count // words_per_minute)
        return read_time

    def _check_has_code(self, content: str) -> bool:
        """检查是否包含代码"""
        code_patterns = [
            "def ",
            "class ",
            "import ",
            "function ",
            "var ",
            "const ",
            "console.",
            "print(",
        ]
        return any(pattern in content for pattern in code_patterns)

    def _check_has_links(self, content: str) -> bool:
        """检查是否包含链接"""
        url_pattern = r"https?://\S+"
        return bool(re.search(url_pattern, content))

    def _identify_topic(self, content: str, title: str = "") -> str:
        """识别主题"""
        topics = {
            "technology": [
                "python",
                "javascript",
                "java",
                "programming",
                "code",
                "software",
                "tech",
            ],
            "business": [
                "business",
                "startup",
                "company",
                "market",
                "money",
                "finance",
                "investment",
            ],
            "news": ["news", "update", "announcement", "report", "latest"],
            "tutorial": ["tutorial", "guide", "how to", "step by step", "learn"],
            "review": ["review", "comparison", "vs", "versus", "better", "best"],
        }

        text = (title + " " + content).lower()

        for topic, keywords in topics.items():
            if any(keyword in text for keyword in keywords):
                return topic

        return "general"

    def _get_default_analysis(self, content: str, title: str = "") -> Dict:
        """获取默认分析结果"""
        keywords = self._extract_keywords(content)
        return {
            "summary": self._generate_summary(content),
            "keywords": keywords if isinstance(keywords, str) else ", ".join(keywords),
            "sentiment": "neutral",
            "key_points": self._extract_key_points(content),
            "business_insights": self._extract_business_insights(content),
            "technical_points": self._extract_technical_points(content),
            "action_items": self._extract_action_items(content),
            "length": len(content),
            "read_time_minutes": self._calculate_read_time(content),
            "has_code": False,
            "has_links": False,
            "topic": "general",
        }

    def batch_analyze(self, articles: List[Dict]) -> List[Dict]:
        """
        批量分析文章

        Args:
            articles: 文章列表，每个元素包含 'content' 和 'title'

        Returns:
            分析结果列表
        """
        results = []

        for i, article in enumerate(articles):
            try:
                analysis = self.analyze_article(
                    article.get("content", ""), article.get("title", "")
                )
                results.append({**article, **analysis})

                # 进度日志
                if (i + 1) % 10 == 0:
                    logger.info(f"批量分析进度: {i + 1}/{len(articles)}")

            except Exception as e:
                logger.error(f"批量分析失败 (文章 {i}): {e}")
                results.append(
                    {
                        **article,
                        **self._get_default_analysis(
                            article.get("content", ""), article.get("title", "")
                        ),
                    }
                )

        logger.info(f"批量分析完成: {len(results)}/{len(articles)} 篇文章")
        return results
