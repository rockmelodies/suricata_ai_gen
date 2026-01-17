<div align="center">

# 🛡️ Suricata规则生成与验证工具

### 基于AI的智能Suricata规则生成、优化与自动化验证平台

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version"></a>
  <a href="#"><img src="https://img.shields.io/badge/Flask-3.0.0-green.svg" alt="Flask"></a>
  <a href="#"><img src="https://img.shields.io/badge/Vue-3.0-brightgreen.svg" alt="Vue3"></a>
  <a href="#"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg" alt="Platform"></a>
  <a href="https://github.com/rockmelodies/suricata_ai_gen/stargazers"><img src="https://img.shields.io/github/stars/rockmelodies/suricata_ai_gen?style=social" alt="GitHub stars"></a>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用指南">使用指南</a> •
  <a href="#api接口文档">API文档</a> •
  <a href="#贡献指南">贡献</a>
</p>

<p align="center">
  <a href="README.md">简体中文</a> |
  <a href="README_EN.md">English</a>
</p>

---

<img src="https://img.shields.io/badge/Status-Active-success" alt="Status">
<img src="https://img.shields.io/badge/Maintained-Yes-brightgreen" alt="Maintained">
<img src="https://img.shields.io/badge/AI%20Powered-360GPT-ff69b4" alt="AI Powered">

</div>

## 功能特性

### 🚀 V2.0 新特性

- 🔐 **JWT认证** - 完整的用户认证和授权系统
- 👥 **用户管理** - 用户注册、登录、权限管理
- 📖 **OpenAPI规范** - 符合OpenAPI 3.0标准，自动生成Swagger文档
- 🎯 **RESTful API** - 基于Flask-RESTX的标准化API设计
- 🔄 **前后端分离** - Vue3 + TypeScript + Element Plus现代化前端

### ✨ 核心功能

✨ **AI智能生成** - 基于360AI大模型，根据漏洞描述自动生成Suricata规则  
🔧 **规则优化** - AI辅助优化规则，提高检测准确率  
✅ **自动验证** - 集成Suricata引擎，自动验证规则有效性  
📊 **数据管理** - SQLite数据库存储规则历史和验证结果  
🎨 **友好界面** - Vue3前端，简洁美观的用户界面  

![img.png](img.png)

![img_3.png](img_3.png)

## 系统架构

```
suricata_ai_gen/
├── backend/              # 后端服务 (Python + Flask)
│   ├── app.py           # Flask主应用 (旧版)
│   ├── app_v2.py        # Flask-RESTX API (v2.0 OpenAPI)
│   ├── user_model.py    # 用户模型
│   ├── ai_client.py     # 360AI客户端
│   ├── database.py      # 数据库管理
│   ├── suricata_validator.py  # Suricata验证器
│   ├── requirements.txt # Python依赖
│   ├── start_v2.sh      # v2.0 启动脚本
│   └── test_api.py      # API测试脚本
├── frontend/            # 前端界面 (旧版 Vue3)
│   └── index.html      # 单页应用
├── frontend-vue3/       # 新版前端 (Vue3 + TS + Element Plus)
│   ├── src/
│   │   ├── api/           # API接口封装
│   │   ├── components/    # 公共组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # Pinia状态管理
│   │   ├── views/         # 页面组件
│   │   └── main.ts        # 入口文件
│   ├── vite.config.ts   # Vite配置
│   └── package.json     # 项目依赖
├── openapi.yaml         # OpenAPI 3.0 规范文档
├── .env                 # 环境变量配置
└── README.md            # 项目说明
```

## 环境要求

### Windows开发环境
- Python 3.8+
- 浏览器 (Chrome/Edge/Firefox)
- **Suricata 6.0+**（可选，用于规则验证）

### Kali Linux验证环境 (可选)
- Suricata 6.0+
- PCAP测试文件

### LLM模型支持

本项目支持多种大型语言模型提供商，包括：

- **OpenAI**: GPT系列模型
- **Google Gemini**: Gemini系列模型
- **Anthropic Claude**: Claude系列模型
- **阿里通义千问**: Qwen系列模型
- **DeepSeek**: DeepSeek系列模型
- **智谱AI**: GLM系列模型
- **月之暗面**: Moonshot系列模型
- **百度文心一言**: ERNIE Bot系列
- **MiniMax**: Abab系列模型
- **字节豆包**: Doubao系列模型
- **Ollama**: 本地模型
- **360智脑**: 360gpt系列模型

每种模型都有其特点和优势，可以根据具体需求选择最合适的模型。

### 👉 Windows上Suricata安装和配置

#### 1. 下载Suricata

访问官方网站下载Windows版本：
- 官方网站：https://suricata.io/download/
- Windows安装包：https://www.openinfosecfoundation.org/download/windows/

或使用Chocolatey安装：
```powershell
# 以管理员身份运行PowerShell
choco install suricata
```

#### 2. 安装Suricata

**方式1：使用安装包**

1. 运行下载的 `.msi` 安装程序
2. 默认安装路径：`C:\Program Files\Suricata`
3. 安装过程中选择添加到PATH环境变量

**方式2：解压版**

1. 下载ZIP包并解压到指定目录，如：`C:\Suricata`
2. 手动配置环境变量（见下文）

#### 3. 配置环境变量

**步骤1：添加Suricata到PATH**

1. 右键“此电脑” → “属性” → “高级系统设置”
2. 点击“环境变量”
3. 在“系统变量”中找到 `Path`，点击“编辑”
4. 点击“新建”，添加：`C:\Program Files\Suricata\bin`
5. 点击“确定”保存

**步骤2：验证安装**

打开CMD或PowerShell，运行：
```powershell
suricata --version
```

应该显示类似于：
```
This is Suricata version 7.0.0
```

#### 4. 创建PCAP目录

创建用于存放测试PCAP文件的目录：
```powershell
mkdir C:\pcap_check
```

#### 5. 配置.env文件

打开 `.env` 文件，取消Windows配置的注释并修改为实际路径：

```bash
# Suricata Configuration
# Windows配置（取消注释）：
SURICATA_RULES_DIR=C:\Program Files\Suricata\rules
SURICATA_CONFIG=C:\Program Files\Suricata\suricata.yaml
SURICATA_LOG_DIR=C:\Program Files\Suricata\log
PCAP_DIR=C:\pcap_check

# Linux/Kali配置（注释掉）：
# SURICATA_RULES_DIR=/var/lib/suricata/rules
# SURICATA_CONFIG=/etc/suricata/suricata.yaml
# SURICATA_LOG_DIR=/var/log/suricata
# PCAP_DIR=/home/kali/pcap_check
```

**注意事项**：
- Windows路径使用反斜杠 `\` 或双反斜杠 `\\`
- 路径中包含空格时不需要引号
- 确保目录存在且有读写权限

#### 6. 验证配置

启动后端服务，检查是否能正常读取Suricata配置：
```powershell
# 激活虚拟环境
.venv\Scripts\activate

# 启动后端
python backend/app.py
```

如果配置正确，不会有错误提示。

#### 7. 常见问题

**问题1：找不到suricata命令**
```powershell
# 检查PATH环境变量是否正确配置
echo %PATH%

# 或使用完整路径
"C:\Program Files\Suricata\bin\suricata.exe" --version
```

**问题2：Suricata启动失败**
```powershell
# 检查配置文件是否存在
dir "C:\Program Files\Suricata\suricata.yaml"

# 检查日志目录权限
dir "C:\Program Files\Suricata\log"
```

**问题3：PCAP文件读取失败**
```powershell
# 确保目录存在
mkdir C:\pcap_check

# 确保有读写权限
icacls C:\pcap_check /grant Everyone:F
```

## 📦 部署说明

### Python虚拟环境配置

**⚠️ 重要：首次使用前必须创建虚拟环境！**

虚拟环境可以隔离项目依赖，避免与系统Python包冲突。

#### Windows环境

```bash
# 1. 检查Python版本（需要3.8+）
python --version

# 2. 进入项目目录
cd F:\data\suricata_ai_gen

# 3. 创建虚拟环境
python -m venv .venv

# 4. 激活虚拟环境
.venv\Scripts\activate

# 激活成功后，命令行前面会显示 (.venv)

# 5. 升级pip（推荐）
python -m pip install --upgrade pip

# 6. 安装项目依赖
pip install -r backend\requirements.txt

# 7. 验证安装
pip list
```

#### Linux/Kali环境

```bash
# 1. 检查Python版本
python3 --version

# 2. 安装venv（如果没有）
sudo apt update
sudo apt install python3-venv python3-pip -y

# 3. 进入项目目录
cd /path/to/suricata_ai_gen

# 4. 创建虚拟环境
python3 -m venv .venv

# 5. 激活虚拟环境
source .venv/bin/activate

# 激活成功后，命令行前面会显示 (.venv)

# 6. 升级pip
pip install --upgrade pip

# 7. 安装项目依赖
pip install -r backend/requirements.txt

# 8. 验证安装
pip list
```

#### 虚拟环境常用操作

```bash
# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux
source .venv/bin/activate

# 退出虚拟环境
deactivate

# 删除虚拟环境（如需重新创建）
# Windows
rmdir /s .venv
# Linux
rm -rf .venv

# 查看已安装的包
pip list

# 导出依赖列表
pip freeze > requirements.txt
```

### Linux/Kali环境部署最佳实践

#### 1. 系统准备

**检查系统兼容性：**
```bash
# 检查操作系统版本
lsb_release -a

# 检查可用内存（建议至少4GB）
free -h

# 检查磁盘空间（建议至少10GB可用空间）
df -h
```

**更新系统包：**
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. 安全配置

**创建专用用户（推荐）：**
```bash
# 创建专用用户
sudo useradd -m -s /bin/bash suricata-ai

# 将用户添加到sudo组
sudo usermod -aG sudo suricata-ai

# 切换到专用用户
sudo su - suricata-ai
```

**设置目录权限：**
```bash
# 创建项目目录
mkdir -p ~/projects/suricata_ai_gen
cd ~/projects/suricata_ai_gen
```

#### 3. 环境变量配置

**使用环境文件：**
```bash
# 创建环境配置文件
touch ~/.suricata-ai-env

# 添加到 ~/.bashrc 或 ~/.zshrc
export SURICATA_AI_ENV_FILE="$HOME/.suricata-ai-env"
```

**配置环境变量：**
```bash
# 编辑环境变量文件
vim ~/.suricata-ai-env

# 添加以下内容
export AI_API_KEY="your_360_api_key_here"
export DB_PATH="/home/suricata-ai/data/suricata_rules.db"
export PCAP_DIR="/home/suricata-ai/pcap_data"
export LOG_DIR="/home/suricata-ai/logs"
```

**加载环境变量：**
```bash
source ~/.suricata-ai-env
```

#### 4. 日志和监控

**创建日志目录：**
```bash
mkdir -p /home/suricata-ai/logs
```

**配置日志轮转：**
```bash
sudo tee /etc/logrotate.d/suricata-ai <<EOF
/home/suricata-ai/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

#### 5. 后台服务管理

**使用systemd管理服务（生产环境推荐）：**

创建服务文件：
```bash
sudo tee /etc/systemd/system/suricata-ai-backend.service <<EOF
[Unit]
Description=Suricata AI Backend Service
After=network.target

[Service]
Type=simple
User=suricata-ai
Group=suricata-ai
WorkingDirectory=/home/suricata-ai/projects/suricata_ai_gen/backend
Environment=PATH=/home/suricata-ai/projects/suricata_ai_gen/.venv/bin
EnvironmentFile=/home/suricata-ai/.suricata-ai-env
ExecStart=/home/suricata-ai/projects/suricata_ai_gen/.venv/bin/python app_v2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=suricata-ai

[Install]
WantedBy=multi-user.target
EOF
```

**启用和启动服务：**
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable suricata-ai-backend

# 启动服务
sudo systemctl start suricata-ai-backend

# 检查服务状态
sudo systemctl status suricata-ai-backend

# 查看服务日志
sudo journalctl -u suricata-ai-backend -f
```

#### 6. 防火墙配置

**配置UFW防火墙：**
```bash
# 安装UFW
sudo apt install ufw -y

# 允许SSH（必须）
sudo ufw allow ssh

# 允许HTTP和HTTPS（如果需要）
sudo ufw allow 'Apache Full'

# 允许应用端口
sudo ufw allow 5000/tcp  # 后端API
sudo ufw allow 5173/tcp  # 前端开发服务器

# 启用防火墙
sudo ufw enable

# 检查状态
sudo ufw status verbose
```

#### 7. 备份策略

**创建备份脚本：**
```bash
#!/bin/bash

# 备份脚本 backup_suricata_ai.sh
BACKUP_DIR="/home/suricata-ai/backups"
DATA_DIR="/home/suricata-ai/data"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp $DATA_DIR/suricata_rules.db $BACKUP_DIR/suricata_rules_$DATE.db

# 备份配置
cp -r /home/suricata-ai/projects/suricata_ai_gen/.env $BACKUP_DIR/config_$DATE/

# 清理超过30天的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "config_*" -mtime +30 -delete
```

**设置定时备份：**
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /home/suricata-ai/scripts/backup_suricata_ai.sh
```

这些Linux/Kali环境的最佳实践将帮助您建立一个稳定、安全且易于维护的部署环境。
### 常见问题排查

#### 问题1：虚拟环境创建失败

**现象**：
```
Error: [WinError 5] 拒绝访问
```

**解决方法**：
```bash
# Windows: 以管理员身份运行PowerShell/CMD
# 或者检查Python安装路径权限
```

#### 问题2：无法激活虚拟环境（Windows PowerShell）

**现象**：
```
无法加载文件 .venv\Scripts\Activate.ps1，因为在此系统上禁止运行脚本
```

**解决方法**：
```powershell
# 方法1: 临时允许执行脚本
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 方法2: 使用CMD而不是PowerShell
cmd
.venv\Scripts\activate.bat

# 方法3: 使用Git Bash
source .venv/Scripts/activate
```

#### 问题3：pip安装依赖失败

**现象**：
```
ERROR: Could not find a version that satisfies the requirement...
```

**解决方法**：
```bash
# 1. 检查Python版本是否>=3.8
python --version

# 2. 升级pip
python -m pip install --upgrade pip

# 3. 使用国内镜像源加速
pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或配置永久镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 问题4：依赖包版本冲突

**解决方法**：
```bash
# 1. 删除现有虚拟环境
rm -rf .venv  # Linux
rmdir /s .venv  # Windows

# 2. 重新创建虚拟环境
python -m venv .venv

# 3. 激活并安装
source .venv/bin/activate  # Linux
.venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt
```

### 自动化部署脚本

#### Windows一键部署脚本

创建 `setup.bat` 文件：
```batch
@echo off
echo ========================================
echo   Suricata规则生成工具 - 自动部署
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/5] 检测Python版本...
python --version

echo.
echo [2/5] 创建虚拟环境...
if exist .venv (
    echo 虚拟环境已存在，跳过创建
) else (
    python -m venv .venv
    echo 虚拟环境创建成功
)

echo.
echo [3/5] 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo [4/5] 升级pip...
python -m pip install --upgrade pip

echo.
echo [5/5] 安装依赖包...
pip install -r backend\requirements.txt

echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 复制 .env.example 为 .env
echo 2. 编辑 .env 文件，配置API密钥
echo 3. 运行 start_all.bat 启动服务
echo.
pause
```

#### Linux一键部署脚本

创建 `setup.sh` 文件：
```bash
#!/bin/bash

echo "========================================"
echo "  Suricata规则生成工具 - 自动部署"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python3未安装"
    echo "请执行: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

echo "[1/5] 检测Python版本..."
python3 --version

echo ""
echo "[2/5] 创建虚拟环境..."
if [ -d ".venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv .venv
    echo "虚拟环境创建成功"
fi

echo ""
echo "[3/5] 激活虚拟环境..."
source .venv/bin/activate

echo ""
echo "[4/5] 升级pip..."
pip install --upgrade pip

echo ""
echo "[5/5] 安装依赖包..."
pip install -r backend/requirements.txt

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. cp .env.example .env"
echo "2. 编辑 .env 文件，配置API密钥"
echo "3. 运行 ./start_all.sh 启动服务"
echo ""
```

使用方法：
```bash
# Windows
setup.bat

# Linux
chmod +x setup.sh
./setup.sh
```

## 快速开始

### 🆕 方式1：V2.0 OpenAPI版本（推荐）

#### 1. 克隆项目

```bash
git clone https://github.com/rockmelodies/suricata_ai_gen.git
cd suricata_ai_gen
```

#### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# =============================================
# 安全配置
# =============================================
# JWT 签名密钥 - 生产环境必须修改为随机字符串！
# 建议使用: openssl rand -hex 32
SECRET_KEY=ffe39a6f6a5cef863cbc8dd09eacb85e050ebb78bc107a519918f49a3b0faafb

# JWT 加密算法
ALGORITHM=HS256

# Token 过期时间（分钟），默认 8 天
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# =============================================
# LLM 通用配置
# =============================================
# 支持的 provider:
# - LiteLLM 适配器: openai, gemini, claude, qwen, deepseek, zhipu, moonshot, ollama
# - 原生适配器: baidu, minimax, doubao
LLM_PROVIDER=openai

# API 密钥
#LLM_API_KEY=sk-0010d2d1eb5348648be01592c550fa5d
LLM_API_KEY=your_api_key_here

# 模型名称（留空使用 provider 默认模型）
# OpenAI: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
# Gemini: gemini-2.0-flash, gemini-1.5-pro
# Claude: claude-3-5-sonnet-20241022, claude-3-haiku-20240307
# Qwen: qwen-turbo, qwen-plus, qwen-max
# DeepSeek: deepseek-chat, deepseek-coder
# Zhipu: glm-4-flash, glm-4
# Moonshot: moonshot-v1-8k, moonshot-v1-32k
# Ollama: llama3, codellama, qwen2.5, deepseek-coder
#LLM_MODEL=deepseek-coder
LLM_MODEL=360gpt-pro

# 自定义 API 端点（API 中转站）
# 示例: https://your-proxy.com/v1
#LLM_BASE_URL=https://api.deepseek.com/v1
LLM_BASE_URL=https://api.360.cn/v1

# 请求超时时间（秒）
LLM_TIMEOUT=150

# 生成温度（0-1，越低越确定性）
LLM_TEMPERATURE=0.1

# 最大生成 Token 数
LLM_MAX_TOKENS=4096

# 360 AI API Configuration (向后兼容)
AI_API_KEY=your_api_key_here
AI_MODEL=360gpt-pro

# Database Configuration
DB_PATH=backend/suricata_rules.db

# Suricata Configuration (Linux)
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_CONFIG=/etc/suricata/suricata.yaml
SURICATA_LOG_DIR=/var/log/suricata
PCAP_DIR=/home/kali/pcap_check
```

#### 3. 启动后端服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# Windows
start_v2.bat

# Linux/Kali
bash start_v2.sh
```

#### 4. 启动前端服务

```bash
cd frontend-vue3

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

#### 5. 访问应用

- **前端应用**：http://localhost:5173
- **Swagger文档**：http://localhost:5000/api/docs
- **API地址**：http://localhost:5000/api
- **OpenAPI规范**：[openapi.yaml](openapi.yaml)

#### 6. 默认管理员账户

- 👤 用户名：`admin`
- 🔑 密码：`admin123`

⚠️ **重要**：生产环境请立即修改默认密码！

#### 7. 功能使用

登录后您可以：

1. **生成验证一体化**：在同一页面完成规则生成和验证（推荐）
2. **生成规则**：输入漏洞信息，使用AI生成Suricata规则
3. **规则列表**：查看、管理、优化已生成的规则
4. **验证规则**：使用PCAP文件验证规则有效性
5. **用户管理**（仅管理员）：管理系统用户

#### 8. API使用示例

```bash
# 1. 用户登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 使用token访问API
curl -X GET http://localhost:5000/api/rules \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 3. 生成规则
curl -X POST http://localhost:5000/api/rules/generate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"vuln_name":"SQL注入","vuln_description":"测试漏洞"}'
```

---

### 🐧 Linux/Kali快速部署

如果您在Linux或Kali环境下部署，我们提供了一键部署脚本：

#### 1. 自动化部署脚本

**创建并运行部署脚本：**

```bash
#!/bin/bash

# Linux/Kali一键部署脚本

echo "========================================"
echo "  Suricata规则生成工具 - Linux/Kali快速部署"
echo "========================================"
echo ""

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
  echo "[警告] 请不要以root用户运行此脚本"
  exit 1
fi

# 检查必要软件
check_dependencies() {
  local deps=("python3" "python3-pip" "nodejs" "npm" "git" "suricata")
  for dep in "${deps[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
      echo "[错误] $dep 未安装"
      return 1
    fi
  done
}

# 安装依赖
install_dependencies() {
  echo "[1/6] 检查系统依赖..."
  if check_dependencies; then
    echo "所有依赖已安装"
  else
    echo "正在安装依赖..."
    sudo apt update
    sudo apt install python3 python3-venv python3-pip nodejs npm git suricata -y
  fi
}

# 克隆项目
clone_project() {
  echo ""
  echo "[2/6] 克隆项目..."
  if [ -d "suricata_ai_gen" ]; then
    echo "项目目录已存在，跳过克隆"
    cd suricata_ai_gen
  else
    git clone https://github.com/rockmelodies/suricata_ai_gen.git
    cd suricata_ai_gen
  fi
}

# 创建虚拟环境
setup_virtualenv() {
  echo ""
  echo "[3/6] 创建虚拟环境..."
  if [ -d ".venv" ]; then
    echo "虚拟环境已存在，跳过创建"
  else
    python3 -m venv .venv
    echo "虚拟环境创建成功"
  fi
}

# 安装Python依赖
install_python_deps() {
  echo ""
  echo "[4/6] 激活虚拟环境并安装Python依赖..."
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r backend/requirements.txt
}

# 安装前端依赖
install_frontend_deps() {
  echo ""
  echo "[5/6] 安装前端依赖..."
  cd frontend-vue3
  npm install
  cd ..
}

# 配置环境变量
setup_env() {
  echo ""
  echo "[6/6] 配置环境变量..."
  if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "已创建 .env 配置文件，请编辑其中的AI_API_KEY等参数"
  else
    echo ".env 文件已存在"
  fi
  
  # 确保使用Linux路径配置
  sed -i 's/^SURICATA_RULES_DIR=.*/SURICATA_RULES_DIR=\/var\/lib\/suricata\/rules/' .env
  sed -i 's/^SURICATA_CONFIG=.*/SURICATA_CONFIG=\/etc\/suricata\/suricata.yaml/' .env
  sed -i 's/^SURICATA_LOG_DIR=.*/SURICATA_LOG_DIR=\/var\/log\/suricata/' .env
  sed -i 's/^PCAP_DIR=.*/PCAP_DIR=\/home\/kali\/pcap_check/' .env
  
  # 配置LLM提供商（如果需要）
  if ! grep -q "LLM_PROVIDER" .env; then
    echo "LLM_PROVIDER=openai" >> .env
    echo "LLM_API_KEY=your_api_key_here" >> .env
    echo "LLM_MODEL=gpt-4o-mini" >> .env
    echo "LLM_BASE_URL=https://api.openai.com/v1" >> .env
  fi
  
  # 确保数据库目录和文件存在
  mkdir -p backend/
  touch backend/suricata_rules.db
  chmod 664 backend/suricata_rules.db
  
  # 确保上传目录存在
  mkdir -p uploads/
  chmod 755 uploads/
}

# 创建PCAP目录
setup_pcap_dir() {
  echo "创建PCAP测试目录..."
  mkdir -p /home/kali/pcap_check
}

# 主流程
main() {
  install_dependencies
  clone_project
  setup_virtualenv
  install_python_deps
  install_frontend_deps
  setup_env
  setup_pcap_dir
  
  echo ""
  echo "========================================"
  echo "  部署完成！"
  echo "========================================"
  echo ""
  echo "下一步操作："
  echo "1. 编辑 .env 文件，配置您的AI_API_KEY"
  echo "   vim .env"
  echo "2. 启动后端服务"
  echo "   cd backend && source ../.venv/bin/activate && python app_v2.py"
  echo "3. 启动前端服务"
  echo "   cd frontend-vue3 && npm run dev"
  echo ""
  echo "或者使用一键启动脚本："
  echo "chmod +x start_all.sh && ./start_all.sh"
  echo ""
  echo "对于Kali Linux环境，我们还提供了专门的启动脚本："
  echo "chmod +x start_kali.sh && ./start_kali.sh"
  echo ""
}

# 运行主流程
main
```

**保存为 `deploy_linux.sh` 并运行：**

```bash
chmod +x deploy_linux.sh
./deploy_linux.sh
```

#### 2. Docker部署（可选）

如果您希望使用Docker部署，可以创建以下Dockerfile：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    suricata \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 创建PCAP目录
RUN mkdir -p /home/kali/pcap_check

# 暴露端口
EXPOSE 5000 5173

# 启动命令
CMD ["python", "backend/app_v2.py"]
```

**构建和运行Docker容器：**

```bash
# 构建镜像
docker build -t suricata-ai-gen .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -p 5173:5173 \
  -v ./pcap_data:/home/kali/pcap_check \
  -v ./config:/app/config \
  --name suricata-ai-container \
  suricata-ai-gen
```

#### 3. Kali Linux特定优化

对于Kali Linux环境，我们建议进行以下优化配置：

**启用Suricata服务：**
```bash
# 启用Suricata服务
sudo systemctl enable suricata
sudo systemctl start suricata

# 检查服务状态
sudo systemctl status suricata
```

**解决数据库权限问题（关键步骤）：**
```bash
# 确保项目目录权限正确
mkdir -p /home/kali/suricata_ai_gen/backend
chmod -R 755 /home/kali/suricata_ai_gen/

# 创建并设置数据库文件权限
touch /home/kali/suricata_ai_gen/backend/suricata_rules.db
chmod 664 /home/kali/suricata_ai_gen/backend/suricata_rules.db

# 或者，如果使用当前目录作为项目目录
mkdir -p backend/
touch backend/suricata_rules.db
chmod 664 backend/suricata_rules.db
```

**配置Suricata规则更新：**
```bash
# 安装suricata-update
sudo apt install suricata-update

# 添加规则源
sudo suricata-update enable-source oisf/trafficid
sudo suricata-update enable-source et/open

# 更新规则
sudo suricata-update update

# 重新加载规则
sudo suricata-update reload
```

**配置高性能模式（可选）：**
```bash
# 编辑Suricata配置
sudo vim /etc/suricata/suricata.yaml

# 在配置文件中启用多线程模式
threading:
  set-cpu-affinity: no
  detect-thread-ratio: 1.0
```

通过以上快速部署方式，您可以在Linux/Kali环境下快速搭建Suricata规则生成与验证工具。

---

### 🔸 方式2：使用旧版本

### 1. 配置环境变量

**重要：为了安全，请先配置API密钥**

复制环境变量示例文件：
```bash
# Windows
copy .env.example .env

# Linux
cp .env.example .env
```

编辑 `.env` 文件，设置您的AI API密钥：
```bash
# 360 AI API Configuration
AI_API_KEY=your_api_key_here  # 请替换为您的真实API密钥
AI_MODEL=360gpt-pro

# Database Configuration
DB_PATH=backend/suricata_rules.db

# Suricata Configuration
# Linux/Kali配置：
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_CONFIG=/etc/suricata/suricata.yaml
SURICATA_LOG_DIR=/var/log/suricata
PCAP_DIR=/home/kali/pcap_check

# Windows配置（修改为实际安装路径）：
# SURICATA_RULES_DIR=C:\Program Files\Suricata\rules
# SURICATA_CONFIG=C:\Program Files\Suricata\suricata.yaml
# SURICATA_LOG_DIR=C:\Program Files\Suricata\log
# PCAP_DIR=C:\pcap_check
```

**⚠️ 安全提示**：
- `.env` 文件已加入 `.gitignore`，不会被提交到Git仓库
- 请勿在代码中硬编码API密钥
- 不要将 `.env` 文件分享给他人

### 2. 安装依赖

首先确保已经创建Python虚拟环境：
```bash
python -m venv .venv
```

激活虚拟环境：
```bash
# Windows
.venv\Scripts\activate

# Linux
source .venv/bin/activate
```

安装后端依赖（包含python-dotenv）：
```bash
pip install -r backend\requirements.txt
```

### 3. 启动后端服务

**Windows:**
```bash
start_backend.bat
```

**Linux/Kali:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**手动启动:**
```bash
cd backend
python app.py
```

后端将运行在 `http://localhost:5000`

### 4. 启动前端界面

**Windows:**
```bash
start_frontend.bat
```

**Linux/Kali:**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

**手动启动:**
```bash
cd frontend
python -m http.server 8080
```

前端将运行在 `http://localhost:8080`

### 5. 一键启动所有服务（推荐）

**Windows:**
```bash
start_all.bat
```

**Linux/Kali:**
```bash
chmod +x start_all.sh
./start_all.sh

# 停止所有服务
chmod +x stop_all.sh
./stop_all.sh
```

**说明**：
- Windows会开启两个命令窗口分别运行前后端
- Linux优先使用tmux管理多窗口，如没有则使用screen或后台进程

### 6. 访问应用

打开浏览器访问: `http://localhost:8080`

## 使用指南

### 规则生成流程

1. **输入漏洞信息**
   - 漏洞名称（必填）
   - 漏洞类型（SQL注入、命令注入等）
   - 漏洞描述（必填）
   - POC示例（可选）

2. **AI生成规则**
   - 点击"🤖 AI生成规则"按钮
   - AI将根据360NDR规范自动生成Suricata规则

3. **验证规则**
   - 设置PCAP文件路径
   - 点击"✓ 验证规则"按钮
   - 查看验证结果和告警统计

4. **优化规则**
   - 根据验证结果，点击"🔧 AI优化"
   - 输入优化建议（可选）
   - AI将生成优化后的规则

### 规则编写规范

本工具遵循Suricata规则编写规范，包括：

#### HTTP类特征选取
- 省略http.method（除非必要）
- URL路径尽量少取1-2级目录
- 去除路径最后的问号?
- 参数拆分成多个content

#### 正则表达式要求
- 必须限制作用域（U/I/H/P等）
- 使用通用正则避免绕过
- 正则必须带上漏洞利用点参数

#### 规则格式示例
```
alert http any any -> any any (msg:"用友NC SQL注入漏洞"; 
    flow:established,to_server; 
    http.uri.raw; content:"infopub/showcontent"; nocase; 
    content:"id="; nocase; 
    pcre:"/id=[^\r\n\x26]{0,10}(select|union|sleep)/Ii"; 
    classtype:web-application-attack; 
    sid:60118865; 
    reference:url,github.com/example; 
    rev:1; 
    metadata:created_at 2024_05_20;)
```

## API接口文档

### 生成规则
```http
POST /api/rules/generate
Content-Type: application/json

{
  "vuln_name": "漏洞名称",
  "vuln_type": "sql_injection",
  "vuln_description": "漏洞描述",
  "poc": "POC示例"
}
```

### 优化规则
```http
POST /api/rules/optimize
Content-Type: application/json

{
  "rule_id": 1,
  "current_rule": "当前规则内容",
  "feedback": "优化建议",
  "validation_result": "验证结果"
}
```

### 验证规则
```http
POST /api/rules/validate
Content-Type: application/json

{
  "rule_content": "规则内容",
  "rule_id": 1,
  "pcap_path": "/path/to/pcap"
}
```

### 获取规则列表
```http
GET /api/rules?page=1&per_page=20
```

### 获取规则详情
```http
GET /api/rules/{rule_id}
```

## 配置说明

### 环境变量配置

在 `.env` 文件中可以通过环境变量配置，支持多种LLM提供商和系统配置：

```bash
# =============================================
# 安全配置
# =============================================
# JWT 签名密钥 - 生产环境必须修改为随机字符串！
# 建议使用: openssl rand -hex 32
SECRET_KEY=ffe39a6f6a5cef863cbc8dd09eacb85e050ebb78bc107a519918f49a3b0faafb

# JWT 加密算法
ALGORITHM=HS256

# Token 过期时间（分钟），默认 8 天
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# =============================================
# LLM 通用配置
# =============================================
# 支持的 provider:
# - LiteLLM 适配器: openai, gemini, claude, qwen, deepseek, zhipu, moonshot, ollama
# - 原生适配器: baidu, minimax, doubao
LLM_PROVIDER=openai

# API 密钥
#LLM_API_KEY=sk-0010d2d1eb5348648be01592c550fa5d
LLM_API_KEY=fk168504229.9Pl3_jloeolkP9ohP5V2fPDJXUAV8l_7f24a0813

# 模型名称（留空使用 provider 默认模型）
# OpenAI: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
# Gemini: gemini-2.0-flash, gemini-1.5-pro
# Claude: claude-3-5-sonnet-20241022, claude-3-haiku-20240307
# Qwen: qwen-turbo, qwen-plus, qwen-max
# DeepSeek: deepseek-chat, deepseek-coder
# Zhipu: glm-4-flash, glm-4
# Moonshot: moonshot-v1-8k, moonshot-v1-32k
# Ollama: llama3, codellama, qwen2.5, deepseek-coder
#LLM_MODEL=deepseek-coder
LLM_MODEL=360gpt-pro

# 自定义 API 端点（API 中转站）
# 示例: https://your-proxy.com/v1
#LLM_BASE_URL=https://api.deepseek.com/v1
LLM_BASE_URL=https://api.360.cn/v1

# 请求超时时间（秒）
LLM_TIMEOUT=150

# 生成温度（0-1，越低越确定性）
LLM_TEMPERATURE=0.1

# 最大生成 Token 数
LLM_MAX_TOKENS=4096

# 360 AI API Configuration (向后兼容)
AI_API_KEY=fk168504229.9Pl3_jloeolkP9ohP5V2fPDJXUAV8l_7f24a0813
AI_MODEL=360gpt-pro

# 数据库路径
DB_PATH=backend/suricata_rules.db

# Suricata配置 (Linux/Kali)
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_CONFIG=/etc/suricata/suricata.yaml
SURICATA_LOG_DIR=/var/log/suricata
PCAP_DIR=/home/kali/pcap_check
UPLOAD_DIR=uploads
CONFIG_FILE_PATH=pcap_config.json

# SSH配置 (Windows连接Kali VM)
SSH_ENABLED=false
SSH_HOST=
SSH_USER=kali
SSH_KEY=

# Flask配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=true
```

## 在Linux/Kali上部署

在Linux或Kali Linux上部署本项目需要进行以下配置：

### 1. 系统要求
- Ubuntu 18.04+/Debian 10+/Kali Linux
- Python 3.8+
- Node.js 16+ (前端开发)

### 2. 安装依赖软件

**安装Python和Node.js：**
```bash
# Ubuntu/Debian/Kali
sudo apt update
sudo apt install python3 python3-venv python3-pip nodejs npm -y
```

**安装Suricata（用于规则验证）：**
```bash
# Ubuntu/Debian
sudo apt install suricata -y

# Kali Linux
sudo apt install suricata -y

# 或从源码编译最新版本
wget https://github.com/OISF/suricata/archive/suricata-7.0.x.tar.gz
tar -xzf suricata-7.0.x.tar.gz
cd suricata-suricata-7.0.x/
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var
make && sudo make install
sudo ldconfig
```

**验证安装：**
```bash
# 检查版本
python3 --version
node --version
suricata --version
```

### 3. 项目部署

**克隆项目：**
```bash
git clone https://github.com/rockmelodies/suricata_ai_gen.git
cd suricata_ai_gen
```

**创建虚拟环境：**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

**安装后端依赖：**
```bash
pip install -r backend/requirements.txt
```

**安装前端依赖（如果需要开发前端）：**
```bash
cd frontend-vue3
npm install
```

### 4. 配置环境变量

**创建配置文件：**
```bash
cp .env.example .env
```

**编辑 .env 文件，配置Linux/Kali环境：**
```bash
# 360 AI API Configuration
AI_API_KEY=your_360_api_key_here
AI_MODEL=360gpt-pro

# Database Configuration
DB_PATH=backend/suricata_rules.db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production

# Suricata Configuration (Linux/Kali)
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_CONFIG=/etc/suricata/suricata.yaml
SURICATA_LOG_DIR=/var/log/suricata
PCAP_DIR=/home/kali/pcap_check
```

**创建PCAP测试目录：**
```bash
mkdir -p /home/kali/pcap_check
# 将您的PCAP测试文件复制到此目录
```

### 5. 验证Suricata配置

**检查配置文件：**
```bash
# 检查Suricata配置是否正确
sudo suricata-update list-sources

# 检查配置语法
suricata -c /etc/suricata/suricata.yaml --dump-config
```

**创建必要的目录：**
```bash
# 确保Suricata相关目录存在
sudo mkdir -p /var/lib/suricata/rules
sudo mkdir -p /var/log/suricata

# 设置适当的权限
sudo chown $USER:$USER /var/lib/suricata/rules
sudo chown $USER:$USER /var/log/suricata
```

### 6. 启动服务

**启动后端服务：**
```bash
# 确保在虚拟环境中
cd backend
source ../.venv/bin/activate
python app_v2.py
```

**或使用启动脚本：**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**启动前端服务：**
```bash
cd frontend-vue3
npm run dev
```

**一键启动所有服务：**
```bash
chmod +x start_all.sh
./start_all.sh
```

### 7. 高级配置（可选）

**配置SSH远程验证（当本地没有Suricata时）：**
如果您在一台机器上开发但在另一台机器上运行Suricata，可以配置SSH连接：

```bash
# 在 .env 文件中添加SSH配置
SSH_ENABLED=true
SSH_HOST=your_kali_vm_ip
SSH_USER=kali
SSH_KEY=/path/to/ssh/private/key
```

**配置说明：**
- `SSH_ENABLED`: 启用SSH远程验证
- `SSH_HOST`: Kali Linux或安装了Suricata的机器IP
- `SSH_USER`: SSH用户名
- `SSH_KEY`: SSH私钥路径（可选，如果使用密码认证则不需要）

### 8. 系统服务配置（生产环境推荐）

**创建Systemd服务（可选）：**

创建后端服务文件：
```bash
sudo tee /etc/systemd/system/suricata-ai-backend.service <<EOF
[Unit]
Description=Suricata AI Backend Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/path/to/suricata_ai_gen/backend
Environment=PATH=/path/to/suricata_ai_gen/.venv/bin
ExecStart=/path/to/suricata_ai_gen/.venv/bin/python app_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

**启用并启动服务：**
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启用服务开机自启
sudo systemctl enable suricata-ai-backend

# 启动服务
sudo systemctl start suricata-ai-backend

# 查看服务状态
sudo systemctl status suricata-ai-backend
```

### 9. Nginx反向代理配置（可选）

如果需要通过域名访问，可以配置Nginx：

```bash
sudo apt install nginx -y
```

创建Nginx配置：
```bash
sudo tee /etc/nginx/sites-available/suricata-ai <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/suricata-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. 常见问题排查

**问题1：权限不足**
```bash
# 检查当前用户是否在sudo组中
groups $USER

# 如果需要sudo权限，添加用户到sudo组
sudo usermod -aG sudo $USER
```

**问题2：端口被占用**
```bash
# 检查端口占用情况
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :5173

# 杀死占用端口的进程
sudo kill -9 $(sudo lsof -t -i:5000)
```

**问题3：Suricata配置错误**
```bash
# 检查Suricata配置
sudo suricata -T -c /etc/suricata/suricata.yaml

# 重新生成默认配置
sudo suricata-update update-sources
sudo suricata-update enable-source oisf/trafficid
sudo suricata-update enable-source et/open
sudo suricata-update
```

**问题4：Python依赖问题**
```bash
# 重新创建虚拟环境
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

**问题5：数据库权限问题**
```bash
# 确保数据库目录有写权限
mkdir -p backend
touch backend/suricata_rules.db
chmod 664 backend/suricata_rules.db
```

### 11. 性能优化建议

**Suricata性能优化：**
- 调整线程数以匹配CPU核心数
- 优化内存使用设置
- 配置适当的规则集

**应用性能优化：**
- 使用Gunicorn部署生产环境
- 配置Redis缓存
- 使用CDN加速静态资源

### 12. 安全加固

**基础安全措施：**
- 更改默认管理员密码
- 使用HTTPS加密通信
- 限制API访问频率
- 定期更新依赖包

**防火墙配置：**
```bash
# 仅开放必要端口
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

## Windows远程连接Kali验证

如果在Windows上开发，但希望利用Linux/Kali环境的强大功能进行规则验证，可以通过SSH连接到Kali VM或Linux服务器进行验证：

### 1. 在Kali Linux上配置SSH服务

**启动SSH服务：**
```bash
# 启动SSH服务
sudo systemctl start ssh

# 设置开机自启
sudo systemctl enable ssh

# 检查SSH服务状态
sudo systemctl status ssh
```

**配置SSH（可选）：**
```bash
# 编辑SSH配置
sudo vim /etc/ssh/sshd_config

# 确保以下设置
Port 22
PermitRootLogin no
PasswordAuthentication yes  # 或 no（如果使用密钥认证）
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# 重启SSH服务
sudo systemctl restart ssh
```

### 2. 配置SSH密钥认证（推荐）

**在Windows上生成SSH密钥：**
```powershell
# 使用Git Bash或PowerShell
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 默认生成位置：
# 公钥：~/.ssh/id_rsa.pub
# 私钥：~/.ssh/id_rsa
```

**将公钥复制到Kali：**
```bash
# 方法1：使用ssh-copy-id（如果在Linux/Mac上）
ssh-copy-id kali@your_kali_ip

# 方法2：手动复制
cat ~/.ssh/id_rsa.pub | ssh kali@your_kali_ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 方法3：直接复制内容
# 将公钥内容复制到Kali的 ~/.ssh/authorized_keys 文件
```

**在Kali上设置权限：**
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown $USER:$USER ~/.ssh/authorized_keys
```

### 3. 在Windows上配置环境变量

**方法1：修改 .env 文件：**
```bash
# 在项目根目录的 .env 文件中添加
SSH_ENABLED=true
SSH_HOST=your_kali_ip_address
SSH_USER=kali
SSH_KEY=C:\\.ssh\private_key_path
```

**方法2：命令行设置（临时）：**
```cmd
# Windows CMD
set SSH_ENABLED=true
set SSH_HOST=192.168.1.100
set SSH_USER=kali
set SSH_KEY=C:\path\to\private_key
```

```powershell
# PowerShell
$env:SSH_ENABLED="true"
$env:SSH_HOST="192.168.1.100"
$env:SSH_USER="kali"
$env:SSH_KEY="C:\path\to\private_key"
```

### 4. 验证SSH连接

**测试连接：**
```bash
# 测试SSH连接
ssh kali@your_kali_ip

# 如果使用私钥文件
ssh -i /path/to/private/key kali@your_kali_ip
```

**验证Suricata是否可用：**
```bash
ssh kali@your_kali_ip "suricata --version"
ssh kali@your_kali_ip "ls -la /var/lib/suricata/rules"
```

### 5. 配置应用使用SSH远程验证

在应用的系统配置页面，您也可以通过界面直接配置SSH连接参数：
- SSH主机地址
- SSH用户名
- SSH私钥路径（可选）

配置完成后，应用将自动通过SSH连接到远程Kali系统执行Suricata验证，无需在Windows上安装Suricata。

### 6. 常见SSH连接问题

**问题1：连接被拒绝**
```bash
# 检查SSH服务状态
sudo systemctl status ssh

# 检查防火墙设置
sudo ufw status
sudo ufw allow ssh

# 检查网络连通性
ping your_kali_ip
```

**问题2：认证失败**
```bash
# 检查公钥是否正确添加
cat ~/.ssh/authorized_keys

# 检查权限设置
ls -la ~/.ssh/

# 使用详细模式调试
ssh -v kali@your_kali_ip
```

**问题3：私钥格式问题**
```bash
# 如果使用PuTTY生成的密钥，需要转换格式
# 使用PuTTYgen转换为OpenSSH格式

# 或在Windows上使用WSL生成密钥
wsl ssh-keygen -t rsa -b 4096
```

### 7. 安全最佳实践

- 使用SSH密钥认证而非密码
- 配置非标准SSH端口
- 限制SSH访问IP
- 定期更换SSH密钥
- 监控SSH登录日志

通过以上配置，您可以在Windows开发环境中利用Linux/Kali的强大功能进行Suricata规则验证。

## 数据库结构

### rules表
- id: 规则ID
- vuln_name: 漏洞名称
- vuln_type: 漏洞类型
- description: 漏洞描述
- original_rule: 原始规则
- current_rule: 当前规则
- created_at: 创建时间
- updated_at: 更新时间
- status: 状态

### optimization_history表
- id: 记录ID
- rule_id: 关联规则ID
- original_rule: 优化前规则
- optimized_rule: 优化后规则
- feedback: 用户反馈
- ai_suggestion: AI建议
- created_at: 创建时间

### validation_results表
- id: 记录ID
- rule_id: 关联规则ID
- pcap_path: PCAP路径
- matched: 是否匹配
- alert_count: 告警数量
- details: 详细信息
- sid_stats: SID统计
- created_at: 创建时间

## 常见问题

### 1. AI API调用失败
- 检查API密钥是否正确
- 确认网络连接正常
- 查看API调用限制

### 2. Suricata验证失败
- 确认Suricata已安装
- 检查配置文件路径
- 验证PCAP文件存在

### 3. 数据库错误
- 确认数据库文件权限
- 检查SQLite版本
- 查看错误日志

### 4. Linux/Kali环境特有问题

**问题1：权限不足**
```bash
# 现象：Permission denied错误
# 解决：
sudo chown $USER:$USER /path/to/database.db
sudo chmod 664 /path/to/database.db

# 对于Suricata相关目录
sudo chown $USER:$USER /var/lib/suricata/rules
sudo chown $USER:$USER /var/log/suricata
```

**问题18：数据库无法打开**
```bash
# 现象：sqlite3.OperationalError: unable to open database file
# 解决方法1：检查并创建数据库目录
mkdir -p backend/
cd backend/
touch suricata_rules.db
chmod 664 suricata_rules.db

# 解决方法2：检查环境变量
printenv | grep DB_PATH

# 解决方法3：使用绝对路径
export DB_PATH=/home/kali/suricata_ai_gen/backend/suricata_rules.db

# 解决方法4：运行专门的启动脚本
python backend/start_app.py
```

**问题2：Python模块找不到**
```bash
# 现象：ModuleNotFoundError
# 解决：确保在虚拟环境中
source .venv/bin/activate
pip list  # 验证模块是否安装
```

**问题3：Suricata规则目录不存在**
```bash
# 创建必要的目录
sudo mkdir -p /var/lib/suricata/rules
sudo mkdir -p /var/log/suricata

# 设置正确的权限
sudo chown $USER:$USER /var/lib/suricata/rules
sudo chown $USER:$USER /var/log/suricata
```

**问题4：端口被占用**
```bash
# 检查端口占用
sudo netstat -tulpn | grep :5000
sudo lsof -i :5000

# 杀死占用进程
sudo kill -9 $(sudo lsof -t -i:5000)
```

**问题5：SSH连接失败**
```bash
# 检查SSH服务状态
sudo systemctl status ssh

# 检查防火墙
sudo ufw status
sudo ufw allow ssh

# 测试连接
ssh -v user@host  # 详细模式
```

**问题6：路径分隔符问题**
```bash
# 确保使用Linux风格路径（正斜杠）
PCAP_DIR=/home/kali/pcap_check  # 正确
PCAP_DIR=/home/kali\pcap_check   # 错误
```

**问题7：PCAP文件无法访问**
```bash
# 检查文件权限
ls -la /path/to/pcap/files

# 确保文件可读
chmod 644 /path/to/pcap/file.pcap

# 检查目录权限
chmod 755 /path/to/pcap/directory
```

**问题8：系统资源不足**
```bash
# 检查内存使用
top
free -h

# 检查磁盘空间
df -h

# 检查CPU使用率
cat /proc/loadavg
```

**问题9：网络连接问题**
```bash
# 检查网络连通性
ping google.com

# 检查DNS解析
dig github.com

# 检查代理设置
env | grep -i proxy
```

**问题10：Git权限问题**
```bash
# 设置Git凭证
git config --global credential.helper store

# 或使用SSH密钥
ssh-keygen -t rsa -b 4096
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**问题16：LLM模型配置问题**
```bash
# 现象：AI API调用失败
# 检查LLM配置
env | grep LLM_

# 检查API密钥是否正确设置
cat .env | grep LLM_API_KEY

# 检查提供商配置
cat .env | grep LLM_PROVIDER

# 确保模型名称正确
cat .env | grep LLM_MODEL
```

**问题17：不同LLM提供商的配置差异**
```bash
# OpenAI配置示例
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.openai.com/v1

# Gemini配置示例
LLM_PROVIDER=gemini
LLM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# 360AI配置示例
LLM_PROVIDER=360ai
LLM_API_KEY=fk168504229.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.360.cn/v1

# Ollama本地配置示例
LLM_PROVIDER=ollama
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3
```

**问题11：服务启动失败**
```bash
# 检查服务状态
sudo systemctl status suricata-ai-backend

# 查看服务日志
sudo journalctl -u suricata-ai-backend -f

# 检查Python环境
source .venv/bin/activate
python --version
which python
```

**问题12：Nginx反向代理配置错误**
```bash
# 检查配置语法
sudo nginx -t

# 重新加载配置
sudo systemctl reload nginx

# 检查错误日志
sudo tail -f /var/log/nginx/error.log
```

**问题13：环境变量未生效**
```bash
# 检查环境变量
printenv | grep SURICATA

# 重新加载环境文件
source ~/.suricata-ai-env

# 检查.env文件权限
ls -la .env
chmod 600 .env  # 限制访问权限
```

**问题14：数据库锁定**
```bash
# 现象：database is locked错误
# 解决：检查是否有其他进程占用数据库
ps aux | grep python

# 检查锁文件
ls -la /tmp/ | grep sqlite
```

**问题15：日志轮转问题**
```bash
# 检查日志轮转配置
sudo logrotate -d /etc/logrotate.d/suricata-ai

# 手动执行日志轮转
sudo logrotate -f /etc/logrotate.d/suricata-ai
```

对于这些问题，大部分可以通过检查日志文件来诊断：
- 应用日志：`backend/logs/app.log`
- Suricata日志：`/var/log/suricata/`
- 系统日志：`/var/log/syslog`
- Nginx日志：`/var/log/nginx/`

如果遇到未列出的问题，请检查相关日志并考虑提交Issue。

## 模型配置指南

本项目支持多种大语言模型提供商，详细配置说明请参见 [MODELS.md](MODELS.md) 文档。

## 开发计划

- [x] 支持多种AI模型 (已实现)
- [ ] 规则模板库
- [ ] 批量导入导出
- [ ] 规则性能分析
- [ ] Web界面优化
- [ ] Docker容器化部署

## 🌟 项目统计

<div align="center">

| 类型 | 数量 | 说明 |
|------|------|------|
| 💻 **后端代码** | 6个文件 | ~1000行Python |
| 🎨 **前端代码** | 1个文件 | 646行Vue3 |
| 📚 **文档** | 8个文件 | ~3500行 |
| ⚙️ **脚本** | 7个 | Windows + Linux |
| 🔌 **API接口** | 8个 | RESTful API |

</div>

## 🎆 技术栈

<div align="center">

### 后端

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

### 前端

![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

### 工具 & 平台

![Suricata](https://img.shields.io/badge/Suricata-6.0+-FF6600?style=for-the-badge&logo=suricata&logoColor=white)
![Kali Linux](https://img.shields.io/badge/Kali_Linux-557C94?style=for-the-badge&logo=kali-linux&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

</div>

## ⭐ Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=rockmelodies/suricata_ai_gen&type=Date)](https://star-history.com/rockmelodies/suricata_ai_gen&Date)

</div>

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

<div align="center">

### 贡献者

<a href="https://github.com/rockmelodies/suricata_ai_gen/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=rockmelodies/suricata_ai_gen" />
</a>

</div>

## 📝 许可证

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

本项目采用 MIT 许可证，仅供学习和研究使用。

</div>

## 📧 联系方式

<div align="center">

如有问题或建议，请通过以下方式反馈：

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-red?style=for-the-badge&logo=github)](https://github.com/rockmelodies/suricata_ai_gen/issues)
[![Email](https://img.shields.io/badge/Email-Contact-blue?style=for-the-badge&logo=gmail)](mailto:rockysocket@gmail.com)

</div>

---

<div align="center">

### ❤️ 感谢使用

如果这个项目对您有帮助，请给个 Star ⭐ 支持一下！

[![Star](https://img.shields.io/github/stars/rockmelodies/suricata_ai_gen?style=social)](https://github.com/rockmelodies/suricata_ai_gen/stargazers)
[![Fork](https://img.shields.io/github/forks/rockmelodies/suricata_ai_gen?style=social)](https://github.com/rockmelodies/suricata_ai_gen/network/members)
[![Watch](https://img.shields.io/github/watchers/rockmelodies/suricata_ai_gen?style=social)](https://github.com/rockmelodies/suricata_ai_gen/watchers)

**Made with ❤️ by Security Researchers**

</div>
