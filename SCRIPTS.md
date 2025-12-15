# 启动脚本说明文档

本项目提供了完整的Windows和Linux启动脚本，方便在不同平台上快速启动应用。

## 📂 脚本清单

### Windows脚本
| 文件名 | 功能 | 说明 |
|--------|------|------|
| `start_all.bat` | 一键启动所有服务 | 同时启动后端和前端，自动打开浏览器 |
| `start_backend.bat` | 启动后端 | 启动Flask API服务 |
| `start_frontend.bat` | 启动前端 | 启动Vue3前端界面 |

### Linux脚本
| 文件名 | 功能 | 说明 |
|--------|------|------|
| `start_all.sh` | 一键启动所有服务 | 使用tmux/screen管理多窗口 |
| `start_backend.sh` | 启动后端 | 启动Flask API服务 |
| `start_frontend.sh` | 启动前端 | 启动Vue3前端界面 |
| `stop_all.sh` | 停止所有服务 | 停止所有运行中的服务 |

---

## 🪟 Windows使用指南

### 一键启动（推荐）

```batch
start_all.bat
```

**功能说明**：
- ✅ 自动检查虚拟环境
- ✅ 自动安装/更新依赖
- ✅ 开启两个窗口分别运行前后端
- ✅ 自动打开浏览器访问应用
- ✅ 显示访问URL和帮助信息

**输出示例**：
```
============================================
  Suricata Rule Generator - Start All
============================================

Starting Backend Server...
Starting Frontend Server...

============================================
  All services are starting...
============================================

  Backend:  http://localhost:5000
  Frontend: http://localhost:8080

  Open your browser and go to:
  http://localhost:8080

============================================
```

### 单独启动后端

```batch
start_backend.bat
```

**功能说明**：
- 检查虚拟环境
- 安装/更新Python依赖
- 启动Flask应用在5000端口

### 单独启动前端

```batch
start_frontend.bat
```

**功能说明**：
- 检查Python环境
- 启动HTTP服务器在8080端口
- 提供静态文件服务

---

## 🐧 Linux/Kali使用指南

### 首次使用准备

```bash
# 添加执行权限（只需一次）
chmod +x start_all.sh start_backend.sh start_frontend.sh stop_all.sh
```

### 一键启动（推荐）

```bash
./start_all.sh
```

**功能说明**：
- ✅ 自动检测并使用tmux/screen/后台进程
- ✅ 自动创建虚拟环境（如不存在）
- ✅ 自动安装/更新依赖
- ✅ 智能管理多窗口
- ✅ 自动尝试打开浏览器

**三种运行模式**：

#### 模式1：tmux（推荐）

如果系统安装了tmux：

```bash
# 安装tmux
sudo apt install tmux -y

# 启动应用
./start_all.sh
```

**tmux操作**：
- `Ctrl+B` 然后 `0` - 切换到后端窗口
- `Ctrl+B` 然后 `1` - 切换到前端窗口
- `Ctrl+B` 然后 `D` - 分离会话（服务继续运行）
- `tmux attach -t suricata_rule_gen` - 重新连接会话
- `tmux kill-session -t suricata_rule_gen` - 停止会话

**输出示例**：
```
============================================
   Services are starting in tmux...
============================================

   Backend:  http://localhost:5000
   Frontend: http://localhost:8080

   To attach to session: tmux attach -t suricata_rule_gen
   To switch windows: Ctrl+B then 0/1
   To detach: Ctrl+B then D
   To kill session: tmux kill-session -t suricata_rule_gen

============================================
```

#### 模式2：screen

如果没有tmux但有screen：

```bash
# 安装screen
sudo apt install screen -y

# 启动应用
./start_all.sh
```

**screen操作**：
- `screen -r suricata_rule_gen_backend` - 查看后端
- `screen -r suricata_rule_gen_frontend` - 查看前端
- `Ctrl+A` 然后 `D` - 分离会话
- `screen -S <session_name> -X quit` - 停止会话

#### 模式3：后台进程

如果都没有，会在后台启动：

```bash
./start_all.sh
```

**输出示例**：
```
============================================
   Services Started
============================================

   Backend PID:  12345
   Frontend PID: 12346

   Backend:  http://localhost:5000
   Frontend: http://localhost:8080

   To stop services:
   kill 12345 12346

============================================

Press Ctrl+C to stop all services...
```

### 单独启动后端

```bash
./start_backend.sh
```

**功能说明**：
- 自动创建/激活虚拟环境
- 安装Python依赖
- 启动Flask应用

### 单独启动前端

```bash
./start_frontend.sh
```

**功能说明**：
- 检查Python环境
- 启动HTTP服务器
- 提供前端静态文件

### 停止所有服务

```bash
./stop_all.sh
```

**功能说明**：
- ✅ 停止tmux会话
- ✅ 停止screen会话
- ✅ 杀死5000和8080端口的进程
- ✅ 显示详细的停止信息

**输出示例**：
```
============================================
   Stopping Suricata Rule Generator
============================================

Stopping tmux session...
✓ Tmux session stopped

Checking for processes on ports 5000 and 8080...
Killing backend process (PID: 12345)...
✓ Backend stopped
Killing frontend process (PID: 12346)...
✓ Frontend stopped

============================================
   All services stopped
============================================
```

---

## 🔧 脚本技术细节

### start_backend.sh

**核心逻辑**：
```bash
1. 获取脚本目录
2. 检查/创建虚拟环境
3. 激活虚拟环境
4. 安装依赖
5. 启动Flask应用
```

**错误处理**：
- 虚拟环境创建失败 → 退出并提示
- 激活失败 → 退出并提示
- 依赖安装失败 → 退出并提示

### start_frontend.sh

**核心逻辑**：
```bash
1. 获取脚本目录
2. 切换到frontend目录
3. 检查Python3
4. 启动HTTP服务器
```

**错误处理**：
- Python3未安装 → 退出并提示

### start_all.sh

**核心逻辑**：
```bash
1. 添加脚本执行权限
2. 检测可用的终端管理工具
3. 根据工具选择启动方式：
   - tmux: 创建会话和窗口
   - screen: 创建后台会话
   - 无: 后台进程方式
4. 尝试打开浏览器
5. 附加到会话或等待中断
```

**智能检测**：
```bash
if command -v tmux &> /dev/null; then
    # 使用tmux
elif command -v screen &> /dev/null; then
    # 使用screen
else
    # 使用后台进程
fi
```

### stop_all.sh

**核心逻辑**：
```bash
1. 检查并停止tmux会话
2. 检查并停止screen会话
3. 通过lsof查找端口占用
4. 杀死对应进程
5. 显示停止状态
```

**端口检测**：
```bash
BACKEND_PID=$(lsof -ti:5000 2>/dev/null)
FRONTEND_PID=$(lsof -ti:8080 2>/dev/null)
```

---

## 📝 使用场景

### 场景1：开发环境（Windows）

```batch
# 首次运行
start_all.bat

# 后续调试时分别启动
start_backend.bat  # 终端1
start_frontend.bat # 终端2
```

### 场景2：生产环境（Kali Linux）

```bash
# 使用tmux持久运行
./start_all.sh

# 分离会话
Ctrl+B, D

# 稍后重新连接
tmux attach -t suricata_rule_gen

# 查看日志
Ctrl+B, 0  # 后端日志
Ctrl+B, 1  # 前端日志
```

### 场景3：测试环境（Linux服务器）

```bash
# 后台运行
./start_all.sh

# 检查服务状态
curl http://localhost:5000/api/health
curl http://localhost:8080

# 停止服务
./stop_all.sh
```

---

## 🚨 常见问题

### Q1: Windows上双击bat文件闪退？

**A**: 右键 → "以管理员身份运行" 或在终端中运行查看错误信息

### Q2: Linux提示"Permission denied"？

**A**: 添加执行权限
```bash
chmod +x *.sh
```

### Q3: 端口被占用？

**A**: 
```bash
# Linux
sudo lsof -ti:5000 | xargs kill -9
sudo lsof -ti:8080 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Q4: tmux/screen未安装？

**A**: 
```bash
# Debian/Ubuntu/Kali
sudo apt install tmux -y

# 或
sudo apt install screen -y
```

### Q5: 虚拟环境创建失败？

**A**: 
```bash
# 确保python3-venv已安装
sudo apt install python3-venv -y

# 手动创建
python3 -m venv .venv
```

---

## 💡 最佳实践

### 开发时

1. **使用分别启动**便于调试
   ```bash
   # 终端1
   ./start_backend.sh
   
   # 终端2
   ./start_frontend.sh
   ```

2. **修改代码后**重启对应服务
   ```bash
   Ctrl+C  # 停止
   ./start_backend.sh  # 重新启动
   ```

### 部署时

1. **使用tmux持久运行**
   ```bash
   ./start_all.sh
   # 分离会话
   Ctrl+B, D
   ```

2. **定期检查服务状态**
   ```bash
   tmux ls  # 查看会话列表
   tmux attach -t suricata_rule_gen  # 连接查看
   ```

3. **优雅停止**
   ```bash
   ./stop_all.sh
   ```

---

## 🎯 快速参考

### Windows

```batch
start_all.bat          # 一键启动
start_backend.bat      # 只启动后端
start_frontend.bat     # 只启动前端
```

### Linux

```bash
./start_all.sh         # 一键启动
./start_backend.sh     # 只启动后端
./start_frontend.sh    # 只启动前端
./stop_all.sh          # 停止所有
```

### tmux快捷键

```
Ctrl+B, 0    切换到窗口0（后端）
Ctrl+B, 1    切换到窗口1（前端）
Ctrl+B, D    分离会话
Ctrl+B, [    进入滚动模式
Ctrl+C       退出滚动模式
```

### 服务端口

```
后端API:  http://localhost:5000
前端界面: http://localhost:8080
```

---

**提示**：首次使用建议先阅读 [QUICKSTART.md](QUICKSTART.md) 快速上手指南。
