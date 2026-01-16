#!/usr/bin/env python
# encoding: utf-8
# PCAP File Manager Module

import os
import shutil
from typing import List, Dict, Optional
import json


class PCAPManager:
    def __init__(self, upload_folder: str = "uploads"):
        self.upload_folder = upload_folder
        self.config_file = "pcap_config.json"
        self.ensure_upload_directory()
        self.load_or_create_config()

    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, exist_ok=True)

    def load_or_create_config(self):
        """Load PCAP configuration or create default if doesn't exist"""
        default_config = {
            "default_pcap_path": "/home/kali/pcap_check",
            "upload_dir": "uploads",
            "uploaded_pcaps": [],
            "config_file_path": "pcap_config.json",
            "suricata_rules_dir": "D:\\Program Files\\Suricata\\rules",
            "suricata_config": "D:\\Program Files\\Suricata\\suricata.yaml",
            "suricata_log_dir": "D:\\Program Files\\Suricata\\log",
            "pcap_dir": "uploads"
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            # 确保新配置项存在
            updated = False
            for key, value in default_config.items():
                if key not in self.config:
                    self.config[key] = value
                    updated = True
            # 如果添加了新配置项，则保存更新后的配置
            if updated:
                self.save_config()
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save PCAP configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_default_pcap_path(self) -> str:
        """Get the default PCAP path"""
        return self.config.get("default_pcap_path", "/home/kali/pcap_check")

    def set_default_pcap_path(self, path: str) -> bool:
        """Set the default PCAP path"""
        self.config["default_pcap_path"] = path
        self.save_config()
        return True
    
    def update_config(self, config_data: dict) -> bool:
        """Update configuration with provided data"""
        for key, value in config_data.items():
            # 更新所有配置项
            self.config[key] = value
            
        # Update upload folder if changed
        if 'upload_dir' in config_data:
            old_upload_folder = self.upload_folder
            self.upload_folder = config_data['upload_dir']
            # Ensure the new directory exists
            self.ensure_upload_directory()
            
        self.save_config()
        return True

    def upload_pcap(self, file_data, filename: str) -> Dict:
        """Upload a PCAP file"""
        try:
            # Sanitize filename to prevent path traversal
            safe_filename = os.path.basename(filename)
            filepath = os.path.join(self.upload_folder, safe_filename)

            # Save file
            with open(filepath, 'wb') as f:
                f.write(file_data.read())

            # Add to uploaded PCAPs list
            pcap_info = {
                "filename": safe_filename,
                "filepath": filepath,
                "size": os.path.getsize(filepath),
                "upload_time": os.path.getctime(filepath)
            }

            self.config["uploaded_pcaps"].append(pcap_info)
            self.save_config()

            return {
                "success": True,
                "message": "PCAP文件上传成功",
                "pcap_info": pcap_info
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"上传失败: {str(e)}"
            }

    def list_uploaded_pcaps(self) -> List[Dict]:
        """List all uploaded PCAP files"""
        return self.config.get("uploaded_pcaps", [])

    def delete_pcap(self, filename: str) -> Dict:
        """Delete an uploaded PCAP file"""
        try:
            # Find the PCAP file in the list
            pcaps = self.config.get("uploaded_pcaps", [])
            pcap_to_delete = None
            index_to_remove = -1

            for i, pcap in enumerate(pcaps):
                if pcap["filename"] == filename:
                    pcap_to_delete = pcap
                    index_to_remove = i
                    break

            if pcap_to_delete is None:
                return {
                    "success": False,
                    "message": "PCAP文件不存在"
                }

            # Delete the physical file
            if os.path.exists(pcap_to_delete["filepath"]):
                os.remove(pcap_to_delete["filepath"])

            # Remove from the list
            del pcaps[index_to_remove]
            self.config["uploaded_pcaps"] = pcaps
            self.save_config()

            return {
                "success": True,
                "message": "PCAP文件删除成功"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }

    def get_pcap_path(self, filename: str) -> Optional[str]:
        """Get the full path of an uploaded PCAP file"""
        pcaps = self.config.get("uploaded_pcaps", [])
        for pcap in pcaps:
            if pcap["filename"] == filename:
                return pcap["filepath"]
        return None

    def get_pcap_info(self, filename: str) -> Optional[Dict]:
        """Get information about a specific PCAP file"""
        pcaps = self.config.get("uploaded_pcaps", [])
        for pcap in pcaps:
            if pcap["filename"] == filename:
                return pcap
        return None


# Global instance
pcap_manager = PCAPManager()