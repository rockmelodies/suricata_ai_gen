#!/usr/bin/env python
# encoding: utf-8
# PCAP File Manager Module - Database Version

import os
import shutil
from typing import List, Dict, Optional
import json


class PCAPManagerDB:
    def __init__(self, db, upload_folder: str = "uploads"):
        self.db = db
        self.upload_folder = upload_folder
        self.ensure_upload_directory()

    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, exist_ok=True)

    def get_default_pcap_path(self) -> str:
        """Get the default PCAP path from config manager"""
        from config_manager import config_manager
        return config_manager.get_config("default_pcap_path", "/home/kali/pcap_check")

    def set_default_pcap_path(self, path: str) -> bool:
        """Set the default PCAP path in config manager"""
        from config_manager import config_manager
        return config_manager.set_config("default_pcap_path", path)

    def upload_pcap(self, file_data, filename: str) -> Dict:
        """Upload a PCAP file"""
        try:
            # Sanitize filename to prevent path traversal
            safe_filename = os.path.basename(filename)
            filepath = os.path.join(self.upload_folder, safe_filename)

            # Save file
            with open(filepath, 'wb') as f:
                f.write(file_data.read())

            # Add to uploaded PCAPs list in database
            pcap_info = {
                "filename": safe_filename,
                "filepath": filepath,
                "size": os.path.getsize(filepath),
                "upload_time": os.path.getctime(filepath)
            }

            # Store the pcap info in database
            self.add_uploaded_pcap(pcap_info)

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

    def add_uploaded_pcap(self, pcap_info: Dict):
        """Add uploaded pcap info to database"""
        # We'll store the list of uploaded pcaps as a JSON string in the config table
        # with key 'uploaded_pcaps'
        current_pcaps = self.list_uploaded_pcaps()
        current_pcaps.append(pcap_info)
        
        from config_manager import config_manager
        config_manager.set_config("uploaded_pcaps", current_pcaps)

    def list_uploaded_pcaps(self) -> List[Dict]:
        """List all uploaded PCAP files"""
        from config_manager import config_manager
        pcaps = config_manager.get_config("uploaded_pcaps", [])
        return pcaps

    def delete_pcap(self, filename: str) -> Dict:
        """Delete an uploaded PCAP file"""
        try:
            # Find the PCAP file in the list
            pcaps = self.list_uploaded_pcaps()
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
            
            # Update the database
            from config_manager import config_manager
            config_manager.set_config("uploaded_pcaps", pcaps)

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
        pcaps = self.list_uploaded_pcaps()
        for pcap in pcaps:
            if pcap["filename"] == filename:
                return pcap["filepath"]
        return None

    def get_pcap_info(self, filename: str) -> Optional[Dict]:
        """Get information about a specific PCAP file"""
        pcaps = self.list_uploaded_pcaps()
        for pcap in pcaps:
            if pcap["filename"] == filename:
                return pcap
        return None


# Global instance
pcap_manager_db = None