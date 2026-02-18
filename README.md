# 🧠🌊 CastMind - 播客智能流系统

![CastMind](https://img.shields.io/badge/CastMind-播客智能流-4F46E5)
![AI智能](https://img.shields.badge/🧠-AI深度分析-F59E0B)
![流畅处理](https://img.shields.io/badge/🌊-流畅工作流-06B6D4)
![知识沉淀](https://img.shields.io/badge/📚-知识沉淀-10B981)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB)
![License](https://img.shields.io/badge/License-MIT-green)

> **智能流动，智慧沉淀** - 自动化播客处理、AI深度分析、知识库集成

## 🎯 核心功能

### 🧠 智能分析层
- **多AI模型路由** - DeepSeek、Kimi、OpenAI等智能选择
- **深度内容理解** - 商业洞察、关键点提取、情感分析
- **成本优化** - 智能预算控制和模型选择

### 🌊 流畅工作流
- **自动化处理** - RSS订阅、音频下载、文字转录、AI总结
- **智能调度** - 定时任务、优先级管理、错误恢复
- **状态监控** - 实时进度、性能指标、健康检查

### 📚 知识沉淀
- **结构化存储** - Markdown笔记、知识图谱、标签系统
- **智能检索** - 语义搜索、相关推荐、知识关联
- **持续学习** - 用户反馈、模型优化、知识更新

## 🚀 快速开始

### 环境要求
- Python 3.9+
- OpenAI API密钥（或其他AI服务密钥）
- Git

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/YearsAlso/castmind.git
cd castmind

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥

# 运行测试
python -m pytest tests/ -v
```

### 基础使用
```bash
# 启动CastMind系统
python castmind.py start

# 添加播客订阅
python castmind.py subscribe --name "商业思维" --url "https://example.com/rss"

# 手动处理播客
python castmind.py process --name "商业思维" --limit 3

# 查看系统状态
python castmind.py status
```

## 📁 项目架构

```
castmind/
├── castmind.py              # 主入口点
├── src/                     # 源代码
│   ├── core/               # 核心模块
│   │   ├── config.py       # 配置管理
│   │   ├── scheduler.py    # 任务调度
│   │   └── monitor.py      # 状态监控
│   ├── intelligence/       # 智能层
│   │   ├── ai_router.py    # AI模型路由
│   │   ├── analyzer.py     # 内容分析
│   │   └── optimizer.py    # 成本优化
│   ├── workflow/           # 工作流层
│   │   ├── rss_parser.py   # RSS解析
│   │   ├── audio_processor.py  # 音频处理
│   │   └── note_generator.py   # 笔记生成
│   └── knowledge/          # 知识层
│       ├── storage.py      # 知识存储
│       ├── search.py       # 智能检索
│       └── graph.py        # 知识图谱
├── config/                  # 配置文件
│   ├── .env.example        # 环境变量模板
│   ├── ai_models.json      # AI模型配置
│   └── workflows.json      # 工作流配置
├── data/                   # 数据文件
│   ├── podcasts/           # 播客数据
│   ├── transcripts/        # 转录文本
│   └── knowledge/          # 知识库
├── docs/                   # 文档
│   ├── architecture.md     # 架构设计
│   ├── api/               # API文档
│   └── guides/            # 使用指南
└── tests/                  # 测试
    ├── unit/              # 单元测试
    └── integration/       # 集成测试
```

## ⚙️ 配置说明

### 环境变量 (.env)
```bash
# AI服务配置
OPENAI_API_KEY=sk-your-openai-key
DEEPSEEK_API_KEY=your-deepseek-key
KIMI_API_KEY=your-kimi-key

# 系统配置
CASTMIND_ENV=development
LOG_LEVEL=INFO
DATA_PATH=./data

# 播客配置
DEFAULT_PODCAST_LIMIT=5
AUTO_PROCESS_INTERVAL=3600  # 秒
```

### AI模型配置 (config/ai_models.json)
```json
{
  "models": {
    "deepseek": {
      "name": "DeepSeek",
      "provider": "deepseek",
      "capabilities": ["analysis", "summary", "translation"],
      "cost_per_token": 0.0000014
    },
    "kimi": {
      "name": "Kimi",
      "provider": "moonshot",
      "capabilities": ["analysis", "qa", "creative"],
      "cost_per_token": 0.0000012
    }
  }
}
```

## 🔧 开发指南

### 项目设置
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 设置预提交钩子
pre-commit install
```

### 代码规范
- 使用Black进行代码格式化
- 使用flake8进行代码检查
- 使用mypy进行类型检查
- 遵循PEP 8规范

### 提交规范
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- style: 代码格式
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程

## 🐳 容器化部署

### Docker
```bash
# 构建镜像
docker build -t castmind:latest .

# 运行容器
docker run -d \
  --name castmind \
  -e OPENAI_API_KEY="your-key" \
  -v ./data:/app/data \
  castmind:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  castmind:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## 📊 监控与日志

### 系统监控
```bash
# 查看系统状态
python castmind.py status --detailed

# 查看处理日志
python castmind.py logs --service workflow

# 查看性能指标
python castmind.py metrics --period 24h
```

### 日志配置
```python
# config/logging.yaml
version: 1
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
  file:
    class: logging.FileHandler
    filename: logs/castmind.log
    level: DEBUG
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持与反馈

- 问题报告: [GitHub Issues](https://github.com/YearsAlso/castmind/issues)
- 功能请求: [GitHub Discussions](https://github.com/YearsAlso/castmind/discussions)
- 文档: [项目Wiki](https://github.com/YearsAlso/castmind/wiki)

## 🌟 特性路线图

### 近期计划 (v1.0)
- [ ] 基础RSS解析和音频处理
- [ ] 多AI模型集成
- [ ] 基础知识存储
- [ ] Web管理界面

### 中期计划 (v2.0)
- [ ] 高级内容分析
- [ ] 知识图谱构建
- [ ] 智能推荐系统
- [ ] 移动端应用

### 长期愿景 (v3.0+)
- [ ] 个性化学习路径
- [ ] 社区知识共享
- [ ] 企业级部署
- [ ] 多语言支持

---

**CastMind - 让知识流动，让智慧沉淀** 🧠🌊