# CastMind Makefile
# 使用 'make <command>' 运行

.PHONY: help install dev test lint format clean run docker-build docker-run

# 默认目标
help:
	@echo "CastMind - 播客智能流系统"
	@echo ""
	@echo "可用命令:"
	@echo "  make install    安装生产依赖 (使用 uv)"
	@echo "  make dev        安装开发依赖 (使用 uv)"
	@echo "  make test       运行测试"
	@echo "  make lint       运行代码检查"
	@echo "  make format     格式化代码"
	@echo "  make clean      清理临时文件"
	@echo "  make run        运行CastMind系统"
	@echo "  make docker-build 构建Docker镜像"
	@echo "  make docker-run   运行Docker容器"
	@echo ""

# 检查是否安装了uv
CHECK_UV := $(shell command -v uv 2> /dev/null)

# 安装生产依赖
install:
ifndef CHECK_UV
	@echo "❌ 未安装 uv，请先安装: https://github.com/astral-sh/uv"
	@echo "   或使用: pip install uv"
	@exit 1
endif
	@echo "📦 安装生产依赖..."
	uv sync
	@echo "✅ 依赖安装完成"

# 安装开发依赖
dev:
ifndef CHECK_UV
	@echo "❌ 未安装 uv，请先安装: https://github.com/astral-sh/uv"
	@echo "   或使用: pip install uv"
	@exit 1
endif
	@echo "🔧 安装开发依赖..."
	uv sync --dev
	uv run pre-commit install
	@echo "✅ 开发环境设置完成"

# 运行测试
test:
	@echo "🧪 运行测试..."
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

# 运行代码检查
lint:
	@echo "🔍 运行代码检查..."
	uv run ruff check src/
	uv run flake8 src/
	uv run mypy src/
	uv run bandit -r src/ -c pyproject.toml
	@echo "✅ 代码检查完成"

# 格式化代码
format:
	@echo "🎨 格式化代码..."
	uv run black src/ tests/
	uv run isort src/ tests/
	uv run ruff check --fix src/ tests/
	@echo "✅ 代码格式化完成"

# 运行所有检查
check: lint test
	@echo "✅ 所有检查通过"

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 运行CastMind系统
run:
	@echo "🚀 启动CastMind系统..."
	uv run python castmind.py start

# 构建Docker镜像
docker-build:
	@echo "🐳 构建Docker镜像..."
	docker build -t castmind:latest .

# 运行Docker容器
docker-run:
	@echo "🐳 运行Docker容器..."
	docker run -it --rm \
		-e OPENAI_API_KEY=$${OPENAI_API_KEY} \
		-e DEEPSEEK_API_KEY=$${DEEPSEEK_API_KEY} \
		-p 8000:8000 \
		castmind:latest

# 开发模式运行（热重载）
dev-run:
	@echo "🚀 启动开发服务器（热重载）..."
	uv run python castmind.py start --reload

# 更新依赖
update:
	@echo "⬆️ 更新依赖..."
	uv sync --upgrade --dev
	@echo "✅ 依赖更新完成"

# 安全检查
security:
	@echo "🔒 运行安全检查..."
	uv run safety check
	uv run bandit -r src/ -c pyproject.toml
	@echo "✅ 安全检查完成"

# 生成文档
docs:
	@echo "📚 生成文档..."
	uv run mkdocs build
	@echo "✅ 文档生成完成"

# 服务文档（本地预览）
serve-docs:
	@echo "🌐 启动文档服务器..."
	uv run mkdocs serve

# 发布版本
release:
	@echo "🚀 准备发布版本..."
	@read -p "版本号 (例如: v1.0.0): " version; \
	git tag -a $$version -m "Release $$version"; \
	git push origin $$version; \
	echo "✅ 版本 $$version 已发布"

# 设置环境
setup: install dev
	@echo "⚙️ 设置环境..."
	cp config/.env.example config/.env
	@echo "✅ 环境设置完成"
	@echo "📝 请编辑 config/.env 文件，填入你的API密钥"