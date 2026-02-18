# 🧠🌊 CastMind - 播客智能流系统

![GitHub](https://img.shields.io/github/license/YearsAlso/castmind)
![GitHub last commit](https://img.shields.io/github/last-commit/YearsAlso/castmind)
![GitHub issues](https://img.shields.io/github/issues/YearsAlso/castmind)
![GitHub stars](https://img.shields.io/github/stars/YearsAlso/castmind)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB)
![uv](https://img.shields.io/badge/uv-快速Python包管理-FFD43B)

![CastMind](https://img.shields.io/badge/CastMind-播客智能流-4F46E5)
![AI智能](https://img.shields.badge/🧠-AI深度分析-F59E0B)
![流畅处理](https://img.shields.io/badge/🌊-流畅工作流-06B6D4)
![知识沉淀](https://img.shields.io/badge/📚-知识沉淀-10B981)
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
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip
- OpenAI API密钥（或其他AI服务密钥）
- Git

### 使用 uv 安装（推荐）

#### 1. 安装 uv
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

#### 2. 使用 uv 初始化项目
```bash
# 克隆仓库
git clone https://github.com/YearsAlso/castmind.git
cd castmind

# 使用 uv 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖（uv会自动处理依赖解析和锁定）
uv pip install -r requirements.txt

# 或直接使用 uv sync（推荐）
uv sync

# 配置环境变量
cp config/.env.example config/.env
# 编辑 config/.env 文件，填入你的API密钥

# 运行测试
uv run python -m pytest tests/ -v
```

### 使用传统 pip 安装
```bash
# 克隆仓库
git clone https://github.com/YearsAlso/castmind.git
cd castmind

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config/.env.example config/.env
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

## ⚡ uv 快速指南

### 为什么使用 uv？
- 🚀 **极速安装** - 比 pip 快 10-100 倍
- 🔒 **可靠依赖** - 内置依赖解析器和锁定文件
- 📦 **一体化工具** - 替代 pip、virtualenv、pip-tools
- 🌍 **跨平台** - 支持 Windows、macOS、Linux

### 常用 uv 命令
```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖（自动生成 uv.lock）
uv sync

# 安装开发依赖
uv sync --dev

# 运行Python脚本
uv run python script.py

# 添加新依赖
uv add package-name
uv add "package-name>=1.0.0"
uv add package-name --dev

# 移除依赖
uv remove package-name

# 更新依赖
uv sync --upgrade

# 查看依赖树
uv tree

# 导出 requirements.txt
uv pip compile pyproject.toml -o requirements.txt
```

### 项目特定的 uv 命令
```bash
# 运行CastMind系统
uv run python castmind.py start

# 运行测试
uv run pytest tests/ -v

# 代码格式化
uv run black src/
uv run isort src/

# 代码检查
uv run flake8 src/
uv run mypy src/

# 生成依赖锁定文件
uv lock

# 检查安全漏洞
uv run safety check

# 运行所有代码质量检查
uv run pre-commit run --all-files
```

### Makefile 简化命令
```bash
# 使用 Makefile 简化开发流程
make setup          # 一键设置环境（安装依赖+复制配置文件）
make install        # 安装生产依赖
make dev            # 安装开发依赖和预提交钩子
make test           # 运行测试
make lint           # 运行代码检查
make format         # 格式化代码
make check          # 运行所有检查（lint + test）
make clean          # 清理临时文件
make run            # 运行CastMind系统
make dev-run        # 开发模式运行（热重载）
make security       # 运行安全检查
make update         # 更新所有依赖
```

### uv 工作流示例
```bash
# 1. 克隆并设置项目
git clone https://github.com/YearsAlso/castmind.git
cd castmind

# 2. 使用 Makefile 一键设置
make setup

# 3. 编辑配置文件
nano config/.env  # 填入你的API密钥

# 4. 运行测试
make test

# 5. 启动系统
make run
```

## 🔧 开发指南

### 使用 uv 进行开发设置（推荐）
```bash
# 使用 uv 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装开发依赖（uv会自动处理依赖冲突）
uv sync --dev

# 或分别安装
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# 设置预提交钩子
uv run pre-commit install

# 运行开发服务器（热重载）
uv run python castmind.py start --reload
```

### 使用传统 pip 进行开发设置
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