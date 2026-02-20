# 🎯 CastMind 核心需求文档提示词

## 📋 项目概述

**项目名称**: CastMind - 智能播客订阅处理平台  
**项目类型**: 后端服务 (FastAPI + SQLite + 定时任务)  
**核心功能**: 播客订阅管理、内容抓取、AI分析、定时处理

## 🏗️ 系统架构

### 技术栈
- **后端框架**: FastAPI (Python 3.8+)
- **数据库**: SQLite (SQLAlchemy ORM)
- **定时任务**: schedule + APScheduler
- **RSS解析**: feedparser
- **AI集成**: OpenAI/DeepSeek API
- **配置管理**: Pydantic Settings + 环境变量

### 目录结构
```
castmind/
├── backend/                    # 后端服务核心
│   ├── app/                   # 应用模块
│   │   ├── api/v1/           # API路由层
│   │   ├── core/             # 核心配置层
│   │   ├── models/           # 数据模型层
│   │   ├── services/         # 业务服务层
│   │   └── scheduler/        # 定时任务层
│   └── main.py              # 应用入口
├── data/                     # 数据存储
├── docs/                     # 项目文档
├── .env.example             # 环境变量示例
├── requirements.txt         # Python依赖
├── start.sh                 # 启动脚本
└── README.md                # 项目说明
```

## 🔧 核心功能需求

### 1. 订阅源管理
- **添加订阅源**: 支持 RSS/Atom URL，设置抓取间隔
- **订阅源列表**: 分页查询，按状态过滤
- **订阅源详情**: 获取详情和统计信息
- **更新订阅源**: 修改名称、分类、间隔、状态
- **删除订阅源**: 级联删除相关文章和任务
- **手动抓取**: 立即抓取订阅源内容

### 2. 文章管理
- **文章列表**: 按订阅源、阅读状态、处理状态过滤
- **文章详情**: 获取完整内容和AI分析结果
- **标记状态**: 标记为已读/已处理
- **统计信息**: 文章数量、未读数量、已处理数量

### 3. 定时任务系统
- **自动抓取**: 基于订阅源设置的智能调度
- **数据清理**: 定期清理旧数据（30天前）
- **状态更新**: 自动更新订阅源状态
- **任务监控**: 完整的任务状态跟踪

### 4. AI内容分析
- **摘要生成**: 自动生成文章摘要
- **关键词提取**: 提取核心关键词
- **情感分析**: 分析内容情感倾向
- **内容分类**: 自动分类文章主题
- **配置灵活**: 支持多种AI服务提供商

### 5. 系统管理
- **健康检查**: 数据库连接、AI服务状态
- **系统统计**: 订阅源、文章、任务统计数据
- **调度器控制**: 启动/停止定时任务
- **手动处理**: 立即处理所有订阅源
- **系统信息**: 服务器资源使用情况

## 🚀 API 接口规范

### 基础信息
- **服务地址**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs (Swagger UI)
- **健康检查**: GET /api/v1/system/health
- **系统统计**: GET /api/v1/system/stats

### 订阅源接口 (GET/POST/PUT/DELETE)
- `GET /api/v1/feeds/` - 获取订阅源列表
- `POST /api/v1/feeds/` - 创建订阅源
- `GET /api/v1/feeds/{feed_id}` - 获取订阅源详情
- `PUT /api/v1/feeds/{feed_id}` - 更新订阅源
- `DELETE /api/v1/feeds/{feed_id}` - 删除订阅源
- `POST /api/v1/feeds/{feed_id}/fetch` - 手动抓取

### 文章接口
- `GET /api/v1/articles/` - 获取文章列表
- `GET /api/v1/articles/{article_id}` - 获取文章详情
- `POST /api/v1/articles/{article_id}/read` - 标记已读
- `POST /api/v1/articles/{article_id}/process` - 标记已处理
- `GET /api/v1/articles/stats/summary` - 文章统计

### 系统接口
- `GET /api/v1/system/health` - 健康检查
- `GET /api/v1/system/stats` - 系统统计
- `GET /api/v1/system/scheduler/status` - 调度器状态
- `POST /api/v1/system/scheduler/start` - 启动调度器
- `POST /api/v1/system/scheduler/stop` - 停止调度器
- `POST /api/v1/system/process/all` - 处理所有订阅源

## ⚙️ 配置管理

### 环境变量 (.env)
```bash
# 应用配置
DEBUG=false
APP_NAME=CastMind
APP_VERSION=1.0.0

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./data/castmind.db

# AI服务配置 (可选)
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# 定时任务配置
FETCH_INTERVAL_MINUTES=10
CLEANUP_DAYS=30

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 依赖文件 (requirements.txt)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.25
feedparser==6.0.10
requests==2.31.0
schedule==1.2.0
apscheduler==3.10.4
openai==1.3.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
python-dateutil==2.8.2
psutil==5.9.8
```

## 🛠️ 开发指南

### 快速启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd castmind

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑 .env 文件配置您的设置

# 4. 启动服务
python backend/main.py
# 或使用启动脚本
./start.sh
```

### 开发命令
```bash
# 开发模式（热重载）
python backend/main.py

# 生产模式
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 数据库初始化
python -c "from backend.app.core.database import init_db; init_db()"

# 测试API
curl http://localhost:8000/api/v1/system/health
curl http://localhost:8000/api/v1/feeds/
```

### 测试数据
```bash
# 创建测试订阅源
curl -X POST http://localhost:8000/api/v1/feeds/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "技术博客示例",
    "url": "https://example.com/rss",
    "category": "技术",
    "interval": 3600
  }'

# 手动抓取
curl -X POST http://localhost:8000/api/v1/feeds/{feed_id}/fetch

# 获取统计
curl http://localhost:8000/api/v1/system/stats
```

## 📊 数据模型

### 数据库表结构
```sql
-- 订阅源表
CREATE TABLE feeds (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    category TEXT DEFAULT '技术',
    interval INTEGER DEFAULT 3600,
    last_fetch TIMESTAMP,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文章表
CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    feed_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    url TEXT NOT NULL,
    published_at TIMESTAMP,
    read_status BOOLEAN DEFAULT FALSE,
    processed_status BOOLEAN DEFAULT FALSE,
    ai_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- 任务表
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    feed_id TEXT,
    task_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    result_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE SET NULL
);
```

## 🤖 AI 助手提示词

### 给 OpenCode/Claude/Cursor 的提示：
```
你是一个全栈开发助手，需要基于以下需求开发 CastMind 项目：

项目概述：智能播客订阅处理平台，使用 FastAPI + SQLite + 定时任务架构。

核心功能：
1. 订阅源管理 - 支持 RSS/Atom URL 的增删改查和手动抓取
2. 文章管理 - 文章列表、详情、状态标记（已读/已处理）
3. 定时任务 - 自动抓取订阅源、清理旧数据、更新状态
4. AI分析 - 内容摘要、关键词提取、情感分析（支持 OpenAI/DeepSeek）
5. 系统管理 - 健康检查、统计信息、调度器控制

技术栈要求：
- 后端：FastAPI (Python 3.8+)
- 数据库：SQLite + SQLAlchemy ORM
- 定时任务：schedule + APScheduler
- RSS解析：feedparser
- 配置：Pydantic Settings + 环境变量
- API文档：自动生成 Swagger/ReDoc

项目结构：
castmind/
├── backend/app/           # 模块化应用
│   ├── api/v1/          # RESTful API 路由
│   ├── core/            # 核心配置和数据库
│   ├── models/          # 数据模型 (SQLAlchemy + Pydantic)
│   ├── services/        # 业务逻辑服务
│   └── scheduler/       # 定时任务调度
├── data/                # 数据存储
├── requirements.txt     # Python依赖
├── .env.example        # 环境变量示例
├── start.sh            # 启动脚本
└── README.md           # 项目文档

请按照这个架构实现完整的后端服务，确保：
1. 所有API接口完整可用
2. 定时任务能正常运行
3. AI分析功能可配置
4. 错误处理和日志完整
5. 配置通过环境变量管理
6. 代码有良好的类型提示和文档

启动命令：python backend/main.py 或 ./start.sh
API文档：http://localhost:8000/api/docs
```

### 给开发者的任务分解：
```
第一阶段：基础架构搭建
1. 创建项目结构和配置文件
2. 实现数据库模型和连接
3. 设置 FastAPI 应用和中间件
4. 创建基础 API 路由框架

第二阶段：核心功能实现
1. 订阅源管理 API (CRUD + 手动抓取)
2. 文章管理 API (列表、详情、状态标记)
3. RSS 解析服务实现
4. 定时任务调度器

第三阶段：高级功能
1. AI 分析服务集成
2. 系统管理和统计 API
3. 错误处理和日志系统
4. 配置管理和环境变量支持

第四阶段：优化和部署
1. 性能优化和缓存
2. 完整的 API 文档
3. 启动脚本和部署配置
4. 测试和验证
```

## 🎯 成功标准

### 功能完整性
- ✅ 所有 API 接口可正常访问
- ✅ 订阅源可以添加、抓取、管理
- ✅ 文章可以查看、标记状态
- ✅ 定时任务自动运行
- ✅ AI 分析功能可用（配置 API 密钥后）
- ✅ 系统监控和统计正常

### 代码质量
- ✅ 模块化设计，职责分离
- ✅ 完整的类型提示和文档
- ✅ 统一的错误处理
- ✅ 结构化日志输出
- ✅ 环境变量配置管理

### 可用性
- ✅ 一键启动：./start.sh
- ✅ 自动 API 文档：/api/docs
- ✅ 健康检查端点：/api/v1/system/health
- ✅ 完整的 README 文档
- ✅ 示例配置和环境文件

## 🔗 相关资源

### 技术文档
- FastAPI 官方文档: https://fastapi.tiangolo.com/
- SQLAlchemy 文档: https://docs.sqlalchemy.org/
- feedparser 文档: https://feedparser.readthedocs.io/
- schedule 文档: https://schedule.readthedocs.io/

### 开发工具
- API 测试: Postman, Insomnia, httpie
- 数据库管理: DB Browser for SQLite, DBeaver
- 代码质量: black, isort, mypy, pylint
- 监控工具: Prometheus, Grafana (可选)

### 部署选项
- **本地开发**: Python 虚拟环境
- **Docker**: 容器化部署
- **云服务**: AWS, Azure, Google Cloud, 阿里云
- **Serverless**: Vercel, AWS Lambda (需要适配)

---

**🎯 提示词使用说明：**

将此文档提供给 AI 编码助手（如 OpenCode、Claude、Cursor 等），助手应该能够：
1. 理解完整的项目需求和技术架构
2. 按照模块化设计实现所有功能
3. 生成可运行的生产就绪代码
4. 提供完整的配置和部署指南
5. 确保代码质量和最佳实践

**项目状态检查清单：**
- [ ] 项目结构完整
- [ ] 所有依赖已安装
- [ ] 环境变量配置正确
- [ ] 数据库初始化完成
- [ ] API 接口可访问
- [ ] 定时任务正常运行
- [ ] AI 分析功能可用
- [ ] 文档完整可用

**遇到问题时的解决步骤：**
1. 检查依赖安装：`pip install -r requirements.txt`
2. 检查环境变量：确保 .env 文件配置正确
3. 检查数据库：确保 data/ 目录有写入权限
4. 查看日志：检查 data/logs/castmind.log
5. 测试 API：使用 curl 或 Postman 测试接口
6. 查看文档：访问 /api/docs 查看 API 文档

**现在可以开始开发或运行项目！** 🚀