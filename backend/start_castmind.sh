#!/bin/bash

# CastMind 后端服务启动脚本

echo "🚀 启动 CastMind 后端服务"
echo "=========================================="

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3"
    exit 1
fi

# 检查依赖
echo "🔍 检查 Python 依赖..."
python3 -c "import uvicorn, fastapi, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少 Python 依赖，正在安装..."
    pip3 install -r requirements.txt --quiet
    echo "✅ 依赖安装完成"
fi

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查数据库
if [ ! -f "data/castmind.db" ]; then
    echo "📝 数据库不存在，运行修复脚本..."
    python3 fix_database.py
fi

# 启动服务
echo ""
echo "🎯 启动 CastMind 服务..."
echo "   访问地址: http://localhost:8000"
echo "   API 文档: http://localhost:8000/api/docs"
echo ""
echo "📋 可用端点:"
echo "   GET  /          - 服务状态"
echo "   GET  /health    - 健康检查"
echo "   GET  /api/docs  - API 文档"
echo ""
echo "🛑 按 Ctrl+C 停止服务"
echo "=========================================="

# 启动 Uvicorn 服务器
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000