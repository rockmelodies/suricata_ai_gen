#!/usr/bin/env python
# encoding: utf-8
# Universal LLM Client supporting multiple providers

import os
import requests
import json
from typing import Optional, Dict, Any


class LLMClient:
    def __init__(self, provider: str = "openai", api_key: str = "", model: str = "", base_url: str = ""):
        """
        Initialize LLM client with specified provider
        
        Args:
            provider: LLM provider (openai, gemini, claude, qwen, deepseek, zhipu, moonshot, ollama, baidu, minimax, doubao, 360ai)
            api_key: API key for the provider
            model: Model name to use
            base_url: Custom API endpoint (optional)
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model or self._get_default_model()
        self.base_url = base_url or self._get_default_base_url()
        
        # Setup headers based on provider
        self.headers = self._setup_headers()

    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        defaults = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-2.0-flash",
            "claude": "claude-3-haiku-20240307",
            "qwen": "qwen-turbo",
            "deepseek": "deepseek-chat",
            "zhipu": "glm-4-flash",
            "moonshot": "moonshot-v1-8k",
            "ollama": "llama3",
            "baidu": "ernie-bot-turbo",
            "minimax": "abab6.5-chat",
            "doubao": "Doubao-lite-128k",
            "360ai": "360gpt-pro"
        }
        return defaults.get(self.provider, "gpt-3.5-turbo")

    def _get_default_base_url(self) -> str:
        """Get default base URL based on provider"""
        defaults = {
            "openai": "https://api.openai.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
            "claude": "https://api.anthropic.com/v1",  # Note: Claude uses different auth
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
            "moonshot": "https://api.moonshot.cn/v1",
            "ollama": "http://localhost:11434/v1",
            "baidu": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
            "minimax": "https://api.minimax.chat/v1",
            "doubao": "https://ark.cn-beijing.volces.com/api/v3",
            "360ai": "https://api.360.cn/v1"
        }
        return defaults.get(self.provider, "https://api.openai.com/v1")

    def _setup_headers(self) -> Dict[str, str]:
        """Setup request headers based on provider"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.provider == "claude":
            headers['x-api-key'] = self.api_key
            headers['anthropic-version'] = '2023-06-01'
        elif self.provider == "baidu":
            # Baidu uses access token in URL params, not headers
            pass
        elif self.provider == "gemini":
            headers['Content-Type'] = 'application/json'
        else:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        return headers

    def _prepare_messages(self, content: str) -> list:
        """Prepare messages in format required by the provider"""
        if self.provider in ["gemini"]:
            # Gemini uses a different format
            return [{"role": "user", "parts": [{"text": content}]}]
        else:
            # Standard OpenAI format
            return [{"role": "user", "content": content}]

    def _build_payload(self, messages: list, stream: bool = False, **kwargs) -> Dict[str, Any]:
        """Build request payload based on provider"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        # Add provider-specific parameters
        if self.provider == "gemini":
            payload.pop("model")  # Gemini doesn't use model in request body for chat
            payload["contents"] = messages
            payload.pop("messages")
        elif self.provider == "baidu":
            payload["url"] = f"{self.base_url}/completions?access_token={self.api_key}"
            payload["params"] = kwargs
        elif self.provider == "claude":
            payload["model"] = self.model  # Claude requires model in payload
            payload["prompt"] = f"\n\nHuman: {messages[0]['content']}\n\nAssistant:"
            payload.pop("messages")
        elif self.provider == "ollama":
            payload["options"] = {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048),
            }
        else:
            # Standard parameters for most providers
            payload.update({
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "top_p": kwargs.get("top_p", 1.0),
            })
        
        return payload

    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process response based on provider format"""
        try:
            if self.provider == "gemini":
                candidates = response.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return {"choices": [{"message": {"content": content}}]}
            elif self.provider == "baidu":
                result = response.get("result", "")
                return {"choices": [{"message": {"content": result}}]}
            elif self.provider == "claude":
                content = response.get("completion", "")
                return {"choices": [{"message": {"content": content}}]}
            elif self.provider == "ollama":
                message = response.get("message", {})
                content = message.get("content", response.get("response", ""))
                return {"choices": [{"message": {"content": content}}]}
        except Exception:
            pass
        
        # Default: return as-is
        return response

    def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using the configured LLM"""
        messages = self._prepare_messages(prompt)
        payload = self._build_payload(messages, **kwargs)
        
        # Handle provider-specific URL construction
        if self.provider == "gemini":
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            headers = {'Content-Type': 'application/json'}
        elif self.provider == "baidu":
            # For Baidu, we need to get access token first or use the token in URL
            url = f"{self.base_url}/completions?access_token={self.api_key}"
            headers = {'Content-Type': 'application/json'}
        elif self.provider == "claude":
            url = f"{self.base_url}/complete"
            headers = self.headers.copy()
        else:
            url = f"{self.base_url}/chat/completions"
            headers = self.headers.copy()
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=kwargs.get("timeout", 150))
            response.raise_for_status()
            result = response.json()
            return self._process_response(result)
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def generate_rule(self, vuln_name: str, vuln_description: str, vuln_type: str = "", poc: str = "") -> Dict[str, Any]:
        """Generate Suricata rule based on vulnerability information"""
        prompt = f"""你是一个专业的网络安全专家和Suricata规则编写专家。请根据以下漏洞信息生成高质量的Suricata检测规则。

漏洞名称: {vuln_name}
漏洞类型: {vuln_type}
漏洞描述: {vuln_description}
POC示例: {poc}

请输出符合以下要求的Suricata规则：
1. 遵循Suricata官方规范
2. 包含恰当的协议和方向设置
3. 使用有效的正则表达式和content匹配
4. 包含适当的分类和参考信息
5. 确保规则具有高检测率和低误报率
6. 使用合适的SID值（如果是新的规则，建议使用大于60000000的SID值）

请直接输出规则内容，不要包含额外解释。"""
        
        return self.generate_text(
            prompt,
            temperature=0.1,
            max_tokens=4096
        )

    def optimize_rule(self, current_rule: str, feedback: str = "") -> Dict[str, Any]:
        """Optimize existing Suricata rule based on feedback"""
        prompt = f"""请优化以下Suricata规则，使其更加精确和高效：

当前规则:
{current_rule}

优化反馈:
{feedback}

请输出优化后的规则，并简要说明优化要点。如果规则本身已经很好，则说明其优点。"""
        
        return self.generate_text(
            prompt,
            temperature=0.3,
            max_tokens=4096
        )


def create_llm_client_from_env():
    """Create LLM client using environment variables"""
    provider = os.getenv('LLM_PROVIDER', '360ai')
    api_key = os.getenv('LLM_API_KEY', os.getenv('AI_API_KEY', ''))
    model = os.getenv('LLM_MODEL', '')
    base_url = os.getenv('LLM_BASE_URL', '')
    
    timeout = int(os.getenv('LLM_TIMEOUT', '150'))
    temperature = float(os.getenv('LLM_TEMPERATURE', '0.1'))
    max_tokens = int(os.getenv('LLM_MAX_TOKENS', '4096'))
    
    return LLMClient(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url
    )


if __name__ == "__main__":
    # Example usage
    client = create_llm_client_from_env()
    
    # Test rule generation
    result = client.generate_rule(
        vuln_name="SQL注入",
        vuln_description="应用程序未对用户输入进行充分过滤，导致SQL注入漏洞",
        vuln_type="web",
        poc="id=1' OR '1'='1"
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))