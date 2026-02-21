"""
播客分析服务
生成播客内容的摘要、章节和要点
"""

import logging
import re
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PodcastAnalysisService:
    """播客分析服务类"""

    def __init__(self):
        logger.info("播客分析服务初始化完成")

    def analyze_podcast(
        self,
        title: str,
        description: str = "",
        transcript: str = None,
        audio_url: str = None,
        audio_duration: int = None,
    ) -> Dict:
        """
        分析播客内容并生成摘要

        Args:
            title: 播客标题
            description: 播客描述/笔记
            transcript: 转录文本（如果有）
            audio_url: 音频URL
            audio_duration: 音频时长（秒）

        Returns:
            播客分析结果
        """
        logger.info(f"开始分析播客: {title}")

        # 使用转录文本或描述进行分析
        content_to_analyze = transcript or description

        if not content_to_analyze:
            logger.warning(f"播客无内容可分析: {title}")
            return self._get_default_analysis(title, audio_url, audio_duration)

        try:
            # 生成播客摘要
            podcast_summary = self._generate_podcast_summary(title, content_to_analyze)

            # 提取关键主题
            key_topics = self._extract_key_topics(content_to_analyze)

            # 提取章节信息
            chapters = self._extract_chapters(content_to_analyze, audio_duration)

            # 提取行动项
            action_items = self._extract_action_items(content_to_analyze)

            result = {
                "podcast_summary": podcast_summary,
                "key_topics": key_topics,
                "chapters": chapters,
                "action_items": action_items,
                "audio_url": audio_url,
                "audio_duration": audio_duration,
                "duration_formatted": self._format_duration(audio_duration)
                if audio_duration
                else None,
            }

            logger.info(f"播客分析完成: {title}")
            return result

        except Exception as e:
            logger.error(f"播客分析失败: {e}")
            return self._get_default_analysis(title, audio_url, audio_duration)

    def _generate_podcast_summary(
        self, title: str, content: str, max_length: int = 500
    ) -> str:
        """生成播客摘要"""
        if not content:
            return "暂无摘要"

        # 清理 HTML 标签
        content = re.sub(r"<[^>]+>", "", content)
        content = content.strip()

        # 如果内容太长，进行 summarization
        if len(content) > max_length:
            # 简单策略：取前几段
            paragraphs = content.split("\n\n")
            summary = ""
            for para in paragraphs:
                if len(summary) + len(para) > max_length:
                    break
                if para.strip():
                    summary += para.strip() + " "

            if len(summary) > max_length:
                summary = summary[:max_length].rsplit(" ", 1)[0] + "..."
            return summary.strip()

        return content[:max_length]

    def _extract_key_topics(self, content: str, max_topics: int = 8) -> List[str]:
        """提取关键主题"""
        if not content:
            return []

        # 清理内容
        content = re.sub(r"<[^>]+>", "", content)
        content_lower = content.lower()

        # 定义常见的主题关键词
        topic_keywords = {
            "技术": [
                "python",
                "javascript",
                "java",
                "code",
                "programming",
                "api",
                "software",
                "ai",
                "machine learning",
                "data",
                "web",
                "cloud",
                "devops",
                "编程",
                "算法",
                "代码",
            ],
            "商业": [
                "business",
                "startup",
                "company",
                "market",
                "revenue",
                "investment",
                "funding",
                "growth",
                "product",
                "商业",
                "创业",
                "融资",
                "市场",
            ],
            "产品": [
                "product",
                "feature",
                "update",
                "release",
                "version",
                "design",
                "ui",
                "ux",
                "产品",
                "功能",
                "设计",
            ],
            "行业": [
                "industry",
                "trend",
                "news",
                "report",
                "analysis",
                "行业",
                "趋势",
                "新闻",
                "分析",
            ],
            "职业": [
                "career",
                "job",
                "skill",
                "experience",
                "interview",
                "职业",
                "技能",
                "经验",
                "面试",
            ],
            "管理": [
                "team",
                "leadership",
                "management",
                "strategy",
                "团队",
                "领导力",
                "管理",
                "战略",
            ],
        }

        # 统计主题出现次数
        topic_counts = {}
        for topic, keywords in topic_keywords.items():
            count = sum(1 for kw in keywords if kw in content_lower)
            if count > 0:
                topic_counts[topic] = count

        # 按出现次数排序
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)

        return [topic for topic, _ in sorted_topics[:max_topics]]

    def _extract_chapters(self, content: str, audio_duration: int = None) -> List[Dict]:
        """提取章节信息"""
        chapters = []

        if not content:
            return chapters

        # 清理内容
        content = re.sub(r"<[^>]+>", "", content)

        # 常见章节标记模式
        chapter_patterns = [
            r"(?:chapter|章节|part|section)\s*(\d+)[:\.]?\s*(.+)",
            r"^(\d+)[:\.]\s*(.+)$",
            r"(?:首先|第一|其次|第二|最后|接下来)(?:我们|来|说|讲)(.+)",
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines[:20]):  # 最多检查前20行
            line = line.strip()
            if len(line) > 5 and len(line) < 150:
                # 简单判断是否为章节标题
                if any(
                    keyword in line.lower()
                    for keyword in [
                        "chapter",
                        "章节",
                        "part",
                        "section",
                        "首先",
                        "第一",
                        "其次",
                        "第二",
                        "最后",
                    ]
                ):
                    # 估算时间点
                    timestamp = None
                    if audio_duration:
                        # 假设章节均匀分布
                        timestamp = (i / len(lines)) * audio_duration

                    chapters.append(
                        {
                            "title": line,
                            "timestamp": timestamp,
                            "timestamp_formatted": self._format_duration(int(timestamp))
                            if timestamp
                            else None,
                        }
                    )

        # 如果没有找到章节，创建一个默认章节
        if not chapters and content:
            chapters.append(
                {"title": "完整内容", "timestamp": 0, "timestamp_formatted": "00:00"}
            )

        return chapters[:10]  # 最多10个章节

    def _extract_action_items(self, content: str) -> str:
        """提取行动项"""
        if not content:
            return "暂无行动项"

        content_lower = content.lower()

        action_keywords = [
            "should",
            "must",
            "need to",
            "recommend",
            "try to",
            "remember to",
            "需要",
            "应该",
            "建议",
            "必须",
            "记住",
            "尝试",
        ]

        sentences = content.split(".")
        action_items = []

        for sentence in sentences:
            sentence = sentence.strip()
            if (
                any(kw in sentence.lower() for kw in action_keywords)
                and 10 < len(sentence) < 150
            ):
                action_items.append(sentence)

        if action_items:
            return "; ".join(action_items[:5])

        return "暂无行动项"

    def _format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if not seconds:
            return "00:00"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def _get_default_analysis(
        self, title: str, audio_url: str = None, audio_duration: int = None
    ) -> Dict:
        """获取默认分析结果"""
        return {
            "podcast_summary": "暂无摘要",
            "key_topics": [],
            "chapters": [],
            "action_items": "暂无行动项",
            "audio_url": audio_url,
            "audio_duration": audio_duration,
            "duration_formatted": self._format_duration(audio_duration)
            if audio_duration
            else None,
        }

    def generate_podcast_document(
        self,
        title: str,
        description: str,
        podcast_summary: str,
        key_topics: List[str],
        chapters: List[Dict],
        action_items: str,
        audio_duration: int = None,
    ) -> str:
        """
        生成播客文档（Markdown 格式）

        Args:
            title: 播客标题
            description: 播客描述
            podcast_summary: 播客摘要
            key_topics: 关键主题
            chapters: 章节信息
            action_items: 行动项
            audio_duration: 音频时长

        Returns:
            Markdown 格式的文档
        """
        doc = f"""# {title}

## 播客摘要
{podcast_summary}

## 关键主题
"""

        for topic in key_topics:
            doc += f"- {topic}\n"

        if chapters:
            doc += """
## 章节内容
"""
            for chapter in chapters:
                time_str = chapter.get("timestamp_formatted", "")
                if time_str:
                    doc += f"- [{time_str}] {chapter['title']}\n"
                else:
                    doc += f"- {chapter['title']}\n"

        if action_items and action_items != "暂无行动项":
            doc += f"""
## 行动项
{action_items}
"""

        if audio_duration:
            doc += f"""
## 播客信息
- 时长: {self._format_duration(audio_duration)}
"""

        return doc


# 全局实例
podcast_analysis_service = PodcastAnalysisService()
