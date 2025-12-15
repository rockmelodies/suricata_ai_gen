#!/usr/bin/env python
# encoding: utf-8
# Suricata Rule Generation and Validation Tool - Backend API

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from database import Database
from ai_client import AIChatClient
from suricata_validator import SuricataValidator

app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = "fk168504229.k2h9hyebSX7c_UzjTA5U5T0t_3IzR10124707b23"
DB_PATH = os.path.join(os.path.dirname(__file__), 'suricata_rules.db')

# Initialize components
db = Database(DB_PATH)
ai_client = AIChatClient(API_KEY, model="360gpt-pro")
suricata_validator = SuricataValidator()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route('/api/rules/generate', methods=['POST'])
def generate_rule():
    """Generate Suricata rule using AI based on vulnerability description"""
    try:
        data = request.json
        vuln_name = data.get('vuln_name', '')
        vuln_description = data.get('vuln_description', '')
        vuln_type = data.get('vuln_type', '')
        poc = data.get('poc', '')
        
        if not vuln_name or not vuln_description:
            return jsonify({"error": "缺少必要参数: vuln_name 和 vuln_description"}), 400
        
        # Build AI prompt based on the specification
        prompt = build_rule_generation_prompt(vuln_name, vuln_description, vuln_type, poc)
        
        # Call AI to generate rule
        payload = ai_client.create_payload(
            user_id="suricata_rule_generator",
            content=prompt,
            temperature=0.7,
            max_tokens=2048
        )
        
        ai_response = ai_client.send_request(payload)
        
        # Extract generated rule from AI response
        if 'choices' in ai_response and len(ai_response['choices']) > 0:
            generated_rule = ai_response['choices'][0]['message']['content'].strip()
            
            # Save to database
            rule_id = db.insert_rule(
                vuln_name=vuln_name,
                original_rule=generated_rule,
                current_rule=generated_rule,
                vuln_type=vuln_type,
                description=vuln_description
            )
            
            return jsonify({
                "success": True,
                "rule_id": rule_id,
                "generated_rule": generated_rule,
                "ai_response": ai_response
            })
        else:
            return jsonify({"error": "AI生成失败", "response": ai_response}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules/optimize', methods=['POST'])
def optimize_rule():
    """Optimize existing rule using AI"""
    try:
        data = request.json
        rule_id = data.get('rule_id')
        current_rule = data.get('current_rule', '')
        feedback = data.get('feedback', '')
        validation_result = data.get('validation_result', '')
        
        if not current_rule:
            return jsonify({"error": "缺少规则内容"}), 400
        
        # Build optimization prompt
        prompt = build_rule_optimization_prompt(current_rule, feedback, validation_result)
        
        # Call AI to optimize rule
        payload = ai_client.create_payload(
            user_id="suricata_rule_optimizer",
            content=prompt,
            temperature=0.6,
            max_tokens=2048
        )
        
        ai_response = ai_client.send_request(payload)
        
        # Extract optimized rule
        if 'choices' in ai_response and len(ai_response['choices']) > 0:
            optimized_rule = ai_response['choices'][0]['message']['content'].strip()
            
            # Update database if rule_id provided
            if rule_id:
                db.update_rule(rule_id, optimized_rule)
                db.insert_optimization_history(
                    rule_id=rule_id,
                    original_rule=current_rule,
                    optimized_rule=optimized_rule,
                    feedback=feedback,
                    ai_suggestion=optimized_rule
                )
            
            return jsonify({
                "success": True,
                "optimized_rule": optimized_rule,
                "ai_response": ai_response
            })
        else:
            return jsonify({"error": "AI优化失败", "response": ai_response}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules/validate', methods=['POST'])
def validate_rule():
    """Validate Suricata rule against PCAP files"""
    try:
        data = request.json
        rule_content = data.get('rule_content', '')
        rule_id = data.get('rule_id')
        pcap_path = data.get('pcap_path', '/home/kali/pcap_check')
        
        if not rule_content:
            return jsonify({"error": "缺少规则内容"}), 400
        
        # Validate the rule
        validation_result = suricata_validator.validate_rule(rule_content, pcap_path)
        
        # Save validation result to database
        if rule_id:
            db.insert_validation_result(
                rule_id=rule_id,
                pcap_path=pcap_path,
                matched=validation_result['matched'],
                alert_count=validation_result['alert_count'],
                details=json.dumps(validation_result['details']),
                sid_stats=json.dumps(validation_result['sid_stats'])
            )
        
        return jsonify({
            "success": True,
            "validation_result": validation_result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules/<int:rule_id>', methods=['GET'])
def get_rule(rule_id):
    """Get rule details by ID"""
    try:
        rule = db.get_rule_by_id(rule_id)
        if rule:
            return jsonify({"success": True, "rule": rule})
        else:
            return jsonify({"error": "规则不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules', methods=['GET'])
def list_rules():
    """List all rules with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        rules = db.get_all_rules(page=page, per_page=per_page)
        total = db.get_rules_count()
        
        return jsonify({
            "success": True,
            "rules": rules,
            "total": total,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules/<int:rule_id>/history', methods=['GET'])
def get_optimization_history(rule_id):
    """Get optimization history for a rule"""
    try:
        history = db.get_optimization_history(rule_id)
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rules/<int:rule_id>/validations', methods=['GET'])
def get_validation_history(rule_id):
    """Get validation history for a rule"""
    try:
        validations = db.get_validation_results(rule_id)
        return jsonify({"success": True, "validations": validations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def build_rule_generation_prompt(vuln_name, vuln_description, vuln_type, poc):
    """Build AI prompt for rule generation"""
    prompt = f"""你是一个Suricata规则编写专家。请根据以下漏洞信息生成一条符合360NDR漏洞类Suricata规则编写规范的规则。

漏洞名称: {vuln_name}
漏洞类型: {vuln_type}
漏洞描述: {vuln_description}
"""
    
    if poc:
        prompt += f"\nPOC示例:\n{poc}\n"
    
    prompt += """
请严格遵循以下规范:
1. HTTP类特征选取:
   - 省略http.method，除非明确只能使用某一固定方法
   - URL路径尽量少取1-2级目录，避免固定安装路径
   - 去除路径最后的问号?，在问号前增加斜杠
   - 请求参数必须包含漏洞利用点，冗余参数可省略
   - 各参数拆分成多个content

2. 正则表达式要求:
   - 必须限制作用域(U/I/H/P等)
   - 使用通用正则避免绕过
   - 正则必须带上漏洞利用点参数

3. 规则格式:
   - alert http any any -> any any (msg:"xxx"; ...)
   - 必须包含: msg, flow, classtype, sid
   - 建议包含: reference, rev, metadata

请直接输出Suricata规则，不要包含其他解释文字。
"""
    
    return prompt


def build_rule_optimization_prompt(current_rule, feedback, validation_result):
    """Build AI prompt for rule optimization"""
    prompt = f"""你是一个Suricata规则优化专家。请优化以下规则，使其更加准确和高效。

当前规则:
{current_rule}
"""
    
    if feedback:
        prompt += f"\n用户反馈:\n{feedback}\n"
    
    if validation_result:
        prompt += f"\n验证结果:\n{validation_result}\n"
    
    prompt += """
优化要求:
1. 确保规则符合360NDR规范
2. 提高检测准确率，减少误报
3. 优化正则表达式，避免绕过
4. 保持规则的可读性和可维护性

请直接输出优化后的Suricata规则，不要包含其他解释文字。
"""
    
    return prompt


if __name__ == '__main__':
    # Initialize database
    db.init_db()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
