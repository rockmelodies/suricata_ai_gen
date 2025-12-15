#!/usr/bin/env python
# encoding: utf-8
# AI Chat Client for 360 AI API

import requests
import json


class AIChatClient:
    def __init__(self, api_key, model="360gpt-pro"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.360.cn/v1/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def create_payload(self, user_id, content, stream=False, temperature=0.9, max_tokens=2048, top_p=0.5, top_k=0,
                       repetition_penalty=1.05, num_beams=1):
        """Create request payload for AI API"""
        messages = [
            {
                "role": "user",
                "content": content
            }
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "num_beams": num_beams,
            "user": user_id
        }
        return json.dumps(payload)

    def send_request(self, payload):
        """Send request to AI API and return response"""
        try:
            response = requests.post(self.url, headers=self.headers, data=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def generate_rule(self, vuln_name, vuln_description, vuln_type="", poc=""):
        """High-level method to generate Suricata rule"""
        prompt = f"""你是一个Suricata规则编写专家。请根据以下漏洞信息生成规则。

漏洞名称: {vuln_name}
漏洞类型: {vuln_type}
描述: {vuln_description}
POC: {poc}

请输出符合Suricata规范的规则，包括正确的正则表达式和作用域。
"""
        payload = self.create_payload(
            user_id="rule_generator",
            content=prompt,
            temperature=0.7
        )
        return self.send_request(payload)

    def optimize_rule(self, current_rule, feedback=""):
        """High-level method to optimize Suricata rule"""
        prompt = f"""请优化以下Suricata规则:

当前规则:
{current_rule}

反馈意见:
{feedback}

请输出优化后的规则。
"""
        payload = self.create_payload(
            user_id="rule_optimizer",
            content=prompt,
            temperature=0.6
        )
        return self.send_request(payload)
