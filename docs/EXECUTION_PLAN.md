# CastMind 执行计划文档

## 📋 项目概述

**项目名称**: CastMind - 智能播客订阅处理平台  
**项目类型**: 全栈应用 (FastAPI + React + SQLite)  
**核心功能**: 播客订阅管理、内容抓取、音频转录、AI分析、定时处理

---

## 🎯 阶段一：基础架构完善

### 1.1 数据库模型扩展

**任务表 (Task)**
```python
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("feeds.id", ondelete="SET NULL"))
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="SET NULL"))
    task_type = Column(String(50))  # fetch, transcription, analysis, cleanup
    status = Column(String(20))  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    result_data = Column(Text)  # JSON 存储结果
    created_at = Column(DateTime, server_default=func.now())
```

**Feed 表扩展**
- 添加 `author` 字段（播客主持人）
- 添加 `image_url` 字段（播客封面图）

**Article 表扩展**
- 添加 `author` 字段（文章作者）

### 1.2 环境配置完善

创建 `.env` 文件模板：
```bash
# AI 服务配置
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
AI_MODEL=gpt-3.5-turbo

# Whisper 转录配置
WHISPER_MODEL=base  # base, small, medium, large
WHISPER_API=openai  # openai, local

# 安全配置
SECRET_KEY=your-secret-key
```

### 1.3 依赖更新

更新 `requirements.txt`：
```txt
# 新增依赖
openai>=1.3.0
whisper>=20231117
aiohttp>=3.9.0
python-dotenv>=1.0.0
```

---

## 🎯 阶段二：播客核心功能

### 2.1 播客下载服务

创建 `app/services/podcast_downloader.py`：

```python
class PodcastDownloader:
    """播客音频下载服务"""
    
    def __init__(self):
        self.download_dir = Path("data/podcasts")
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_audio(self, audio_url: str, article_id: int) -> str:
        """下载播客音频文件"""
        # 实现逻辑：
        # 1. 发送 HTTP 请求下载音频
        # 2. 保存到 data/podcasts/{article_id}.{ext}
        # 3. 返回本地文件路径
    
    def get_audio_path(self, article_id: int, extension: str) -> Path:
        """获取音频文件路径"""
```

### 2.2 音频转录服务

创建 `app/services/transcription_service.py`：

```python
class TranscriptionService:
    """音频转录服务"""
    
    def __init__(self):
        self.model = os.getenv("WHISPER_MODEL", "base")
        self.provider = os.getenv("WHISPER_API", "openai")
    
    async def transcribe_audio(self, audio_path: str, article_id: int) -> str:
        """转录音频为文字"""
        # 实现逻辑：
        # 1. 检查音频文件是否存在
        # 2. 根据 provider 选择转录方式：
        #    - OpenAI Whisper API
        #    - 本地 Whisper 模型
        # 3. 保存转录文本到数据库
        # 4. 返回转录内容
    
    async def transcribe_from_url(self, audio_url: str, article_id: int) -> str:
        """从 URL 直接转录（流式处理）"""
```

**支持两种模式：**
- **API 模式**: 使用 OpenAI Whisper API（需要 API Key）
- **本地模式**: 使用本地 Whisper 模型（需要安装 whisper）

### 2.3 AI 分析服务增强

更新 `app/services/ai_service.py`：

```python
class AIService:
    """AI 分析服务"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.model = os.getenv("AI_MODEL", "gpt-3.5-turbo")
    
    def analyze_podcast_transcript(
        self, 
        transcript: str, 
        title: str,
        audio_duration: int = None
    ) -> Dict:
        """分析播客转录内容"""
        # 实现逻辑：
        # 1. 调用 LLM (GPT-3.5/GPT-4/DeepSeek)
        # 2. 生成结构化分析：
        #    - 播客摘要
        #    - 关键要点
        #    - 章节划分
        #    - 行动建议
        # 3. 返回分析结果
    
    def generate_podcast_summary(self, transcript: str) -> str:
        """生成播客摘要"""
    
    def extract_chapters(self, transcript: str) -> List[Dict]:
        """提取章节信息"""
    
    def extract_action_items(self, transcript: str) -> List[str]:
        """提取行动项"""
```

### 2.4 定时任务扩展

更新 `app/scheduler/tasks.py`：

```python
class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        # ... 现有初始化
    
    def transcribe_pending_podcasts(self, limit: int = 10) -> dict:
        """转录待处理的播客"""
        # 逻辑：
        # 1. 查询 is_podcast=True 且 transcript 为空的文章
        # 2. 依次下载音频并转录
        # 3. 更新数据库
    
    def analyze_pending_transcripts(self, limit: int = 10) -> dict:
        """分析待处理的转录"""
        # 逻辑：
        # 1. 查询有 transcript 且未 AI 分析的文章
        # 2. 调用 AI 服务分析
        # 3. 更新分析结果
```

---

## 🎯 阶段三：API 接口扩展

### 3.1 播客相关接口

更新 `app/api/v1/articles.py`：

```python
@router.post("/{article_id}/download-audio")
async def download_podcast_audio(article_id: int, db: Session = Depends(get_db)):
    """下载播客音频"""
    # 1. 获取文章音频 URL
    # 2. 调用下载服务
    # 3. 返回下载状态

@router.post("/{article_id}/transcribe")
async def transcribe_podcast(article_id: int, db: Session = Depends(get_db)):
    """转录播客音频"""
    # 1. 检查音频文件是否存在
    # 2. 调用转录服务
    # 3. 保存转录文本
    # 4. 返回转录结果

@router.post("/{article_id}/analyze-transcript")
async def analyze_podcast_transcript(article_id: int, db: Session = Depends(get_db)):
    """分析播客转录内容"""
    # 1. 获取转录文本
    # 2. 调用 AI 分析服务
    # 3. 保存分析结果
    # 4. 返回分析结果

@router.post("/{article_id}/full-pipeline")
async def full_podcast_pipeline(article_id: int, db: Session = Depends(get_db)):
    """完整流程：下载+转录+分析"""
    # 依次调用下载、转录、分析
    # 返回完整结果
```

### 3.2 任务管理接口

```python
@router.get("/tasks")
async def list_tasks(
    status: str = None,
    task_type: str = None,
    skip: int = 0,
    limit: int = 20
):
    """获取任务列表"""

@router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    """获取任务详情"""

@router.post("/tasks/{task_id}/retry")
async def retry_task(task_id: int):
    """重试失败的任务"""
```

---

## 🎯 阶段四：前端功能

### 4.1 播客列表页面

创建或更新 `pages/Podcasts.tsx`：
- 显示所有播客文章
- 显示转录状态（未转录、转录中、已完成）
- 显示 AI 分析状态
- 播放按钮（跳转到音频 URL）
- 一键转录按钮
- 一键分析按钮

### 4.2 播客详情页面

更新 `pages/Excerpts.tsx`：
- 播客卡片显示更多信息：
  - 音频时长
  - 转录状态
  - 分析状态
- 操作按钮：
  - 下载音频
  - 转录音频
  - AI 分析
  - 查看完整转录

### 4.3 仪表板增强

更新 `pages/Dashboard.tsx`：
- 添加播客统计卡片
- 显示待处理任务数量

### 4.4 系统设置页面

更新 `pages/System.tsx`：
- AI 服务配置（API Key、模型选择）
- 转录服务配置（Whisper 模式选择）
- 任务队列状态

---

## 🎯 阶段五：系统优化

### 5.1 错误处理和重试机制

```python
class TaskRetryMixin:
    """任务重试混合类"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 60  # 秒
    
    def execute_with_retry(self, func, *args, **kwargs):
        """带重试的执行"""
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise
                time.sleep(self.RETRY_DELAY)
```

### 5.2 任务队列优化

- 使用 Redis 作为任务队列（可选）
- 实现任务优先级
- 任务超时处理

### 5.3 监控和日志

```python
# 任务事件记录
class TaskEventLogger:
    """任务事件记录器"""
    
    def log_task_start(self, task_id: int, task_type: str):
        """记录任务开始"""
    
    def log_task_complete(self, task_id: int, result: dict):
        """记录任务完成"""
    
    def log_task_error(self, task_id: int, error: str):
        """记录任务错误"""
```

---

## 📅 执行顺序

| 阶段 | 优先级 | 任务 | 预计工作量 |
|------|--------|------|------------|
| 1 | P0 | 数据库模型扩展（Task表、作者字段） | 0.5天 |
| 1 | P0 | 环境配置完善（.env、依赖） | 0.5天 |
| 2 | P1 | 播客下载服务 | 1天 |
| 2 | P1 | 音频转录服务 | 2天 |
| 2 | P1 | AI分析服务增强 | 1天 |
| 3 | P1 | API接口扩展 | 1天 |
| 4 | P2 | 前端播客功能 | 2天 |
| 5 | P3 | 错误处理和优化 | 1天 |

**总计预计：9天**

---

## 🔧 技术栈确认

| 功能 | 技术方案 |
|------|----------|
| 后端框架 | FastAPI |
| 数据库 | SQLite + SQLAlchemy |
| 定时任务 | APScheduler |
| RSS解析 | feedparser |
| 音频下载 | aiohttp |
| 音频转录 | OpenAI Whisper API / 本地 Whisper |
| AI分析 | OpenAI GPT API / DeepSeek API |
| 前端 | React + Tailwind CSS |
| 状态管理 | React Query |

---

## 📝 注意事项

1. **API 密钥安全**：所有 API 密钥存储在环境变量中，不提交到 Git
2. **大文件处理**：音频文件可能很大，需要流式处理和进度显示
3. **转录时间**：长音频转录可能需要较长时间，考虑异步处理
4. **成本控制**：OpenAI API 按调用收费，需要实现缓存和限制
5. **错误恢复**：网络中断等情况下需要支持断点续传

---

*文档版本: v1.0*  
*最后更新: 2026-02-22*
