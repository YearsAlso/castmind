"""
音频转录服务
支持多种转录方案：Deepgram、AssemblyAI、Faster Whisper 或手动输入
"""

import logging
import os
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class TranscriptionService:
    """音频转录服务"""

    def __init__(self):
        # 转录提供商: deepgram, assemblyai, faster_whisper, manual
        self.provider = os.getenv("TRANSCRIPTION_PROVIDER", "faster_whisper")

        # Deepgram 配置
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")

        # AssemblyAI 配置
        self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")

        # Faster Whisper 配置
        self.faster_whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.faster_whisper_device = os.getenv("WHISPER_DEVICE", "cpu")  # cpu 或 cuda
        self.faster_whisper_model_dir = os.getenv(
            "WHISPER_MODEL_DIR", "data/whisper_models"
        )

        # 初始化 Faster Whisper 模型
        self._faster_whisper_model = None

        logger.info(f"转录服务初始化完成，提供商: {self.provider}")

    def _get_faster_whisper_model(self):
        """获取 Faster Whisper 模型"""
        if self._faster_whisper_model is None:
            try:
                from faster_whisper import WhisperModel

                # 确保模型目录存在
                model_path = Path(self.faster_whisper_model_dir)
                model_path.mkdir(parents=True, exist_ok=True)

                logger.info(f"加载 Faster Whisper 模型: {self.faster_whisper_model}")

                self._faster_whisper_model = WhisperModel(
                    self.faster_whisper_model,
                    device=self.faster_whisper_device,
                    compute_type="int8"
                    if self.faster_whisper_device == "cpu"
                    else "float16",
                )

                logger.info("Faster Whisper 模型加载成功")
            except ImportError:
                logger.warning(
                    "faster_whisper 库未安装，请运行: pip install faster-whisper"
                )
                return None
            except Exception as e:
                logger.error(f"加载 Faster Whisper 模型失败: {e}")
                return None
        return self._faster_whisper_model

    async def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        audio_url: Optional[str] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict:
        """
        转录音频文件

        Args:
            audio_path: 音频文件路径
            language: 语言代码 (zh, en, 等)
            audio_url: 音频 URL（用于流式转录）
            progress_callback: 进度回调

        Returns:
            转录结果
        """
        # 根据提供商选择转录方式
        if self.provider == "manual":
            return {
                "success": False,
                "error": "请手动输入转录文本",
                "requires_manual_input": True,
            }
        elif self.provider == "faster_whisper":
            return await self._transcribe_faster_whisper(audio_path, language)
        elif self.provider == "deepgram" and audio_url:
            return await self._transcribe_deepgram_url(audio_url, language)
        elif self.provider == "assemblyai" and audio_url:
            return await self._transcribe_assemblyai_url(audio_url, language)

        return {"success": False, "error": f"当前模式 {self.provider} 不支持此操作"}

    async def _transcribe_faster_whisper(
        self, audio_path: str, language: Optional[str] = None
    ) -> Dict:
        """使用 Faster Whisper 本地转录"""
        import asyncio

        try:
            audio_file = Path(audio_path)

            if not audio_file.exists():
                return {"success": False, "error": "音频文件不存在"}

            model = self._get_faster_whisper_model()
            if not model:
                return {"success": False, "error": "Faster Whisper 模型加载失败"}

            logger.info(f"使用 Faster Whisper 转录音频: {audio_file.name}")

            def transcribe():
                return model.transcribe(
                    str(audio_file), language=language, beam_size=5, vad_filter=True
                )

            # 在线程中执行
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, transcribe)

            text = result.text

            logger.info(f"Faster Whisper 转录完成，文字长度: {len(text)} 字符")

            return {
                "success": True,
                "text": text,
                "language": result.language or language or "zh",
                "provider": "faster_whisper",
                "model": self.faster_whisper_model,
            }

        except Exception as e:
            logger.error(f"Faster Whisper 转录失败: {e}")
            return {"success": False, "error": str(e)}

    async def _transcribe_deepgram_url(
        self, audio_url: str, language: Optional[str] = None
    ) -> Dict:
        """使用 Deepgram API 从 URL 转录"""
        try:
            import aiohttp

            if not self.deepgram_api_key:
                return {"success": False, "error": "未配置 DEEPGRAM_API_KEY"}

            url = "https://api.deepgram.com/v1/listen"
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "url": audio_url,
                "model": "nova-2",
                "language": language or "zh-CN",
                "smart_format": True,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": f"Deepgram API 错误: {error}",
                        }

                    data = await response.json()
                    transcript = data["results"]["channels"][0]["alternatives"][0][
                        "transcript"
                    ]

                    return {
                        "success": True,
                        "text": transcript,
                        "language": language or "zh-CN",
                        "provider": "deepgram",
                    }

        except Exception as e:
            logger.error(f"Deepgram 转录失败: {e}")
            return {"success": False, "error": str(e)}

    async def _transcribe_assemblyai_url(
        self, audio_url: str, language: Optional[str] = None
    ) -> Dict:
        """使用 AssemblyAI 从 URL 转录"""
        try:
            import aiohttp

            if not self.assemblyai_api_key:
                return {"success": False, "error": "未配置 ASSEMBLYAI_API_KEY"}

            # 第一步：提交转录任务
            transcript_url = "https://api.assemblyai.com/v2/transcript"
            headers = {
                "Authorization": self.assemblyai_api_key,
                "Content-Type": "application/json",
            }
            payload = {
                "audio_url": audio_url,
                "language_code": language or "zh",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    transcript_url, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        return {"success": False, "error": f"AssemblyAI 错误: {error}"}

                    result = await response.json()
                    transcript_id = result["id"]

                # 第二步：等待转录完成
                status_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

                while True:
                    async with session.get(
                        status_url, headers=headers
                    ) as status_response:
                        status_result = await status_response.json()
                        status = status_result["status"]

                        if status == "completed":
                            transcript = status_result["text"]
                            return {
                                "success": True,
                                "text": transcript,
                                "language": language or "zh",
                                "provider": "assemblyai",
                            }
                        elif status == "error":
                            return {
                                "success": False,
                                "error": status_result.get("error", "转录失败"),
                            }
                        else:
                            await asyncio.sleep(3)

        except Exception as e:
            logger.error(f"AssemblyAI 转录失败: {e}")
            return {"success": False, "error": str(e)}

    async def transcribe_from_url(
        self,
        audio_url: str,
        article_id: int,
        downloader,
        language: Optional[str] = None,
    ) -> Dict:
        """
        从 URL 直接转录
        """
        if self.provider == "manual":
            return {
                "success": False,
                "error": "请手动输入转录文本",
                "requires_manual_input": True,
            }

        # Faster Whisper 需要下载文件
        if self.provider == "faster_whisper":
            download_result = await downloader.download_audio(audio_url, article_id)
            if not download_result["success"]:
                return {
                    "success": False,
                    "error": f"下载失败: {download_result.get('error')}",
                }
            return await self.transcribe_audio(download_result["local_path"], language)

        # 其他提供商可以直接从 URL 转录
        if self.provider == "deepgram":
            return await self._transcribe_deepgram_url(audio_url, language)
        elif self.provider == "assemblyai":
            return await self._transcribe_assemblyai_url(audio_url, language)

        return {"success": False, "error": f"不支持的提供商: {self.provider}"}

    def get_available_providers(self) -> list:
        """获取可用的转录提供商"""
        providers = ["manual", "faster_whisper"]

        if self.deepgram_api_key:
            providers.append("deepgram")
        if self.assemblyai_api_key:
            providers.append("assemblyai")

        return providers

    def check_provider_status(self) -> Dict:
        """检查转录服务状态"""
        return {
            "current_provider": self.provider,
            "available_providers": self.get_available_providers(),
            "deepgram_configured": bool(self.deepgram_api_key),
            "assemblyai_configured": bool(self.assemblyai_api_key),
            "faster_whisper_model": self.faster_whisper_model
            if self.provider == "faster_whisper"
            else None,
        }


# 全局实例
transcription_service = TranscriptionService()
