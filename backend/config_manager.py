#!/usr/bin/env python
# encoding: utf-8
# Configuration Manager Module

import os
import json
from typing import Dict, Optional


class ConfigManager:
    def __init__(self, db):
        self.db = db
        self.load_or_create_defaults()

    def load_or_create_defaults(self):
        """Load configuration or create defaults if they don't exist"""
        # Define default configuration values
        defaults = {
            "default_pcap_path": "/home/kali/pcap_check",
            "upload_dir": "uploads",
            "config_file_path": "pcap_config.json",
            "suricata_rules_dir": ":\\Program Files\\Suricata\\rules",
            "suricata_config": "C:\\Program Files\\Suricata\\suricata.yaml",
            "suricata_log_dir": "C:\\Program Files\\Suricata\\log",
            "pcap_dir": "C:\\pcap_check",
            "ssh_host": "",
            "ssh_user": "",
            "ssh_key": ""
        }
        
        # Load or create each config value
        for key, default_value in defaults.items():
            value = self.db.get_config(key)
            if value is None:
                # Convert string value to appropriate type if needed
                self.db.set_config(key, json.dumps(default_value))

    def get_config(self, key: str, default=None):
        """Get configuration value by key"""
        value_str = self.db.get_config(key)
        if value_str is not None:
            try:
                return json.loads(value_str)
            except (json.JSONDecodeError, TypeError):
                return value_str
        return default

    def set_config(self, key: str, value) -> bool:
        """Set configuration value by key"""
        try:
            # Serialize the value to JSON string
            value_str = json.dumps(value)
            return self.db.set_config(key, value_str)
        except Exception as e:
            print(f"Error serializing config value for {key}: {e}")
            return False

    def get_all_configs(self) -> Dict[str, any]:
        """Get all configuration values"""
        all_configs = self.db.get_all_configs()
        result = {}
        for key, value_str in all_configs.items():
            try:
                result[key] = json.loads(value_str)
            except (json.JSONDecodeError, TypeError):
                result[key] = value_str
        return result

    def update_configs(self, configs: Dict[str, any]) -> bool:
        """Update multiple configuration values"""
        success = True
        for key, value in configs.items():
            if not self.set_config(key, value):
                success = False
        return success

    def get_default_pcap_path(self) -> str:
        """Get the default PCAP path"""
        return self.get_config("default_pcap_path", "/home/kali/pcap_check")

    def set_default_pcap_path(self, path: str) -> bool:
        """Set the default PCAP path"""
        return self.set_config("default_pcap_path", path)



# Global instance will be assigned in app_v2.py with proper database connection
config_manager = None  # Will be set in app_v2.py