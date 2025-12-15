# 🚀 远程部署指南

本文档说明如何将Suricata规则生成工具部署到远程服务器，并支持远程访问。

## 📋 部署架构

```
┌─────────────────┐         ┌──────────────────────┐
│   客户端浏览器   │ ──────> │   服务器 (IP/域名)    │
│                 │         │                      │
│  访问前端页面    │         │  前端: Port 8080     │
│  http://IP:8080│         │  后端: Port 5000     │
└─────────────────┘         └──────────────────────┘
```

## 🔧 问题说明

### 为什么远程访问失败？

当您在远程访问前端页面时，前端JavaScript会尝试请求API。如果API地址硬编码为`localhost:5000`，浏览器会尝试访问**客户端本地**的5000端口，而不是服务器的5000端口，导致无法连接。

**错误场景**：
```
客户端浏览器访问: http://192.168.1.100:8080
前端JS尝试请求:  http://localhost:5000/api  ❌ 错误！访问的是客户端本地
应该请求:        http://192.168.1.100:5000/api  ✅ 正确！
```

### 解决方案

本项目已实现**自动API地址检测**，会根据当前页面URL自动确定后端API地址。

## ✅ 自动配置（推荐）

### 工作原理

前端代码会自动检测：
```javascript
// 自动使用当前页面的协议和主机名
const protocol = window.location.protocol; // http: 或 https:
const hostname = window.location.hostname; // 实际访问的IP或域名
const apiUrl = `${protocol}//${hostname}:5000/api`;
```

**示例**：
- 访问 `http://localhost:8080` → API地址: `http://localhost:5000/api`
- 访问 `http://192.168.1.100:8080` → API地址: `http://192.168.1.100:5000/api`
- 访问 `https://example.com:8080` → API地址: `https://example.com:5000/api`

### 部署步骤

1. **服务器上部署**
```bash
# 1. 启动后端（监听0.0.0.0:5000）
./start_backend.sh

# 2. 启动前端（监听0.0.0.0:8080）
./start_frontend.sh
```

2. **防火墙配置**
```bash
# 允许访问端口5000和8080
sudo ufw allow 5000
sudo ufw allow 8080

# 或使用iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

3. **访问应用**
```
浏览器访问: http://服务器IP:8080
自动连接后端: http://服务器IP:5000/api
```

## 🔧 手动配置（可选）

如果需要自定义API地址（例如使用反向代理），可以手动指定：

### 方式1：修改index.html

编辑 `frontend/index.html`，取消注释并修改：

```html
<head>
    <!-- ... -->
    
    <!-- 取消下面的注释并修改API地址 -->
    <script>
        window.API_BASE_URL = 'http://your-server-ip:5000/api';
    </script>
    
    <!-- ... -->
</head>
```

### 方式2：使用Nginx反向代理

**推荐用于生产环境**

1. **Nginx配置示例**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/suricata_ai_gen/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:5000/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

2. **前端配置**（使用相对路径）

```html
<script>
    // 使用相对路径，Nginx会代理到后端
    window.API_BASE_URL = '/api';
</script>
```

3. **优势**
- ✅ 统一端口访问（80或443）
- ✅ 支持HTTPS
- ✅ 隐藏后端端口
- ✅ 负载均衡支持

## 🌐 部署场景

### 场景1：内网部署

**服务器IP**: 192.168.1.100

```bash
# 服务器上
./start_all.sh

# 客户端访问
http://192.168.1.100:8080
```

**自动配置**：无需修改，自动适配

### 场景2：公网部署（无域名）

**服务器IP**: 123.45.67.89

```bash
# 服务器上
./start_all.sh

# 配置防火墙
sudo ufw allow 5000
sudo ufw allow 8080

# 客户端访问
http://123.45.67.89:8080
```

**自动配置**：无需修改，自动适配

### 场景3：域名部署（使用Nginx）

**域名**: suricata.example.com

1. **Nginx配置**（如上）

2. **启动服务**
```bash
./start_backend.sh  # 后端
sudo nginx -s reload  # Nginx
```

3. **前端配置**
```html
<script>
    window.API_BASE_URL = '/api';  // 使用相对路径
</script>
```

4. **访问**
```
https://suricata.example.com
```

### 场景4：Docker部署

**docker-compose.yml**:

```yaml
version: '3'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - AI_API_KEY=${AI_API_KEY}
    volumes:
      - ./backend:/app
      - ./.env:/app/.env
    
  frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
    depends_on:
      - backend
```

**访问**: `http://server-ip:8080`

## 🔍 故障排查

### 问题1：前端能访问，后端API无法连接

**现象**：
```
前端页面显示正常
点击"AI生成规则"按钮无响应
浏览器控制台报错: ERR_CONNECTION_REFUSED
```

**原因**：防火墙阻止5000端口

**解决**：
```bash
# 检查后端是否运行
netstat -tlnp | grep 5000

# 开放5000端口
sudo ufw allow 5000

# 或临时关闭防火墙测试
sudo ufw disable
```

### 问题2：CORS跨域错误

**现象**：
```
Access to XMLHttpRequest at 'http://...:5000/api' from origin 'http://...:8080' 
has been blocked by CORS policy
```

**原因**：后端未配置CORS

**解决**：检查 `backend/app.py`
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 确保这行存在
```

### 问题3：API地址仍然是localhost

**现象**：浏览器控制台看到请求 `http://localhost:5000/api`

**原因**：
1. 缓存问题
2. 手动配置了window.API_BASE_URL

**解决**：
```bash
# 清除浏览器缓存
Ctrl + Shift + Delete

# 或强制刷新
Ctrl + F5 (Windows)
Cmd + Shift + R (Mac)

# 检查index.html中是否手动配置了API_BASE_URL
```

### 问题4：连接超时

**现象**：
```
timeout of XXXms exceeded
```

**可能原因**：
1. 后端未启动
2. 网络不通
3. 防火墙阻止

**排查步骤**：
```bash
# 1. 检查后端是否运行
ps aux | grep python
netstat -tlnp | grep 5000

# 2. 测试网络连通性
curl http://server-ip:5000/api/health

# 3. 检查防火墙
sudo ufw status
sudo iptables -L
```

## 📊 验证部署

### 1. 检查后端

```bash
# 方式1：curl测试
curl http://server-ip:5000/api/health

# 预期输出
{"status":"ok","timestamp":"2024-12-15T..."}

# 方式2：浏览器访问
http://server-ip:5000/api/health
```

### 2. 检查前端

```bash
# 浏览器访问
http://server-ip:8080

# F12打开开发者工具
# Console标签查看是否有错误
# Network标签查看API请求地址是否正确
```

### 3. 端到端测试

1. 访问前端页面
2. 填写漏洞信息
3. 点击"AI生成规则"
4. F12查看Network标签
5. 确认请求URL格式：`http://server-ip:5000/api/rules/generate`

## 🔐 安全建议

### 生产环境部署

1. **使用HTTPS**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ...
}
```

2. **限制访问IP**
```nginx
location /api {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://localhost:5000;
}
```

3. **添加认证**
```nginx
location /api {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # ...
}
```

4. **后端只监听本地**
```python
# app.py
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)  # 只监听本地
```

然后通过Nginx代理访问。

## 📝 部署清单

- [ ] 服务器环境准备（Python 3.8+）
- [ ] 创建虚拟环境
- [ ] 安装依赖
- [ ] 配置 .env 文件（API密钥）
- [ ] 启动后端服务
- [ ] 启动前端服务
- [ ] 配置防火墙（开放5000、8080端口）
- [ ] 测试API连通性
- [ ] 测试前端访问
- [ ] 端到端功能测试
- [ ] （可选）配置Nginx反向代理
- [ ] （可选）配置HTTPS
- [ ] （可选）配置域名解析

## 🎯 快速命令

```bash
# 完整部署流程（Linux/Kali）
cd /path/to/suricata_ai_gen

# 1. 自动部署
chmod +x setup.sh
./setup.sh

# 2. 配置API密钥
vim .env  # 设置 AI_API_KEY

# 3. 启动服务
chmod +x start_all.sh
./start_all.sh

# 4. 开放端口
sudo ufw allow 5000
sudo ufw allow 8080

# 5. 访问测试
curl http://localhost:5000/api/health
```

---

**提示**：大多数情况下，使用自动配置即可，无需手动修改代码！
