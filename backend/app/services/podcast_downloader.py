"""
播客下载服务
负责下载播客音频文件到本地
"""

import logging
import os
import aiohttp
import asyncio
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class PodcastDownloader:
    """播客音频下载服务"""

    def __init__(self, download_dir: Optional[str] = None):
        if download_dir:
            self.download_dir = Path(download_dir)
        else:
            self.download_dir = Path("data/podcasts")

        self.download_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"播客下载服务初始化完成，下载目录: {self.download_dir}")

    def get_audio_path(self, article_id: int, extension: str) -> Path:
        """获取音频文件保存路径"""
        return self.download_dir / f"{article_id}.{extension}"

    def get_extension_from_url(self, url: str) -> str:
        """从 URL 提取文件扩展名"""
        url_lower = url.lower()

        # 常见的音频格式
        extensions = [".mp3", ".m4a", ".wav", ".ogg", ".flac", ".aac", ".wma"]

        for ext in extensions:
            if ext in url_lower:
                return ext.lstrip(".")

        # 默认返回 mp3
        return "mp3"

    async def download_audio(
        self,
        audio_url: str,
        article_id: int,
        progress_callback: Optional[callable] = None,
    ) -> Dict:
        """
        下载播客音频文件

        Args:
            audio_url: 音频文件 URL
            article_id: 文章 ID
            progress_callback: 进度回调函数

        Returns:
            下载结果字典
        """
        try:
            extension = self.get_extension_from_url(audio_url)
            local_path = self.get_audio_path(article_id, extension)

            # 如果文件已存在，跳过下载
            if local_path.exists():
                logger.info(f"音频文件已存在，跳过下载: {local_path}")
                return {
                    "success": True,
                    "local_path": str(local_path),
                    "size": local_path.stat().st_size,
                    "skipped": True,
                }

            logger.info(f"开始下载播客音频: {audio_url}")

            # 使用 aiohttp 下载文件
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"HTTP {response.status}"}

                    # 获取文件大小
                    total_size = response.headers.get("Content-Length")
                    if total_size:
                        total_size = int(total_size)

                    # 下载文件
                    downloaded = 0
                    chunks = []

                    async for chunk in response.content.iter_chunked(8192):
                        chunks.append(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size:
                            progress = int(downloaded / total_size * 100)
                            progress_callback(progress)

                    # 保存文件
                    with open(local_path, "wb") as f:
                        f.write(b"".join(chunks))

                    file_size = local_path.stat().st_size

                    logger.info(f"音频下载完成: {local_path}, 大小: {file_size} bytes")

                    return {
                        "success": True,
                        "local_path": str(local_path),
                        "size": file_size,
                        "skipped": False,
                    }

        except asyncio.TimeoutError:
            logger.error(f"下载超时: {audio_url}")
            return {"success": False, "error": "下载超时"}
        except Exception as e:
            logger.error(f"下载失败: {audio_url}, 错误: {e}")
            return {"success": False, "error": str(e)}

    async def download_audio_with_retry(
        self,
        audio_url: str,
        article_id: int,
        max_retries: int = 3,
        progress_callback: Optional[callable] = None,
    ) -> Dict:
        """带重试的下载"""
        for attempt in range(max_retries):
            result = await self.download_audio(audio_url, article_id, progress_callback)

            if result["success"]:
                return result

            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                logger.warning(
                    f"下载失败，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(wait_time)

        return {"success": False, "error": f"重试 {max_retries} 次后仍失败"}

    def delete_audio(self, article_id: int) -> bool:
        """删除本地音频文件"""
        for ext in ["mp3", "m4a", "wav", "ogg", "flac", "aac", "wma"]:
            local_path = self.get_audio_path(article_id, ext)
            if local_path.exists():
                local_path.unlink()
                logger.info(f"删除音频文件: {local_path}")
                return True
        return False

    def get_audio_info(self, article_id: int) -> Optional[Dict]:
        """获取本地音频文件信息"""
        for ext in ["mp3", "m4a", "wav", "ogg", "flac", "aac", "wma"]:
            local_path = self.get_audio_path(article_id, ext)
            if local_path.exists():
                stat = local_path.stat()
                return {
                    "local_path": str(local_path),
                    "size": stat.st_size,
                    "extension": ext,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
        return None


# 全局实例
podcast_downloader = PodcastDownloader()
