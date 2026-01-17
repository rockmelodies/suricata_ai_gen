#!/bin/bash

# Suricata规则生成工具 - Kali Linux启动脚本
# 用于解决Kali Linux上的常见权限和路径问题

echo "========================================"
echo "  Suricata规则生成工具 - Kali Linux启动"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "backend/app_v2.py" ]; then
    echo "[错误] 未找到 backend/app_v2.py，请确保在项目根目录下运行此脚本"
    exit 1
fi

# 检查Python
echo "[1/7] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python3未安装"
    echo "执行: sudo apt install python3 python3-pip"
    exit 1
fi

python3 --version

# 检查虚拟环境
echo ""
echo "[2/7] 检查虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[错误] 创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
source .venv/bin/activate
echo "虚拟环境已激活"

# 检查并安装依赖
echo ""
echo "[3/7] 检查并安装Python依赖..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 检查环境变量文件
echo ""
echo "[4/7] 检查环境变量配置..."
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，创建示例文件..."
    cp .env.example .env
    echo "请编辑 .env 文件并配置 AI_API_KEY 等参数"
    echo "特别注意配置正确的 Suricata 路径!"
fi

# 确保数据库和上传目录存在
echo ""
echo "[5/7] 初始化目录..."
mkdir -p backend/
touch backend/suricata_rules.db
chmod 664 backend/suricata_rules.db

mkdir -p uploads/
chmod 755 uploads/

# 检查Suricata
echo ""
echo "[6/7] 检查Suricata..."
if command -v suricata &> /dev/null; then
    echo "Suricata版本: $(suricata --version)"
else
    echo "警告: Suricata未安装，规则验证功能将不可用"
    echo "安装命令: sudo apt install suricata"
fi

echo ""
echo "========================================"
echo "  启动后端服务..."
echo "========================================"

# 启动后端服务
cd backend
python start_app.py

echo ""
echo "========================================"
echo "  服务已停止"
echo "========================================"