"""
订阅源 API 路由
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import Feed
from app.models.schemas import FeedCreate, FeedUpdate, FeedResponse
from app.services.feed_service import FeedService
from app.scheduler.tasks import TaskScheduler

router = APIRouter()


@router.get("/", response_model=List[FeedResponse])
async def list_feeds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    获取订阅源列表
    """
    query = db.query(Feed)

    if status:
        query = query.filter(Feed.status == status)
    if category:
        query = query.filter(Feed.category == category)

    feeds = query.offset(skip).limit(limit).all()
    return feeds


@router.get("/{feed_id}", response_model=FeedResponse)
async def get_feed(feed_id: int, db: Session = Depends(get_db)):
    """
    获取单个订阅源
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")
    return feed


@router.post("/", response_model=FeedResponse, status_code=201)
async def create_feed(feed_data: FeedCreate, db: Session = Depends(get_db)):
    """
    创建新订阅源
    """
    # 检查 URL 是否已存在
    existing = db.query(Feed).filter(Feed.url == feed_data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="该 URL 已存在")

    feed = Feed(**feed_data.model_dump())
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return feed


@router.put("/{feed_id}", response_model=FeedResponse)
async def update_feed(
    feed_id: int, feed_data: FeedUpdate, db: Session = Depends(get_db)
):
    """
    更新订阅源
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")

    for key, value in feed_data.model_dump(exclude_unset=True).items():
        setattr(feed, key, value)

    db.commit()
    db.refresh(feed)
    return feed


@router.delete("/{feed_id}", status_code=204)
async def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    """
    删除订阅源
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")

    db.delete(feed)
    db.commit()


@router.post("/{feed_id}/fetch", response_model=FeedResponse)
async def fetch_feed(feed_id: int, db: Session = Depends(get_db)):
    """
    手动抓取订阅源
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")

    # 这里应该调用实际的抓取逻辑
    # 暂时只是更新最后抓取时间
    feed.last_fetch = datetime.now()
    db.commit()
    db.refresh(feed)

    return feed


@router.post("/fetch-all")
async def fetch_all_feeds():
    """
    手动抓取所有订阅源
    """
    try:
        task_scheduler = TaskScheduler()
        result = task_scheduler.fetch_all_feeds()
        return {
            "status": "success",
            "message": f"抓取完成: 成功 {result.get('success', 0)}, 失败 {result.get('error', 0)}",
            "timestamp": datetime.now().isoformat(),
            "data": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"抓取失败: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/{feed_id}/articles")
async def get_feed_articles(
    feed_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    获取订阅源的文章列表
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")

    articles = feed.articles
    return {
        "feed_id": feed_id,
        "feed_name": feed.name,
        "total": len(articles),
        "articles": articles[skip : skip + limit],
    }


# RSSHub 相关端点
@router.get("/rsshub/examples")
async def get_rsshub_examples():
    """
    获取 RSSHub 示例订阅源
    """
    from app.services.rss_service import RSSService

    examples = RSSService.get_rsshub_examples()
    return {"total": len(examples), "examples": examples}


@router.get("/rsshub/search")
async def search_rsshub_routes(
    query: str = Query(..., min_length=1, description="搜索关键词"),
):
    """
    搜索 RSSHub 路由
    """
    from app.services.rss_service import RSSService

    results = RSSService.search_rsshub_routes(query)
    return {"query": query, "total": len(results), "results": results}


@router.post("/rsshub/validate")
async def validate_rsshub_url(url: str = Query(..., description="RSSHub URL 或路由")):
    """
    验证 RSSHub URL
    """
    from app.services.rss_service import RSSService

    # 检查是否为 RSSHub URL
    if not RSSService.is_rsshub_url(url):
        return {"is_rsshub": False, "valid": False, "message": "不是有效的 RSSHub URL"}

    # 验证 URL
    is_valid, message = RSSService.validate_feed_url(url)

    return {
        "is_rsshub": True,
        "valid": is_valid,
        "message": message,
        "normalized_url": RSSService.normalize_rsshub_url(url) if is_valid else None,
    }


@router.post("/rsshub/test-parse")
async def test_parse_rsshub_url(url: str = Query(..., description="RSSHub URL 或路由")):
    """
    测试解析 RSSHub URL
    """
    from app.services.rss_service import RSSService

    # 检查是否为 RSSHub URL
    if not RSSService.is_rsshub_url(url):
        raise HTTPException(status_code=400, detail="不是有效的 RSSHub URL")

    # 解析订阅源
    feed_info = RSSService.parse_feed(url)

    if not feed_info:
        raise HTTPException(status_code=400, detail="无法解析 RSSHub 订阅源")

    return {
        "url": url,
        "normalized_url": RSSService.normalize_rsshub_url(url),
        "feed_info": {
            "title": feed_info.get("title"),
            "description": feed_info.get("description"),
            "source_type": feed_info.get("source_type", "unknown"),
            "entry_count": len(feed_info.get("entries", [])),
            "sample_entries": feed_info.get("entries", [])[:3],  # 返回前3条作为示例
        },
    }
