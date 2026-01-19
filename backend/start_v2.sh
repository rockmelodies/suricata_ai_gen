#!/usr/bin/env bash
# Start Backend API v2 (OpenAPI)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "   Suricata Rule Generator API v2.0"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# Activate virtual environment
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# Install/Update dependencies
echo "📦 检查并安装依赖..."
pip install -r requirements.txt > /dev/null 2>&1

# Load environment variables
if [ -f "../.env" ]; then
    export $(grep -v '^#' ../.env | xargs)
fi

# Run the API server
echo "🚀 启动API服务器..."
echo ""
echo "📖 API文档: http://localhost:5000/api/docs"
echo "🔐 默认管理员: admin / admin123"
echo "🌐 服务地址: http://localhost:5000/api"
echo ""
echo "========================================"

# Save PID
PID_FILE="$SCRIPT_DIR/backend_v2.pid"

python app_with_auth.py &
BACKEND_PID=$!

echo $BACKEND_PID > "$PID_FILE"
echo "✓ 后端进程 PID: $BACKEND_PID"

# Keep the script running
wait $BACKEND_PID
