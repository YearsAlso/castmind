"""
订阅源 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import Feed
from app.models.schemas import FeedCreate, FeedUpdate, FeedResponse
from app.services.feed_service import FeedService

router = APIRouter()

@router.get("/", response_model=List[FeedResponse])
async def list_feeds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
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
async def get_feed(
    feed_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个订阅源
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")
    return feed

@router.post("/", response_model=FeedResponse, status_code=201)
async def create_feed(
    feed_data: FeedCreate,
    db: Session = Depends(get_db)
):
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
    feed_id: int,
    feed_data: FeedUpdate,
    db: Session = Depends(get_db)
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
async def delete_feed(
    feed_id: int,
    db: Session = Depends(get_db)
):
    """
    删除订阅源
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")
    
    db.delete(feed)
    db.commit()

@router.post("/{feed_id}/fetch", response_model=FeedResponse)
async def fetch_feed(
    feed_id: int,
    db: Session = Depends(get_db)
):
    """
    手动抓取订阅源
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")
    
    # 这里应该调用实际的抓取逻辑
    # 暂时只是更新最后抓取时间
    from datetime import datetime
    feed.last_fetch = datetime.now()
    db.commit()
    db.refresh(feed)
    
    return feed

@router.get("/{feed_id}/articles")
async def get_feed_articles(
    feed_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
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
        "articles": articles[skip:skip+limit]
    }