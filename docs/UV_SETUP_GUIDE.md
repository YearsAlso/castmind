# 🚀 CastMind UV 环境配置指南

## 📋 什么是 UV？

**UV** 是一个用 Rust 编写的极速 Python 包管理器和解析器，由 Astral 团队开发（与 Ruff 同一团队）。它比传统的 pip 快 10-100 倍！

### UV 的主要优势：
- ⚡ **极速安装**：比 pip 快 10-100 倍
- 🎯 **精确解析**：快速且确定性的依赖解析
- 🔒 **安全可靠**：内置的依赖验证和锁定
- 🛠️ **功能丰富**：支持虚拟环境、包发布等
- 🌍 **跨平台**：支持 macOS、Linux、Windows

## 🔧 安装 UV

### macOS (推荐使用 Homebrew)
```bash
# 使用 Homebrew 安装
brew install uv

# 验证安装
uv --version
```

### Linux / 其他平台
```bash
# 使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pipx
pipx install uv
```

### Windows
```bash
# 使用 PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 Winget
winget install astral.uv
```

## 🚀 使用 UV 启动 CastMind

### 方法1：使用 UV 直接运行（推荐）
```bash
# 进入项目目录
cd ~/Projects/castmind

# 使用 uv 安装依赖并运行
uv run python backend/main.py

# 或使用 uvx（自动安装依赖）
uvx --from pyproject.toml python backend/main.py
```

### 方法2：创建虚拟环境
```bash
# 创建虚拟环境
uv venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 安装依赖
uv pip install -e .

# 运行应用
python backend/main.py
```

### 方法3：使用 UV 脚本
```bash
# 使用 uv 运行脚本
uv run castmind

# 或使用开发模式
uv run castmind-dev
```

## 📦 依赖管理

### 安装依赖
```bash
# 安装所有依赖（包括开发依赖）
uv pip install -e ".[dev]"

# 只安装核心依赖
uv pip install -e .

# 安装 AI 功能（可选）
uv pip install -e ".[ai]"

# 安装测试依赖
uv pip install -e ".[test]"
```

### 更新依赖
```bash
# 更新所有包到最新版本
uv pip compile --upgrade pyproject.toml -o requirements.txt
uv pip install -r requirements.txt

# 更新特定包
uv pip install --upgrade fastapi sqlalchemy
```

### 生成 requirements.txt
```bash
# 生成锁定文件
uv pip compile pyproject.toml -o requirements.txt

# 生成带哈希的锁定文件（生产环境）
uv pip compile pyproject.toml --generate-hashes -o requirements.lock
```

## ⚙️ 配置优化

### 1. 使用清华镜像源加速
`pyproject.toml` 中已经配置了清华镜像源：
```toml
[tool.uv]
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
trusted-host = ["pypi.tuna.tsinghua.edu.cn"]
```

### 2. 环境变量配置
创建 `.env` 文件：
```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
nano .env
```

`.env` 文件内容：
```bash
# CastMind 配置
DEBUG=true
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./data/castmind.db
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# 定时任务配置
FETCH_INTERVAL_MINUTES=10
CLEANUP_DAYS=30

# AI 服务配置（可选）
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 3. 数据目录准备
```bash
# 创建数据目录
mkdir -p data/logs data/exports

# 设置权限（如果需要）
chmod -R 755 data/
```

## 🧪 开发工作流

### 开发环境设置
```bash
# 1. 克隆项目（如果尚未克隆）
git clone <repository-url>
cd castmind

# 2. 使用 UV 创建虚拟环境
uv venv .venv
source .venv/bin/activate

# 3. 安装开发依赖
uv pip install -e ".[dev]"

# 4. 安装预提交钩子（可选）
uv pip install pre-commit
pre-commit install

# 5. 启动开发服务器
uv run python backend/main.py
```

### 代码质量工具
```bash
# 代码格式化
uv run black backend/
uv run isort backend/

# 类型检查
uv run mypy backend/

# 运行测试
uv run pytest tests/

# 代码质量检查
uv run pylint backend/
```

### 热重载开发
```bash
# 使用 uvicorn 热重载
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 或使用开发脚本
uv run python backend/main.py
```

## 🐳 Docker 集成

### 使用 UV 的 Dockerfile
```dockerfile
FROM python:3.12-slim

# 安装 uv
RUN pip install uv

WORKDIR /app

# 复制项目文件
COPY pyproject.toml README.md ./
COPY backend/ ./backend/

# 使用 uv 安装依赖
RUN uv pip install --system -e .

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "backend/main.py"]
```

### Docker Compose 配置
```yaml
version: '3.8'

services:
  castmind:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/data/logs
    environment:
      - DATABASE_URL=sqlite:////app/data/castmind.db
      - DEBUG=false
    restart: unless-stopped
```

## 📊 性能优化

### UV 缓存配置
```bash
# 查看 UV 缓存
uv cache dir

# 清理缓存
uv cache clean

# 设置缓存目录
export UV_CACHE_DIR=~/.cache/uv
```

### 并行安装
```bash
# UV 默认使用并行安装，可以通过环境变量控制
export UV_PARALLEL=8  # 设置并行任务数
```

### 离线模式
```bash
# 使用离线模式（如果已经缓存了依赖）
uv pip install --offline -e .
```

## 🔍 故障排除

### 常见问题

#### 1. UV 命令找不到
```bash
# 确保 UV 已正确安装
which uv

# 如果使用 Homebrew，可能需要重新加载 shell
exec $SHELL
```

#### 2. 依赖解析失败
```bash
# 清理缓存并重试
uv cache clean
uv pip install -e .

# 使用更宽松的版本约束
# 编辑 pyproject.toml 中的版本约束
```

#### 3. Python 版本不匹配
```bash
# 检查当前 Python 版本
python --version

# 使用特定 Python 版本
uv venv .venv --python 3.12
```

#### 4. 权限问题
```bash
# 使用 --user 标志
uv pip install --user -e .

# 或使用虚拟环境
uv venv .venv
source .venv/bin/activate
```

### 调试命令
```bash
# 查看 UV 版本和配置
uv --version
uv config list

# 查看已安装的包
uv pip list

# 查看包详情
uv pip show fastapi

# 检查依赖树
uv pip tree
```

## 🎯 生产部署

### 1. 生成生产依赖
```bash
# 生成带哈希的锁定文件
uv pip compile pyproject.toml --generate-hashes -o requirements.lock

# 安装生产依赖（不安装开发依赖）
uv pip install -r requirements.lock
```

### 2. 使用 Systemd 服务
创建 `/etc/systemd/system/castmind.service`：
```ini
[Unit]
Description=CastMind Podcast Subscription Service
After=network.target

[Service]
Type=simple
User=castmind
WorkingDirectory=/opt/castmind
Environment="PATH=/opt/castmind/.venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/castmind/.env
ExecStart=/opt/castmind/.venv/bin/python backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. 使用 Supervisor
创建 `/etc/supervisor/conf.d/castmind.conf`：
```ini
[program:castmind]
command=/opt/castmind/.venv/bin/python backend/main.py
directory=/opt/castmind
user=castmind
autostart=true
autorestart=true
stderr_logfile=/var/log/castmind.err.log
stdout_logfile=/var/log/castmind.out.log
environment=PYTHONUNBUFFERED="1"
```

## 📈 性能监控

### 使用 UV 的监控功能
```bash
# 查看安装统计
uv pip install --report install-report.json

# 分析依赖
uv pip audit
```

### 集成监控工具
```bash
# 安装监控依赖
uv pip install prometheus-client psutil

# 启动带监控的服务
uv run python backend/main.py --with-metrics
```

## 🔄 迁移指南

### 从传统 pip 迁移到 UV
```bash
# 1. 备份现有环境
pip freeze > requirements-old.txt

# 2. 安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 创建新的虚拟环境
uv venv .venv
source .venv/bin/activate

# 4. 从 pyproject.toml 安装
uv pip install -e .

# 5. 验证安装
uv pip list
```

### 从 requirements.txt 迁移
```bash
# 生成 pyproject.toml（如果还没有）
# 然后使用 UV 安装
uv pip install -r requirements.txt

# 或直接使用 UV 编译
uv pip compile requirements.txt -o requirements.lock
uv pip install -r requirements.lock
```

## 🎉 快速开始脚本

创建 `start-with-uv.sh`：
```bash
#!/bin/bash
# CastMind UV 快速启动脚本

set -e

echo "🚀 CastMind UV 快速启动"
echo "========================"

# 检查 UV 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ UV 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ UV 安装完成"
fi

# 进入项目目录
cd "$(dirname "$0")"

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo "🐍 创建虚拟环境..."
    uv venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
uv pip install -e ".[dev]"

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/logs

# 检查环境文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚙️  创建环境文件..."
        cp .env.example .env
        echo "⚠️  请编辑 .env 文件配置您的设置"
    fi
fi

# 启动服务
echo "🚀 启动 CastMind 服务..."
echo ""
echo "🌐 访问地址:"
echo "  服务: http://localhost:8000"
echo "  API文档: http://localhost:8000/api/docs"
echo "  健康检查: http://localhost:8000/api/v1/system/health"
echo ""
echo "📋 按 Ctrl+C 停止服务"
echo ""

uv run python backend/main.py
```

给脚本执行权限：
```bash
chmod +x start-with-uv.sh
./start-with-uv.sh
```

## 📚 更多资源

### 官方文档
- [UV 官方文档](https://docs.astral.sh/uv/)
- [UV GitHub 仓库](https://github.com/astral-sh/uv)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

### 社区资源
- [UV Discord 社区](https://discord.gg/astral-sh)
- [FastAPI 社区](https://discord.gg/VQjSZaeJ)
- [Python 中文社区](https://python.cn/)

### 学习资源
- [UV 快速入门教程](https://docs.astral.sh/uv/getting-started/)
- [FastAPI 教程](https://fastapi.tiangolo.com/tutorial/)
- [现代 Python 开发工作流](https://hynek.me/articles/python-production-dependencies/)

---

**🎯 现在你可以享受 UV 带来的极速开发体验了！**

**主要优势总结：**
- ⚡ **安装速度**：比 pip 快 10-100 倍
- 🎯 **依赖管理**：精确且确定性的解析
- 🔒 **安全性**：内置的依赖验证
- 🛠️ **工具集成**：与现有工具链完美集成
- 🌍 **跨平台**：一致的开发体验

**立即开始：**
```bash
# 最简单的方式
uv run python backend/main.py

# 或使用快速启动脚本
./start-with-uv.sh
```

**Happy coding with UV!** 🚀