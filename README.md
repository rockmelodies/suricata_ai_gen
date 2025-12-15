<div align="center">

# 🛡️ Suricata规则生成与验证工具

### 基于AI的智能Suricata规则生成、优化与自动化验证平台

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version"></a>
  <a href="#"><img src="https://img.shields.io/badge/Flask-3.0.0-green.svg" alt="Flask"></a>
  <a href="#"><img src="https://img.shields.io/badge/Vue-3.0-brightgreen.svg" alt="Vue3"></a>
  <a href="#"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg" alt="Platform"></a>
  <a href="https://github.com/yourusername/suricata_ai_gen/stargazers"><img src="https://img.shields.io/github/stars/yourusername/suricata_ai_gen?style=social" alt="GitHub stars"></a>
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

✨ **AI智能生成** - 基于360AI大模型，根据漏洞描述自动生成Suricata规则  
🔧 **规则优化** - AI辅助优化规则，提高检测准确率  
✅ **自动验证** - 集成Suricata引擎，自动验证规则有效性  
📊 **数据管理** - SQLite数据库存储规则历史和验证结果  
🎨 **友好界面** - Vue3前端，简洁美观的用户界面  

## 系统架构

```
suricata_ai_gen/
├── backend/              # 后端服务 (Python + Flask)
│   ├── app.py           # Flask主应用
│   ├── ai_client.py     # 360AI客户端
│   ├── database.py      # 数据库管理
│   ├── suricata_validator.py  # Suricata验证器
│   ├── config.py        # 配置文件
│   └── requirements.txt # Python依赖
├── frontend/            # 前端界面 (Vue3)
│   └── index.html      # 单页应用
├── start_backend.bat   # 后端启动脚本
├── start_frontend.bat  # 前端启动脚本
└── README.md           # 项目说明
```

## 环境要求

### Windows开发环境
- Python 3.8+
- 浏览器 (Chrome/Edge/Firefox)

### Kali Linux验证环境 (可选)
- Suricata 6.0+
- PCAP测试文件

## 快速开始

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

# 其他配置...
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

在 `backend/config.py` 中可以通过环境变量配置：

```bash
# AI API配置
AI_API_KEY=your_api_key_here
AI_MODEL=360gpt-pro

# 数据库路径
DB_PATH=/path/to/database.db

# Suricata配置 (Linux/Kali)
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_CONFIG=/etc/suricata/suricata.yaml
SURICATA_LOG_DIR=/var/log/suricata
PCAP_DIR=/home/kali/pcap_check

# SSH配置 (Windows连接Kali VM)
SSH_ENABLED=false
SSH_HOST=192.168.1.100
SSH_USER=kali
SSH_KEY=/path/to/private_key

# Flask配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=true
```

## 在Kali Linux上部署

如果需要在Kali Linux上直接部署和验证：

1. 安装Suricata
```bash
sudo apt update
sudo apt install suricata
```

2. 准备PCAP测试文件
```bash
mkdir -p /home/kali/pcap_check
# 将测试PCAP文件放入该目录
```

3. 配置Suricata
```bash
sudo vim /etc/suricata/suricata.yaml
# 确保规则路径配置正确
```

4. 运行应用
```bash
python backend/app.py
```

## Windows远程连接Kali验证

如果在Windows上开发，可以通过SSH连接到Kali VM进行验证：

1. 在Kali上配置SSH服务
```bash
sudo systemctl start ssh
sudo systemctl enable ssh
```

2. 配置SSH密钥认证
```bash
ssh-keygen -t rsa
ssh-copy-id kali@your_kali_ip
```

3. 在Windows上配置环境变量
```bash
set SSH_ENABLED=true
set SSH_HOST=192.168.1.100
set SSH_USER=kali
set SSH_KEY=C:\path\to\private_key
```

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

## 开发计划

- [ ] 支持更多AI模型
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

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/suricata_ai_gen&type=Date)](https://star-history.com/#yourusername/suricata_ai_gen&Date)

</div>

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

<div align="center">

### 贡献者

<a href="https://github.com/yourusername/suricata_ai_gen/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/suricata_ai_gen" />
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

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-red?style=for-the-badge&logo=github)](https://github.com/yourusername/suricata_ai_gen/issues)
[![Email](https://img.shields.io/badge/Email-Contact-blue?style=for-the-badge&logo=gmail)](mailto:your.email@example.com)

</div>

---

<div align="center">

### ❤️ 感谢使用

如果这个项目对您有帮助，请给个 Star ⭐ 支持一下！

[![Star](https://img.shields.io/github/stars/yourusername/suricata_ai_gen?style=social)](https://github.com/yourusername/suricata_ai_gen/stargazers)
[![Fork](https://img.shields.io/github/forks/yourusername/suricata_ai_gen?style=social)](https://github.com/yourusername/suricata_ai_gen/network/members)
[![Watch](https://img.shields.io/github/watchers/yourusername/suricata_ai_gen?style=social)](https://github.com/yourusername/suricata_ai_gen/watchers)

**Made with ❤️ by Security Researchers**

</div>
