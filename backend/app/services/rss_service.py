"""
RSS 解析服务（支持 RSSHub）
"""

import logging
from typing import List, Dict, Optional, Tuple
import feedparser
from datetime import datetime

from .rsshub_service import RSSHubService

logger = logging.getLogger(__name__)


class RSSService:
    """RSS 解析服务类（支持 RSSHub）"""

    @staticmethod
    def parse_feed(url: str) -> Optional[Dict]:
        """
        解析 RSS/Atom 订阅源（支持 RSSHub）

        Args:
            url: RSS/Atom 订阅源 URL 或 RSSHub 路由

        Returns:
            解析后的订阅源信息，或 None 如果解析失败
        """
        try:
            # 检查是否为 RSSHub URL
            if RSSHubService.is_rsshub_url(url):
                logger.info(f"检测到 RSSHub URL，使用 RSSHub 解析器: {url}")
                return RSSHubService.parse_rsshub_feed(url)

            logger.info(f"开始解析标准 RSS 订阅源: {url}")

            # 解析标准 RSS 订阅源
            feed = feedparser.parse(url)

            if feed.bozo:
                logger.warning(f"RSS 解析警告: {feed.bozo_exception}")

            # 提取订阅源信息
            feed_info = {
                "source_type": "standard",
                "title": feed.feed.get("title", "未知标题"),
                "description": feed.feed.get("description", ""),
                "link": feed.feed.get("link", url),
                "language": feed.feed.get("language", ""),
                "updated": feed.feed.get("updated", ""),
                "entries": [],
            }

            # 提取文章条目
            for entry in feed.entries[:50]:  # 限制最多50条
                article = {
                    "title": entry.get("title", "无标题"),
                    "link": entry.get("link", ""),
                    "description": entry.get("description", ""),
                    "content": entry.get("content", [{}])[0].get("value", "")
                    if entry.get("content")
                    else "",
                    "published": entry.get("published", entry.get("updated", "")),
                    "author": entry.get("author", ""),
                    "categories": entry.get("tags", []),
                }
                feed_info["entries"].append(article)

            logger.info(
                f"成功解析 RSS 订阅源: {feed_info['title']}, 找到 {len(feed_info['entries'])} 篇文章"
            )
            return feed_info

        except Exception as e:
            logger.error(f"RSS 解析失败: {url}, 错误: {e}")
            return None

    @staticmethod
    def extract_articles(feed_info: Dict) -> List[Dict]:
        """
        从解析的订阅源中提取文章信息

        Args:
            feed_info: 解析后的订阅源信息

        Returns:
            文章信息列表
        """
        articles = []

        for entry in feed_info.get("entries", []):
            try:
                # 解析发布时间
                published_str = entry.get("published", "")
                published_at = None

                if published_str:
                    try:
                        # 尝试解析各种时间格式
                        published_at = datetime.fromisoformat(
                            published_str.replace("Z", "+00:00")
                        )
                    except ValueError:
                        try:
                            # 尝试其他格式
                            import dateutil.parser

                            published_at = dateutil.parser.parse(published_str)
                        except:
                            published_at = datetime.now()
                else:
                    published_at = datetime.now()

                # 提取播客音频信息
                audio_info = RSSService._extract_audio_info(entry)

                article = {
                    "title": entry.get("title", "无标题"),
                    "url": entry.get("link", ""),
                    "content": entry.get("content") or entry.get("description", ""),
                    "summary": entry.get("description", "")[:500],  # 摘要限制长度
                    "published_at": published_at,
                    "author": entry.get("author", ""),
                    "categories": ", ".join(
                        [tag.get("term", "") for tag in entry.get("categories", [])]
                    ),
                    # 播客相关字段
                    "is_podcast": audio_info["is_podcast"],
                    "audio_url": audio_info["url"],
                    "audio_type": audio_info["type"],
                    "audio_duration": audio_info["duration"],
                    "audio_size": audio_info["size"],
                    "podcast_description": entry.get("description", ""),
                }
                articles.append(article)

            except Exception as e:
                logger.error(f"提取文章信息失败: {e}")
                continue

        return articles

    @staticmethod
    def _extract_audio_info(entry: Dict) -> Dict:
        """
        从 RSS 条目中提取音频信息

        Args:
            entry: RSS 条目

        Returns:
            音频信息字典
        """
        audio_info = {
            "is_podcast": False,
            "url": None,
            "type": None,
            "duration": None,
            "size": None,
        }

        # 检查 enclosure 标签（标准的播客音频方式）
        if "enclosures" in entry and entry["enclosures"]:
            for enclosure in entry["enclosures"]:
                if enclosure.get("type", "").startswith("audio/"):
                    audio_info["is_podcast"] = True
                    audio_info["url"] = enclosure.get("url")
                    audio_info["type"] = enclosure.get("type", "").replace("audio/", "")
                    audio_info["size"] = enclosure.get("length")
                    break

        # 检查 media:content 标签
        if not audio_info["is_podcast"] and "media_content" in entry:
            for media in entry["media_content"]:
                if media.get("type", "").startswith("audio/"):
                    audio_info["is_podcast"] = True
                    audio_info["url"] = media.get("url")
                    audio_info["type"] = media.get("type", "").replace("audio/", "")
                    audio_info["duration"] = media.get("duration")
                    audio_info["size"] = media.get("fileSize")
                    break

        # 检查 itunes:image 和 itunes:duration
        if audio_info["is_podcast"]:
            if "itunes_duration" in entry and entry["itunes_duration"]:
                try:
                    duration_str = entry["itunes_duration"]
                    # 解析时长 (可能是秒数或 HH:MM:SS 格式)
                    if isinstance(duration_str, int):
                        audio_info["duration"] = duration_str
                    elif isinstance(duration_str, str):
                        if ":" in duration_str:
                            parts = duration_str.split(":")
                            if len(parts) == 3:
                                audio_info["duration"] = (
                                    int(parts[0]) * 3600
                                    + int(parts[1]) * 60
                                    + int(parts[2])
                                )
                            elif len(parts) == 2:
                                audio_info["duration"] = int(parts[0]) * 60 + int(
                                    parts[1]
                                )
                        else:
                            audio_info["duration"] = int(duration_str)
                except (ValueError, TypeError):
                    pass

        return audio_info

    @staticmethod
    def validate_feed_url(url: str) -> Tuple[bool, str]:
        """
        验证 RSS 订阅源 URL 是否有效（支持 RSSHub）

        Args:
            url: RSS/Atom 订阅源 URL 或 RSSHub 路由

        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 检查是否为 RSSHub URL
            if RSSHubService.is_rsshub_url(url):
                logger.info(f"检测到 RSSHub URL，使用 RSSHub 验证器: {url}")
                return RSSHubService.validate_rsshub_url(url)

            # 验证标准 RSS 订阅源
            feed = feedparser.parse(url)

            # 基本验证
            if feed.bozo and isinstance(
                feed.bozo_exception, feedparser.ThingsNobodyCaresAboutButMe
            ):
                # 忽略一些无关紧要的警告
                pass
            elif feed.bozo:
                warning_msg = f"RSS 验证警告: {feed.bozo_exception}"
                logger.warning(warning_msg)
                return False, warning_msg

            # 检查是否有基本内容
            if not hasattr(feed, "feed") or not feed.feed:
                error_msg = "RSS 验证失败: 无 feed 内容"
                logger.warning(error_msg)
                return False, error_msg

            if not feed.entries:
                error_msg = "RSS 验证失败: 无文章条目"
                logger.warning(error_msg)
                return False, error_msg

            logger.info(f"RSS 订阅源验证成功: {url}")
            return True, "验证成功"

        except Exception as e:
            error_msg = f"RSS 验证失败: {e}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def get_rsshub_examples() -> List[Dict]:
        """
        获取 RSSHub 示例订阅源

        Returns:
            示例订阅源列表
        """
        return RSSHubService.get_rsshub_examples()

    @staticmethod
    def search_rsshub_routes(query: str) -> List[Dict]:
        """
        搜索 RSSHub 路由

        Args:
            query: 搜索关键词

        Returns:
            匹配的路由列表
        """
        return RSSHubService.search_rsshub_routes(query)

    @staticmethod
    def is_rsshub_url(url: str) -> bool:
        """
        判断是否为 RSSHub URL

        Args:
            url: 要检查的 URL

        Returns:
            是否为 RSSHub URL
        """
        return RSSHubService.is_rsshub_url(url)

    @staticmethod
    def normalize_rsshub_url(url: str) -> str:
        """
        标准化 RSSHub URL

        Args:
            url: 原始 URL

        Returns:
            标准化后的 URL
        """
        return RSSHubService.normalize_rsshub_url(url)
