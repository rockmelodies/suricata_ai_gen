#!/usr/bin/env python
# encoding: utf-8
# Suricata Rule Generation and Validation Tool - Backend API v2

import sys
import os

# Attempt to import dependencies with error handling
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError as e:
    print(f"Error importing Flask dependencies: {e}")
    print("Try installing packages with sudo: sudo pip install -r requirements.txt")
    sys.exit(1)

import json
import hmac
import hashlib
import base64
import secrets
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration - Load from environment variables
# First try to get from LLM_API_KEY, fallback to AI_API_KEY for backward compatibility
API_KEY = os.getenv('LLM_API_KEY') or os.getenv('AI_API_KEY')
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables. Please set either LLM_API_KEY or AI_API_KEY in your .env file")

# Use LLM_MODEL first, then AI_MODEL for backward compatibility
AI_MODEL = os.getenv('LLM_MODEL') or os.getenv('AI_MODEL', '360gpt-pro')
DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), 'suricata_rules.db'))

try:
    from database import Database
    from llm_client import create_llm_client_from_env
    from suricata_validator import SuricataValidator
    from config_manager import ConfigManager
    from user_model import UserModel
except ImportError as e:
    print(f"Error importing internal modules: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# JWT secret key - load from env or generate a stable one
JWT_SECRET = os.getenv('JWT_SECRET_KEY') or os.getenv('SECRET_KEY', secrets.token_hex(32))
JWT_EXPIRE_HOURS = int(os.getenv('JWT_EXPIRE_HOURS', '24'))


def _create_token(user_id: int) -> str:
    """Create a simple HMAC-signed token"""
    expire = int((datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp())
    payload = f"{user_id}:{expire}"
    sig = hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _verify_token(token: str):
    """Verify token and return user_id, or None if invalid"""
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        parts = raw.rsplit(':', 1)
        if len(parts) != 2:
            return None
        payload, sig = parts
        expected_sig = hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        user_id_str, expire_str = payload.split(':', 1)
        if int(expire_str) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return int(user_id_str)
    except Exception:
        return None

# Initialize components
db = Database(DB_PATH)
db.init_db()  # Initialize database tables
llm_client = create_llm_client_from_env()

# Initialize config manager
config_manager = ConfigManager(db)
# Update the config_manager module's global variable
config_manager_module = __import__('config_manager')
config_manager_module.config_manager = config_manager

# 现在完全依赖环境变量进行配置，不再从JSON文件迁移配置
# 所有配置应通过 .env 文件进行设置

# Initialize pcap manager DB
from pcap_manager_db import PCAPManagerDB
pcap_manager_db = PCAPManagerDB(db)

# 注意：为了避免在启动时使用错误的默认值，我们将不在这里创建全局实例
# 而是在每个请求中动态创建，以确保使用最新的配置
suricata_validator = None  # 不再使用全局实例
user_model = UserModel(DB_PATH)


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
        
        # Call LLM to generate rule
        ai_response = llm_client.generate_text(
            prompt,
            temperature=0.1,
            max_tokens=4096
        )
        
        # Extract generated rule from AI response
        if 'error' in ai_response:
            return jsonify({"error": f"AI调用失败: {ai_response['error']}"}), 502

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
        
        # Call LLM to optimize rule
        ai_response = llm_client.generate_text(
            prompt,
            temperature=0.3,
            max_tokens=4096
        )
        
        # Extract optimized rule
        if 'error' in ai_response:
            return jsonify({"error": f"AI调用失败: {ai_response['error']}"}), 502

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
        # 从环境变量获取默认PCAP路径，优先使用PCAP_DIR（兼容旧配置），然后是PCAP_UPLOAD_DIR
        default_pcap_path = os.getenv('PCAP_DIR') or os.getenv('PCAP_UPLOAD_DIR', os.path.join(os.path.dirname(__file__), 'uploads'))
        pcap_path = data.get('pcap_path', default_pcap_path)
        
        if not rule_content:
            return jsonify({"error": "缺少规则内容"}), 400
        
        # 使用环境变量配置创建临时SuricataValidator实例
        from suricata_validator import SuricataValidator
        # 优先从环境变量获取配置，这是主要的配置源
        rules_dir = os.getenv('SURICATA_RULES_DIR', '/var/lib/suricata/rules')
        suricata_config = os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml')
        log_dir = os.getenv('SURICATA_LOG_DIR', '/var/log/suricata')
        
        current_suricata_validator = SuricataValidator.create_validator(
            rules_dir=rules_dir,
            suricata_config=suricata_config,
            log_dir=log_dir
        )
        
        # Validate the rule
        validation_result = current_suricata_validator.validate_rule(rule_content, pcap_path)
        
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


@app.route('/api/pcap/config', methods=['GET'])
def get_pcap_config():
    """Get current PCAP configuration"""
    try:
        # Get configs from both database and environment variables
        db_config = config_manager.get_all_configs()
        
        # Add environment variable configurations
        # Prioritize PCAP_DIR (current config) over PCAP_UPLOAD_DIR (legacy config)
        pcap_dir = os.getenv('PCAP_DIR') or os.getenv('PCAP_UPLOAD_DIR', os.path.join(os.path.dirname(__file__), 'uploads'))
        env_config = {
            'default_pcap_path': pcap_dir,
            'suricata_rules_dir': os.getenv('SURICATA_RULES_DIR', '/var/lib/suricata/rules'),
            'suricata_config': os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml'),
            'suricata_log_dir': os.getenv('SURICATA_LOG_DIR', '/var/log/suricata'),
        }
        
        # Merge configurations (database configs override environment configs)
        merged_config = env_config.copy()
        merged_config.update(db_config)
        
        return jsonify({
            "success": True,
            "config": merged_config
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pcap/config', methods=['POST'])
def set_pcap_config():
    """Set PCAP configuration"""
    try:
        data = request.json
        
        # Support both old format (just path) and new format (full config)
        if 'default_pcap_path' in data or 'upload_dir' in data or 'suricata_rules_dir' in data or 'suricata_config' in data or 'suricata_log_dir' in data or 'pcap_dir' in data:
            success = config_manager.update_configs(data)
        else:
            # Backward compatibility - just update the path
            path = data.get('default_pcap_path', '/home/kali/pcap_check')
            success = config_manager.set_default_pcap_path(path)
        if success:
            return jsonify({
                "success": True,
                "message": "PCAP配置已保存"
            })
        else:
            return jsonify({
                "success": False,
                "message": "保存配置失败"
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pcap/upload', methods=['POST'])
def upload_pcap():
    """Upload PCAP file"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有上传文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "文件名为空"}), 400
        
        if not file.filename.lower().endswith('.pcap'):
            return jsonify({"error": "只支持PCAP格式文件"}), 400
        
        result = pcap_manager_db.upload_pcap(file, file.filename)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pcap/list', methods=['GET'])
def list_pcaps():
    """List all uploaded PCAP files"""
    try:
        pcaps = pcap_manager_db.list_uploaded_pcaps()
        return jsonify({
            "success": True,
            "pcaps": pcaps
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pcap/delete/<filename>', methods=['DELETE'])
def delete_pcap(filename):
    """Delete uploaded PCAP file"""
    try:
        result = pcap_manager_db.delete_pcap(filename)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pcap/validate', methods=['POST'])
def validate_with_uploaded_pcap():
    """Validate rule with uploaded PCAP file"""
    try:
        data = request.json
        rule_content = data.get('rule_content', '')
        rule_id = data.get('rule_id')
        pcap_filename = data.get('pcap_filename', '')
        
        if not rule_content:
            return jsonify({"error": "缺少规则内容"}), 400
        
        if not pcap_filename:
            return jsonify({"error": "请选择PCAP文件"}), 400
        
        # Get the full path of the uploaded PCAP
        pcap_path = pcap_manager_db.get_pcap_path(pcap_filename)
        if not pcap_path:
            return jsonify({"error": "PCAP文件不存在"}), 404
        
        # Get the directory of the PCAP file
        pcap_dir = os.path.dirname(pcap_path)
        
        # Ensure directory exists
        if not os.path.exists(pcap_dir):
            return jsonify({"error": "PCAP目录不存在"}), 404
        
        # 使用环境变量配置创建临时SuricataValidator实例
        from suricata_validator import SuricataValidator
        # 优先从环境变量获取配置，这是主要的配置源
        rules_dir = os.getenv('SURICATA_RULES_DIR', '/var/lib/suricata/rules')
        suricata_config = os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml')
        log_dir = os.getenv('SURICATA_LOG_DIR', '/var/log/suricata')
        
        current_suricata_validator = SuricataValidator.create_validator(
            rules_dir=rules_dir,
            suricata_config=suricata_config,
            log_dir=log_dir
        )
        
        # Validate the rule
        validation_result = current_suricata_validator.validate_rule(rule_content, pcap_dir)
        
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


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        
        user = user_model.verify_password(username, password)
        if user:
            # 返回用户信息（移除密码哈希）
            safe_user = user_model.to_safe_dict(user)
            return jsonify({
                "success": True,
                "message": "登录成功",
                "user": safe_user,
                "access_token": _create_token(user['id'])
            })
        else:
            return jsonify({"error": "用户名或密码错误"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        
        try:
            user_id = user_model.create_user(username=username, password=password, email=email)
            user = user_model.get_by_id(user_id)
            safe_user = user_model.to_safe_dict(user)
            return jsonify({
                "success": True,
                "message": "注册成功",
                "user": safe_user
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/suricata/check', methods=['GET'])
def check_suricata():
    """Check if Suricata engine is available"""
    try:
        import platform
        import subprocess
        import shutil
        
        result = {
            "os": platform.system(),
            "suricata_available": False,
            "version": None,
            "config_found": False,
            "config_path": None,
            "rules_dir_exists": False,
            "log_dir_exists": False,
            "message": "",
            "recommendation": ""
        }
        
        # Check if suricata is available
        suricata_cmd = shutil.which('suricata')
        
        if suricata_cmd:
            result["suricata_available"] = True
            result["message"] += f"找到Suricata命令: {suricata_cmd}"
            
            # Try to get version
            try:
                version_result = subprocess.run([suricata_cmd, '--version'], 
                                              capture_output=True, text=True, timeout=10)
                if version_result.returncode == 0:
                    version_line = version_result.stdout.strip().split('\n')[0]
                    result["version"] = version_line
                    result["message"] += f", 版本: {version_line}"
            except Exception as e:
                result["message"] += f", 但无法获取版本信息: {str(e)}"
        else:
            result["message"] = "未找到Suricata命令"
            result["recommendation"] = "请安装Suricata (Ubuntu/Debian: sudo apt-get install suricata)"
            
            # Check if we have SSH config for remote validation
            ssh_host = config_manager.get_config('ssh_host')
            ssh_user = config_manager.get_config('ssh_user')
            if ssh_host and ssh_user:
                result["recommendation"] += "\n已配置SSH参数，可通过SSH连接到远程系统进行验证。"
            else:
                result["recommendation"] += "\n建议配置SSH连接到Linux/Kali系统以进行远程验证。请在系统配置页面设置SSH参数。"
        
        # Check config file
        possible_configs = [
            "/etc/suricata/suricata.yaml",
            "/usr/local/etc/suricata/suricata.yaml",
            "/etc/default/suricata",
            # Also check configured path from environment variable
            os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml')
        ]
        
        # Remove duplicates and check each config file
        unique_configs = list(dict.fromkeys(possible_configs))  # Remove duplicates while preserving order
        found_configs = []
        missing_configs = []
        
        for config_path in unique_configs:
            if os.path.exists(config_path):
                found_configs.append(config_path)
            else:
                missing_configs.append(config_path)
        
        if found_configs:
            result["config_found"] = True
            result["config_path"] = found_configs[0]  # Use the first found config
            result["found_configs"] = found_configs
            result["message"] += f", 找到配置文件: {found_configs[0]}"
        else:
            result["config_found"] = False
            result["missing_configs"] = missing_configs
            result["message"] += f", 未找到配置文件。已检查路径: {', '.join(missing_configs)}"
            
        # Check if configured directories exist
        rules_dir = os.getenv('SURICATA_RULES_DIR', '/var/lib/suricata/rules')
        log_dir = os.getenv('SURICATA_LOG_DIR', '/var/log/suricata')
        
        result["rules_dir_exists"] = os.path.exists(rules_dir)
        result["log_dir_exists"] = os.path.exists(log_dir)
        
        # Update the message to include actual configured paths
        if result["rules_dir_exists"]:
            result["message"] += f", 规则目录存在: {rules_dir}"
        else:
            result["message"] += f", 规则目录不存在: {rules_dir}"
        
        if result["log_dir_exists"]:
            result["message"] += f", 日志目录存在: {log_dir}"
        else:
            result["message"] += f", 日志目录不存在: {log_dir}"
        
        # Final status
        if result["suricata_available"] and result["config_found"]:
            result["status"] = "ready"
            result["message"] = "Suricata引擎已准备好，可以进行规则验证"
        elif result["suricata_available"]:
            result["status"] = "partial"
            result["message"] = "Suricata已安装但配置文件路径可能需要调整"
        else:
            result["status"] = "unavailable"
            result["message"] = "Suricata未安装或不可用，验证功能受限"
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "未授权"}), 401

        token = auth_header.split(' ')[1]
        user_id = _verify_token(token)
        if user_id is None:
            return jsonify({"error": "无效或已过期的令牌"}), 401

        user = user_model.get_by_id(user_id)
        if user:
            safe_user = user_model.to_safe_dict(user)
            return jsonify({
                "success": True,
                "user": safe_user
            })
        else:
            return jsonify({"error": "用户不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 通配符路由，用于处理前端路由
@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users"""
    try:
        # 检查认证
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "未授权"}), 401

        token = auth_header.split(' ')[1]
        user_id = _verify_token(token)
        if user_id is None:
            return jsonify({"error": "无效或已过期的令牌"}), 401
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        users_info = user_model.get_all_users(page=page, per_page=per_page)
        return jsonify({
            "success": True,
            "users": users_info['users'],
            "total": users_info['total'],
            "page": users_info['page'],
            "per_page": users_info['per_page']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agent/run', methods=['POST'])
def agent_run():
    """
    Agent API - 一次调用完成规则生成+验证全流程
    支持 API Key 认证（X-API-Key header 或 api_key query param）
    也支持 Bearer token 认证

    请求体:
      vuln_name: str (必填)
      vuln_description: str (必填)
      vuln_type: str (可选)
      poc: str (可选)
      pcap_filename: str (可选，已上传的PCAP文件名，不填则跳过验证)
      auto_optimize: bool (可选，默认false，验证失败时是否自动优化)
      max_optimize_rounds: int (可选，默认2，最大优化轮次)

    返回:
      task_id, status, generated_rule, validation_result, optimize_history
    """
    try:
        # 认证：支持 API Key 或 Bearer token
        api_key_header = request.headers.get('X-API-Key') or request.args.get('api_key')
        auth_header = request.headers.get('Authorization', '')

        authenticated = False
        if api_key_header:
            # API Key 认证：与 JWT_SECRET 比对（或单独配置 AGENT_API_KEY）
            expected_key = os.getenv('AGENT_API_KEY') or JWT_SECRET
            if hmac.compare_digest(api_key_header, expected_key):
                authenticated = True
        elif auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if _verify_token(token) is not None:
                authenticated = True

        if not authenticated:
            return jsonify({"error": "未授权，请提供有效的 X-API-Key 或 Bearer token"}), 401

        data = request.json or {}
        vuln_name = data.get('vuln_name', '').strip()
        vuln_description = data.get('vuln_description', '').strip()
        vuln_type = data.get('vuln_type', '')
        poc = data.get('poc', '')
        pcap_filename = data.get('pcap_filename', '')
        auto_optimize = data.get('auto_optimize', False)
        max_optimize_rounds = min(int(data.get('max_optimize_rounds', 2)), 5)

        if not vuln_name or not vuln_description:
            return jsonify({"error": "缺少必要参数: vuln_name 和 vuln_description"}), 400

        result = {
            "status": "started",
            "vuln_name": vuln_name,
            "vuln_type": vuln_type,
            "rule_id": None,
            "generated_rule": None,
            "validation_result": None,
            "optimize_history": [],
            "final_rule": None,
            "steps": []
        }

        # Step 1: 生成规则
        result["steps"].append({"step": "generate", "status": "running"})
        prompt = build_rule_generation_prompt(vuln_name, vuln_description, vuln_type, poc)
        ai_response = llm_client.generate_text(prompt, temperature=0.1, max_tokens=4096)

        if 'error' in ai_response:
            result["status"] = "failed"
            result["steps"][-1]["status"] = "failed"
            result["steps"][-1]["error"] = ai_response['error']
            return jsonify(result), 502

        if not ('choices' in ai_response and len(ai_response['choices']) > 0):
            result["status"] = "failed"
            result["steps"][-1]["status"] = "failed"
            result["steps"][-1]["error"] = "AI未返回有效内容"
            return jsonify(result), 500

        generated_rule = ai_response['choices'][0]['message']['content'].strip()
        rule_id = db.insert_rule(
            vuln_name=vuln_name,
            original_rule=generated_rule,
            current_rule=generated_rule,
            vuln_type=vuln_type,
            description=vuln_description
        )
        result["generated_rule"] = generated_rule
        result["final_rule"] = generated_rule
        result["rule_id"] = rule_id
        result["steps"][-1]["status"] = "done"
        result["steps"][-1]["rule"] = generated_rule

        # Step 2: 验证+修复循环（如果提供了 pcap_filename）
        MAX_FIX_ROUNDS = 3
        if pcap_filename:
            pcap_path = pcap_manager_db.get_pcap_path(pcap_filename)
            if not pcap_path:
                result["steps"].append({"step": "validate", "status": "skipped", "reason": f"PCAP文件不存在: {pcap_filename}"})
                result["final_status"] = "draft"
            else:
                pcap_dir = os.path.dirname(pcap_path)
                rules_dir = os.getenv('SURICATA_RULES_DIR', '/var/lib/suricata/rules')
                suricata_config = os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml')
                log_dir = os.getenv('SURICATA_LOG_DIR', '/var/log/suricata')

                current_rule = generated_rule
                validation_result = None
                fix_round = 0
                final_status = 'draft'

                while True:
                    # 执行验证
                    step_name = 'validate' if fix_round == 0 else f'validate_after_fix_{fix_round}'
                    result["steps"].append({"step": step_name, "status": "running"})

                    validator = SuricataValidator.create_validator(rules_dir, suricata_config, log_dir)
                    vr = validator.validate_rule(current_rule, pcap_dir)

                    db.insert_validation_result(
                        rule_id=rule_id,
                        pcap_path=pcap_path,
                        matched=vr['matched'],
                        alert_count=vr['alert_count'],
                        details=json.dumps(vr['details']),
                        sid_stats=json.dumps(vr['sid_stats'])
                    )
                    validation_result = vr
                    result["steps"][-1].update({
                        "status": "done",
                        "matched": vr['matched'],
                        "alert_count": vr['alert_count']
                    })

                    if vr['matched']:
                        # 验证通过，写入数据库并标记合格
                        final_status = 'validated'
                        db.update_rule(rule_id, current_rule, status='validated')
                        break

                    if fix_round >= MAX_FIX_ROUNDS:
                        # 超过最大修复次数，标记不合格
                        final_status = 'failed_validation'
                        db.update_rule(rule_id, current_rule, status='failed_validation')
                        break

                    # 尝试修复
                    fix_round += 1
                    result["steps"].append({"step": f"fix_round_{fix_round}", "status": "running"})

                    opt_prompt = build_rule_optimization_prompt(
                        current_rule,
                        feedback=f"第{fix_round}次修复：验证未匹配，请优化规则以提高检测率",
                        validation_result=json.dumps(vr, ensure_ascii=False)
                    )
                    opt_response = llm_client.generate_text(opt_prompt, temperature=0.3, max_tokens=4096)

                    if 'error' in opt_response or 'choices' not in opt_response:
                        result["steps"][-1]["status"] = "failed"
                        result["steps"][-1]["error"] = opt_response.get('error', 'AI修复失败')
                        final_status = 'failed_validation'
                        db.update_rule(rule_id, current_rule, status='failed_validation')
                        break

                    optimized_rule = opt_response['choices'][0]['message']['content'].strip()
                    db.update_rule(rule_id, optimized_rule)
                    db.insert_optimization_history(
                        rule_id=rule_id,
                        original_rule=current_rule,
                        optimized_rule=optimized_rule,
                        feedback=f"agent第{fix_round}次自动修复",
                        ai_suggestion=optimized_rule
                    )
                    result["optimize_history"].append({
                        "round": fix_round,
                        "original_rule": current_rule,
                        "optimized_rule": optimized_rule
                    })
                    result["steps"][-1].update({
                        "status": "done",
                        "optimized_rule": optimized_rule
                    })
                    current_rule = optimized_rule
                    result["final_rule"] = optimized_rule

                result["validation_result"] = validation_result
                result["final_status"] = final_status
                result["fix_rounds"] = fix_round
        else:
            result["steps"].append({"step": "validate", "status": "skipped", "reason": "未提供pcap_filename"})
            result["final_status"] = "draft"

        result["status"] = "completed"
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    """返回 Agent API 的基本信息和使用说明"""
    return jsonify({
        "name": "Suricata Rule Agent API",
        "version": "1.0",
        "description": "一次调用完成Suricata规则生成和自动化验证",
        "auth_methods": [
            "X-API-Key header: 使用 AGENT_API_KEY 环境变量配置的密钥",
            "Authorization: Bearer <token>: 使用登录接口获取的token"
        ],
        "endpoints": {
            "POST /api/agent/run": {
                "description": "生成规则并可选验证",
                "required": ["vuln_name", "vuln_description"],
                "optional": ["vuln_type", "poc", "pcap_filename", "auto_optimize", "max_optimize_rounds"]
            }
        },
        "example_request": {
            "vuln_name": "用友NC SQL注入漏洞",
            "vuln_description": "用友NC系统某接口存在SQL注入漏洞，攻击者可通过id参数注入恶意SQL语句",
            "vuln_type": "SQL注入",
            "poc": "GET /uapws/service/xxx?id=1' OR '1'='1",
            "pcap_filename": "attack_traffic.pcap",
            "auto_optimize": True,
            "max_optimize_rounds": 2
        }
    })


def build_rule_generation_prompt(vuln_name, vuln_description, vuln_type, poc):
    """Build AI prompt for rule generation"""
    prompt = f"""你是一个Suricata规则编写专家。请根据以下漏洞信息生成一条Suricata规则。

漏洞名称: {vuln_name}
漏洞类型: {vuln_type}
漏洞描述: {vuln_description}
"""
    
    if poc:
        prompt += f"\nPOC示例:\n{poc}\n"
    
    prompt += '''
请严格遵循以下规范:

1. 基本规则格式:
   - 必须包含: msg, flow, sid, rev
   - 不要包含: reference, classtype, affected_version, detection_accuracy, affected_product, metadata
   - msg字段只包含漏洞名称，不要添加任何前缀
   - sid值使用9000000-9999999范围内的随机数
   - rev固定为1

2. HTTP类特征选取:
   - 省略http.method，除非明确只能使用某一固定方法
   - URL路径尽量少取1-2级目录，避免固定安装路径
   - 去除路径最后的问号?，在问号前增加斜杠
   - 请求参数必须包含漏洞利用点，冗余参数可省略
   - 各参数拆分成多个content

3. 正则表达式要求:
   - 必须使用pcre
   - 必须限制作用域(U/I/H/P等)
   - 严格按照下面的模板使用，只修改参数名，匹配注入的正则不要修改
   
4.  **字符转义保护**：
    - **禁止**将正则中的十六进制转义序列（如 `\\x26`, `\\x5f`）转换为它们所代表的ASCII字符（`&`, `_`）。
    - **禁止**将类似 `(\\x5f|%5f)` 的结构简化为 `(_|%5f)` 或任何其他形式。
    - 必须保持模板中PCRE字符串的**原始文本**，包括所有反斜杠`\\`和字母数字组合。模型的任务是**填充变量，而非解析代码**。
5.  **使用方式**：请严格遵循第四部分提供的模板。**只允许**替换模板中明确指出的"参数名"或"漏洞标题"等中文描述部分。PCRE表达式的主体结构（如 `[^\\r\\n\\x26]{0,10}(select|union|...)` 和 `load(\\x5f|%5f)file`）**严禁修改**.


6. 不同漏洞类型的模板（严格遵循）:

【SQL注入】强制要求：不要修改模版中pcre部分[^\\r\\n\\x26]、load(\\x5f|%5f)
alert http any any -> any any (msg:"漏洞标题"; flow:established,to_server; http.uri.raw; content:"请求uri的内容"; nocase; content:"可以执行sql注入命令的参数="; nocase; pcre:"/可以执行sql注入命令的参数=[^\\r\\n\\x26]{0,10}(select|union|sleep|load(\\x5f|%5f)file|update|from|concat|where|outfile|count|waitfor|create|mysql|updatexml|insert|hextoraw|(\\x2d|%2d){2}|\\x27|%27|\\x23|%23)/Ii"; sid:XXXXXXX; rev:1;)
或者
alert http any any -> any any (msg:"漏洞标题"; flow:established,to_server; http.uri; content:"请求uri的内容";http.request_body;nocase; content:"可以执行sql注入命令的参数="; nocase; pcre:"/可以执行sql注入命令的参数==[^\\r\\n\\x26]{0,10}(select|union|sleep|load(\\x5f|\\x255f)file|update|from|concat|where|outfile|count|waitfor|create|mysql|updatexml|insert|hextoraw|(\\x2d|%2d){2}|\\x27|%27|\\x23|%23)/Pi"; sid:XXXXXXX; rev:1;)

【命令注入】
alert http any any -> any any (msg:"漏洞标题"; flow:established,to_server; http.uri; content:"请求uri的内容"; nocase; http.request_body; content:"可以执行命令的参数key="; nocase; pcre:"/可以执行命令的参数=[^\\r\\n\\x26]{0,10}(\\x60|\\x2560|\\x27|\\x2527|\\x3b|\\x253b|\\x7c|\\x257c)/Pi"; sid:XXXXXXX; rev:1;)

【文件读取/目录遍历/路径遍历】
alert http any any -> any any (msg:"漏洞标题"; flow:to_server,established; http.uri.raw; content:"请求uri的内容"; nocase; content:"存在文件读取或目录遍历或路径遍历的参数="; nocase; pcre:"/存在文件读取或目录遍历或路径遍历的参数=[^\\r\\n\\x26]{0,10}((\\x2e|\\x252e){1,2}|[A-Z](\\x3a|%3a))(\\x2f|%2f|\\x5c|\\x255c)/Ii"; sid:XXXXXXX; rev:1;)

【服务端请求伪造(SSRF)】
alert http any any -> any any (msg:"漏洞标题"; flow:established,to_server; http.method; content:"GET"; http.uri; content:"请求uri的内容"; nocase; content:"存在服务端请求伪造(SSRF)的参数="; nocase; pcre:"/存在服务端请求伪造(SSRF)的参数=(https?|files?|.?ftp|dict)(\\x3a|%3a)(\\x2f|%2f)/Ui"; sid:XXXXXXX; rev:1;)

【文件上传攻击】
alert http any any -> any any (msg:"漏洞标题"; flow:established,to_server; http.uri; content:"请求uri的内容"; nocase; http.request_body; content:"name=|22|上传XX功能柜使用的特地字段名|22|"; nocase; content:"filename="; nocase; content:"编程语言起始标签"; distance:0; sid:XXXXXXX; rev:1;)

【未授权访问/权限绕过】
alert http any any -> any any (msg:"漏洞标题"; flow:established,to_server; http.uri; content:"请求uri的内容"; nocase; content:"参考这个op=GetUsersInfo套用吧"; nocase; http.header.raw; content:!"|0a|参考这个Authorization套用吧"; nocase; content:!"|0a|参考这个Cookie套用吧"; nocase; sid:XXXXXXX; rev:1;)

7. 重要注意事项:
   - 强制使用模版中pcre部分[^\\r\\n\\x26]、load(\\x5f|%5f)
   - pcre正则表达式中的匹配部分[^\\r\\n\\x26]{0,10}(select|union|sleep|load(\\x5f|\\x255f)file|update|from|concat|where|outfile|count|waitfor|create|mysql|updatexml|insert|hextoraw|(-|%2d){2}|'|%27|#|%23)/Pi"; 等）不要修改，只替换参数名
   - 严格按照模板格式，不要添加reference, classtype, affected_version等字段
   - sid必须是7位数字，范围在9000000-9999999
   - 根据漏洞类型选择对应的模板，严格遵循模板结构
   
   
请直接输出Suricata规则，不要包含其他解释文字。
'''
    
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
1. 确保规则格式符合规范
2. 提高检测准确率，减少误报
3. 优化正则表达式，避免绕过，但不要修改pcre中的匹配模式（select|union等）
4. 保持规则的可读性和可维护性
5. 只保留: msg, flow, http.相关字段, content, pcre, sid, rev
6. 移除: reference, classtype, affected_version, detection_accuracy, affected_product, metadata
7. msg字段只保留漏洞名称，移除任何前缀

请直接输出优化后的Suricata规则，不要包含其他解释文字。
"""
    
    return prompt


if __name__ == '__main__':
    # Initialize database and ensure directory exists
    db_dir = os.path.dirname(db.db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    db.init_db()
    
    # Check if debug mode is enabled via environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)