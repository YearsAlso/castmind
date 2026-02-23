# API 端点文档

## 订阅源 API

### GET /api/v1/feeds/
获取所有订阅源

### POST /api/v1/feeds/
创建订阅源
```json
{
  "name": "string",
  "url": "string",
  "category": "技术",
  "interval": 3600
}
```

### PUT /api/v1/feeds/{id}
更新订阅源

### DELETE /api/v1/feeds/{id}
删除订阅源

### POST /api/v1/feeds/{id}/fetch
手动抓取订阅源

---

## 文章 API

### GET /api/v1/articles/
获取文章列表
- `?feed_id=` 筛选订阅源
- `?status=` 筛选状态
- `?limit=` 数量限制

### GET /api/v1/articles/{id}
获取文章详情

### POST /api/v1/articles/{id}/analyze
分析文章

---

## 播客 API

### GET /api/v1/articles/podcasts
获取播客列表

### POST /api/v1/articles/{id}/download-audio
下载播客音频

### POST /api/v1/articles/{id}/transcribe
转录音频

### POST /api/v1/articles/{id}/analyze-transcript
分析转录文本

### POST /api/v1/articles/{id}/full-podcast-full-pipeline
完整流程：下载+转录+分析

---

## 系统 API

### GET /api/v1/system/health
健康检查

### GET /api/v1/system/stats
统计数据
