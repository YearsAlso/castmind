#!/usr/bin/env python3
"""
CastMind - RSS解析模块
负责解析播客RSS feed，提取播客信息和剧集列表
"""

import feedparser
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class PodcastEpisode:
    """播客剧集数据类"""
    title: str
    url: str  # 音频文件URL
    published: datetime
    description: str
    duration: Optional[str] = None  # 时长（秒或HH:MM:SS格式）
    file_size: Optional[int] = None  # 文件大小（字节）
    guid: Optional[str] = None  # 唯一标识符

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title': self.title,
            'url': self.url,
            'published': self.published.isoformat() if self.published else None,
            'description': self.description,
            'duration': self.duration,
            'file_size': self.file_size,
            'guid': self.guid
        }


@dataclass
class PodcastInfo:
    """播客信息数据类"""
    title: str
    description: str
    link: str  # 播客网站链接
    feed_url: str  # RSS feed URL
    language: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    categories: List[str] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title': self.title,
            'description': self.description,
            'link': self.link,
            'feed_url': self.feed_url,
            'language': self.language,
            'author': self.author,
            'image_url': self.image_url,
            'categories': self.categories,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class RSSParser:
    """RSS解析器"""

    def __init__(self, timeout: int = 30, user_agent: str = None):
        """
        初始化RSS解析器
        
        Args:
            timeout: 请求超时时间（秒）
            user_agent: 自定义User-Agent
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; CastMind/1.0; +https://github.com/YearsAlso/castmind)"
        )

    def parse_feed(self, feed_url: str) -> Optional[PodcastInfo]:
        """
        解析RSS feed，返回播客信息
        
        Args:
            feed_url: RSS feed URL
            
        Returns:
            PodcastInfo对象，如果解析失败则返回None
        """
        try:
            # 设置请求头
            headers = {'User-Agent': self.user_agent}

            # 下载并解析feed
            response = requests.get(feed_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # 使用feedparser解析
            feed = feedparser.parse(response.content)

            if feed.bozo:  # 解析错误
                logger.warning(f"RSS解析错误: {feed.bozo_exception}")
                return None

            # 提取播客信息
            return self._extract_podcast_info(feed, feed_url)

        except requests.RequestException as e:
            logger.error(f"下载RSS feed失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析RSS feed失败: {e}")
            return None

    def _extract_podcast_info(self, feed: feedparser.FeedParserDict, feed_url: str) -> PodcastInfo:
        """从feed中提取播客信息"""
        channel = feed.feed

        # 处理发布时间
        last_updated = None
        if hasattr(channel, 'updated_parsed') and channel.updated_parsed:
            last_updated = datetime(*channel.updated_parsed[:6])

        # 处理分类
        categories = []
        if hasattr(channel, 'tags'):
            categories = [tag.term for tag in channel.tags if hasattr(tag, 'term')]

        # 处理图片
        image_url = None
        if hasattr(channel, 'image') and hasattr(channel.image, 'href'):
            image_url = channel.image.href

        return PodcastInfo(
            title=channel.title if hasattr(channel, 'title') else '未知播客',
            description=channel.description if hasattr(channel, 'description') else '',
            link=channel.link if hasattr(channel, 'link') else feed_url,
            feed_url=feed_url,
            language=getattr(channel, 'language', None),
            author=getattr(channel, 'author', None),
            image_url=image_url,
            categories=categories,
            last_updated=last_updated
        )

    def get_episodes(self, feed_url: str, limit: int = 10) -> List[PodcastEpisode]:
        """
        获取播客剧集列表
        
        Args:
            feed_url: RSS feed URL
            limit: 返回的最大剧集数量
            
        Returns:
            剧集列表
        """
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(feed_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo:
                logger.warning(f"RSS解析错误: {feed.bozo_exception}")
                return []

            episodes = []
            for entry in feed.entries[:limit]:
                episode = self._extract_episode_info(entry)
                if episode:
                    episodes.append(episode)

            return episodes

        except requests.RequestException as e:
            logger.error(f"下载RSS feed失败: {e}")
            return []
        except Exception as e:
            logger.error(f"解析剧集失败: {e}")
            return []

    def _extract_episode_info(self, entry: feedparser.FeedParserDict) -> Optional[PodcastEpisode]:
        """从feed条目中提取剧集信息"""
        try:
            # 查找音频链接
            audio_url = None
            file_size = None
            duration = None

            # 检查enclosures
            if hasattr(entry, 'enclosures'):
                for enclosure in entry.enclosures:
                    if enclosure.type.startswith('audio/'):
                        audio_url = enclosure.href
                        if hasattr(enclosure, 'length'):
                            try:
                                file_size = int(enclosure.length)
                            except (ValueError, TypeError):
                                pass
                        break

            # 如果没有找到enclosure，检查links
            if not audio_url and hasattr(entry, 'links'):
                for link in entry.links:
                    if link.type.startswith('audio/'):
                        audio_url = link.href
                        break

            # 如果没有音频链接，跳过这个剧集
            if not audio_url:
                return None

            # 处理发布时间
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])

            # 处理时长
            if hasattr(entry, 'itunes_duration'):
                duration = entry.itunes_duration

            return PodcastEpisode(
                title=entry.title if hasattr(entry, 'title') else '未知标题',
                url=audio_url,
                published=published,
                description=entry.description if hasattr(entry, 'description') else '',
                duration=duration,
                file_size=file_size,
                guid=entry.get('id') or entry.get('guid')
            )

        except Exception as e:
            logger.error(f"提取剧集信息失败: {e}")
            return None

    def validate_feed(self, feed_url: str) -> Dict[str, Any]:
        """
        验证RSS feed
        
        Args:
            feed_url: RSS feed URL
            
        Returns:
            验证结果字典
        """
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(feed_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            # 检查基本信息
            has_title = hasattr(feed.feed, 'title')
            has_entries = len(feed.entries) > 0

            # 检查音频链接
            has_audio = False
            if has_entries:
                for entry in feed.entries[:3]:  # 检查前3个条目
                    if self._extract_episode_info(entry):
                        has_audio = True
                        break

            return {
                'valid': not feed.bozo,
                'has_title': has_title,
                'has_entries': has_entries,
                'has_audio': has_audio,
                'entry_count': len(feed.entries),
                'error': str(feed.bozo_exception) if feed.bozo else None,
                'content_type': response.headers.get('Content-Type', ''),
                'status_code': response.status_code
            }

        except requests.RequestException as e:
            return {
                'valid': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }


# 工具函数
def test_rss_feed(feed_url: str = "https://feeds.fireside.fm/bibleinayear/rss"):
    """测试RSS解析功能"""
    parser = RSSParser()

    print(f"测试RSS feed: {feed_url}")
    print("=" * 60)

    # 验证feed
    validation = parser.validate_feed(feed_url)
    print(f"验证结果: {'有效' if validation['valid'] else '无效'}")
    if validation['error']:
        print(f"错误: {validation['error']}")
    print(f"条目数量: {validation['entry_count']}")
    print(f"包含音频: {validation['has_audio']}")

    if validation['valid']:
        # 获取播客信息
        podcast_info = parser.parse_feed(feed_url)
        if podcast_info:
            print(f"\n播客信息:")
            print(f"  标题: {podcast_info.title}")
            print(f"  描述: {podcast_info.description[:100]}...")
            print(f"  作者: {podcast_info.author or '未知'}")
            print(f"  分类: {', '.join(podcast_info.categories) if podcast_info.categories else '无'}")

        # 获取剧集列表
        episodes = parser.get_episodes(feed_url, limit=3)
        print(f"\n最新剧集 ({len(episodes)}个):")
        for i, episode in enumerate(episodes, 1):
            print(f"  {i}. {episode.title}")
            print(f"     发布时间: {episode.published}")
            print(f"     音频URL: {episode.url}")
            if episode.duration:
                print(f"     时长: {episode.duration}")
            print()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 测试
    test_rss_feed()
