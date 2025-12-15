# 🚀 Nginx反向代理部署指南

## 📋 为什么使用Nginx反向代理？

### 问题场景

**直接访问方式的问题**：
```
前端: http://服务器IP:8080  ← 需要开放8080端口
后端: http://服务器IP:5000  ← 需要开放5000端口
```

**问题**：
1. ❌ 需要开放多个端口（8080、5000）
2. ❌ 防火墙配置复杂
3. ❌ 用户需要记住端口号
4. ❌ 无法使用HTTPS
5. ❌ 无法进行负载均衡
6. ❌ 静态文件需要独立的Web服务器

### Nginx反向代理的优势

**统一入口**：
```
用户访问: http://服务器IP  ← 只需80端口，无需端口号
   ↓
Nginx监听80端口
   ├─ / → frontend静态文件
   └─ /api → 代理到后端5000端口
```

**优势**：
1. ✅ 统一80端口访问，无需记忆端口
2. ✅ 后端可以只监听127.0.0.1（更安全）
3. ✅ 方便添加HTTPS
4. ✅ 支持负载均衡
5. ✅ Gzip压缩、缓存等优化
6. ✅ 隐藏后端架构细节

## 🚀 快速部署（推荐）

### 方式1：一键部署脚本

```bash
# 1. 确保项目已完成基础设置
./setup.sh

# 2. 运行Nginx部署脚本（需要sudo权限）
sudo ./deploy_nginx.sh

# 3. 访问
# 浏览器打开: http://服务器IP
```

**脚本会自动完成**：
- ✅ 安装Nginx（如果未安装）
- ✅ 创建并配置Nginx配置文件
- ✅ 启动后端服务
- ✅ 配置前端使用代理模式
- ✅ 开放防火墙端口
- ✅ 测试服务可用性

### 方式2：手动部署

适合需要自定义配置的场景。

## 📝 手动部署详细步骤

### 步骤1：安装Nginx

#### Kali/Debian/Ubuntu
```bash
sudo apt-get update
sudo apt-get install -y nginx
```

#### CentOS/RHEL
```bash
sudo yum install -y nginx
```

#### 验证安装
```bash
nginx -v
# 输出: nginx version: nginx/1.x.x
```

### 步骤2：配置Nginx

#### 2.1 编辑配置文件

项目已提供配置模板：`nginx/suricata_rule_gen.conf`

**修改配置中的路径**：

```bash
# 打开配置文件
vim nginx/suricata_rule_gen.conf

# 修改第26行，替换为实际项目路径
root /path/to/suricata_ai_gen/frontend;
# 改为：
root /home/kali/suricata_ai_gen/frontend;  # 替换为实际路径
```

#### 2.2 复制配置文件

**Kali/Debian/Ubuntu**：
```bash
# 复制配置文件
sudo cp nginx/suricata_rule_gen.conf /etc/nginx/sites-available/

# 创建软链接
sudo ln -s /etc/nginx/sites-available/suricata_rule_gen.conf \
            /etc/nginx/sites-enabled/

# 删除默认配置（可选）
sudo rm /etc/nginx/sites-enabled/default
```

**CentOS/RHEL**：
```bash
# 复制配置文件
sudo cp nginx/suricata_rule_gen.conf /etc/nginx/conf.d/
```

#### 2.3 测试Nginx配置

```bash
sudo nginx -t

# 正确输出：
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**如果出错**，检查：
- 路径是否正确
- 语法是否有误
- 端口是否被占用

### 步骤3：配置前端

前端需要告知使用Nginx代理，而不是直接访问后端。

#### 3.1 修改index.html

编辑 `frontend/index.html`，找到第11-14行：

```html
<!-- 当前（注释状态）-->
<script>
    // 使用Nginx反向代理时，取消下面的注释
    // window.USE_NGINX_PROXY = true;
```

**取消注释**，改为：

```html
<!-- 修改后 -->
<script>
    // 使用Nginx反向代理时，取消下面的注释
    window.USE_NGINX_PROXY = true;  ← 取消注释
```

#### 3.2 保存并验证

```bash
# 查看修改
grep "USE_NGINX_PROXY" frontend/index.html

# 应该看到（无注释符号）：
#     window.USE_NGINX_PROXY = true;
```

### 步骤4：启动后端服务

后端只需要监听本地127.0.0.1即可（更安全）。

```bash
# 激活虚拟环境
source .venv/bin/activate

# 后台启动后端
nohup python backend/app.py > backend.log 2>&1 &

# 记录进程ID
echo $! > backend.pid
```

#### 验证后端运行

```bash
# 测试本地API
curl http://127.0.0.1:5000/api/health

# 应该返回：
# {"status":"ok","timestamp":"..."}
```

### 步骤5：启动Nginx

```bash
# 启动Nginx
sudo systemctl start nginx

# 或重启
sudo systemctl restart nginx

# 设置开机自启
sudo systemctl enable nginx
```

#### 检查Nginx状态

```bash
sudo systemctl status nginx

# 应该看到：
# Active: active (running)
```

### 步骤6：配置防火墙

#### UFW (Ubuntu/Debian/Kali)
```bash
# 允许HTTP
sudo ufw allow 80/tcp

# 允许HTTPS（如果需要）
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status
```

#### Firewalld (CentOS/RHEL)
```bash
# 允许HTTP
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# 重载配置
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```

### 步骤7：测试访问

#### 7.1 本地测试

```bash
# 测试前端
curl -I http://localhost/

# 应该返回 200 OK

# 测试API代理
curl http://localhost/api/health

# 应该返回：
# {"status":"ok","timestamp":"..."}
```

#### 7.2 远程测试

```bash
# 获取服务器IP
ip addr show | grep "inet " | grep -v "127.0.0.1"
```

**在其他机器上**：
```bash
# Windows PowerShell
Invoke-WebRequest -Uri http://192.168.1.100/api/health

# Linux/Mac
curl http://192.168.1.100/api/health
```

#### 7.3 浏览器测试

1. **访问前端**：`http://服务器IP`
2. **F12打开开发者工具**
3. **查看Console**，应该看到：
   ```
   [API配置] Nginx反向代理模式: /api
   ```
   或
   ```
   [API配置] 检测到标准HTTP/HTTPS端口，使用相对路径: /api
   ```

4. **测试功能**：填写漏洞信息，点击"AI生成规则"
5. **查看Network标签**，API请求应该是：
   ```
   Request URL: http://服务器IP/api/rules/generate  ✅
   ```

## 🔍 故障排查

### 问题1: 页面404错误

**现象**：访问 `http://服务器IP` 返回404

**排查步骤**：

```bash
# 1. 检查Nginx配置中的root路径
grep "root" /etc/nginx/sites-available/suricata_rule_gen.conf

# 2. 确认路径存在且有index.html
ls -la /path/to/suricata_ai_gen/frontend/index.html

# 3. 检查Nginx错误日志
sudo tail -f /var/log/nginx/suricata_rule_gen_error.log
```

**解决方法**：
- 确保配置文件中的路径正确
- 确保Nginx有读取权限：`sudo chmod -R 755 frontend/`

### 问题2: API请求502错误

**现象**：前端能访问，但API请求返回502 Bad Gateway

**原因**：后端服务未运行或无法连接

**排查步骤**：

```bash
# 1. 检查后端是否运行
ps aux | grep "python.*backend/app.py"

# 2. 测试后端连接
curl http://127.0.0.1:5000/api/health

# 3. 检查Nginx错误日志
sudo tail -f /var/log/nginx/suricata_rule_gen_error.log
```

**解决方法**：
```bash
# 启动后端
source .venv/bin/activate
python backend/app.py &
```

### 问题3: 静态资源加载失败

**现象**：页面能打开，但样式丢失或功能异常

**排查**：F12查看Console和Network，看哪些资源加载失败

**常见原因**：
1. CDN资源被墙（Vue、Axios）
2. 路径配置错误

**解决方法**：
```bash
# 检查网络连接
curl -I https://unpkg.com/vue@3/dist/vue.global.js

# 如果CDN无法访问，考虑下载到本地
```

### 问题4: CORS错误（不应该出现）

**现象**：Console显示CORS跨域错误

**原因**：前端仍在使用完整URL而非相对路径

**检查**：
```bash
# 查看前端配置
grep "USE_NGINX_PROXY" frontend/index.html

# 应该是（无//注释符）：
#     window.USE_NGINX_PROXY = true;
```

**解决**：
```bash
# 取消USE_NGINX_PROXY的注释
sed -i 's|// window.USE_NGINX_PROXY = true;|window.USE_NGINX_PROXY = true;|g' frontend/index.html

# 清除浏览器缓存
# Ctrl+Shift+Delete → 清除缓存 → Ctrl+F5强制刷新
```

### 问题5: 防火墙阻止

**现象**：本地访问正常，远程无法访问

**排查**：
```bash
# 检查防火墙状态
sudo ufw status
# 或
sudo firewall-cmd --list-all

# 测试端口
sudo netstat -tlnp | grep :80
```

**解决**：
```bash
# 开放80端口
sudo ufw allow 80
# 或
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

## 📊 验证部署成功

### 完整验证清单

- [ ] Nginx服务运行正常：`systemctl status nginx`
- [ ] 后端服务运行正常：`curl http://127.0.0.1:5000/api/health`
- [ ] 本地前端访问正常：`curl -I http://localhost/`
- [ ] 本地API代理正常：`curl http://localhost/api/health`
- [ ] 远程前端访问正常：浏览器打开 `http://服务器IP`
- [ ] 远程API功能正常：测试"AI生成规则"功能
- [ ] Console显示正确配置：`[API配置] Nginx反向代理模式: /api`
- [ ] Network显示正确URL：`http://服务器IP/api/...`

### 成功标志

**Nginx状态**：
```bash
$ sudo systemctl status nginx
● nginx.service - A high performance web server
   Active: active (running)
```

**后端状态**：
```bash
$ curl http://127.0.0.1:5000/api/health
{"status":"ok","timestamp":"2024-12-15T..."}
```

**代理状态**：
```bash
$ curl http://localhost/api/health
{"status":"ok","timestamp":"2024-12-15T..."}
```

**浏览器Console**：
```
[API配置] Nginx反向代理模式: /api
```

**浏览器Network**：
```
Request URL: http://192.168.1.100/api/rules/generate
Status: 200 OK
```

## 🔐 安全加固（可选）

### 1. 配置HTTPS

```bash
# 使用Let's Encrypt免费证书
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 限制访问IP

编辑Nginx配置：
```nginx
location /api {
    # 只允许特定IP访问
    allow 192.168.1.0/24;
    deny all;
    
    proxy_pass http://127.0.0.1:5000/api;
    # ...
}
```

### 3. 添加HTTP基本认证

```bash
# 创建密码文件
sudo htpasswd -c /etc/nginx/.htpasswd admin

# 在Nginx配置中添加
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # ...
}
```

### 4. 限制请求速率

```nginx
# 在http块中添加
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# 在location /api中添加
limit_req zone=api_limit burst=20;
```

## 📝 日志管理

### 查看日志

```bash
# Nginx访问日志
sudo tail -f /var/log/nginx/suricata_rule_gen_access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/suricata_rule_gen_error.log

# 后端日志
tail -f backend.log
```

### 日志轮转

Nginx日志会自动轮转（由logrotate管理）。

后端日志需要手动管理：
```bash
# 创建logrotate配置
sudo vim /etc/logrotate.d/suricata_rule_gen

# 内容：
/path/to/suricata_ai_gen/backend.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## 🎯 常用管理命令

```bash
# === Nginx ===
sudo systemctl start nginx      # 启动
sudo systemctl stop nginx       # 停止
sudo systemctl restart nginx    # 重启
sudo systemctl reload nginx     # 重载配置（不中断服务）
sudo systemctl status nginx     # 查看状态
sudo nginx -t                   # 测试配置

# === 后端 ===
# 启动
source .venv/bin/activate
nohup python backend/app.py > backend.log 2>&1 &
echo $! > backend.pid

# 停止
kill $(cat backend.pid)

# 查看日志
tail -f backend.log

# === 防火墙 ===
sudo ufw allow 80              # 开放端口
sudo ufw status                # 查看状态

# === 系统 ===
sudo netstat -tlnp | grep :80  # 查看80端口
sudo netstat -tlnp | grep :5000 # 查看5000端口
ps aux | grep nginx            # Nginx进程
ps aux | grep python           # Python进程
```

## 🔄 回滚到直接访问模式

如果需要回退到之前的直接访问方式（前端8080，后端5000）：

```bash
# 1. 恢复前端配置
cd frontend
mv index.html.bak index.html  # 如果有备份

# 或手动注释
sed -i 's|window.USE_NGINX_PROXY = true;|// window.USE_NGINX_PROXY = true;|g' index.html

# 2. 停止Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# 3. 使用原始启动方式
./start_all.sh
```

## 📚 架构对比

### 直接访问模式
```
客户端浏览器
    ├─ http://服务器:8080  → Python HTTP Server (前端)
    └─ http://服务器:5000  → Flask (后端API)
    
需要开放: 8080, 5000 两个端口
```

### Nginx反向代理模式
```
客户端浏览器
    └─ http://服务器:80 (或 :443)
           ↓
       Nginx (监听80)
           ├─ /       → 静态文件 (frontend/)
           └─ /api    → 代理 → Flask (127.0.0.1:5000)
    
只需开放: 80 (HTTP) 或 443 (HTTPS)
后端监听: 127.0.0.1:5000 (仅本地，更安全)
```

---

**部署完成后，访问 `http://服务器IP` 即可使用！** 🎉
