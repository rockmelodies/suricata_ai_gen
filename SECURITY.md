# 安全配置说明

## 🔐 API密钥管理

本项目使用 `.env` 文件来安全地管理API密钥和其他敏感配置信息。

### 为什么使用 .env 文件？

1. **安全性** - API密钥不会被硬编码在代码中
2. **可移植性** - 不同环境可以使用不同的配置
3. **版本控制** - `.env` 文件不会被提交到Git仓库
4. **便捷性** - 集中管理所有环境变量

## 📋 配置步骤

### 1. 创建 .env 文件

```bash
# Windows
copy .env.example .env

# Linux
cp .env.example .env
```

### 2. 编辑配置

打开 `.env` 文件，配置以下参数：

```bash
# ============================================
# 360 AI API 配置
# ============================================
AI_API_KEY=your_api_key_here  # 必填：您的360 AI API密钥
AI_MODEL=360gpt-pro            # 可选：AI模型名称

# ============================================
# 数据库配置
# ============================================
DB_PATH=backend/suricata_rules.db  # 数据库文件路径

# ============================================
# Suricata 配置（仅Linux/Kali环境）
# ============================================
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_CONFIG=/etc/suricata/suricata.yaml
SURICATA_LOG_DIR=/var/log/suricata
PCAP_DIR=/home/kali/pcap_check

# ============================================
# SSH 配置（Windows远程连接Kali时使用）
# ============================================
SSH_ENABLED=false              # 是否启用SSH验证
SSH_HOST=                      # Kali主机IP地址
SSH_USER=kali                  # SSH用户名
SSH_KEY=                       # SSH私钥路径

# ============================================
# Flask 服务配置
# ============================================
FLASK_HOST=0.0.0.0            # 监听地址
FLASK_PORT=5000               # 监听端口
FLASK_DEBUG=true              # 调试模式
```

### 3. 获取API密钥

访问 [360 AI开放平台](https://ai.360.cn/) 获取您的API密钥。

## ⚠️ 安全注意事项

### DO（应该做的）

✅ **使用环境变量** - 始终通过 `.env` 文件配置敏感信息
✅ **加入 .gitignore** - 确保 `.env` 在 `.gitignore` 中
✅ **定期更换密钥** - 定期更新API密钥提高安全性
✅ **权限控制** - 限制 `.env` 文件的读取权限
```bash
# Linux
chmod 600 .env
```

### DON'T（不应该做的）

❌ **硬编码密钥** - 不要在代码中直接写入API密钥
```python
# ❌ 错误示例
API_KEY = "fk168504229.k2h9hyebSX7c_UzjTA5U5T0t_3IzR10124707b23"

# ✅ 正确示例
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('AI_API_KEY')
```

❌ **提交到Git** - 不要将 `.env` 文件提交到版本控制
❌ **公开分享** - 不要在公共场合分享包含密钥的文件
❌ **使用默认密钥** - 不要使用示例中的密钥

## 🔍 检查配置

### 验证 .env 文件是否正确加载

运行以下Python脚本测试：

```python
from dotenv import load_dotenv
import os

load_dotenv()

# 检查API密钥
api_key = os.getenv('AI_API_KEY')
if api_key:
    print(f"✅ API密钥已加载: {api_key[:10]}...")
else:
    print("❌ API密钥未找到，请检查 .env 文件")

# 检查其他配置
print(f"AI模型: {os.getenv('AI_MODEL')}")
print(f"数据库路径: {os.getenv('DB_PATH')}")
```

### 验证 .gitignore 配置

确认 `.gitignore` 文件包含：

```gitignore
# Environment
.env
.env.local
```

检查文件是否被Git忽略：

```bash
git status

# .env 文件不应该出现在未跟踪文件列表中
```

## 🛡️ 密钥泄露应对

如果不小心泄露了API密钥：

1. **立即禁用** - 在360 AI平台禁用泄露的密钥
2. **生成新密钥** - 创建新的API密钥
3. **更新配置** - 更新 `.env` 文件中的密钥
4. **检查日志** - 查看是否有异常的API调用
5. **重新部署** - 使用新密钥重启服务

## 📚 相关文档

- [python-dotenv 文档](https://pypi.org/project/python-dotenv/)
- [环境变量最佳实践](https://12factor.net/config)
- [360 AI API 文档](https://ai.360.cn/docs)

## 🔄 环境变量加载优先级

1. 系统环境变量（最高优先级）
2. `.env` 文件
3. 代码中的默认值（最低优先级）

示例：
```python
# 会按以下优先级查找 AI_API_KEY：
# 1. 系统环境变量中的 AI_API_KEY
# 2. .env 文件中的 AI_API_KEY
# 3. 如果都没有，则为 None
API_KEY = os.getenv('AI_API_KEY')
```

## 💡 最佳实践示例

### 开发环境

`.env` 文件：
```bash
AI_API_KEY=dev_key_here
FLASK_DEBUG=true
DB_PATH=backend/dev_database.db
```

### 生产环境

`.env` 文件：
```bash
AI_API_KEY=prod_key_here
FLASK_DEBUG=false
DB_PATH=/var/lib/suricata_ai/database.db
FLASK_HOST=127.0.0.1
```

### 测试环境

`.env.test` 文件：
```bash
AI_API_KEY=test_key_here
FLASK_DEBUG=true
DB_PATH=:memory:  # SQLite内存数据库
```

加载测试配置：
```python
from dotenv import load_dotenv

# 加载测试环境配置
load_dotenv('.env.test')
```

## 🚨 常见问题

### Q: 提示"AI_API_KEY not found"？

**A**: 检查以下几点：
1. `.env` 文件是否存在于项目根目录
2. `.env` 文件中是否有 `AI_API_KEY=your_key` 配置
3. 是否正确安装了 `python-dotenv`
4. 是否在代码中调用了 `load_dotenv()`

### Q: 如何在Docker中使用环境变量？

**A**: 使用 `docker-compose.yml`：
```yaml
version: '3'
services:
  backend:
    build: .
    env_file:
      - .env
    ports:
      - "5000:5000"
```

或使用命令行：
```bash
docker run --env-file .env -p 5000:5000 suricata-backend
```

### Q: 多人协作如何管理配置？

**A**: 
1. **不要共享 .env 文件** - 每个人使用自己的密钥
2. **共享 .env.example** - 提供配置模板
3. **文档说明** - 在README中说明必需的配置项
4. **使用密钥管理服务** - 生产环境考虑使用HashiCorp Vault等

### Q: 如何在CI/CD中使用？

**A**: 使用CI平台的密钥管理功能：

**GitHub Actions:**
```yaml
env:
  AI_API_KEY: ${{ secrets.AI_API_KEY }}
```

**GitLab CI:**
```yaml
variables:
  AI_API_KEY: $AI_API_KEY  # 在GitLab Settings中配置
```

## 📖 延伸阅读

- 本项目使用的加载方式：[`backend/app.py`](backend/app.py)
- 环境变量示例：[`.env.example`](.env.example)
- 快速开始指南：[`QUICKSTART.md`](QUICKSTART.md)
- 完整文档：[`README.md`](README.md)

---

**安全提示**：保护好您的API密钥就像保护密码一样重要！ 🔐
