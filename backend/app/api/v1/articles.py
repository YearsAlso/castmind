"""
文章 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import Article, Feed
from app.models.schemas import ArticleCreate, ArticleUpdate, ArticleResponse

router = APIRouter()

@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    feed_id: Optional[int] = None,
    read_status: Optional[bool] = None,
    processed_status: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取文章列表
    """
    query = db.query(Article)
    
    if feed_id:
        query = query.filter(Article.feed_id == feed_id)
    if read_status is not None:
        query = query.filter(Article.read_status == read_status)
    if processed_status is not None:
        query = query.filter(Article.processed_status == processed_status)
    
    articles = query.offset(skip).limit(limit).all()
    
    # 添加 feed_name 到响应
    for article in articles:
        feed = db.query(Feed).filter(Feed.id == article.feed_id).first()
        if feed:
            article.feed_name = feed.name
    
    return articles

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个文章
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")
    
    # 添加 feed_name 到响应
    feed = db.query(Feed).filter(Feed.id == article.feed_id).first()
    if feed:
        article.feed_name = feed.name
    
    return article

@router.post("/", response_model=ArticleResponse, status_code=201)
async def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db)
):
    """
    创建新文章
    """
    # 检查 feed 是否存在
    feed = db.query(Feed).filter(Feed.id == article_data.feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="订阅源未找到")
    
    # 检查 URL 是否已存在
    existing = db.query(Article).filter(Article.url == article_data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="该 URL 已存在")
    
    article = Article(**article_data.model_dump())
    db.add(article)
    db.commit()
    db.refresh(article)
    
    # 更新订阅源的文章计数
    feed.article_count = db.query(Article).filter(Article.feed_id == feed.id).count()
    db.commit()
    
    # 添加 feed_name 到响应
    article.feed_name = feed.name
    
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db)
):
    """
    更新文章
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")
    
    for key, value in article_data.model_dump(exclude_unset=True).items():
        setattr(article, key, value)
    
    db.commit()
    db.refresh(article)
    
    # 添加 feed_name 到响应
    feed = db.query(Feed).filter(Feed.id == article.feed_id).first()
    if feed:
        article.feed_name = feed.name
    
    return article

@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    删除文章
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")
    
    # 更新订阅源的文章计数
    feed = db.query(Feed).filter(Feed.id == article.feed_id).first()
    
    db.delete(article)
    db.commit()
    
    if feed:
        feed.article_count = db.query(Article).filter(Article.feed_id == feed.id).count()
        db.commit()

@router.post("/{article_id}/mark-read", response_model=ArticleResponse)
async def mark_article_read(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    标记文章为已读
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")
    
    article.read_status = True
    db.commit()
    db.refresh(article)
    
    # 添加 feed_name 到响应
    feed = db.query(Feed).filter(Feed.id == article.feed_id).first()
    if feed:
        article.feed_name = feed.name
    
    return article

@router.post("/{article_id}/mark-unread", response_model=ArticleResponse)
async def mark_article_unread(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    标记文章为未读
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")
    
    article.read_status = False
    db.commit()
    db.refresh(article)
    
    # 添加 feed_name 到响应
    feed = db.query(Feed).filter(Feed.id == article.feed_id).first()
    if feed:
        article.feed_name = feed.name
    
    return article

@router.get("/stats/summary")
async def get_article_stats(
    db: Session = Depends(get_db)
):
    """
    获取文章统计摘要
    """
    total = db.query(Article).count()
    unread = db.query(Article).filter(Article.read_status == False).count()
    processed = db.query(Article).filter(Article.processed_status == True).count()
    
    return {
        "total": total,
        "unread": unread,
        "read": total - unread,
        "processed": processed,
        "unprocessed": total - processed
    }