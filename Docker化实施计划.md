# 🐳 CastMind Docker 化实施计划

## 🎯 目标
将当前的单机 Python 脚本系统改造为可 Docker 化部署的生产级服务

## 📋 当前状态 vs 目标状态

### 当前状态（单机脚本）
```
架构: 单机 Python 脚本
执行: 手动命令行执行
存储: 本地文件系统
调度: 无自动化
API: 无
监控: 文件日志
部署: 手动复制文件
```

### 目标状态（Docker 容器）
```
架构: 微服务容器
执行: 自动化任务调度
存储: 持久化卷 + 可选对象存储
调度: Celery + Redis
API: FastAPI RESTful 服务
监控: Prometheus + Grafana
部署: Docker Compose / Kubernetes
```

## 🚀 实施步骤

### 阶段1: 基础容器化（1-2天）

#### 1.1 创建 Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 castmind && \
    chown -R castmind:castmind /app
USER castmind

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 1.2 创建 docker-compose.yml
```yaml
# docker-compose.yml
version: '3.8'

services:
  # CastMind 主服务
  castmind:
    build: .
    container_name: castmind
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - castmind_data:/app/data
      - castmind_logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL:-https://api.deepseek.com}
      - DEFAULT_AI_MODEL=${DEFAULT_AI_MODEL:-deepseek-chat}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///data/castmind.db}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    depends_on:
      - redis
    networks:
      - castmind_network

  # Redis 服务（任务队列）
  redis:
    image: redis:7-alpine
    container_name: castmind-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - castmind_network

  # Celery Worker（可选）
  celery-worker:
    build: .
    container_name: castmind-celery-worker
    restart: unless-stopped
    command: celery -A app.tasks worker --loglevel=info
    volumes:
      - castmind_data:/app/data
      - castmind_logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
      - castmind
    networks:
      - castmind_network

  # Celery Beat（定时任务，可选）
  celery-beat:
    build: .
    container_name: castmind-celery-beat
    restart: unless-stopped
    command: celery -A app.tasks beat --loglevel=info
    volumes:
      - castmind_data:/app/data
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - castmind_network

volumes:
  castmind_data:
  castmind_logs:
  redis_data:

networks:
  castmind_network:
    driver: bridge
```

#### 1.3 创建环境配置模板
```bash
# .env.template
# API 配置
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com
DEFAULT_AI_MODEL=deepseek-chat

# 数据库配置
DATABASE_URL=sqlite:///data/castmind.db
# 可选 PostgreSQL: postgresql://user:password@postgres:5432/castmind

# Redis 配置
REDIS_URL=redis://redis:6379/0

# 应用配置
LOG_LEVEL=INFO
DEBUG=false
HOST=0.0.0.0
PORT=8000

# 任务配置
PROCESS_BATCH_SIZE=5
MAX_RETRIES=3
RETRY_DELAY=60

# 存储配置
DATA_DIR=/app/data
LOGS_DIR=/app/logs
UPLOAD_DIR=/app/data/uploads
```

### 阶段2: 服务化改造（2-3天）

#### 2.1 创建 FastAPI 应用结构
```
app/
├── __init__.py
├── main.py              # FastAPI 应用入口
├── config.py           # 配置管理
├── database.py         # 数据库连接
├── models.py           # 数据模型
├── schemas.py          # Pydantic 模式
├── crud.py             # 数据库操作
├── api/               # API 路由
│   ├── __init__.py
│   ├── v1/            # API v1
│   │   ├── __init__.py
│   │   ├── podcasts.py
│   │   ├── tasks.py
│   │   └── health.py
├── services/          # 业务逻辑
│   ├── __init__.py
│   ├── podcast_service.py
│   ├── ai_service.py
│   └── file_service.py
├── tasks.py           # Celery 任务
└── utils/            # 工具函数
    ├── __init__.py
    ├── rss_parser.py
    └── logger.py
```

#### 2.2 实现基础 API
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import podcasts, tasks, health
from app.config import settings

app = FastAPI(
    title="CastMind API",
    description="播客智能处理系统",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(podcasts.router, prefix="/api/v1", tags=["podcasts"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 初始化数据库
    # 创建必要目录
    # 启动定时任务
    pass
```

#### 2.3 实现健康检查端点
```python
# app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "castmind",
            "version": "1.0.0",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }, 503
```

### 阶段3: 任务调度系统（2-3天）

#### 3.1 创建 Celery 任务
```python
# app/tasks.py
from celery import Celery
from app.config import settings
from app.services.podcast_service import PodcastService

# 创建 Celery 应用
celery_app = Celery(
    "castmind",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# 配置 Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=25 * 60,
)

@celery_app.task(bind=True, max_retries=3)
def process_podcast_task(self, podcast_id: int, limit: int = 1):
    """处理播客任务"""
    try:
        service = PodcastService()
        result = service.process_podcast(podcast_id, limit)
        return {"status": "success", "result": result}
    except Exception as e:
        # 重试逻辑
        self.retry(exc=e, countdown=60)

@celery_app.task
def process_all_podcasts_task(limit: int = 1):
    """处理所有播客任务"""
    service = PodcastService()
    results = service.process_all_podcasts(limit)
    return {"status": "success", "results": results}

# 定时任务配置
celery_app.conf.beat_schedule = {
    "process-daily-podcasts": {
        "task": "app.tasks.process_all_podcasts_task",
        "schedule": 3600.0,  # 每小时执行一次
        "args": (1,),  # 每次处理1期
    },
}
```

### 阶段4: 监控和运维（1-2天）

#### 4.1 添加 Prometheus 指标
```python
# app/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time
from fastapi import Request, Response
from fastapi.routing import APIRoute

# 定义指标
REQUEST_COUNT = Counter(
    "castmind_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "castmind_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)

ACTIVE_TASKS = Gauge(
    "castmind_active_tasks",
    "Number of active tasks"
)

PODCASTS_PROCESSED = Counter(
    "castmind_podcasts_processed_total",
    "Total number of podcasts processed"
)

class MonitoringRoute(APIRoute):
    """监控路由中间件"""
    
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request):
            start_time = time.time()
            
            try:
                response = await original_route_handler(request)
                status_code = response.status_code
            except Exception:
                status_code = 500
                raise
            finally:
                latency = time.time() - start_time
                
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=status_code
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=request.method,
                    endpoint=request.url.path
                ).observe(latency)
            
            return response
        
        return custom_route_handler
```

#### 4.2 创建监控 docker-compose
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: castmind-prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - castmind_network

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: castmind-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    networks:
      - castmind_network

volumes:
  prometheus_data:
  grafana_data:

networks:
  castmind_network:
    external: true
```

### 阶段5: 部署和文档（1天）

#### 5.1 创建部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 开始部署 CastMind..."

# 检查环境变量
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 文件"
    echo "请复制 .env.template 并配置环境变量"
    exit 1
fi

# 构建镜像
echo "📦 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查健康状态
echo "🏥 检查健康状态..."
curl -f http://localhost:8000/api/v1/health || echo "❌ 健康检查失败"

echo "✅ 部署完成！"
echo ""
echo "📊 访问地址:"
echo "   CastMind API: http://localhost:8000/docs"
echo "   Grafana: http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "📝 查看日志:"
echo "   docker-compose logs -f castmind"
```

#### 5.2 创建使用文档
```markdown
# 📚 CastMind Docker 部署指南

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd castmind
```

### 2. 配置环境变量
```bash
cp .env.template .env
# 编辑 .env 文件，配置你的 API Key
```

### 3. 启动服务
```bash
./deploy.sh
```

### 4. 访问服务
- API 文档: http://localhost:8000/docs
- 监控面板: http://localhost:3000
- 指标: http://localhost:9090

## API 使用示例

### 添加播客
```bash
curl -X POST "http://localhost:8000/api/v1/podcasts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "知行小酒馆",
    "rss_url": "https://rsshub.rssforever.com/xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216",
    "category": "投资理财"
  }'
```

### 处理播客
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/process" \
  -H "Content-Type: application/json" \
  -d '{
    "podcast_id": 1,
    "limit": 1
  }'
```

## 监控和运维

### 查看日志
```bash
# 查看所有日志
docker-compose logs

# 实时查看 CastMind 日志
docker-compose logs -f castmind

# 查看 Celery 任务日志
docker-compose logs -f celery-worker
```

### 备份数据
```bash
# 备份数据库
docker exec castmind sqlite3 /app/data/castmind.db .dump > backup.sql

# 备份文件
tar -czf castmind_backup_$(date +%Y%m%d).tar.gz data/ logs/
```

### 更新服务
```bash
# 拉取最新代码
git pull

# 重新构建和部署
docker-compose down
docker-compose build
docker-compose up -d
```

## 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细错误信息
docker-compose logs castmind

# 检查端口占用
netstat -tulpn | grep :8000
```

#### 2. 数据库连接问题
```bash
# 检查数据库文件权限
ls -la data/

# 重建数据库
docker-compose exec castmind python -c "from app.database import init_db;