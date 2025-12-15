# 使用教程 - Suricata规则生成与验证工具

## 目录
1. [安装与启动](#安装与启动)
2. [界面介绍](#界面介绍)
3. [规则生成](#规则生成)
4. [规则验证](#规则验证)
5. [规则优化](#规则优化)
6. [历史管理](#历史管理)
7. [实战案例](#实战案例)
8. [常见问题](#常见问题)

---

## 安装与启动

### 第一步：安装依赖

```bash
# 激活虚拟环境（如果还未激活）
.venv\Scripts\activate

# 安装Python依赖
pip install -r backend\requirements.txt
```

### 第二步：启动服务

**方法1：一键启动（推荐）**
```bash
# 双击或运行
start_all.bat
```

**方法2：手动启动**
```bash
# 终端1：启动后端
start_backend.bat

# 终端2：启动前端
start_frontend.bat
```

### 第三步：访问应用

浏览器打开：`http://localhost:8080`

---

## 界面介绍

### 主界面布局

```
┌──────────────────────────────────────────────────────┐
│        🛡️ Suricata规则生成与验证工具                   │
│     基于AI的智能规则生成、优化与自动化验证平台            │
├──────────────────────────────────────────────────────┤
│  [规则生成]  [历史记录]                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────┐  ┌──────────────────┐          │
│  │  漏洞信息输入    │  │   规则操作       │          │
│  │                │  │                  │          │
│  │ 漏洞名称       │  │ 生成的规则       │          │
│  │ 漏洞类型       │  │                  │          │
│  │ 漏洞描述       │  │ PCAP路径        │          │
│  │ POC示例        │  │                  │          │
│  │                │  │ [验证] [优化]    │          │
│  │ [AI生成规则]   │  │                  │          │
│  │                │  │ 验证结果         │          │
│  └─────────────────┘  └──────────────────┘          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 功能区域说明

| 区域 | 功能 | 说明 |
|------|------|------|
| **标题栏** | 应用标识 | 显示应用名称和描述 |
| **标签栏** | 功能切换 | 规则生成 / 历史记录 |
| **左侧面板** | 信息输入 | 填写漏洞信息，触发AI生成 |
| **右侧面板** | 规则操作 | 编辑、验证、优化规则 |
| **消息提示** | 状态反馈 | 显示操作成功/失败消息 |

---

## 规则生成

### 步骤1：填写漏洞信息

#### 必填字段

**漏洞名称**
```
示例：用友NC SQL注入漏洞(CVE-2024-12345)
建议：包含产品名、漏洞类型、CVE编号
```

**漏洞描述**
```
示例：
用友NC系统在infopub/showcontent接口的id参数存在SQL注入漏洞。
攻击者可通过构造恶意SQL语句获取数据库敏感信息。
影响版本：NC 6.5及以下版本
危害等级：高危
```

#### 可选字段

**漏洞类型**（下拉选择）
- SQL注入
- 命令注入
- 文件上传
- 路径穿越
- SSRF
- 未授权访问
- 其他

**POC示例**
```
示例：
GET /infopub/showcontent?id=1' union select 1,2,database()-- HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0
Accept: */*
Connection: close
```

### 步骤2：AI生成规则

1. **点击按钮**：点击"🤖 AI生成规则"
2. **等待处理**：显示"生成中..."（通常3-10秒）
3. **查看结果**：规则显示在右侧文本框

### 生成示例

**输入信息**：
```
漏洞名称：用友NC SQL注入漏洞
漏洞类型：sql_injection
漏洞描述：infopub/showcontent接口id参数SQL注入
POC：GET /infopub/showcontent?id=1' union select 1,2,3--
```

**AI生成的规则**：
```
alert http any any -> any any (
    msg:"用友NC SQL注入漏洞"; 
    flow:established,to_server; 
    http.uri.raw; 
    content:"infopub/showcontent"; nocase; 
    content:"id="; nocase; 
    pcre:"/id=[^\r\n\x26]{0,10}(select|union|sleep|load|from|concat|where|outfile)/Ii"; 
    classtype:web-application-attack; 
    sid:60118865; 
    reference:url,github.com/example; 
    rev:1; 
    metadata:created_at 2024_12_15;
)
```

### 规则解析

| 部分 | 说明 | 示例值 |
|------|------|--------|
| `alert http` | 协议类型 | HTTP协议 |
| `msg` | 规则描述 | "用友NC SQL注入漏洞" |
| `flow` | 流向 | established,to_server |
| `content` | 匹配内容 | "infopub/showcontent" |
| `pcre` | 正则表达式 | 检测SQL注入关键字 |
| `classtype` | 分类 | web-application-attack |
| `sid` | 规则ID | 60118865 |
| `rev` | 版本号 | 1 |

---

## 规则验证

### 步骤1：设置PCAP路径

**默认路径**：`/home/kali/pcap_check`

**自定义路径**：
- 单个文件：`/path/to/test.pcap`
- 目录：`/path/to/pcap_folder/`

### 步骤2：执行验证

1. **点击按钮**：点击"✓ 验证规则"
2. **等待处理**：显示"验证中..."（5-30秒）
3. **查看结果**：验证结果显示在下方

### 验证结果解读

#### 结果示例1：匹配成功
```
┌─────────────────────────────────────┐
│ 验证结果                             │
├─────────────────────────────────────┤
│ 匹配状态: ✓                          │
│ 告警数量: 15                         │
├─────────────────────────────────────┤
│ 告警详情:                            │
│ 01/15 12:34:56.789 [**] [1:6011... │
│ 01/15 12:35:01.234 [**] [1:6011... │
│ 01/15 12:35:05.678 [**] [1:6011... │
├─────────────────────────────────────┤
│ SID统计:                             │
│ 15x [1:60118865:1]                  │
└─────────────────────────────────────┘
```

**解读**：
- ✅ 规则成功匹配恶意流量
- ✅ 检测到15次攻击尝试
- ✅ 规则工作正常

#### 结果示例2：未匹配
```
┌─────────────────────────────────────┐
│ 验证结果                             │
├─────────────────────────────────────┤
│ 匹配状态: ✗                          │
│ 告警数量: 0                          │
└─────────────────────────────────────┘
```

**可能原因**：
- ⚠️ PCAP中无对应攻击流量
- ⚠️ 规则特征不匹配
- ⚠️ 规则语法错误

**建议操作**：
1. 检查PCAP是否包含攻击流量
2. 尝试优化规则
3. 检查规则语法

#### Windows环境说明

```
┌─────────────────────────────────────┐
│ 验证结果                             │
├─────────────────────────────────────┤
│ 匹配状态: ✓ (模拟)                   │
│ 告警数量: 1                          │
│ 注意: 这是模拟验证结果               │
│ (Suricata not available on Windows) │
└─────────────────────────────────────┘
```

**说明**：Windows环境返回模拟结果，真实验证需Kali Linux

---

## 规则优化

### 何时优化？

优化规则的常见场景：

1. **验证未匹配**：规则未检测到已知攻击
2. **误报过多**：正常流量被误判为攻击
3. **性能问题**：规则影响网络性能
4. **规范调整**：需要符合新的检测规范

### 步骤1：准备优化信息

**验证结果反馈**：
```
示例1：未匹配
- PCAP中确认存在SQL注入攻击
- 规则未触发告警
- 可能是正则表达式过于严格

示例2：误报
- 正常业务请求被标记为攻击
- 需要更精确的特征匹配
- 建议添加更多限制条件
```

**用户反馈**：
```
示例：
1. 规则未检测到base64编码的注入
2. 希望增加对时间盲注的检测
3. 需要降低误报率
```

### 步骤2：执行优化

1. **点击按钮**：点击"🔧 AI优化"
2. **输入建议**：在弹窗中输入优化建议（可选）
3. **等待处理**：AI分析并生成优化规则
4. **对比查看**：查看优化前后的差异

### 优化示例

**优化前**：
```
alert http any any -> any any (
    msg:"SQL注入检测"; 
    content:"id="; 
    pcre:"/id=.*select/i"; 
    sid:10001;
)
```

**优化建议**：
```
1. 添加HTTP流向限制
2. 优化正则表达式，避免绕过
3. 增加更多SQL关键字
4. 添加分类和参考信息
```

**优化后**：
```
alert http any any -> any any (
    msg:"SQL注入检测 - 优化版"; 
    flow:established,to_server; 
    http.uri.raw; 
    content:"id="; nocase; 
    pcre:"/id=[^\r\n\x26]{0,10}(select|union|sleep|load|from|concat|where|outfile|waitfor|updatexml)/Ii"; 
    classtype:web-application-attack; 
    sid:10001; 
    rev:2;
)
```

**改进点**：
- ✅ 添加flow限制
- ✅ 优化正则表达式作用域
- ✅ 增加SQL关键字覆盖
- ✅ 添加分类信息
- ✅ 更新版本号

### 步骤3：验证优化效果

1. **再次验证**：点击"✓ 验证规则"
2. **对比结果**：比较优化前后的检测效果
3. **迭代优化**：根据需要继续优化

---

## 历史管理

### 查看历史记录

1. **切换标签**：点击"历史记录"标签
2. **浏览列表**：查看所有生成的规则
3. **加载规则**：点击任意记录加载到编辑器

### 历史记录卡片

```
┌──────────────────────────────────────┐
│ 2024-12-15 14:30:25                  │
│ 用友NC SQL注入漏洞                    │
│ 类型: sql_injection | 状态: draft    │
│ ─────────────────────────────────    │
│ alert http any any -> any any (      │
│   msg:"用友NC SQL注入漏洞";          │
│   flow:established,to_server;        │
│   ...                                │
│ )                                    │
└──────────────────────────────────────┘
```

### 规则状态

| 状态 | 说明 | 图标 |
|------|------|------|
| draft | 草稿 | 📝 |
| validated | 已验证 | ✅ |
| optimized | 已优化 | 🔧 |
| deployed | 已部署 | 🚀 |

---

## 实战案例

### 案例1：文件上传漏洞检测

**场景**：检测PHP文件上传攻击

**步骤**：

1. **输入信息**
```
漏洞名称：SourceCodester 文件上传漏洞(CVE-2024-24498)
漏洞类型：file_upload
漏洞描述：
Employee Management System存在任意文件上传漏洞，
攻击者可上传PHP WebShell获取服务器权限。

POC：
POST /Admin/edit-photo.php HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="avatar"; filename="shell.php"
Content-Type: image/jpeg

<?php eval($_POST['cmd']); ?>
------WebKitFormBoundary--
```

2. **AI生成规则**
```
alert http any any -> any any (
    msg:"SourceCodester 文件上传漏洞(CVE-2024-24498)"; 
    flow:established,to_server; 
    http.uri; 
    content:"/Admin/edit-photo.php"; nocase; 
    http.request_body; 
    content:"name=|22|avatar|22|"; nocase; 
    content:"filename="; nocase; 
    content:"<?php"; distance:0; 
    reference:cve,2024-24498; 
    classtype:web-application-attack; 
    sid:60118800; 
    rev:1;
)
```

3. **验证结果**
- ✅ 成功检测到PHP文件上传
- ✅ 匹配到`<?php`标记
- ✅ 告警数量：5

### 案例2：命令注入漏洞检测

**场景**：检测路由器命令注入

**步骤**：

1. **输入信息**
```
漏洞名称：Netis WF2780 命令注入(CVE-2021-26747)
漏洞类型：command_injection
漏洞描述：
Netis路由器在netcore_get.cgi的tools_ip_url参数存在命令注入，
攻击者可通过分号、管道符等执行任意系统命令。

POC：
POST /cgi-bin-igd/netcore_get.cgi HTTP/1.1

tools_ip_url=127.0.0.1;cat /etc/passwd
```

2. **AI生成规则**
```
alert http any any -> any any (
    msg:"Netis WF2780 命令注入(CVE-2021-26747)"; 
    flow:established,to_server; 
    http.uri; 
    content:"/cgi-bin-igd/netcore_get.cgi"; nocase; 
    http.request_body; 
    content:"tools_ip_url="; nocase; 
    pcre:"/tools_ip_url=[^\r\n\x26]{0,10}(\x60|\x2560|\x27|\x2527|\x3b|\x253b|\x7c|\x257c)/Pi"; 
    classtype:web-application-attack; 
    sid:60117503; 
    rev:1;
)
```

3. **优化**（增加命令关键字检测）
```
建议：添加对cat、ls、wget等命令的检测
```

优化后增加：
```
pcre:"/tools_ip_url=.{0,20}(cat|ls|wget|curl|bash|sh|nc)/Pi";
```

---

## 常见问题

### Q1: AI生成速度慢？

**A**: 正常情况3-10秒，如果超过30秒：
1. 检查网络连接
2. 确认AI API可用
3. 简化漏洞描述长度

### Q2: 验证一直失败？

**A**: 排查步骤：
1. 确认PCAP路径正确
2. 检查Suricata是否安装（Linux）
3. Windows环境查看模拟结果
4. 检查规则语法是否正确

### Q3: 如何提高规则质量？

**A**: 最佳实践：
1. 提供详细的POC示例
2. 准确描述漏洞利用点
3. 使用真实的PCAP验证
4. 多次迭代优化规则

### Q4: 数据库文件在哪？

**A**: 
```
位置：backend/suricata_rules.db
查看：使用SQLite工具打开
备份：复制db文件即可
```

### Q5: 如何导出规则？

**A**: 
```
方法1：从历史记录复制
方法2：直接访问数据库
方法3：使用API导出（计划中）
```

### Q6: 支持哪些漏洞类型？

**A**: 当前支持：
- ✅ SQL注入
- ✅ 命令注入
- ✅ 文件上传
- ✅ 路径穿越
- ✅ SSRF
- ✅ 未授权访问
- ✅ XSS攻击
- ✅ XXE注入

### Q7: 能否批量生成规则？

**A**: 
当前版本需逐个生成，批量功能在规划中。
临时方案：使用API接口编写批量脚本。

---

## 进阶技巧

### 技巧1：使用API批量操作

```python
import requests

api = "http://localhost:5000/api"

# 批量生成
vulns = [
    {"name": "漏洞1", "desc": "描述1"},
    {"name": "漏洞2", "desc": "描述2"},
]

for vuln in vulns:
    requests.post(f"{api}/rules/generate", json=vuln)
```

### 技巧2：规则模板化

创建常用规则模板，加快生成速度：

```python
templates = {
    "sql_injection": """
漏洞类型：SQL注入
检测位置：URL参数
关键字：select, union, sleep
    """,
    "command_injection": """
漏洞类型：命令注入
检测符号：; | ` $
关键命令：cat, ls, wget
    """
}
```

### 技巧3：规则测试最佳实践

1. **准备多样化PCAP**
   - 正常流量样本
   - 攻击流量样本
   - 边界情况样本

2. **持续验证**
   - 每次优化后验证
   - 使用不同PCAP验证
   - 记录验证结果

3. **性能测试**
   - 大流量PCAP测试
   - 监控CPU使用
   - 检查内存占用

---

## 总结

### 完整工作流程

```
输入漏洞信息 
    ↓
AI生成规则
    ↓
编辑/调整规则
    ↓
PCAP验证
    ↓
查看结果 → 满意？ → 是 → 保存/部署
    ↓              ↓
    否            结束
    ↓
AI优化规则
    ↓
重新验证
    ↓
迭代优化
```

### 快捷键

| 功能 | 快捷操作 |
|------|----------|
| 生成规则 | 填写信息后直接点击生成 |
| 验证规则 | Ctrl+Enter（规则框内） |
| 保存规则 | 自动保存到数据库 |
| 加载历史 | 点击历史记录卡片 |

### 下一步

- 🎯 开始生成你的第一条规则
- 📚 阅读规则编写规范
- 🔧 尝试优化现有规则
- 🚀 部署规则到生产环境

---

**祝您使用愉快！** 🎉

有问题请查看 [README.md](README.md) 或 [QUICKSTART.md](QUICKSTART.md)
