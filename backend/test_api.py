#!/usr/bin/env python
# encoding: utf-8
"""
API测试脚本 - 测试后端v2的所有功能
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """打印响应"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")

def test_api():
    """测试API"""
    
    # 1. 健康检查
    print("\n" + "="*60)
    print("🚀 开始API测试")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print_response("1. 健康检查", response)
    
    # 2. 用户登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("2. 管理员登录", response)
    
    if response.status_code != 200:
        print("\n❌ 登录失败，停止测试")
        return
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. 获取当前用户信息
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("3. 获取当前用户信息", response)
    
    # 4. 获取用户列表
    response = requests.get(f"{BASE_URL}/users?page=1&per_page=10", headers=headers)
    print_response("4. 获取用户列表", response)
    
    # 5. 注册新用户
    register_data = {
        "username": "testuser",
        "password": "test123",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response("5. 注册新用户", response)
    
    # 6. 生成规则（需要AI API Key）
    rule_data = {
        "vuln_name": "测试SQL注入漏洞",
        "vuln_description": "存在SQL注入漏洞，可通过id参数注入恶意SQL语句",
        "vuln_type": "SQL注入",
        "poc": "http://example.com/user.php?id=1' union select 1,2,3--"
    }
    response = requests.post(f"{BASE_URL}/rules/generate", json=rule_data, headers=headers)
    print_response("6. 生成Suricata规则", response)
    
    # 7. 获取规则列表
    response = requests.get(f"{BASE_URL}/rules?page=1&per_page=10", headers=headers)
    print_response("7. 获取规则列表", response)
    
    # 8. 如果有规则，获取详情
    if response.status_code == 200:
        rules = response.json().get('rules', [])
        if rules:
            rule_id = rules[0]['id']
            response = requests.get(f"{BASE_URL}/rules/{rule_id}", headers=headers)
            print_response(f"8. 获取规则详情 (ID: {rule_id})", response)
    
    print("\n" + "="*60)
    print("✅ API测试完成")
    print("="*60)
    print("\n📖 在浏览器中访问 http://localhost:5000/api/docs 查看完整API文档")

if __name__ == '__main__':
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到API服务器")
        print("请确保后端服务正在运行: cd backend && bash start_v2.sh")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
