# 使用官方Python镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.cargo/bin/uv /usr/local/bin/uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY requirements.txt ./
COPY src/ ./src/
COPY config/ ./config/
COPY castmind.py ./

# 创建虚拟环境并安装依赖
RUN uv venv \
    && uv sync --frozen

# 创建非root用户
RUN useradd -m -u 1000 castmind \
    && chown -R castmind:castmind /app

USER castmind

# 暴露端口（如果需要）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 默认命令
CMD ["python", "castmind.py", "start"]