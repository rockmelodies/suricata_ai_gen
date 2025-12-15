# 快速开始指南

## 配置环境变量（首次使用）

**⚠️ 重要：为了安全，请先配置API密钥！**

1. **复制环境变量模板文件**
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux
   cp .env.example .env
   ```

2. **编辑 `.env` 文件**
   
   使用文本编辑器打开 `.env` 文件，修改以下内容：
   ```bash
   # 360 AI API Configuration
   AI_API_KEY=your_api_key_here  # ← 请替换为您的真实API密钥
   AI_MODEL=360gpt-pro
   
   # 其他配置保持默认即可
   ```

3. **安全提示**
   - ✅ `.env` 文件已自动加入 `.gitignore`，不会被提交
   - ❌ 请勿在代码中硬编码API密钥
   - ❌ 不要分享 `.env` 文件给他人

## 一键启动

### Windows环境

1. **安装依赖**（首次运行）
   ```bash
   # 确保已激活虚拟环境
   .venv\Scripts\activate
   
   # 安装依赖
   pip install -r backend\requirements.txt
   ```

2. **一键启动所有服务**
   ```bash
   start_all.bat
   ```
   
   这将自动启动：
   - 后端服务（Flask）在 `http://localhost:5000`
   - 前端界面（Vue3）在 `http://localhost:8080`
   - 自动打开浏览器

3. **分别启动**（可选）
   ```bash
   # 只启动后端
   start_backend.bat
   
   # 只启动前端
   start_frontend.bat
   ```

### Linux/Kali环境

1. **安装依赖**（首次运行）
   ```bash
   # 确保已激活虚拟环境（如果没有会自动创建）
   source .venv/bin/activate
   
   # 安装依赖
   pip install -r backend/requirements.txt
   ```

2. **一键启动所有服务**（推荐使用tmux）
   ```bash
   # 添加执行权限
   chmod +x start_all.sh
   
   # 启动所有服务
   ./start_all.sh
   ```
   
   **说明**：
   - 优先使用 `tmux` 管理多窗口（推荐）
   - 如果没有tmux，会使用 `screen`
   - 如果都没有，会在后台启动
   
   **tmux操作**：
   - 切换窗口：`Ctrl+B` 然后按 `0` 或 `1`
   - 分离会话：`Ctrl+B` 然后按 `D`
   - 重新连接：`tmux attach -t suricata_rule_gen`
   - 停止所有：`tmux kill-session -t suricata_rule_gen`

3. **分别启动**（可选）
   ```bash
   # 添加执行权限
   chmod +x start_backend.sh start_frontend.sh
   
   # 终端1：启动后端
   ./start_backend.sh
   
   # 终端2：启动前端
   ./start_frontend.sh
   ```

4. **停止所有服务**
   ```bash
   # 添加执行权限
   chmod +x stop_all.sh
   
   # 停止所有服务
   ./stop_all.sh
   ```

## 使用流程

### 1. 生成规则

1. 打开浏览器访问：`http://localhost:8080`
2. 在"规则生成"标签页填写信息：
   - **漏洞名称**：例如"用友NC SQL注入漏洞"
   - **漏洞类型**：选择SQL注入、命令注入等
   - **漏洞描述**：详细描述漏洞利用方式
   - **POC示例**（可选）：粘贴攻击请求示例
3. 点击"🤖 AI生成规则"按钮
4. 等待AI生成结果（通常3-10秒）

### 2. 验证规则

1. 生成规则后，在右侧面板查看
2. 设置PCAP文件路径（默认：`/home/kali/pcap_check`）
3. 点击"✓ 验证规则"按钮
4. 查看验证结果：
   - 匹配状态
   - 告警数量
   - 告警详情
   - SID统计

**注意**：
- Windows环境下会返回模拟验证结果
- 真实验证需要在Kali Linux环境

### 3. 优化规则

1. 根据验证结果，点击"🔧 AI优化"
2. 输入优化建议（可选）
3. AI将生成改进后的规则
4. 可以再次验证优化后的规则

### 4. 查看历史

1. 切换到"历史记录"标签页
2. 查看所有生成的规则
3. 点击任意记录可加载到编辑器

## 示例：生成SQL注入规则

### 输入信息
```
漏洞名称: 用友NC SQL注入漏洞
漏洞类型: sql_injection
漏洞描述: 用友NC系统在infopub/showcontent接口的id参数存在SQL注入漏洞，
         攻击者可通过构造恶意SQL语句获取数据库敏感信息

POC示例:
GET /infopub/showcontent?id=1' union select 1,2,database()-- HTTP/1.1
Host: target.com
```

### 生成的规则示例
```
alert http any any -> any any (
    msg:"用友NC SQL注入漏洞"; 
    flow:established,to_server; 
    http.uri.raw; content:"infopub/showcontent"; nocase; 
    content:"id="; nocase; 
    pcre:"/id=[^\r\n\x26]{0,10}(select|union|sleep|load|update|from|concat|where)/Ii"; 
    classtype:web-application-attack; 
    sid:60100001; 
    rev:1;
)
```

## 在Kali Linux上验证

### 准备环境

1. **安装Suricata**
   ```bash
   sudo apt update
   sudo apt install suricata -y
   ```

2. **准备PCAP文件**
   ```bash
   mkdir -p /home/kali/pcap_check
   # 将测试PCAP文件放入该目录
   ```

3. **配置Suricata**
   ```bash
   # 检查配置文件
   sudo vim /etc/suricata/suricata.yaml
   
   # 确保规则路径正确
   # default-rule-path: /var/lib/suricata/rules
   ```

### 方式一：本地运行（推荐）

直接在Kali上运行整个应用：

```bash
# 克隆或复制项目到Kali
cd /path/to/suricata_ai_gen

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt

# 启动后端
python backend/app.py

# 在另一个终端启动前端
cd frontend
python3 -m http.server 8080
```

### 方式二：SSH远程验证

Windows通过SSH连接Kali进行验证：

1. **在Kali上启动SSH**
   ```bash
   sudo systemctl start ssh
   sudo systemctl enable ssh
   ```

2. **配置SSH密钥**
   ```bash
   # 在Windows上生成密钥
   ssh-keygen -t rsa
   
   # 复制公钥到Kali
   ssh-copy-id kali@192.168.1.100
   ```

3. **在Windows上配置环境变量**
   ```bash
   set SSH_ENABLED=true
   set SSH_HOST=192.168.1.100
   set SSH_USER=kali
   set SSH_KEY=C:\Users\YourName\.ssh\id_rsa
   ```

4. **重启后端服务**

## 使用Python API

### 示例代码

```python
import requests

API_URL = "http://localhost:5000/api"

# 生成规则
response = requests.post(f"{API_URL}/rules/generate", json={
    "vuln_name": "测试漏洞",
    "vuln_type": "sql_injection",
    "vuln_description": "这是一个SQL注入测试",
    "poc": "GET /test?id=1' union select 1,2,3--"
})

result = response.json()
print(result['generated_rule'])

# 验证规则
response = requests.post(f"{API_URL}/rules/validate", json={
    "rule_content": result['generated_rule'],
    "pcap_path": "/home/kali/pcap_check"
})

validation = response.json()
print(f"Matched: {validation['validation_result']['matched']}")
```

### 运行测试脚本

```bash
# 确保后端正在运行
python test_example.py
```

## 常见问题

### Q: 后端启动失败
**A**: 检查依赖是否安装：
```bash
pip install -r backend\requirements.txt
```

### Q: 前端无法访问
**A**: 确认端口未被占用：
```bash
netstat -ano | findstr :8080
```

### Q: AI生成失败
**A**: 
1. 检查API密钥是否正确
2. 确认网络连接
3. 查看后端日志

### Q: 数据库错误
**A**: 删除数据库文件重新初始化：
```bash
del backend\suricata_rules.db
# 重启后端会自动创建
```

### Q: Suricata验证失败（Windows）
**A**: Windows环境会返回模拟结果。真实验证需要：
1. 使用Kali Linux环境
2. 或通过SSH连接Kali VM

## 下一步

- 📖 查看完整文档：[README.md](README.md)
- 🔧 配置说明：[backend/config.py](backend/config.py)
- 📝 规则编写规范：参考README中的规则示例
- 🎯 提交Issue报告问题或建议

## 技术支持

遇到问题？
1. 查看 [README.md](README.md) 完整文档
2. 检查后端日志输出
3. 提交GitHub Issue

祝使用愉快！🎉
