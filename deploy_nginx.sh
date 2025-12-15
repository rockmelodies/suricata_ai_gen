#!/bin/bash

# Nginx反向代理部署脚本
# 用途：自动配置Nginx反向代理，前后端统一使用80端口

echo "=========================================="
echo "  Suricata规则生成工具 - Nginx部署脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}警告: 需要sudo权限来配置Nginx${NC}"
    echo "请使用: sudo ./deploy_nginx.sh"
    exit 1
fi

# 步骤1: 检查Nginx是否安装
echo "[1/8] 检查Nginx..."
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Nginx未安装，正在安装...${NC}"
    
    # 检测系统类型
    if [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y nginx
    elif [ -f /etc/redhat-release ]; then
        yum install -y nginx
    else
        echo -e "${RED}不支持的系统类型，请手动安装Nginx${NC}"
        exit 1
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Nginx安装失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Nginx安装成功${NC}"
else
    echo -e "${GREEN}✓ Nginx已安装${NC}"
fi

# 步骤2: 创建Nginx配置
echo ""
echo "[2/8] 创建Nginx配置文件..."

# 替换路径占位符
sed "s|/path/to/suricata_ai_gen|$PROJECT_DIR|g" \
    "$PROJECT_DIR/nginx/suricata_rule_gen.conf" > /tmp/suricata_rule_gen.conf

# 检测配置文件位置
if [ -d /etc/nginx/sites-available ]; then
    # Debian/Ubuntu/Kali
    NGINX_AVAILABLE="/etc/nginx/sites-available/suricata_rule_gen.conf"
    NGINX_ENABLED="/etc/nginx/sites-enabled/suricata_rule_gen.conf"
    
    cp /tmp/suricata_rule_gen.conf "$NGINX_AVAILABLE"
    
    # 创建软链接
    if [ ! -L "$NGINX_ENABLED" ]; then
        ln -s "$NGINX_AVAILABLE" "$NGINX_ENABLED"
    fi
    
    # 删除默认站点（可选）
    if [ -L /etc/nginx/sites-enabled/default ]; then
        echo -e "${YELLOW}删除默认Nginx站点配置${NC}"
        rm -f /etc/nginx/sites-enabled/default
    fi
    
elif [ -d /etc/nginx/conf.d ]; then
    # CentOS/RHEL
    NGINX_CONF="/etc/nginx/conf.d/suricata_rule_gen.conf"
    cp /tmp/suricata_rule_gen.conf "$NGINX_CONF"
else
    echo -e "${RED}无法确定Nginx配置目录${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Nginx配置文件已创建${NC}"
echo "配置文件位置: $NGINX_AVAILABLE"

# 步骤3: 测试Nginx配置
echo ""
echo "[3/8] 测试Nginx配置..."
nginx -t
if [ $? -ne 0 ]; then
    echo -e "${RED}Nginx配置测试失败${NC}"
    echo "请检查配置文件: $NGINX_AVAILABLE"
    exit 1
fi
echo -e "${GREEN}✓ Nginx配置测试通过${NC}"

# 步骤4: 启用前端Nginx代理模式
echo ""
echo "[4/8] 配置前端使用Nginx代理..."

# 备份原文件
cp "$PROJECT_DIR/frontend/index.html" "$PROJECT_DIR/frontend/index.html.bak"

# 取消USE_NGINX_PROXY的注释
sed -i 's|// window.USE_NGINX_PROXY = true;|window.USE_NGINX_PROXY = true;|g' "$PROJECT_DIR/frontend/index.html"

echo -e "${GREEN}✓ 前端已配置为Nginx代理模式${NC}"
echo "原文件备份: frontend/index.html.bak"

# 步骤5: 启动后端服务
echo ""
echo "[5/8] 启动Flask后端服务..."

# 检查是否已运行
if pgrep -f "python.*backend/app.py" > /dev/null; then
    echo -e "${YELLOW}后端服务已在运行，跳过启动${NC}"
else
    # 切换到项目目录
    cd "$PROJECT_DIR"
    
    # 激活虚拟环境并启动
    if [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
        nohup python backend/app.py > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}虚拟环境不存在，请先运行 ./setup.sh${NC}"
        exit 1
    fi
fi

# 等待后端启动
echo "等待后端启动..."
sleep 3

# 测试后端
if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
else
    echo -e "${RED}✗ 后端服务启动失败${NC}"
    echo "请检查日志: cat backend.log"
    exit 1
fi

# 步骤6: 重启Nginx
echo ""
echo "[6/8] 重启Nginx服务..."
systemctl restart nginx
if [ $? -ne 0 ]; then
    echo -e "${RED}Nginx重启失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Nginx已重启${NC}"

# 步骤7: 配置防火墙
echo ""
echo "[7/8] 配置防火墙..."

if command -v ufw &> /dev/null; then
    # UFW (Ubuntu/Debian/Kali)
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo -e "${GREEN}✓ 已开放端口 80 和 443${NC}"
elif command -v firewall-cmd &> /dev/null; then
    # Firewalld (CentOS/RHEL)
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
    echo -e "${GREEN}✓ 已开放HTTP和HTTPS服务${NC}"
else
    echo -e "${YELLOW}未检测到防火墙管理工具，请手动开放80端口${NC}"
fi

# 步骤8: 获取访问地址
echo ""
echo "[8/8] 部署完成！"
echo "=========================================="

# 获取IP地址
IP_ADDR=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | head -n 1 | awk '{print $2}' | cut -d'/' -f1)

echo -e "${GREEN}✓ Nginx反向代理部署成功！${NC}"
echo ""
echo "访问地址："
echo "  本地: http://localhost"
if [ ! -z "$IP_ADDR" ]; then
    echo "  远程: http://$IP_ADDR"
fi
echo ""
echo "服务状态："
echo "  前端: 由Nginx提供 (80端口)"
echo "  后端: http://127.0.0.1:5000 (仅本地)"
echo "  代理: Nginx转发 /api -> 后端"
echo ""
echo "日志位置："
echo "  Nginx访问日志: /var/log/nginx/suricata_rule_gen_access.log"
echo "  Nginx错误日志: /var/log/nginx/suricata_rule_gen_error.log"
echo "  后端日志: $PROJECT_DIR/backend.log"
echo ""
echo "管理命令："
echo "  查看Nginx状态: sudo systemctl status nginx"
echo "  重启Nginx: sudo systemctl restart nginx"
echo "  查看后端日志: tail -f $PROJECT_DIR/backend.log"
echo "  停止后端: kill \$(cat $PROJECT_DIR/backend.pid)"
echo ""
echo "=========================================="

# 测试访问
echo ""
echo "正在测试访问..."
if curl -s http://localhost/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API代理测试成功！${NC}"
else
    echo -e "${YELLOW}⚠ API代理测试失败，请检查配置${NC}"
fi

echo ""
echo -e "${GREEN}部署完成！请在浏览器访问上述地址${NC}"
