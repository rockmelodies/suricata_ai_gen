#!/usr/bin/env bash
# Start Frontend (Vue3)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "   Suricata Rule Generator - Frontend"
echo "========================================"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  依赖未安装，正在安装..."
    npm install
    echo "✓ 依赖安装成功"
fi

echo "🚀 启动前端开发服务器..."
echo ""
echo "========================================"
echo "   访问地址: http://localhost:5173"
echo "   后端API: http://localhost:5000/api"
echo "========================================"
echo ""

npm run dev
