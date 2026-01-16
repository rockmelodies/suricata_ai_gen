#!/usr/bin/env python
# Test script to verify configuration saving and loading

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from config_manager import ConfigManager

def test_config():
    print("=== 测试配置管理 ===")
    
    # 创建数据库实例
    db = Database('suricata_rules.db')
    db.init_db()
    
    # 创建配置管理器
    config_manager = ConfigManager(db)
    
    print("\n1. 当前所有配置:")
    all_configs = config_manager.get_all_configs()
    for key, value in all_configs.items():
        print(f"   {key}: {value}")
    
    print("\n2. 测试更新配置...")
    # 测试更新一些配置
    test_configs = {
        "suricata_rules_dir": "D:\\Test\\Suricata\\Rules",
        "suricata_config": "D:\\Test\\Suricata\\suricata.yaml",
        "suricata_log_dir": "D:\\Test\\Suricata\\Logs"
    }
    
    success = config_manager.update_configs(test_configs)
    if success:
        print("   配置更新成功!")
    else:
        print("   配置更新失败!")
    
    print("\n3. 更新后的配置:")
    all_configs = config_manager.get_all_configs()
    for key, value in all_configs.items():
        if key in test_configs:
            print(f"   {key}: {value} (已更新)")
        else:
            print(f"   {key}: {value}")
    
    print("\n4. 单独获取测试配置:")
    for key in test_configs.keys():
        value = config_manager.get_config(key)
        print(f"   {key}: {value}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_config()