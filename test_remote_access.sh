#!/bin/bash

# 远程访问测试和排查脚本

echo "=========================================="
echo "  Suricata规则生成工具 - 远程访问测试"
echo "=========================================="
echo ""

# 获取本机IP
echo "[1] 检查网络配置"
echo "----------------------------------------"
echo "本机IP地址："
ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print "  " $2}' || ifconfig | grep "inet " | grep -v "127.0.0.1" | awk '{print "  " $2}'
echo ""

# 检查端口监听
echo "[2] 检查端口监听状态"
echo "----------------------------------------"
echo "后端端口 (5000)："
if netstat -tlnp 2>/dev/null | grep ":5000" > /dev/null; then
    netstat -tlnp 2>/dev/null | grep ":5000" | awk '{print "  ✓ " $4 " " $7}'
    LISTEN_ADDR=$(netstat -tlnp 2>/dev/null | grep ":5000" | awk '{print $4}')
    if [[ $LISTEN_ADDR == "0.0.0.0:5000" ]] || [[ $LISTEN_ADDR == ":::5000" ]]; then
        echo "  ✓ 监听地址正确 (允许远程访问)"
    else
        echo "  ✗ 警告: 只监听在 $LISTEN_ADDR (可能无法远程访问)"
        echo "  建议: 修改后端代码 app.run(host='0.0.0.0', port=5000)"
    fi
else
    echo "  ✗ 后端服务未运行或未监听5000端口"
    echo "  请运行: ./start_backend.sh"
fi
echo ""

echo "前端端口 (8080)："
if netstat -tlnp 2>/dev/null | grep ":8080" > /dev/null; then
    netstat -tlnp 2>/dev/null | grep ":8080" | awk '{print "  ✓ " $4 " " $7}'
    LISTEN_ADDR=$(netstat -tlnp 2>/dev/null | grep ":8080" | awk '{print $4}')
    if [[ $LISTEN_ADDR == "0.0.0.0:8080" ]] || [[ $LISTEN_ADDR == ":::8080" ]]; then
        echo "  ✓ 监听地址正确 (允许远程访问)"
    else
        echo "  ✗ 警告: 只监听在 $LISTEN_ADDR (可能无法远程访问)"
        echo "  建议: python3 -m http.server 8080 --bind 0.0.0.0"
    fi
else
    echo "  ✗ 前端服务未运行或未监听8080端口"
    echo "  请运行: ./start_frontend.sh"
fi
echo ""

# 检查防火墙
echo "[3] 检查防火墙状态"
echo "----------------------------------------"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | grep "Status:" | awk '{print $2}')
    echo "UFW防火墙: $UFW_STATUS"
    if [ "$UFW_STATUS" == "active" ]; then
        echo "端口5000状态："
        sudo ufw status | grep "5000" || echo "  ✗ 未开放5000端口"
        echo "端口8080状态："
        sudo ufw status | grep "8080" || echo "  ✗ 未开放8080端口"
        echo ""
        echo "如需开放端口，请运行："
        echo "  sudo ufw allow 5000"
        echo "  sudo ufw allow 8080"
    fi
elif command -v firewall-cmd &> /dev/null; then
    echo "Firewalld状态："
    sudo firewall-cmd --state 2>/dev/null
    echo "开放的端口："
    sudo firewall-cmd --list-ports 2>/dev/null || echo "  (无法查询，可能需要sudo权限)"
else
    echo "未检测到UFW或Firewalld"
    echo "请手动检查iptables: sudo iptables -L -n"
fi
echo ""

# 测试API连接
echo "[4] 测试API连接"
echo "----------------------------------------"
echo "本地API测试 (localhost:5000)："
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    RESPONSE=$(curl -s http://localhost:5000/api/health)
    echo "  ✓ API响应正常"
    echo "  响应: $RESPONSE"
else
    echo "  ✗ 无法连接到API"
    echo "  请确认后端服务是否启动"
fi
echo ""

# 获取本机非localhost IP进行测试
LOCAL_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | head -n 1 | awk '{print $2}' | cut -d'/' -f1)
if [ ! -z "$LOCAL_IP" ]; then
    echo "本机IP API测试 ($LOCAL_IP:5000)："
    if curl -s --connect-timeout 3 http://$LOCAL_IP:5000/api/health > /dev/null 2>&1; then
        RESPONSE=$(curl -s http://$LOCAL_IP:5000/api/health)
        echo "  ✓ 远程API访问正常"
        echo "  响应: $RESPONSE"
    else
        echo "  ✗ 无法通过IP访问API"
        echo "  可能原因: 防火墙阻止或后端未监听0.0.0.0"
    fi
fi
echo ""

# 浏览器访问指引
echo "[5] 浏览器访问指引"
echo "----------------------------------------"
echo "本地访问："
echo "  http://localhost:8080"
echo ""
echo "远程访问（从其他机器）："
if [ ! -z "$LOCAL_IP" ]; then
    echo "  http://$LOCAL_IP:8080"
else
    echo "  http://<你的IP地址>:8080"
fi
echo ""
echo "测试步骤："
echo "  1. 在远程机器的浏览器打开上述URL"
echo "  2. F12打开开发者工具"
echo "  3. 查看Console标签，应该看到："
echo "     [API配置] 自动检测: ..."
echo "     hostname应该是Kali的IP，不是localhost"
echo "  4. 点击'AI生成规则'按钮"
echo "  5. 查看Network标签，API请求URL应该是:"
if [ ! -z "$LOCAL_IP" ]; then
    echo "     http://$LOCAL_IP:5000/api/rules/generate"
else
    echo "     http://<Kali-IP>:5000/api/rules/generate"
fi
echo ""

# 常见问题排查
echo "[6] 常见问题排查"
echo "----------------------------------------"
echo "问题1: 页面能访问，但功能无法使用"
echo "  → 打开浏览器F12，查看Console是否有错误"
echo "  → 查看Network标签，确认API请求地址"
echo "  → 确认API请求地址不是localhost"
echo ""
echo "问题2: API请求地址仍然是localhost"
echo "  → 清除浏览器缓存: Ctrl+Shift+Delete"
echo "  → 强制刷新页面: Ctrl+F5"
echo "  → 确认index.html已更新（包含getApiBaseUrl函数）"
echo ""
echo "问题3: 连接超时或拒绝连接"
echo "  → 检查防火墙是否开放5000和8080端口"
echo "  → 检查后端是否监听0.0.0.0:5000"
echo "  → 检查前端是否监听0.0.0.0:8080"
echo ""
echo "问题4: CORS跨域错误"
echo "  → 确认backend/app.py中有: CORS(app)"
echo "  → 重启后端服务"
echo ""

echo "=========================================="
echo "  测试完成"
echo "=========================================="
echo ""
echo "如有问题，请按上述步骤逐一排查"
echo ""
