"""
RSSHub 解析服务 - 支持 RSSHub 订阅源
"""
import logging
import re
from typing import List, Dict, Optional, Tuple
import feedparser
from datetime import datetime
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class RSSHubService:
    """RSSHub 解析服务类"""
    
    # RSSHub 官方实例
    RSSHUB_BASE_URLS = [
        "https://rsshub.app",
        "https://rsshub.rssforever.com",
        "https://rsshub.uneasy.win",
    ]
    
    # 常见的 RSSHub 路由模式
    RSSHUB_ROUTES = {
        # 社交媒体
        "twitter": "/twitter/user/:id",
        "weibo": "/weibo/user/:id",
        "zhihu": "/zhihu/people/activities/:id",
        "bilibili": "/bilibili/user/video/:uid",
        "youtube": "/youtube/channel/:id",
        "github": "/github/repos/:user/:repo",
        
        # 新闻媒体
        "reuters": "/reuters/:category?",
        "bbc": "/bbc/:channel?",
        "nytimes": "/nytimes/:section?",
        
        # 技术社区
        "hackernews": "/hackernews/:type?",
        "producthunt": "/producthunt/:type?",
        "v2ex": "/v2ex/tab/:tab?",
        
        # 博客平台
        "medium": "/medium/:user",
        "wordpress": "/:domain/feed",
        "blogger": "/blogger/:blog",
        
        # 其他
        "reddit": "/reddit/r/:subreddit",
        "douban": "/douban/group/:groupid",
        "tiktok": "/tiktok/user/:user",
    }
    
    @staticmethod
    def is_rsshub_url(url: str) -> bool:
        """
        判断是否为 RSSHub URL
        
        Args:
            url: 要检查的 URL
            
        Returns:
            是否为 RSSHub URL
        """
        try:
            parsed = urlparse(url)
            
            # 检查是否是 RSSHub 官方实例
            for base_url in RSSHubService.RSSHUB_BASE_URLS:
                if parsed.netloc == urlparse(base_url).netloc:
                    return True
            
            # 检查路径模式是否匹配 RSSHub 路由
            path = parsed.path
            for route_pattern in RSSHubService.RSSHUB_ROUTES.values():
                # 简单的模式匹配（实际应该使用更复杂的匹配）
                if re.match(r'^/[a-zA-Z0-9]+/', path) and not path.endswith('.xml') and not path.endswith('.rss'):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查 RSSHub URL 失败: {e}")
            return False
    
    @staticmethod
    def normalize_rsshub_url(url: str) -> str:
        """
        标准化 RSSHub URL
        
        Args:
            url: 原始 URL
            
        Returns:
            标准化后的 URL
        """
        try:
            parsed = urlparse(url)
            
            # 如果已经是完整的 RSSHub URL，直接返回
            for base_url in RSSHubService.RSSHUB_BASE_URLS:
                if parsed.netloc == urlparse(base_url).netloc:
                    return url
            
            # 如果不是完整的 URL，尝试构建
            if not parsed.scheme:
                # 假设是 RSSHub 路由路径
                return f"https://rsshub.app{url if url.startswith('/') else '/' + url}"
            
            return url
            
        except Exception as e:
            logger.error(f"标准化 RSSHub URL 失败: {e}")
            return url
    
    @staticmethod
    def parse_rsshub_feed(url: str) -> Optional[Dict]:
        """
        解析 RSSHub 订阅源
        
        Args:
            url: RSSHub 订阅源 URL
            
        Returns:
            解析后的订阅源信息，或 None 如果解析失败
        """
        try:
            logger.info(f"开始解析 RSSHub 订阅源: {url}")
            
            # 标准化 URL
            normalized_url = RSSHubService.normalize_rsshub_url(url)
            
            # 添加 .rss 后缀（如果需要）
            if not normalized_url.endswith('.rss') and not normalized_url.endswith('.xml'):
                normalized_url = f"{normalized_url}.rss"
            
            # 解析 RSS 订阅源
            feed = feedparser.parse(normalized_url)
            
            if feed.bozo:
                logger.warning(f"RSSHub 解析警告: {feed.bozo_exception}")
            
            # 提取订阅源信息
            feed_info = {
                "source_type": "rsshub",
                "original_url": url,
                "normalized_url": normalized_url,
                "title": feed.feed.get("title", "RSSHub 订阅源"),
                "description": feed.feed.get("description", "通过 RSSHub 生成的订阅源"),
                "link": feed.feed.get("link", url),
                "language": feed.feed.get("language", ""),
                "updated": feed.feed.get("updated", ""),
                "entries": []
            }
            
            # 提取文章条目
            for entry in feed.entries[:50]:  # 限制最多50条
                article = {
                    "title": entry.get("title", "无标题"),
                    "link": entry.get("link", ""),
                    "description": entry.get("description", ""),
                    "content": entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "",
                    "published": entry.get("published", entry.get("updated", "")),
                    "author": entry.get("author", ""),
                    "categories": entry.get("tags", []),
                    "rsshub_metadata": {
                        "source": "rsshub",
                        "original_url": url,
                    }
                }
                feed_info["entries"].append(article)
            
            logger.info(f"成功解析 RSSHub 订阅源: {feed_info['title']}, 找到 {len(feed_info['entries'])} 篇文章")
            return feed_info
            
        except Exception as e:
            logger.error(f"RSSHub 解析失败: {url}, 错误: {e}")
            return None
    
    @staticmethod
    def get_rsshub_examples() -> List[Dict]:
        """
        获取 RSSHub 示例订阅源
        
        Returns:
            示例订阅源列表
        """
        return [
            {
                "name": "Twitter 用户",
                "description": "Twitter 用户的最新推文",
                "url": "https://rsshub.app/twitter/user/elonmusk",
                "category": "社交媒体"
            },
            {
                "name": "GitHub 仓库",
                "description": "GitHub 仓库的最新动态",
                "url": "https://rsshub.app/github/repos/vuejs/vue",
                "category": "技术"
            },
            {
                "name": "B站 UP 主",
                "description": "Bilibili UP 主的视频更新",
                "url": "https://rsshub.app/bilibili/user/video/208259",
                "category": "视频"
            },
            {
                "name": "知乎用户",
                "description": "知乎用户的动态",
                "url": "https://rsshub.app/zhihu/people/activities/zhouyuan",
                "category": "知识"
            },
            {
                "name": "Hacker News",
                "description": "Hacker News 最新文章",
                "url": "https://rsshub.app/hackernews",
                "category": "技术新闻"
            },
            {
                "name": "Reuters 新闻",
                "description": "路透社新闻",
                "url": "https://rsshub.app/reuters",
                "category": "新闻"
            },
            {
                "name": "Product Hunt",
                "description": "Product Hunt 今日产品",
                "url": "https://rsshub.app/producthunt/today",
                "category": "产品"
            },
            {
                "name": "Reddit 社区",
                "description": "Reddit 子版块",
                "url": "https://rsshub.app/reddit/r/programming",
                "category": "社区"
            },
            {
                "name": "Medium 用户",
                "description": "Medium 作者文章",
                "url": "https://rsshub.app/medium/@freeCodeCamp",
                "category": "博客"
            },
            {
                "name": "豆瓣小组",
                "description": "豆瓣小组讨论",
                "url": "https://rsshub.app/douban/group/648102",
                "category": "社区"
            }
        ]
    
    @staticmethod
    def search_rsshub_routes(query: str) -> List[Dict]:
        """
        搜索 RSSHub 路由
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的路由列表
        """
        results = []
        query_lower = query.lower()
        
        for name, pattern in RSSHubService.RSSHUB_ROUTES.items():
            if query_lower in name.lower() or query_lower in pattern.lower():
                results.append({
                    "name": name,
                    "pattern": pattern,
                    "example": f"https://rsshub.app{pattern.replace(':id', 'example').replace(':user', 'username').replace(':repo', 'repository')}",
                    "description": f"RSSHub {name} 路由"
                })
        
        return results
    
    @staticmethod
    def validate_rsshub_url(url: str) -> Tuple[bool, str]:
        """
        验证 RSSHub URL 是否有效
        
        Args:
            url: RSSHub 订阅源 URL
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            normalized_url = RSSHubService.normalize_rsshub_url(url)
            
            # 测试访问
            response = requests.get(normalized_url, timeout=10)
            
            if response.status_code == 200:
                # 检查是否是有效的 RSS
                feed = feedparser.parse(response.text)
                
                if feed.bozo and not isinstance(feed.bozo_exception, feedparser.ThingsNobodyCaresAboutButMe):
                    return False, f"无效的 RSS 格式: {feed.bozo_exception}"
                
                if not hasattr(feed, 'feed') or not feed.feed:
                    return False, "无 feed 内容"
                
                return True, "验证成功"
            else:
                return False, f"HTTP 错误: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, "连接失败"
        except Exception as e:
            return False, f"验证失败: {e}"