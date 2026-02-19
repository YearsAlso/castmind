"""
🎧 CastMind Zoo - Zoo Framework + FastAPI 集成框架

基于 Zoo Framework 的 CastMind 播客处理系统
"""

__version__ = "0.1.0"
__author__ = "牛马 AI 助手"
__email__ = "castmind@example.com"
__license__ = "MIT"

from .master import CastMindMaster
from .workers import *
from .api import *
from .config import *

__all__ = [
    "CastMindMaster",
    "config",
    "api",
    "workers",
]