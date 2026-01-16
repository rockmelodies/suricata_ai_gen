#!/usr/bin/env python
# Script to update configuration directly

import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from config_manager import ConfigManager

def update_suricata_paths():
    print("=== 更新Suricata配置路径 ===")
    
    # 创建数据库实例
    db = Database('suricata_rules.db')
    db.init_db()
    
    # 创建配置管理器
    config_manager = ConfigManager(db)
    
    print("\n当前配置:")
    all_configs = config_manager.get_all_configs()
    for key, value in all_configs.items():
        print(f"   {key}: {value}")
    
    # 询问用户想要设置的路径
    print("\n请输入新的路径 (直接回车使用当前值):")
    
    current_rules_dir = config_manager.get_config('suricata_rules_dir', 'D:\\Program Files\\Suricata\\rules')
    current_config = config_manager.get_config('suricata_config', 'D:\\Program Files\\Suricata\\suricata.yaml')
    current_log_dir = config_manager.get_config('suricata_log_dir', 'D:\\Program Files\\Suricata\\log')
    current_pcap_dir = config_manager.get_config('pcap_dir', 'uploads')
    
    new_rules_dir = input(f"Suricata规则目录 (当前: {current_rules_dir}): ").strip()
    if not new_rules_dir:
        new_rules_dir = current_rules_dir
    
    new_config = input(f"Suricata配置文件 (当前: {current_config}): ").strip()
    if not new_config:
        new_config = current_config
    
    new_log_dir = input(f"Suricata日志目录 (当前: {current_log_dir}): ").strip()
    if not new_log_dir:
        new_log_dir = current_log_dir
    
    new_pcap_dir = input(f"PCAP目录 (当前: {current_pcap_dir}): ").strip()
    if not new_pcap_dir:
        new_pcap_dir = current_pcap_dir
    
    # 更新配置
    updated_configs = {
        'suricata_rules_dir': new_rules_dir,
        'suricata_config': new_config,
        'suricata_log_dir': new_log_dir,
        'pcap_dir': new_pcap_dir
    }
    
    success = config_manager.update_configs(updated_configs)
    
    if success:
        print("\n✅ 配置更新成功!")
        print("更新后的配置:")
        for key, value in updated_configs.items():
            print(f"   {key}: {value}")
    else:
        print("\n❌ 配置更新失败!")
    
    print("\n=== 更新完成 ===")

if __name__ == "__main__":
    update_suricata_paths()