#!/usr/bin/env python
# encoding: utf-8
# Test and Example Script for Suricata Rule Generator

"""
This script demonstrates how to use the Suricata Rule Generator API
Run the backend first: python backend/app.py
Then run this script: python test_example.py
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:5000/api"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def test_health_check():
    """Test health check endpoint"""
    print_header("Testing Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_generate_rule():
    """Test rule generation"""
    print_header("Testing Rule Generation")
    
    # Example vulnerability information
    vuln_data = {
        "vuln_name": "用友NC SQL注入漏洞测试",
        "vuln_type": "sql_injection",
        "vuln_description": "用友NC系统在infopub/showcontent接口存在SQL注入漏洞，攻击者可通过id参数注入恶意SQL语句",
        "poc": """
GET /infopub/showcontent?id=1' union select 1,2,database()-- HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0
"""
    }
    
    try:
        print("Sending request to generate rule...")
        print(f"Vulnerability: {vuln_data['vuln_name']}")
        
        response = requests.post(
            f"{API_BASE_URL}/rules/generate",
            json=vuln_data,
            timeout=60
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("\n✓ Rule generated successfully!")
                print(f"\nRule ID: {result['rule_id']}")
                print(f"\nGenerated Rule:\n{'-'*60}")
                print(result['generated_rule'])
                print('-'*60)
                return result['rule_id'], result['generated_rule']
            else:
                print(f"\n✗ Generation failed: {result.get('error')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None, None

def test_validate_rule(rule_content, rule_id=None):
    """Test rule validation"""
    print_header("Testing Rule Validation")
    
    validation_data = {
        "rule_content": rule_content,
        "rule_id": rule_id,
        "pcap_path": "/home/kali/pcap_check"
    }
    
    try:
        print("Sending validation request...")
        print(f"Rule to validate:\n{rule_content[:100]}...")
        
        response = requests.post(
            f"{API_BASE_URL}/rules/validate",
            json=validation_data,
            timeout=300
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                validation = result['validation_result']
                print("\n✓ Validation completed!")
                print(f"\nMatched: {validation.get('matched')}")
                print(f"Alert Count: {validation.get('alert_count')}")
                
                if validation.get('details'):
                    print(f"\nAlert Details:")
                    for detail in validation['details'][:3]:
                        print(f"  {detail}")
                
                if validation.get('sid_stats'):
                    print(f"\nSID Statistics:")
                    for sid, count in validation['sid_stats'].items():
                        print(f"  {sid}: {count}")
                
                if validation.get('note'):
                    print(f"\nNote: {validation['note']}")
                
                return validation
            else:
                print(f"\n✗ Validation failed: {result.get('error')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_optimize_rule(rule_content, rule_id=None):
    """Test rule optimization"""
    print_header("Testing Rule Optimization")
    
    optimization_data = {
        "rule_id": rule_id,
        "current_rule": rule_content,
        "feedback": "请优化正则表达式，提高检测准确率，避免误报"
    }
    
    try:
        print("Sending optimization request...")
        
        response = requests.post(
            f"{API_BASE_URL}/rules/optimize",
            json=optimization_data,
            timeout=60
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("\n✓ Rule optimized successfully!")
                print(f"\nOptimized Rule:\n{'-'*60}")
                print(result['optimized_rule'])
                print('-'*60)
                return result['optimized_rule']
            else:
                print(f"\n✗ Optimization failed: {result.get('error')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_list_rules():
    """Test listing rules"""
    print_header("Testing List Rules")
    
    try:
        response = requests.get(f"{API_BASE_URL}/rules?page=1&per_page=10")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"\n✓ Retrieved {len(result['rules'])} rules")
                print(f"Total rules in database: {result['total']}")
                
                if result['rules']:
                    print("\nRecent Rules:")
                    for rule in result['rules'][:3]:
                        print(f"\n  ID: {rule['id']}")
                        print(f"  Name: {rule['vuln_name']}")
                        print(f"  Type: {rule.get('vuln_type', 'N/A')}")
                        print(f"  Created: {rule['created_at']}")
            else:
                print(f"\n✗ Failed: {result.get('error')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def run_full_workflow():
    """Run complete workflow demonstration"""
    print_header("SURICATA RULE GENERATOR - FULL WORKFLOW TEST")
    
    print("This script will test the complete workflow:")
    print("1. Health Check")
    print("2. Generate Rule")
    print("3. Validate Rule")
    print("4. Optimize Rule")
    print("5. List Rules")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Health Check
    if not test_health_check():
        print("\n✗ Backend is not running!")
        print("Please start the backend first: python backend/app.py")
        return
    
    time.sleep(1)
    
    # Step 2: Generate Rule
    rule_id, rule_content = test_generate_rule()
    
    if not rule_content:
        print("\n✗ Rule generation failed. Stopping workflow.")
        return
    
    time.sleep(1)
    
    # Step 3: Validate Rule
    validation_result = test_validate_rule(rule_content, rule_id)
    
    time.sleep(1)
    
    # Step 4: Optimize Rule
    if rule_content:
        optimized_rule = test_optimize_rule(rule_content, rule_id)
        
        if optimized_rule:
            time.sleep(1)
            # Validate optimized rule
            test_validate_rule(optimized_rule, rule_id)
    
    time.sleep(1)
    
    # Step 5: List Rules
    test_list_rules()
    
    print_header("WORKFLOW COMPLETE")
    print("Check the database file: backend/suricata_rules.db")
    print("Open the frontend to view results: http://localhost:8080")

if __name__ == "__main__":
    try:
        run_full_workflow()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
