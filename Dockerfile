# 🐳 CastMind Docker 容器配置
# 版本: 1.0.0
# 描述: CastMind 播客智能处理系统

# 使用 Python 3.9 官方镜像作为基础
FROM python:3.9-slim AS builder

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # 音频处理依赖
    ffmpeg \
    # 构建工具
    build-essential \
    # 清理缓存
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt requirements-dev.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# 生产阶段
FROM python:3.9-slim AS production

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已安装的依赖
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y \
    # 音频处理运行时依赖
    ffmpeg \
    # 时区数据
    tzdata \
    # 清理缓存
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# 创建非 root 用户
RUN groupadd -r castmind && useradd -r -g castmind -u 1000 castmind

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/config \
    && chown -R castmind:castmind /app

# 切换到非 root 用户
USER castmind

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('/app/data/castmind.db'); conn.execute('SELECT 1'); conn.close()" || exit 1

# 默认命令（后台服务模式）
CMD ["python", "castmind_service.py"]

# ============================================
# 开发阶段
FROM builder AS development

# 安装开发依赖
RUN pip install --no-cache-dir -r requirements-dev.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/config

# 开发模式命令
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# 标签
LABEL org.opencontainers.image.title="CastMind" \
      org.opencontainers.image.description="播客智能处理系统" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="牛马 AI 助手" \
      org.opencontainers.image.url="https://github.com/your-org/castmind" \
      org.opencontainers.image.source="https://github.com/your-org/castmind" \
      org.opencontainers.image.licenses="MIT"

# 暴露端口
EXPOSE 8000  # FastAPI Web 服务
EXPOSE 5678  # 调试端口（仅开发）

# 数据卷
VOLUME ["/app/data", "/app/logs", "/app/config"]