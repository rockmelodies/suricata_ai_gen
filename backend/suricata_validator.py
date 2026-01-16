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
                "config_file": self.suricata_config,
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
                cmd = suricata_cmd + [
                    '-c', f'"{self.suricata_config}"',
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
        """Create appropriate validator instance based on platform"""
        import platform
        if platform.system().lower() == 'windows':
            # Check if suricata is available on Windows
            import shutil
            suricata_available = shutil.which('suricata') or shutil.which('suricata.exe')
            if suricata_available:
                # Use regular validator if suricata is installed on Windows
                return SuricataValidator(rules_dir, suricata_config, log_dir)
            else:
                # Use Windows validator if no suricata found
                # Try to get SSH config from config manager
                ssh_host = ssh_user = ssh_key = None
                if config_manager:
                    ssh_host = config_manager.get_config('ssh_host')
                    ssh_user = config_manager.get_config('ssh_user')
                    ssh_key = config_manager.get_config('ssh_key')
                
                return SuricataValidatorWindows(
                    rules_dir, suricata_config, log_dir,
                    ssh_host=ssh_host, ssh_user=ssh_user, ssh_key=ssh_key
                )
        else:
            # Use regular validator on Unix-like systems
            return SuricataValidator(rules_dir, suricata_config, log_dir)


class SuricataValidatorWindows(SuricataValidator):
    """
    Windows-compatible validator that simulates Suricata validation
    This is a fallback when Suricata is not available on Windows
    """
    
    def __init__(self, rules_dir="/var/lib/suricata/rules", suricata_config="/etc/suricata/suricata.yaml", log_dir="/var/log/suricata", ssh_host=None, ssh_user=None, ssh_key=None):
        """
        Initialize Windows validator with optional SSH connection to Kali VM
        
        Args:
            rules_dir: Directory for rules
            suricata_config: Path to suricata config
            log_dir: Directory for logs
            ssh_host: SSH host (Kali VM IP)
            ssh_user: SSH username
            ssh_key: SSH private key path
        """
        super().__init__(rules_dir, suricata_config, log_dir)
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
    
    def validate_rule(self, rule_content: str, pcap_path: str) -> Dict:
        """
        Validate rule using SSH to remote Kali system
        """
        # First try to get SSH config from config manager if not provided
        if not self.ssh_host or not self.ssh_user:
            # Try to get from config manager if available
            try:
                from config_manager import config_manager as global_config_manager
                if global_config_manager:
                    self.ssh_host = getattr(global_config_manager, 'ssh_host', None) or self.ssh_host
                    self.ssh_user = getattr(global_config_manager, 'ssh_user', None) or self.ssh_user
                    self.ssh_key = getattr(global_config_manager, 'ssh_key', None) or self.ssh_key
            except ImportError:
                pass  # If config manager not available, continue with existing values
        
        if self.ssh_host and self.ssh_user:
            return self._validate_via_ssh(rule_content, pcap_path)
        else:
            return self._mock_validation(rule_content, pcap_path)

    def _validate_via_ssh(self, rule_content: str, pcap_path: str) -> Dict:
        """Validate via SSH to Kali VM"""
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
            # Check if rule content is valid
            if not rule_content or not rule_content.strip():
                result["error"] = "规则内容为空或无效"
                result["engine_status"] = "invalid_input"
                return result
            
            # Check if SSH config is complete
            if not self.ssh_host or not self.ssh_user:
                result["error"] = "SSH配置不完整，请检查SSH主机和用户名设置"
                result["engine_status"] = "ssh_config_missing"
                result["execution_details"] = {
                    "ssh_host": bool(self.ssh_host),
                    "ssh_user": bool(self.ssh_user),
                    "ssh_key": bool(self.ssh_key)
                }
                return result
            
            # Create temporary script
            # Convert PCAP path to absolute path for cross-platform compatibility and normalize path separators
            abs_pcap_path = os.path.abspath(pcap_path).replace('\\', '/')
            script_content = f'''#!/bin/bash
RULES_DIR="/var/lib/suricata/rules"
SURICATA_CONFIG="{shlex.quote(self.suricata_config)}"
PCAP_PATH="{abs_pcap_path}"
LOG_DIR="{shlex.quote(self.log_dir)}"

# Create rule file
cat > "$RULES_DIR/vul.rules" << 'EOFR'
{rule_content}
EOFR

# Clear logs
> "$LOG_DIR/fast.log"

# Run suricata
if [ -d "$PCAP_PATH" ]; then
    for pcap in "$PCAP_PATH"/*.pcap; do
        [ -f "$pcap" ] && suricata -c "$SURICATA_CONFIG" -k none -r "$pcap" -l "$LOG_DIR"
    done
else
    suricata -c "$SURICATA_CONFIG" -k none -r "$PCAP_PATH" -l "$LOG_DIR"
fi

# Output results
if [ -s "$LOG_DIR/fast.log" ]; then
    echo "MATCHED:true"
    echo "COUNT:$(wc -l < "$LOG_DIR/fast.log")"
    echo "DETAILS:"
    head -10 "$LOG_DIR/fast.log"
else
    echo "MATCHED:false"
fi
'''
            
            result["engine_status"] = "executing"
            result["execution_details"] = {
                "remote_execution": True,
                "ssh_host": self.ssh_host,
                "ssh_user": self.ssh_user,
                "pcap_path": pcap_path
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script_content)
                script_file = f.name
            
            # Execute via SSH
            ssh_cmd = [
                'ssh',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'ConnectTimeout=30'
            ]
            
            if self.ssh_key:
                ssh_cmd.extend(['-i', self.ssh_key])
            
            ssh_cmd.extend([
                f'{self.ssh_user}@{self.ssh_host}',
                'bash -s'
            ])
            
            result["execution_details"]["executed_command"] = ' '.join([f'"{arg}"' if ' ' in arg and arg[0] != chr(34) and arg[-1] != chr(34) else arg for arg in ssh_cmd])
            
            with open(script_file, 'r') as f:
                proc = subprocess.run(
                    ssh_cmd,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            
            os.unlink(script_file)
            
            if proc.returncode != 0:
                result["error"] = f"SSH执行失败: {proc.stderr}"
                result["engine_status"] = "ssh_execution_failed"
                result["execution_details"]["return_code"] = proc.returncode
                result["execution_details"]["stderr"] = proc.stderr
                result["execution_details"]["stdout"] = proc.stdout
                return result
            
            # Parse output
            output = proc.stdout
            if 'MATCHED:true' in output:
                result["matched"] = True
                # Parse count and details
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('COUNT:'):
                        try:
                            result["alert_count"] = int(line.split(':')[1])
                        except:
                            result["alert_count"] = 0
                    elif line.startswith('DETAILS:'):
                        # Collect details that follow
                        for j in range(i+1, len(lines)):
                            detail_line = lines[j].strip()
                            if detail_line and not detail_line.startswith(('MATCHED:', 'COUNT:')):
                                result["details"].append(detail_line)
            
            result["success"] = True
            result["engine_status"] = "validation_success"
            result["execution_details"]["final_status"] = result["engine_status"]
            
        except subprocess.TimeoutExpired:
            result["error"] = "SSH验证超时"
            result["engine_status"] = "timeout"
        except Exception as e:
            result["error"] = str(e)
            result["engine_status"] = "internal_error"
        
        return result
    
    def _mock_validation(self, rule_content: str, pcap_path: str) -> Dict:
        """Mock validation for development/testing"""
        result = {
            "success": True,
            "matched": True,  # Simulated match
            "alert_count": 1,
            "details": [
                f"[Mock] Simulated alert for rule: {rule_content[:50]}..."
            ],
            "sid_stats": {
                "[1:60000001:1]": 1
            },
            "error": None,
            "note": "This is a mock validation result (Suricata not available on Windows)"
        }
        
        return result
