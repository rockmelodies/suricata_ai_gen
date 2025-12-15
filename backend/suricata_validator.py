#!/usr/bin/env python
# encoding: utf-8
# Suricata Rule Validator - Integrates with Suricata engine

import os
import subprocess
import tempfile
import re
from datetime import datetime
from typing import Dict, List


class SuricataValidator:
    def __init__(self, 
                 rules_dir="/var/lib/suricata/rules",
                 suricata_config="/etc/suricata/suricata.yaml",
                 log_dir="/var/log/suricata"):
        self.rules_dir = rules_dir
        self.suricata_config = suricata_config
        self.log_dir = log_dir
        self.backup_suffix = f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
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
            "error": None
        }
        
        try:
            # Create temporary rule file
            rule_file = os.path.join(self.rules_dir, "vul.rules")
            
            # Backup existing rules if they exist
            if os.path.exists(rule_file):
                backup_file = f"{rule_file}{self.backup_suffix}"
                subprocess.run(['cp', rule_file, backup_file], check=False)
            
            # Write new rule
            with open(rule_file, 'w') as f:
                f.write(rule_content)
            
            # Clear previous logs
            fast_log = os.path.join(self.log_dir, "fast.log")
            eve_log = os.path.join(self.log_dir, "eve.json")
            
            if os.path.exists(fast_log):
                open(fast_log, 'w').close()
            if os.path.exists(eve_log):
                open(eve_log, 'w').close()
            
            # Run Suricata validation
            pcap_files = self._get_pcap_files(pcap_path)
            
            for pcap in pcap_files:
                cmd = [
                    'suricata',
                    '-c', self.suricata_config,
                    '-k', 'none',
                    '-r', pcap,
                    '-l', self.log_dir
                ]
                
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if proc.returncode != 0:
                    result["error"] = f"Suricata error: {proc.stderr}"
                    return result
            
            # Parse results from fast.log
            if os.path.exists(fast_log) and os.path.getsize(fast_log) > 0:
                result["matched"] = True
                result["details"], result["alert_count"] = self._parse_fast_log(fast_log)
                result["sid_stats"] = self._parse_sid_stats(fast_log)
            else:
                result["matched"] = False
                result["alert_count"] = 0
            
            result["success"] = True
            
        except subprocess.TimeoutExpired:
            result["error"] = "Suricata validation timeout"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _get_pcap_files(self, pcap_path: str) -> List[str]:
        """Get list of PCAP files from path"""
        pcap_files = []
        
        if os.path.isdir(pcap_path):
            for file in os.listdir(pcap_path):
                if file.endswith('.pcap') or file.endswith('.pcapng'):
                    pcap_files.append(os.path.join(pcap_path, file))
        elif os.path.isfile(pcap_path):
            pcap_files.append(pcap_path)
        
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
                temp_rule_file = f.name
            
            # Run suricata syntax check
            cmd = [
                'suricata',
                '-T',  # Test mode
                '-c', self.suricata_config,
                '-S', temp_rule_file
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


class SuricataValidatorWindows(SuricataValidator):
    """
    Windows-compatible validator that simulates Suricata validation
    This is a fallback when Suricata is not available on Windows
    """
    
    def __init__(self, ssh_host=None, ssh_user=None, ssh_key=None):
        """
        Initialize Windows validator with optional SSH connection to Kali VM
        
        Args:
            ssh_host: SSH host (Kali VM IP)
            ssh_user: SSH username
            ssh_key: SSH private key path
        """
        super().__init__()
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
    
    def validate_rule(self, rule_content: str, pcap_path: str) -> Dict:
        """
        Validate rule using SSH to remote Kali system
        """
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
            "error": None
        }
        
        try:
            # Create temporary script
            script_content = f'''#!/bin/bash
RULES_DIR="/var/lib/suricata/rules"
SURICATA_CONFIG="/etc/suricata/suricata.yaml"
PCAP_PATH="{pcap_path}"
LOG_DIR="/var/log/suricata"

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
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script_content)
                script_file = f.name
            
            # Execute via SSH
            ssh_cmd = [
                'ssh',
                '-i', self.ssh_key,
                f'{self.ssh_user}@{self.ssh_host}',
                'bash -s'
            ]
            
            with open(script_file, 'r') as f:
                proc = subprocess.run(
                    ssh_cmd,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            
            os.unlink(script_file)
            
            # Parse output
            output = proc.stdout
            if 'MATCHED:true' in output:
                result["matched"] = True
                # Parse count and details
                for line in output.split('\n'):
                    if line.startswith('COUNT:'):
                        result["alert_count"] = int(line.split(':')[1])
                    elif line.strip() and not line.startswith(('MATCHED:', 'COUNT:', 'DETAILS:')):
                        result["details"].append(line)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
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
