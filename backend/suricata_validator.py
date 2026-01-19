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
from datetime import datetime
from typing import Dict, List


class SuricataValidator:
    def __init__(self, 
                 rules_dir="/var/lib/suricata/rules",
                 suricata_config="/etc/suricata/suricata.yaml",
                 log_dir="/var/log/suricata"):
        # Normalize path separators for cross-platform compatibility
        self.rules_dir = rules_dir.replace('\\', '/')
        self.suricata_config = suricata_config.replace('\\', '/')
        self.log_dir = log_dir.replace('\\', '/')
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
            rule_file = os.path.join(self.rules_dir, "vul.rules").replace('\\', '/')
            
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
            
            # Backup existing rules if they exist
            if os.path.exists(rule_file):
                backup_file = f"{rule_file}{self.backup_suffix}".replace('\\', '/')
                shutil.copy2(rule_file, backup_file)  # Cross-platform file copy
            
            # Write new rule
            with open(rule_file, 'w') as f:
                f.write(rule_content)
            
            # Clear previous logs and normalize path separators
            fast_log = os.path.join(self.log_dir, "fast.log").replace('\\', '/')
            eve_log = os.path.join(self.log_dir, "eve.json").replace('\\', '/')
            
            # Check existence with original path format, then operate with normalized path
            fast_log_orig = fast_log.replace('/', '\\')
            eve_log_orig = eve_log.replace('/', '\\')
            if os.path.exists(fast_log_orig):
                open(fast_log, 'w').close()
            if os.path.exists(eve_log_orig):
                open(eve_log, 'w').close()
            
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
            
            # Check if config files exist - normalize path separators
            normalized_config = self.suricata_config.replace('\\', '/')
            if not os.path.exists(self.suricata_config):
                result["error"] = f"Suricata配置文件不存在: {self.suricata_config}"
                result["engine_status"] = "config_missing"
                result["execution_details"] = {
                    "config_file": normalized_config,
                    "suricata_available": True,
                    "config_exists": False
                }
                return result
            
            # Check if config file exists - normalize path separators
            # Look for the actual config file among possible locations
            possible_configs = []
            
            # Add the configured path first
            possible_configs.append(self.suricata_config)
            
            # Add common Kali Linux paths if using default
            if self.suricata_config == '/etc/suricata/suricata.yaml':
                possible_configs.extend([
                    '/etc/suricata/suricata.yaml',
                    '/usr/local/etc/suricata/suricata.yaml',
                    '/etc/default/suricata',
                    '/usr/etc/suricata/suricata.yaml'
                ])
            
            # Find the first existing config file
            actual_config = None
            for config_path in possible_configs:
                if os.path.exists(config_path):
                    # Get absolute path to ensure consistency
                    actual_config = os.path.abspath(config_path)
                    break
            
            if actual_config is None:
                result["error"] = f"Suricata配置文件不存在: {self.suricata_config} (及常见位置)"
                result["engine_status"] = "config_missing"
                result["execution_details"] = {
                    "config_file": self.suricata_config,
                    "suricata_available": True,
                    "config_exists": False
                }
                return result
            
            # Only check log directory if we're not using the default config
            # since default config doesn't need explicit -l flag
            if actual_config != '/etc/suricata/suricata.yaml' and actual_config != '/usr/local/etc/suricata/suricata.yaml' and actual_config != '/usr/etc/suricata/suricata.yaml':
                # Normalize log directory path
                normalized_log_dir = self.log_dir.replace('\\', '/')
                if not os.path.exists(self.log_dir):
                    result["error"] = f"Suricata日志目录不存在: {self.log_dir}"
                    result["engine_status"] = "log_dir_missing"
                    result["execution_details"] = {
                        "log_dir": normalized_log_dir,
                        "suricata_available": True,
                        "config_exists": True,
                        "log_dir_exists": False
                    }
                    return result
            
            # Run Suricata validation
            result["engine_status"] = "executing"
            result["execution_details"] = {
                "suricata_available": True,
                "config_file": actual_config,
                "using_default_config": actual_config in ['/etc/suricata/suricata.yaml', '/usr/local/etc/suricata/suricata.yaml', '/usr/etc/suricata/suricata.yaml'],
                "log_dir": self.log_dir,
                "pcap_path": pcap_path,
                "rule_file": rule_file
            }
            
            pcap_files = self._get_pcap_files(pcap_path)
            
            if not pcap_files:
                result["error"] = f"在指定路径中未找到PCAP文件: {pcap_path}"
                result["engine_status"] = "no_pcap_files"
                return result
            
            for pcap in pcap_files:
                result["execution_details"]["current_pcap"] = pcap
                # Convert to absolute path and normalize path separators for cross-platform compatibility
                abs_pcap_path = os.path.abspath(pcap).replace('\\', '/')
                
                if actual_config in ['/etc/suricata/suricata.yaml', '/usr/local/etc/suricata/suricata.yaml', '/usr/etc/suricata/suricata.yaml']:
                    # For standard configs, use default config (don't specify -c flag) and no explicit -l flag
                    cmd = suricata_cmd + [
                        '-k', 'none',
                        '-r', abs_pcap_path
                    ]
                else:
                    # For custom configs, use -c flag to specify config and -l flag for log directory
                    cmd = suricata_cmd + [
                        '-c', f'"{actual_config}"',
                        '-k', 'none',
                        '-r', abs_pcap_path,
                        '-l', f'"{self.log_dir}"'
                    ]
                
                # Store the command for debugging
                result["execution_details"]["executed_command"] = ' '.join([f'"{arg}"' if ' ' in arg and arg[0] != chr(34) and arg[-1] != chr(34) else arg for arg in cmd])
                
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if proc.returncode != 0:
                    result["error"] = f"Suricata执行失败: {proc.stderr}"
                    result["engine_status"] = "execution_failed"
                    result["execution_details"]["return_code"] = proc.returncode
                    result["execution_details"]["stderr"] = proc.stderr
                    result["execution_details"]["stdout"] = proc.stdout
                    return result
            
            # Parse results from fast.log
            if os.path.exists(fast_log) and os.path.getsize(fast_log) > 0:
                result["matched"] = True
                result["details"], result["alert_count"] = self._parse_fast_log(fast_log)
                result["sid_stats"] = self._parse_sid_stats(fast_log)
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
    def create_validator(rules_dir, suricata_config, log_dir, config_manager=None):
        """Create validator instance for Kali Linux (no Windows support)"""
        # Always return the standard validator (Kali Linux)
        return SuricataValidator(rules_dir, suricata_config, log_dir)


# Removed Windows validator class as per requirement to focus on Kali Linux only
