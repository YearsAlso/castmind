"""
API v1 路由
"""

from fastapi import APIRouter
from . import feeds, articles, system

api_router = APIRouter()

# 注册所有路由 - 移除前缀斜杠以避免重复
api_router.include_router(feeds.router, prefix="/feeds", tags=["订阅源"])
api_router.include_router(articles.router, prefix="/articles", tags=["文章"])
api_router.include_router(system.router, prefix="/system", tags=["系统"])
