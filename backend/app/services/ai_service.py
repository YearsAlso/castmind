"""
AI 分析服务
支持基于规则的简单分析和 OpenAI/DeepSeek LLM 深度分析
"""

import logging
import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIService:
    """AI 分析服务类"""

    def __init__(self):
        # API 配置
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEFAULT_AI_MODEL", "deepseek-chat")

        # 选择使用的 API
        self.ai_provider = (
            "deepseek"
            if self.deepseek_api_key
            else ("openai" if self.openai_api_key else "rule")
        )

        logger.info(
            f"AI 服务初始化完成，提供商: {self.ai_provider}, 模型: {self.model}"
        )

    def analyze_article(self, content: str, title: str = "") -> Dict:
        """
        分析文章内容（现有方法，保持兼容性）
        """
        if not content:
            return self._get_default_analysis(title)

        try:
            analysis = {
                "summary": self._generate_summary(content),
                "keywords": self._extract_keywords(content),
                "sentiment": self._analyze_sentiment(content),
                "key_points": self._extract_key_points(content),
                "business_insights": self._extract_business_insights(content),
                "technical_points": self._extract_technical_points(content),
                "action_items": self._extract_action_items(content),
            }

            return analysis

        except Exception as e:
            logger.error(f"文章分析失败: {e}")
            return self._get_default_analysis(title)

    def analyze_podcast_transcript(
        self, transcript: str, title: str, audio_duration: int = None
    ) -> Dict:
        """
        分析播客转录内容（深度分析）

        Args:
            transcript: 转录文本
            title: 播客标题
            audio_duration: 音频时长（秒）

        Returns:
            深度分析结果
        """
        if not transcript:
            return {"success": False, "error": "转录文本为空"}

        # 如果配置了 LLM，使用 LLM 分析
        if self.ai_provider != "rule":
            return self._analyze_with_llm(transcript, title, audio_duration)
        else:
            # 使用基于规则的分析
            return self._analyze_with_rules(transcript, title, audio_duration)

    def _analyze_with_llm(
        self, transcript: str, title: str, audio_duration: int = None
    ) -> Dict:
        """使用 LLM 进行深度分析"""
        try:
            from openai import OpenAI

            # 配置 API
            api_key = self.deepseek_api_key or self.openai_api_key
            client = OpenAI(api_key=api_key, base_url=self.base_url)

            # 构建提示词
            duration_str = (
                f"（时长约 {audio_duration // 60} 分钟）" if audio_duration else ""
            )

            system_prompt = """你是一个专业的播客内容分析师。请分析以下播客转录内容，生成结构化的分析报告。

请严格按照以下 JSON 格式输出：
{
    "podcast_summary": "播客核心内容摘要，100-200字",
    "key_topics": ["主题1", "主题2", "主题3", "主题4", "主题5"],
    "chapters": [
        {"timestamp": "00:05", "title": "章节标题1"},
        {"timestamp": "00:15", "title": "章节标题2"}
    ],
    "action_items": ["行动建议1", "action item 2"],
    "guest_info": "嘉宾信息（如有）",
    "key_quotes": ["精彩引言1", "引言2"]
}"""

            user_prompt = f"""播客标题：{title} {duration_str}

转录内容：
{transcript[:8000]}  # 限制输入长度

请分析以上播客内容并输出 JSON 格式的分析结果。"""

            # 调用 API
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            # 解析响应
            content = response.choices[0].message.content

            # 尝试解析 JSON
            try:
                # 提取 JSON 部分
                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(content)

                return {
                    "success": True,
                    "podcast_summary": result.get("podcast_summary", ""),
                    "key_topics": result.get("key_topics", []),
                    "chapters": result.get("chapters", []),
                    "action_items": result.get("action_items", []),
                    "guest_info": result.get("guest_info", ""),
                    "key_quotes": result.get("key_quotes", []),
                    "provider": self.ai_provider,
                    "model": self.model,
                }

            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {e}")
                # 返回原始文本作为摘要
                return {
                    "success": True,
                    "podcast_summary": content[:500],
                    "key_topics": [],
                    "chapters": [],
                    "action_items": [],
                    "provider": self.ai_provider,
                    "raw_response": content,
                }

        except Exception as e:
            logger.error(f"LLM 分析失败: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_with_rules(
        self, transcript: str, title: str, audio_duration: int = None
    ) -> Dict:
        """使用规则进行基础分析"""

        # 生成摘要
        podcast_summary = self._generate_summary(transcript)

        # 提取主题
        key_topics = self._extract_keywords(transcript)

        # 提取章节（基于时间标记或内容分段）
        chapters = self._extract_chapters_from_transcript(transcript, audio_duration)

        # 提取行动项
        action_items_list = self._extract_action_items_list(transcript)

        return {
            "success": True,
            "podcast_summary": podcast_summary,
            "key_topics": key_topics,
            "chapters": chapters,
            "action_items": action_items_list,
            "provider": "rule",
        }

    def _generate_summary(self, content: str, max_length: int = 300) -> str:
        """生成摘要"""
        if not content:
            return "无内容"

        # 清理 HTML
        content = re.sub(r"<[^>]+>", "", content)
        content = content.strip()

        if len(content) <= max_length:
            return content

        # 取前 N 个字符
        summary = content[:max_length]
        # 在句号处截断
        summary = summary.rsplit(".", 1)[0]

        return summary + "..."

    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        if not content:
            return []

        words = re.findall(r"\b\w{3,}\b", content.lower())

        # 停用词
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
            "的",
            "是",
            "在",
            "了",
            "和",
            "与",
            "或",
            "及",
            "等",
            "着",
            "就",
        }

        filtered = [w for w in words if w not in stop_words]

        # 词频统计
        from collections import Counter

        word_counts = Counter(filtered)

        return [w for w, _ in word_counts.most_common(max_keywords)]

    def _analyze_sentiment(self, content: str) -> str:
        """分析情感"""
        if not content:
            return "neutral"

        positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "best",
            "love",
            "happy",
            "好",
            "棒",
            "优秀",
        }
        negative_words = {
            "bad",
            "terrible",
            "awful",
            "worst",
            "hate",
            "sad",
            "problem",
            "差",
            "糟糕",
        }

        content_lower = content.lower()

        positive = sum(1 for w in positive_words if w in content_lower)
        negative = sum(1 for w in negative_words if w in content_lower)

        if positive > negative:
            return "positive"
        elif negative > positive:
            return "negative"
        return "neutral"

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
            "注意",
        ]

        for sentence in sentences[:10]:
            sentence = sentence.strip()
            if 20 < len(sentence) < 200:
                if any(ind in sentence.lower() for ind in important_indicators):
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
            "创业",
            "公司",
        ]

        content_lower = content.lower()

        if not any(kw in content_lower for kw in business_keywords):
            return "暂无商业洞察"

        sentences = content.split(".")
        insights = []

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
            "系统",
        ]

        content_lower = content.lower()

        if not any(kw in content_lower for kw in tech_keywords):
            return "暂无技术要点"

        sentences = content.split(".")
        tech_points = []

        for sentence in sentences:
            if any(kw in sentence.lower() for kw in tech_keywords):
                sentence = sentence.strip()
                if 20 < len(sentence) < 150:
                    tech_points.append(sentence)

        return "; ".join(tech_points[:2]) if tech_points else "暂无技术要点"

    def _extract_action_items(self, content: str) -> str:
        """提取行动项（字符串格式）"""
        items = self._extract_action_items_list(content)
        return "; ".join(items) if items else "暂无行动项"

    def _extract_action_items_list(self, content: str) -> List[str]:
        """提取行动项列表"""
        if not content:
            return []

        action_keywords = [
            "should",
            "must",
            "need to",
            "recommend",
            "todo",
            "需要",
            "建议",
            "应该",
            "必须",
            "行动",
        ]

        sentences = content.split(".")
        actions = []

        for sentence in sentences:
            if any(kw in sentence.lower() for kw in action_keywords):
                sentence = sentence.strip()
                if 10 < len(sentence) < 100:
                    actions.append(sentence)

        return actions[:3]

    def _extract_chapters_from_transcript(
        self, content: str, audio_duration: int = None
    ) -> List[Dict]:
        """从转录中提取章节"""
        chapters = []

        if not content:
            return chapters

        # 按段落分割
        paragraphs = content.split("\n\n")

        if not paragraphs:
            paragraphs = content.split(".")

        total_paragraphs = len(paragraphs)

        for i, para in enumerate(paragraphs[:10]):
            para = para.strip()
            if len(para) > 10 and len(para) < 150:
                # 估算时间戳
                if audio_duration and total_paragraphs > 0:
                    timestamp = int((i / total_paragraphs) * audio_duration)
                    minutes = timestamp // 60
                    seconds = timestamp % 60
                    time_str = f"{minutes:02d}:{seconds:02d}"
                else:
                    time_str = None

                chapters.append(
                    {
                        "title": para[:50] + "..." if len(para) > 50 else para,
                        "timestamp": time_str,
                    }
                )

        return chapters

    def _get_default_analysis(self, title: str = "") -> Dict:
        """获取默认分析结果"""
        return {
            "summary": "暂无分析",
            "keywords": [],
            "sentiment": "neutral",
            "key_points": "",
            "business_insights": "暂无",
            "technical_points": "暂无",
            "action_items": "暂无",
        }

    def check_ai_status(self) -> Dict:
        """检查 AI 服务状态"""
        if self.ai_provider == "rule":
            return {
                "enabled": False,
                "provider": "rule",
                "message": "未配置 AI API，使用规则分析",
            }

        return {
            "enabled": True,
            "provider": self.ai_provider,
            "model": self.model,
            "message": f"使用 {self.ai_provider} ({self.model}) 进行分析",
        }


# 全局实例
ai_service = AIService()
