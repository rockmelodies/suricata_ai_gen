# 更新日志

## 2024-12-15

### 🎨 优化：msg字段格式调整

**修改内容**：
- AI生成规则时，msg字段只包含漏洞名称，不再添加"360NDR VULNERABILITY"等前缀

**影响范围**：
- `backend/app.py` - 规则生成提示词
- `backend/app.py` - 规则优化提示词

**修改前**：
```
msg:"360NDR VULNERABILITY - Apache Struts2 RCE"
```

**修改后**：
```
msg:"Apache Struts2 RCE"
```

**原因**：
- 简化msg字段，使规则更简洁
- 避免重复的前缀信息
- 直接显示漏洞名称，更易读

---

## 2024-12-15

### 🚀 新增：Nginx反向代理部署支持

**新增文件**：
- `nginx/suricata_rule_gen.conf` - Nginx配置文件
- `deploy_nginx.sh` - 一键部署脚本
- `NGINX_DEPLOYMENT.md` - Nginx部署文档

**修改文件**：
- `frontend/index.html` - 支持Nginx代理模式和自动端口检测

**功能**：
- ✅ 前后端统一80端口访问
- ✅ 自动化Nginx部署脚本
- ✅ 支持三种API配置模式
- ✅ 详细的部署和故障排查文档

**使用方法**：
```bash
sudo ./deploy_nginx.sh
# 访问: http://服务器IP
```

---

## 2024-12-15

### 🔧 修复：远程访问API地址问题

**问题**：
- 远程访问时，前端请求localhost:5000导致无法连接后端

**解决方案**：
- 前端自动检测访问地址并动态生成API URL
- 支持手动配置API地址
- 添加调试日志输出

**新增文件**：
- `test_remote_access.sh` - 远程访问测试脚本
- `REMOTE_ACCESS_FIX.md` - 详细修复指南
- `DEPLOYMENT.md` - 通用部署文档

**修改文件**：
- `frontend/index.html` - 添加getApiBaseUrl()函数
- `start_frontend.sh` - 添加--bind 0.0.0.0
- `start_frontend.bat` - 添加--bind 0.0.0.0

---

## 2024-12-15（初始版本）

### ✨ 功能：API密钥安全化

**修改内容**：
- 使用.env文件管理API密钥
- 添加python-dotenv依赖
- 创建安全配置文档

**新增文件**：
- `.env` - 环境变量配置
- `.env.example` - 配置模板
- `SECURITY.md` - 安全配置指南

**修改文件**：
- `backend/app.py` - 使用环境变量加载API密钥
- `backend/requirements.txt` - 添加python-dotenv

---

## 2024-12-15（初始版本）

### 📚 文档：README美化

**修改内容**：
- 添加项目徽章（badges）
- 添加语言切换（中文/英文）
- 添加技术栈展示
- 添加Star History图表
- 添加贡献者展示

**新增文件**：
- `README_EN.md` - 英文版README
- `LICENSE` - MIT许可证
- `BADGES_GUIDE.md` - 徽章使用指南

---

## 2024-12-15（初始版本）

### 🚀 功能：Linux启动脚本

**新增文件**：
- `start_backend.sh` - Linux后端启动脚本
- `start_frontend.sh` - Linux前端启动脚本
- `start_all.sh` - 一键启动所有服务（支持tmux/screen）
- `stop_all.sh` - 停止所有服务脚本

**特性**：
- 支持tmux多窗口管理
- 支持screen会话管理
- 后台进程降级方案
- 完整的错误处理

---

## 2024-12-15（初始版本）

### 🎉 项目初始化

**核心功能**：
- ✅ AI驱动的Suricata规则生成
- ✅ 规则优化建议
- ✅ Suricata引擎验证
- ✅ SQLite数据库存储
- ✅ Vue3前端界面
- ✅ Flask后端API

**技术栈**：
- 前端: Vue3, Axios
- 后端: Flask, Python 3.8+
- 数据库: SQLite3
- AI: 360AI API

**文件结构**：
```
suricata_ai_gen/
├── backend/
│   ├── app.py              # Flask主应用
│   ├── ai_client.py        # AI客户端
│   ├── database.py         # 数据库管理
│   ├── suricata_validator.py  # 规则验证器
│   └── requirements.txt    # Python依赖
├── frontend/
│   └── index.html          # Vue3单页应用
├── start_all.bat           # Windows启动脚本
├── setup.bat               # Windows部署脚本
├── README.md               # 项目文档
└── QUICKSTART.md           # 快速开始指南
```
