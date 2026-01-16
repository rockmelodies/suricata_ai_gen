#!/usr/bin/env python
# encoding: utf-8
"""
快速检查Suricata引擎是否可用
"""

import os
import subprocess
import platform
import shutil


def check_suricata():
    """检查Suricata引擎"""
    print("检查Suricata引擎状态...")
    print(f"操作系统: {platform.system()}")
    
    # 检查是否能找到Suricata命令
    suricata_cmd = shutil.which('suricata') or shutil.which('suricata.exe')
    
    if suricata_cmd:
        print(f"✓ 找到Suricata: {suricata_cmd}")
        
        # 尝试获取版本
        try:
            result = subprocess.run([suricata_cmd, '-V'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ 版本信息: {result.stdout.strip()}")
            else:
                print(f"✗ 获取版本失败: {result.stderr}")
        except Exception as e:
            print(f"✗ 版本检查出错: {e}")
        
        return True
    else:
        print("✗ 未找到Suricata命令")
        print("\n解决方案:")
        if platform.system() == "Windows":
            print("- 从 https://github.com/OISF/suricata/releases 下载并安装Suricata")
            print("- 或配置SSH连接到Linux/Kali系统进行远程验证")
        else:
            print("- Ubuntu/Debian: sudo apt-get install suricata")
            print("- CentOS/RHEL: sudo yum install suricata 或 sudo dnf install suricata")
            print("- 确保安装完成后将suricata添加到系统PATH")
        
        return False


def check_config_files():
    """检查Suricata配置文件"""
    print("\n检查Suricata配置文件...")
    
    possible_configs = [
        "/etc/suricata/suricata.yaml",
        "/usr/local/etc/suricata/suricata.yaml",
        "/etc/default/suricata",
        "D:\\Program Files\\Suricata\\suricata.yaml",
        "D:\\suricata\\suricata.yaml",
        "D:\\Program Files (x86)\\Suricata\\suricata.yaml"
    ]
    
    found_config = False
    for config_path in possible_configs:
        if os.path.exists(config_path):
            print(f"✓ 找到配置文件: {config_path}")
            found_config = True
            break
    
    if not found_config:
        print("✗ 未找到Suricata配置文件")
        print("  请确认Suricata已正确安装")
    
    return found_config


def check_directories():
    """检查Suricata常用目录"""
    print("\n检查Suricata常用目录...")
    
    possible_dirs = {
        "rules": [
            "/var/lib/suricata/rules",
            "/etc/suricata/rules",
            "D:\\Program Files\\Suricata\\rules",
            "D:\\suricata\\rules"
        ],
        "logs": [
            "/var/log/suricata",
            "/var/lib/suricata/logs",
            "D:\\Program Files\\Suricata\\log",
            "D:\\suricata\\log"
        ]
    }
    
    for dir_type, possible_paths in possible_dirs.items():
        print(f"  {dir_type}目录:")
        found = False
        for path in possible_paths:
            if os.path.exists(path):
                print(f"    ✓ {path}")
                found = True
                break
        if not found:
            print(f"    ✗ 未找到{dir_type}目录")


def main():
    """主函数"""
    print("="*50)
    print("Suricata引擎可用性检查")
    print("="*50)
    
    suricata_found = check_suricata()
    config_found = check_config_files()
    check_directories()
    
    print("\n" + "="*50)
    print("检查总结:")
    
    if suricata_found and config_found:
        print("✓ Suricata引擎已正确安装并可使用")
        print("  您可以正常使用规则验证功能")
    elif suricata_found:
        print("~ Suricata已安装但配置文件可能需要调整")
        print("  请检查配置文件路径是否正确")
    else:
        print("✗ Suricata未安装或不可用")
        print("  请先安装Suricata后再使用规则验证功能")
    
    print("="*50)
    
    return suricata_found and config_found


if __name__ == "__main__":
    main()