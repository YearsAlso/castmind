#!/bin/bash
# CastMind 开发服务器启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Starting CastMind development servers..."

# 启动后端
echo "Starting backend..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "Starting frontend..."
cd ../frontend
pnpm dev &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "CastMind 服务器已启动"
echo "========================================="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获 Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
