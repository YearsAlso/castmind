#!/bin/bash

# CastMind 安装脚本
# 快速安装和配置 CastMind 系统

set -e

echo "🎯 CastMind 安装脚本"
echo "====================="

# 检查 Python 版本
echo "检查 Python 版本..."
python3 --version || { echo "❌ 需要 Python 3.8+"; exit 1; }

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境？(y/n, 默认 n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装依赖
echo "安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建配置文件
if [ ! -f ".env" ]; then
    echo "创建环境配置文件..."
    cp .env.example .env
    echo "✅ 请编辑 .env 文件配置 API 密钥和其他设置"
fi

# 创建数据目录
echo "创建数据目录..."
mkdir -p data/logs data/exports

# 初始化数据库
echo "初始化数据库..."
python3 -c "
from backend.app.core.database import init_db
init_db()
print('✅ 数据库初始化完成')
" || echo "⚠️  数据库初始化可能需要手动运行"

# 前端安装（可选）
read -p "是否安装前端依赖？(y/n, 默认 n): " install_frontend
if [[ $install_frontend == "y" || $install_frontend == "Y" ]]; then
    echo "安装前端依赖..."
    cd frontend
    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v yarn &> /dev/null; then
        yarn install
    else
        npm install
    fi
    cd ..
    echo "✅ 前端依赖安装完成"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件配置 API 密钥"
echo "2. 启动后端服务: python backend/main.py"
echo "3. (可选) 启动前端: cd frontend && npm run dev"
echo ""
echo "访问地址："
echo "- 后端 API: http://localhost:8000"
echo "- API 文档: http://localhost:8000/api/docs"
echo "- 前端界面: http://localhost:3000"
echo ""
echo "更多信息请查看 README.md"