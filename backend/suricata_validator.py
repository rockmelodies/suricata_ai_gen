#!/usr/bin/env python
# encoding: utf-8
# Suricata Rule Validator - Integrates with Suricata engine

import os
import subprocess
import tempfile
import re
import shutil
import platform
import shlex
import uuid
import pwd
import grp
import sys
import json
from datetime import datetime
from typing import Dict, List


class SuricataValidator:
    def __init__(self, 
                 rules_dir=None,
                 suricata_config=None,
                 log_dir=None):
        # Read configuration from environment variables if available, fallback to defaults
        env_rules_dir = os.getenv('SURICATA_RULES_DIR', rules_dir or '/var/lib/suricata/rules')
        env_suricata_config = os.getenv('SURICATA_CONFIG_PATH', suricata_config or '/etc/suricata/suricata.yaml')
        env_log_dir = os.getenv('SURICATA_LOG_DIR', log_dir or '/var/log/suricata')
        
        # Normalize path separators for cross-platform compatibility
        self.rules_dir = env_rules_dir.replace('\\', '/')
        self.suricata_config = env_suricata_config.replace('\\', '/')
        self.log_dir = env_log_dir.replace('\\', '/')
        self.backup_suffix = f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.is_windows = platform.system().lower() == 'windows'
    
    def _get_suricata_command(self):
        """Get appropriate suricata command based on platform"""
        if self.is_windows:
            # Try different possible locations for suricata on Windows
            suricata_cmd = shutil.which('suricata') or shutil.which('suricata.exe')
            if suricata_cmd:
                return [suricata_cmd]
            else:
                # Suricata not found on Windows
                return None
        else:
            # In Kali Linux, suricata might be in different locations
            suricata_cmd = shutil.which('suricata')
            if suricata_cmd:
                return [suricata_cmd]
            else:
                # Try common locations in Kali Linux
                for cmd_path in ['/usr/bin/suricata', '/usr/local/bin/suricata', '/sbin/suricata']:
                    if os.path.exists(cmd_path):
                        return [cmd_path]
                # If not found anywhere, return default
                return ['suricata']
    
    def validate_rule(self, rule_content: str, pcap_path: str) -> Dict:
        """
        Validate Suricata rule against PCAP file(s)
        
        Args:
            rule_content: The Suricata rule to validate
            pcap_path: Path to PCAP file or directory
        
        Returns:
            Dict with validation results
        """
        result = {
            "success": False,
            "matched": False,
            "alert_count": 0,
            "details": [],
            "sid_stats": {},
            "error": None,
            "engine_status": "not_started",
            "execution_details": {}
        }
        
        try:
            # Create temporary rule file and normalize path separators
            # Use a unique rule filename to avoid conflicts
            unique_rule_filename = f"vul_{uuid.uuid4().hex[:8]}.rules"
            # Ensure all path separators are forward slashes for Linux compatibility
            rule_file = os.path.join(self.rules_dir, unique_rule_filename).replace('\\', '/')
            
            # Check if rule content is valid
            if not rule_content or not rule_content.strip():
                result["error"] = "规则内容为空或无效"
                result["engine_status"] = "invalid_input"
                return result
            
            # Check if pcap path exists - convert relative path to absolute for Windows and normalize path separators
            abs_pcap_path = os.path.abspath(pcap_path).replace('\\', '/')
            # Check if path exists either as given or as absolute path
            path_exists = os.path.exists(pcap_path) or os.path.exists(abs_pcap_path)
            if not path_exists:
                result["error"] = f"PCAP路径不存在: {pcap_path} (resolved as: {abs_pcap_path})"
                result["engine_status"] = "invalid_pcap_path"
                return result
            
            # Write new rule
            try:
                with open(rule_file, 'w') as f:
                    f.write(rule_content)
                print(f"规则文件已创建: {rule_file}")
                print(f"规则内容长度: {len(rule_content)}")
            except Exception as e:
                result["error"] = f"创建规则文件失败: {str(e)}"
                result["engine_status"] = "rule_write_failed"
                return result
            
            # Verify that the rule file exists and has content
            if not os.path.exists(rule_file):
                result["error"] = f"规则文件不存在: {rule_file}"
                result["engine_status"] = "rule_file_missing"
                return result
            
            if os.path.getsize(rule_file) == 0:
                result["error"] = f"规则文件为空: {rule_file}"
                result["engine_status"] = "rule_file_empty"
                return result
            
            # Since we're not using -l flag, Suricata will likely create logs in the current directory
            # Prepare paths for where logs might be created
            current_dir_fast_log = os.path.join(os.getcwd(), "fast.log")
            current_dir_eve_log = os.path.join(os.getcwd(), "eve.json")
            
            # Clear logs in current directory where suricata likely writes them
            try:
                with open(current_dir_fast_log, 'w') as f:
                    pass  # Truncate fast.log
            except IOError:
                pass  # May not be able to write, that's ok
            try:
                with open(current_dir_eve_log, 'w') as f:
                    pass  # Truncate eve.json
            except IOError:
                pass  # May not be able to write, that's ok
            
            # Check if suricata is available
            suricata_cmd = self._get_suricata_command()
            if not suricata_cmd:
                # Suricata not available, return mock result
                result["success"] = True
                result["matched"] = False
                result["alert_count"] = 0
                result["details"] = []
                result["sid_stats"] = {}
                result["error"] = "Suricata未找到。请安装Suricata或配置远程验证。"
                result["engine_status"] = "suricata_not_found"
                result["execution_details"] = {
                    "suricata_available": False,
                    "attempted_command": "suricata",
                    "platform": platform.system()
                }
                return result
            
            # Since we're not using -c flag, we don't need to check config file existence
            # Let suricata use its default configuration
            actual_config = self.suricata_config
            
            # Since we're not using -l flag, skip log directory check
            # Suricata will use its default log location
            pass
            
            # Run Suricata validation
            result["engine_status"] = "executing"
            result["execution_details"] = {
                "suricata_available": True,
                "config_file": actual_config,
                "using_default_config": actual_config in ['/etc/suricata/suricata.yaml', '/usr/local/etc/suricata/suricata.yaml', '/usr/etc/suricata/suricata.yaml'],
                "log_dir": self.log_dir,
                "pcap_path": pcap_path,
                "rule_file": rule_file,
                "command_using_c_flag": False,
                "command_using_s_flag": True,
                "command_using_l_flag": False
            }
            
            # Get PCAP files to process
            pcap_files = self._get_pcap_files(pcap_path)
            
            if not pcap_files:
                result["error"] = f"在指定路径中未找到PCAP文件: {pcap_path}"
                result["engine_status"] = "no_pcap_files"
                return result
            
            # Process each PCAP file
            for pcap in pcap_files:
                result["execution_details"]["current_pcap"] = pcap
                # Convert to absolute path and normalize path separators for cross-platform compatibility
                abs_pcap_path = os.path.abspath(pcap).replace('\\', '/')
                
                # Execute suricata with rule file and pcap
                # For security, we'll call a separate script with elevated privileges if needed
                cmd = []
                
                # Check if we're running as root to determine execution method
                if os.geteuid() == 0:
                    # We're already running with elevated privileges
                    cmd = suricata_cmd + [
                        '-S', rule_file,
                        '-k', 'none',
                        '-r', abs_pcap_path
                    ]
                    
                    print(f"正在测试: {abs_pcap_path}")
                    print(f"执行命令: {' '.join(cmd)}")
                    proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                else:
                    # We need to call our helper script with sudo
                    # This is safer than running the entire web application with sudo
                    helper_script = os.path.join(os.path.dirname(__file__), 'run_suricata_as_root.py')
                    
                    if os.path.exists(helper_script):
                        cmd = ['sudo', sys.executable, helper_script, 
                               '--rules-file', rule_file,
                               '--pcap-file', abs_pcap_path]
                        
                        # Add config file if it exists
                        if os.path.exists(self.suricata_config):
                            cmd.extend(['--config-file', self.suricata_config])
                        
                        print(f"正在测试: {abs_pcap_path}")
                        print(f"执行命令: {' '.join(cmd)}")
                        proc = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        
                        # Parse the JSON response from our helper script
                        try:
                            helper_result = json.loads(proc.stdout)
                            # Simulate the original proc object behavior
                            class MockProc:
                                def __init__(self, result):
                                    self.returncode = result['returncode']
                                    self.stdout = result['stdout']
                                    self.stderr = result['stderr']
                            proc = MockProc(helper_result)
                        except json.JSONDecodeError:
                            # If JSON parsing fails, treat as error
                            proc = subprocess.CompletedProcess([], 1, "", "Failed to parse helper script output")
                    else:
                        # Fallback: try to run directly (may fail due to permissions)
                        cmd = suricata_cmd + [
                            '-S', rule_file,
                            '-k', 'none',
                            '-r', abs_pcap_path
                        ]
                        
                        print(f"正在测试: {abs_pcap_path}")
                        print(f"执行命令: {' '.join(cmd)}")
                        proc = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                
                # Store the command for debugging
                result["execution_details"]["executed_command"] = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in cmd])
                result["execution_details"]["running_with_sudo_helper"] = (os.geteuid() != 0)
                
                if proc.returncode != 0:
                    result["error"] = f"Suricata执行失败: {proc.stderr}"
                    result["engine_status"] = "execution_failed"
                    result["execution_details"]["return_code"] = proc.returncode
                    result["execution_details"]["stderr"] = proc.stderr
                    result["execution_details"]["stdout"] = proc.stdout
                    print(f"Suricata执行失败: {proc.stderr}")
                    return result
            
            # Parse results from fast.log
            # Since we're not using -l flag, check logs in current directory
            current_dir_fast_log = os.path.join(os.getcwd(), "fast.log")
            
            if os.path.exists(current_dir_fast_log) and os.path.getsize(current_dir_fast_log) > 0:
                result["matched"] = True
                result["details"], result["alert_count"] = self._parse_fast_log(current_dir_fast_log)
                result["sid_stats"] = self._parse_sid_stats(current_dir_fast_log)
                result["engine_status"] = "validation_success"
            else:
                result["matched"] = False
                result["alert_count"] = 0
                result["engine_status"] = "no_alerts_detected"
            
            result["success"] = True
            result["execution_details"]["final_status"] = result["engine_status"]
            
        except subprocess.TimeoutExpired:
            result["error"] = "Suricata验证超时"
            result["engine_status"] = "timeout"
        except Exception as e:
            result["error"] = str(e)
            result["engine_status"] = "internal_error"
        finally:
            # Clean up the temporary rule file
            try:
                # Only attempt cleanup if rule_file was defined and os module is available
                if 'rule_file' in locals() and 'os' in globals() and os.path.exists(rule_file):
                    os.remove(rule_file)
            except Exception as cleanup_error:
                # Log the cleanup error but don't fail the validation
                if 'rule_file' in locals():
                    print(f"Warning: Could not clean up temporary rule file {rule_file}: {cleanup_error}")
                else:
                    print(f"Warning: Could not clean up temporary rule file: {cleanup_error}")
        
        return result
    
    def _get_pcap_files(self, pcap_path: str) -> List[str]:
        """Get list of PCAP files from path"""
        pcap_files = []
        
        # Convert to absolute path and normalize path separators for cross-platform compatibility
        abs_pcap_path = os.path.abspath(pcap_path).replace('\\', '/')
        
        if os.path.isdir(abs_pcap_path):
            for file in os.listdir(abs_pcap_path):
                if file.endswith('.pcap') or file.endswith('.pcapng'):
                    # Also normalize the individual file paths
                    file_path = os.path.join(abs_pcap_path, file).replace('\\', '/')
                    pcap_files.append(file_path)
        elif os.path.isfile(abs_pcap_path):
            pcap_files.append(abs_pcap_path.replace('\\', '/'))
        
        return pcap_files
    
    def _parse_fast_log(self, fast_log: str) -> tuple:
        """Parse fast.log to extract alerts"""
        details = []
        count = 0
        
        try:
            with open(fast_log, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        details.append(line)
                        count += 1
        except Exception as e:
            print(f"Error parsing fast.log: {e}")
        
        return details[:10], count  # Return first 10 details and total count
    
    def _parse_sid_stats(self, fast_log: str) -> Dict:
        """Parse SID statistics from fast.log"""
        sid_stats = {}
        
        try:
            with open(fast_log, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Extract SID pattern [gid:sid:rev]
                    match = re.search(r'\[(\d+):(\d+):(\d+)\]', line)
                    if match:
                        sid = f"[{match.group(1)}:{match.group(2)}:{match.group(3)}]"
                        sid_stats[sid] = sid_stats.get(sid, 0) + 1
        except Exception as e:
            print(f"Error parsing SID stats: {e}")
        
        # Sort by count descending
        sorted_stats = dict(sorted(sid_stats.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_stats
    
    def validate_rule_syntax(self, rule_content: str) -> Dict:
        """
        Validate Suricata rule syntax without running against PCAP
        
        Args:
            rule_content: The Suricata rule to validate
        
        Returns:
            Dict with syntax validation results
        """
        result = {
            "valid": False,
            "error": None
        }
        
        try:
            # Create temporary rule file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rules', delete=False) as f:
                f.write(rule_content)
                temp_rule_file = f.name.replace('\\', '/')
            
            # Check if suricata is available
            suricata_cmd = self._get_suricata_command()
            if not suricata_cmd:
                # Suricata not available
                result["error"] = "Suricata not found. Please install Suricata or configure remote validation."
                return result
            
            # Run suricata syntax check
            # Convert to absolute paths for cross-platform compatibility and normalize path separators
            abs_config_path = os.path.abspath(self.suricata_config).replace('\\', '/')
            abs_rule_file = os.path.abspath(temp_rule_file).replace('\\', '/')
            cmd = suricata_cmd + [
                '-T',  # Test mode
                '-c', f'"{abs_config_path}"',
                '-S', abs_rule_file
            ]
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up temp file
            os.unlink(temp_rule_file)
            
            if proc.returncode == 0:
                result["valid"] = True
            else:
                result["error"] = proc.stderr
            
        except subprocess.TimeoutExpired:
            result["error"] = "Syntax validation timeout"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def create_validator(rules_dir=None, suricata_config=None, log_dir=None):
        """Create validator instance for Kali Linux (no Windows support)"""
        # Always return the standard validator (Kali Linux)
        return SuricataValidator(rules_dir, suricata_config, log_dir)


# Removed Windows validator class as per requirement to focus on Kali Linux only
