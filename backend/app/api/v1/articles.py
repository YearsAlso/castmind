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
    db: Session = Depends(get_db),
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
async def get_article(article_id: int, db: Session = Depends(get_db)):
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
async def create_article(article_data: ArticleCreate, db: Session = Depends(get_db)):
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
    article_id: int, article_data: ArticleUpdate, db: Session = Depends(get_db)
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
async def delete_article(article_id: int, db: Session = Depends(get_db)):
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
        feed.article_count = (
            db.query(Article).filter(Article.feed_id == feed.id).count()
        )
        db.commit()


@router.post("/{article_id}/mark-read", response_model=ArticleResponse)
async def mark_article_read(article_id: int, db: Session = Depends(get_db)):
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
async def mark_article_unread(article_id: int, db: Session = Depends(get_db)):
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
async def get_article_stats(db: Session = Depends(get_db)):
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
        "unprocessed": total - processed,
    }


@router.post("/{article_id}/analyze-podcast")
async def analyze_podcast(
    article_id: int,
    generate_summary: bool = True,
    extract_chapters: bool = True,
    db: Session = Depends(get_db),
):
    """
    分析播客内容并生成摘要
    """
    from datetime import datetime
    from app.services.podcast_service import podcast_analysis_service

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")

    # 检查是否为播客
    if not article.is_podcast and not article.audio_url:
        return {
            "status": "info",
            "message": "该文章不是播客内容",
            "article_id": article_id,
        }

    try:
        # 执行播客分析
        result = podcast_analysis_service.analyze_podcast(
            title=article.title,
            description=article.podcast_description or article.content or "",
            transcript=article.transcript,
            audio_url=article.audio_url,
            audio_duration=article.audio_duration,
        )

        # 更新数据库
        if generate_summary:
            article.podcast_summary = result.get("podcast_summary", "")
            article.key_points = ", ".join(result.get("key_topics", []))

        if extract_chapters:
            import json

            article.chapters = json.dumps(
                result.get("chapters", []), ensure_ascii=False
            )

        article.action_items = result.get("action_items", "")
        article.processed_status = True

        db.commit()
        db.refresh(article)

        return {
            "status": "success",
            "message": "播客分析完成",
            "article_id": article_id,
            "data": {
                "podcast_summary": result.get("podcast_summary"),
                "key_topics": result.get("key_topics"),
                "chapters": result.get("chapters"),
                "action_items": result.get("action_items"),
                "duration_formatted": result.get("duration_formatted"),
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"播客分析失败: {str(e)}",
            "article_id": article_id,
        }


@router.get("/{article_id}/podcast-document")
async def get_podcast_document(article_id: int, db: Session = Depends(get_db)):
    """
    获取播客文档（Markdown 格式）
    """
    from datetime import datetime
    from app.services.podcast_service import podcast_analysis_service

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")

    # 生成文档
    doc = podcast_analysis_service.generate_podcast_document(
        title=article.title,
        description=article.podcast_description or "",
        podcast_summary=article.podcast_summary or article.summary or "",
        key_topics=article.key_points.split(", ") if article.key_points else [],
        chapters=eval(article.chapters) if article.chapters else [],
        action_items=article.action_items or "",
        audio_duration=article.audio_duration,
    )

    return {
        "article_id": article_id,
        "title": article.title,
        "document": doc,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/podcasts")
async def list_podcasts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    获取播客列表
    """
    podcasts = (
        db.query(Article)
        .filter(Article.is_podcast == True)
        .order_by(Article.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": db.query(Article).filter(Article.is_podcast == True).count(),
        "podcasts": podcasts,
    }


# ============ 播客下载、转录、分析 API ============


@router.post("/{article_id}/download-audio")
async def download_podcast_audio(article_id: int, db: Session = Depends(get_db)):
    """
    下载播客音频到本地
    """
    from datetime import datetime
    from app.services.podcast_downloader import podcast_downloader

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")

    if not article.audio_url:
        return {
            "status": "error",
            "message": "该文章没有音频 URL",
            "article_id": article_id,
        }

    try:
        # 更新状态
        article.transcription_status = "running"
        db.commit()

        # 下载音频
        result = await podcast_downloader.download_audio(article.audio_url, article_id)

        if result["success"]:
            article.audio_local_path = result["local_path"]
            article.audio_size = result.get("size")
            article.transcription_status = "completed"
            db.commit()

            return {
                "status": "success",
                "message": "音频下载成功",
                "article_id": article_id,
                "data": {
                    "local_path": result["local_path"],
                    "size": result.get("size"),
                    "skipped": result.get("skipped", False),
                },
                "timestamp": datetime.now().isoformat(),
            }
        else:
            article.transcription_status = "failed"
            db.commit()

            return {
                "status": "error",
                "message": f"下载失败: {result.get('error')}",
                "article_id": article_id,
            }

    except Exception as e:
        article.transcription_status = "failed"
        db.commit()
        return {"status": "error", "message": str(e), "article_id": article_id}


@router.post("/{article_id}/transcribe")
async def transcribe_podcast(
    article_id: int, language: Optional[str] = None, db: Session = Depends(get_db)
):
    """
    转录音频为文字
    """
    from datetime import datetime
    from app.services.podcast_downloader import podcast_downloader
    from app.services.transcription_service import transcription_service

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")

    if not article.audio_url and not article.audio_local_path:
        return {
            "status": "error",
            "message": "该文章没有音频",
            "article_id": article_id,
        }

    try:
        # 更新状态
        article.transcription_status = "running"
        db.commit()

        # 确定音频路径
        audio_path = article.audio_local_path
        audio_url = article.audio_url

        if not audio_path and audio_url:
            # 需要先下载
            download_result = await podcast_downloader.download_audio(
                audio_url, article_id
            )
            if not download_result["success"]:
                article.transcription_status = "failed"
                db.commit()
                return {
                    "status": "error",
                    "message": f"下载失败: {download_result.get('error')}",
                    "article_id": article_id,
                }
            audio_path = download_result["local_path"]
            article.audio_local_path = audio_path
            article.audio_size = download_result.get("size")

        # 转录音频
        result = await transcription_service.transcribe_audio(audio_path, language)

        if result["success"]:
            article.transcript = result["text"]
            article.transcription_status = "completed"
            db.commit()

            return {
                "status": "success",
                "message": "转录成功",
                "article_id": article_id,
                "data": {
                    "text_length": len(result["text"]),
                    "language": result.get("language"),
                    "provider": result.get("provider"),
                },
                "timestamp": datetime.now().isoformat(),
            }
        else:
            article.transcription_status = "failed"
            db.commit()

            return {
                "status": "error",
                "message": f"转录失败: {result.get('error')}",
                "article_id": article_id,
            }

    except Exception as e:
        article.transcription_status = "failed"
        db.commit()
        return {"status": "error", "message": str(e), "article_id": article_id}


@router.post("/{article_id}/analyze-transcript")
async def analyze_podcast_transcript(article_id: int, db: Session = Depends(get_db)):
    """
    分析播客转录内容（使用 LLM）
    """
    from datetime import datetime
    from app.services.ai_service import ai_service

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")

    if not article.transcript:
        return {
            "status": "error",
            "message": "该文章没有转录文本，请先执行转录",
            "article_id": article_id,
        }

    try:
        # 更新状态
        article.analysis_status = "running"
        db.commit()

        # 使用 AI 分析
        result = ai_service.analyze_podcast_transcript(
            transcript=article.transcript,
            title=article.title,
            audio_duration=article.audio_duration,
        )

        if result.get("success", True):
            # 更新数据库
            import json

            article.podcast_summary = result.get("podcast_summary", "")
            article.key_points = ", ".join(result.get("key_topics", []))
            article.chapters = json.dumps(
                result.get("chapters", []), ensure_ascii=False
            )
            article.action_items = "; ".join(result.get("action_items", []))
            article.analysis_status = "completed"
            article.processed_status = True
            db.commit()

            return {
                "status": "success",
                "message": "分析完成",
                "article_id": article_id,
                "data": {
                    "podcast_summary": result.get("podcast_summary"),
                    "key_topics": result.get("key_topics"),
                    "chapters": result.get("chapters"),
                    "action_items": result.get("action_items"),
                    "provider": result.get("provider"),
                },
                "timestamp": datetime.now().isoformat(),
            }
        else:
            article.analysis_status = "failed"
            db.commit()

            return {
                "status": "error",
                "message": f"分析失败: {result.get('error')}",
                "article_id": article_id,
            }

    except Exception as e:
        article.transcription_status = "failed"
        db.commit()
        return {"status": "error", "message": str(e), "article_id": article_id}


@router.post("/{article_id}/transcript/manual")
async def set_manual_transcript(
    article_id: int, transcript: str, db: Session = Depends(get_db)
):
    """
    手动输入转录文本
    """
    from datetime import datetime

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")

    try:
        article.transcript = transcript
        article.transcription_status = "completed"
        db.commit()

        return {
            "status": "success",
            "message": "转录文本保存成功",
            "article_id": article_id,
            "text_length": len(transcript),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "article_id": article_id}


@router.get("/transcription-providers")
async def get_transcription_providers():
    """
    获取可用的转录提供商
    """
    from app.services.transcription_service import transcription_service

    return transcription_service.check_provider_status()


@router.post("/{article_id}/full-pipeline")
async def full_podcast_pipeline(
    article_id: int, language: Optional[str] = None, db: Session = Depends(get_db)
):
    """
    完整流程：下载 + 转录 + 分析
    """
    from datetime import datetime

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章未找到")

    if not article.audio_url:
        return {
            "status": "error",
            "message": "该文章没有音频 URL",
            "article_id": article_id,
        }

    results = {"download": None, "transcribe": None, "analyze": None}

    try:
        # 步骤 1: 下载
        download_response = await download_podcast_audio(article_id, db)
        results["download"] = download_response

        if download_response.get("status") != "success":
            return {
                "status": "error",
                "message": "下载失败，终止流程",
                "article_id": article_id,
                "results": results,
            }

        # 步骤 2: 转录
        transcribe_response = await transcribe_podcast(article_id, language, db)
        results["transcribe"] = transcribe_response

        if transcribe_response.get("status") != "success":
            return {
                "status": "error",
                "message": "转录失败，终止流程",
                "article_id": article_id,
                "results": results,
            }

        # 步骤 3: 分析
        analyze_response = await analyze_podcast_transcript(article_id, db)
        results["analyze"] = analyze_response

        return {
            "status": "success"
            if analyze_response.get("status") == "success"
            else "partial",
            "message": "处理完成",
            "article_id": article_id,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "article_id": article_id,
            "results": results,
        }
