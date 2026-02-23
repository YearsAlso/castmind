# 项目结构

## 目录结构

```
castmind/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   └── v1/
│   │   │       ├── articles.py   # 文章/播客 API
│   │   │       ├── feeds.py      # 订阅源 API
│   │   │       └── system.py      # 系统 API
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   │   ├── database.py # SQLAlchemy 模型
│   │   │   └── schemas.py  # Pydantic 模式
│   │   ├── scheduler/      # 定时任务
│   │   │   ├── manager.py
│   │   │   └── tasks.py
│   │   └── services/       # 业务逻辑
│   │       ├── ai_service.py           # AI 分析
│   │       ├── feed_service.py         # 订阅服务
│   │       ├── podcast_downloader.py   # 播客下载
│   │       ├── podcast_service.py      # 播客服务
│   │       ├── rss_service.py          # RSS 解析
│   │       ├── rsshub_service.py       # RSSHub
│   │       └── transcription_service.py # 转录服务
│   └── main.py             # 入口文件
├── frontend/               # React + TypeScript 前端
│   └── src/
│       ├── pages/          # 页面组件
│       │   ├── Dashboard.tsx
│       │   ├── Feeds.tsx
│       │   ├── Articles.tsx
│       │   ├── Excerpts.tsx
│       │   ├── Podcasts.tsx
│       │   └── System.tsx
│       └── App.tsx
├── data/                  # 数据存储
├── docs/                  # 文档
└── tests/                 # 测试
```

## 技术栈

- **后端**: FastAPI, SQLAlchemy, APScheduler
- **前端**: React, TypeScript, TailwindCSS, TanStack Query
- **数据库**: SQLite
- **AI**: OpenAI, DeepSeek
