# 支持的大语言模型配置指南

本文档详细介绍了如何配置和使用不同的大语言模型提供商。

## 目录
- [支持的模型提供商](#支持的模型提供商)
- [通用配置说明](#通用配置说明)
- [各提供商配置示例](#各提供商配置示例)
- [性能优化建议](#性能优化建议)

## 支持的模型提供商

### 原生支持的提供商
- **OpenAI**: GPT系列模型
- **Google Gemini**: Gemini系列模型
- **Anthropic Claude**: Claude系列模型
- **阿里通义千问**: Qwen系列模型
- **DeepSeek**: DeepSeek系列模型
- **智谱AI**: GLM系列模型
- **月之暗面**: Moonshot系列模型
- **360智脑**: 360gpt系列模型

### 通过LiteLLM支持的提供商
- **Ollama**: 本地模型
- **百度文心一言**: ERNIE Bot系列
- **MiniMax**: Abab系列模型
- **字节豆包**: Doubao系列模型

## 通用配置说明

### 环境变量配置

在 `.env` 文件中配置以下变量：

```bash
# LLM 通用配置
LLM_PROVIDER=openai                    # 模型提供商
LLM_API_KEY=your_api_key_here          # API密钥
LLM_MODEL=gpt-4o-mini                  # 模型名称
LLM_BASE_URL=https://api.openai.com/v1 # API端点（可选）
LLM_TIMEOUT=150                        # 请求超时时间
LLM_TEMPERATURE=0.1                    # 生成温度
LLM_MAX_TOKENS=4096                    # 最大Token数
```

### 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `LLM_PROVIDER` | 模型提供商标识 | `openai` |
| `LLM_API_KEY` | API访问密钥 | - |
| `LLM_MODEL` | 具体模型名称 | 根据提供商而定 |
| `LLM_BASE_URL` | API端点URL | 根据提供商而定 |
| `LLM_TIMEOUT` | 请求超时时间(秒) | `150` |
| `LLM_TEMPERATURE` | 生成温度(0-1) | `0.1` |
| `LLM_MAX_TOKENS` | 最大Token数 | `4096` |

## 各提供商配置示例

### OpenAI

```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `gpt-4o-mini` - 高性价比模型
- `gpt-4o` - 高性能模型
- `gpt-3.5-turbo` - 经济型模型

### Google Gemini

```bash
LLM_PROVIDER=gemini
LLM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=gemini-2.0-flash
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `gemini-2.0-flash` - 快速响应模型
- `gemini-1.5-pro` - 强大推理能力
- `gemini-1.5-flash` - 平衡性能模型

### Anthropic Claude

```bash
LLM_PROVIDER=claude
LLM_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `claude-3-5-sonnet-20241022` - 最新高性能模型
- `claude-3-opus-20240229` - 专业推理模型
- `claude-3-haiku-20240307` - 快速经济模型

### 阿里通义千问

```bash
LLM_PROVIDER=qwen
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=qwen-turbo
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `qwen-turbo` - 高效推理模型
- `qwen-plus` - 平衡性能模型
- `qwen-max` - 强大推理模型

### DeepSeek

```bash
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `deepseek-chat` - 通用聊天模型
- `deepseek-coder` - 代码专用模型

### 智谱AI

```bash
LLM_PROVIDER=zhipu
LLM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=glm-4-flash
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `glm-4-flash` - 快速响应模型
- `glm-4-air` - 经济实用模型
- `glm-4` - 高性能模型

### 月之暗面

```bash
LLM_PROVIDER=moonshot
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=moonshot-v1-8k
LLM_BASE_URL=https://api.moonshot.cn/v1
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `moonshot-v1-8k` - 短文本处理
- `moonshot-v1-32k` - 长文本处理
- `moonshot-v1-128k` - 超长文本处理

### 360智脑

```bash
LLM_PROVIDER=360ai
LLM_API_KEY=fk168504229.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=360gpt-pro
LLM_BASE_URL=https://api.360.cn/v1
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `360gpt-pro` - 高性能模型
- `360gpt-turbo` - 快速经济模型

### Ollama (本地模型)

```bash
LLM_PROVIDER=ollama
LLM_API_KEY=ollama
LLM_MODEL=llama3
LLM_BASE_URL=http://localhost:11434/v1
LLM_TEMPERATURE=0.1
```

**推荐模型**:
- `llama3` - Meta Llama3模型
- `codellama` - 代码专用模型
- `mistral` - Mistral模型
- `phi3` - Microsoft Phi3模型

## 性能优化建议

### 选择合适的模型

对于Suricata规则生成任务，推荐以下模型选择策略：

1. **高精度要求**: Claude 3.5 Sonnet, GPT-4o, GLM-4
2. **成本效益**: GPT-4o Mini, Gemini Flash, Qwen Turbo
3. **代码相关**: DeepSeek Coder, CodeLlama, Phi3
4. **本地部署**: Ollama系列模型

### 温度设置建议

- **规则生成**: `LLM_TEMPERATURE=0.1` - 确保输出一致性
- **创意优化**: `LLM_TEMPERATURE=0.3` - 平衡创造性和准确性
- **探索性任务**: `LLM_TEMPERATURE=0.5` - 增加多样性

### Token配置建议

- **LLM_MAX_TOKENS=4096** - 适用于复杂规则生成
- **LLM_MAX_TOKENS=2048** - 适用于简单规则优化
- **LLM_MAX_TOKENS=1024** - 适用于快速验证任务

### 故障排除

如果遇到API调用失败，请检查：

1. API密钥是否正确
2. 模型名称是否支持
3. API端点URL是否正确
4. 网络连接是否正常
5. API配额是否充足

## 最佳实践

1. **安全存储**: API密钥应存储在环境变量中，不要硬编码
2. **定期轮换**: 定期更换API密钥以增强安全性
3. **监控用量**: 监控API使用量以控制成本
4. **备用配置**: 准备备用模型提供商以防单点故障
5. **性能测试**: 定期测试不同模型的性能表现

通过合理配置和使用这些模型，您可以获得最佳的Suricata规则生成效果。