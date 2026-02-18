# 🛠️ CastMind 开发指南

欢迎开发者！本指南将帮助您设置开发环境、理解代码结构，并参与CastMind项目的开发。

## 🚀 开发环境设置

### 系统要求
- Python 3.9+
- Git
- 4GB以上内存
- 10GB以上磁盘空间

### 1. 克隆仓库
```bash
git clone https://github.com/YearsAlso/castmind.git
cd castmind
```

### 2. 使用uv设置开发环境（推荐）
```bash
# 安装uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装开发依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装所有依赖（生产+开发）
uv sync --dev

# 设置预提交钩子
uv run pre-commit install
```

### 3. 使用传统pip设置
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

### 4. 配置开发环境
```bash
# 复制环境变量模板
cp config/.env.example config/.env

# 编辑配置文件（使用测试API密钥）
nano config/.env
```

## 🏗️ 项目架构

### 代码结构
```
castmind/
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
├── tests/                  # 测试
│   ├── unit/              # 单元测试
│   └── integration/       # 集成测试
└── docs/                  # 文档
```

### 架构设计原则
1. **模块化设计** - 每个模块职责单一，接口清晰
2. **依赖注入** - 降低模块间耦合度
3. **配置驱动** - 所有行为可通过配置调整
4. **错误处理** - 完善的错误处理和恢复机制
5. **可测试性** - 易于编写单元测试和集成测试

## 🧪 测试指南

### 运行测试
```bash
# 运行所有测试
make test

# 运行单元测试
uv run pytest tests/unit/ -v

# 运行集成测试
uv run pytest tests/integration/ -v

# 运行特定测试文件
uv run pytest tests/unit/test_config.py -v

# 运行测试并生成覆盖率报告
uv run pytest tests/ --cov=src --cov-report=html
```

### 编写测试
#### 单元测试示例
```python
# tests/unit/test_config.py
import pytest
from src.core.config import ConfigManager

def test_config_loading():
    """测试配置加载"""
    config = ConfigManager()
    assert config.get("CASTMIND_ENV") == "development"
    
def test_ai_model_config():
    """测试AI模型配置"""
    config = ConfigManager()
    model_config = config.get_ai_model_config("deepseek")
    assert model_config is not None
    assert model_config["name"] == "DeepSeek"
```

#### 集成测试示例
```python
# tests/integration/test_workflow.py
import pytest
from src.workflow.rss_parser import RSSParser

@pytest.mark.integration
def test_rss_parsing():
    """测试RSS解析集成"""
    parser = RSSParser()
    feed_url = "https://feeds.fireside.fm/bibleinayear/rss"
    
    podcast_info = parser.parse_feed(feed_url)
    assert podcast_info is not None
    assert podcast_info.title is not None
    
    episodes = parser.get_episodes(feed_url, limit=2)
    assert len(episodes) > 0
```

### 测试标记
```python
@pytest.mark.unit          # 单元测试
@pytest.mark.integration   # 集成测试
@pytest.mark.slow          # 慢速测试
@pytest.mark.api           # API测试
@pytest.mark.database      # 数据库测试
```

## 📝 代码规范

### 代码格式化
```bash
# 使用Black格式化代码
make format

# 或手动运行
uv run black src/ tests/

# 使用isort排序导入
uv run isort src/ tests/
```

### 代码检查
```bash
# 运行所有代码检查
make lint

# 或分别运行
uv run flake8 src/          # 代码风格检查
uv run mypy src/            # 类型检查
uv run bandit -r src/       # 安全扫描
uv run ruff check src/      # 快速检查
```

### 提交规范
使用Conventional Commits规范：
- `feat:` - 新功能
- `fix:` - Bug修复
- `docs:` - 文档更新
- `style:` - 代码格式
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建过程

示例：
```bash
git commit -m "feat: add audio download module with progress tracking"
git commit -m "fix: resolve memory leak in RSS parser"
git commit -m "docs: update API documentation"
```

## 🔄 开发工作流

### 1. 创建功能分支
```bash
# 从main分支创建新功能分支
git checkout -b feat/audio-download

# 或从develop分支创建
git checkout develop
git checkout -b feat/audio-download
```

### 2. 开发新功能
```bash
# 编写代码
# 运行测试
make test

# 代码检查
make lint

# 格式化代码
make format
```

### 3. 提交更改
```bash
# 添加更改
git add .

# 提交（遵循提交规范）
git commit -m "feat: add audio download with retry mechanism"

# 推送到远程
git push -u origin feat/audio-download
```

### 4. 创建Pull Request
1. 访问GitHub仓库
2. 点击"New Pull Request"
3. 选择正确的分支
4. 填写PR描述
5. 等待代码审查

### 5. 代码审查
- 确保所有测试通过
- 代码符合规范
- 文档已更新
- 没有引入安全漏洞

## 🐛 调试技巧

### 日志调试
```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 在代码中添加日志
logger = logging.getLogger(__name__)
logger.debug("Processing audio file: %s", audio_path)
logger.info("Download completed: %s", file_size)
logger.warning("Network connection unstable")
logger.error("Failed to parse RSS feed: %s", error)
```

### 使用调试器
```bash
# 使用pdb调试
python -m pdb castmind.py start

# 在代码中添加断点
import pdb; pdb.set_trace()
```

### 性能分析
```bash
# 使用cProfile分析性能
python -m cProfile -o profile.stats castmind.py process --name "test"

# 分析结果
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('time').print_stats(10)"
```

## 📚 文档编写

### 代码文档
使用Google风格文档字符串：
```python
def process_audio(audio_path: str, output_format: str = "mp3") -> str:
    """处理音频文件，转换为指定格式。
    
    Args:
        audio_path: 音频文件路径
        output_format: 输出格式，支持'mp3', 'wav', 'flac'
        
    Returns:
        处理后的文件路径
        
    Raises:
        FileNotFoundError: 音频文件不存在
        ValueError: 不支持的输出格式
    """
    # 实现代码
    pass
```

### API文档
使用OpenAPI规范：
```yaml
openapi: 3.0.0
info:
  title: CastMind API
  version: 1.0.0
paths:
  /api/v1/podcasts:
    get:
      summary: 获取播客列表
      responses:
        '200':
          description: 成功返回播客列表
```

### 用户文档
- 使用清晰的中文
- 包含代码示例
- 添加截图和图表
- 提供故障排除指南

## 🔧 工具链

### 开发工具
- **编辑器**: VS Code、PyCharm、Neovim
- **终端**: iTerm2、Windows Terminal
- **版本控制**: Git、GitHub
- **包管理**: uv、pip

### 质量工具
- **代码格式化**: Black、isort
- **代码检查**: flake8、mypy、bandit、ruff
- **测试框架**: pytest、coverage
- **预提交钩子**: pre-commit

### 部署工具
- **容器化**: Docker、Docker Compose
- **CI/CD**: GitHub Actions
- **监控**: Prometheus、Grafana
- **日志**: structlog、ELK Stack

## 🤝 贡献指南

### 如何贡献
1. Fork项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 确保代码质量
5. 提交Pull Request

### 贡献范围
- 新功能开发
- Bug修复
- 性能优化
- 文档改进
- 测试用例
- 代码重构

### 行为准则
- 尊重其他贡献者
- 建设性讨论
- 遵守代码规范
- 及时响应反馈

## 🆘 获取帮助

### 开发问题
- 查看现有Issue
- 搜索文档
- 在Discussions提问
- 联系核心开发者

### 学习资源
- [Python官方文档](https://docs.python.org/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [pytest文档](https://docs.pytest.org/)
- [Git教程](https://git-scm.com/book/)

### 社区支持
- **GitHub Issues**: 问题报告
- **GitHub Discussions**: 技术讨论
- **Discord频道**: 实时交流
- **邮件列表**: 更新通知

---

**最后更新**: 2026-02-18  
**文档版本**: v1.0.0