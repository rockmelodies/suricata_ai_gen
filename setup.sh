#!/bin/bash

echo "========================================"
echo "  Suricata规则生成工具 - 自动部署"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] Python3未安装${NC}"
    echo "请执行以下命令安装："
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Kali Linux: sudo apt install python3-venv python3-pip"
    exit 1
fi

echo -e "${GREEN}[1/6] 检测Python版本...${NC}"
python3 --version

echo ""
echo -e "${GREEN}[2/6] 创建虚拟环境...${NC}"
if [ -d ".venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 虚拟环境创建失败${NC}"
        echo "请检查python3-venv是否已安装"
        echo "执行: sudo apt install python3-venv"
        exit 1
    fi
    echo "虚拟环境创建成功"
fi

echo ""
echo -e "${GREEN}[3/6] 激活虚拟环境...${NC}"
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 虚拟环境激活失败${NC}"
    exit 1
fi
echo "虚拟环境已激活"

echo ""
echo -e "${GREEN}[4/6] 升级pip...${NC}"
pip install --upgrade pip

echo ""
echo -e "${GREEN}[5/6] 安装依赖包...${NC}"
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}[警告] 依赖安装失败，尝试使用国内镜像...${NC}"
    pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

echo ""
echo -e "${GREEN}[6/6] 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo ".env 文件已创建，请编辑配置API密钥"
    else
        echo -e "${YELLOW}[警告] .env.example 文件不存在${NC}"
    fi
else
    echo ".env 文件已存在，跳过创建"
fi

echo ""
echo "========================================"
echo -e "${GREEN}  部署完成！${NC}"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. 编辑 .env 文件，配置您的AI_API_KEY"
echo "   vim .env  或  nano .env"
echo "2. 运行 ./start_all.sh 启动服务"
echo ""
echo "提示：如需重新部署，请先删除 .venv 目录"
echo "      rm -rf .venv"
echo ""
