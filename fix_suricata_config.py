#!/usr/bin/env python
# encoding: utf-8
# Suricata配置文件修复工具

import os
import subprocess
import sys

def check_and_fix_config():
    """检查并修复Suricata配置问题"""
    print("=== Suricata配置检查与修复 ===\n")
    
    # 1. 检查环境变量设置
    print("1. 检查环境变量配置...")
    suricata_config = os.getenv('SURICATA_CONFIG')
    
    if not suricata_config:
        print("⚠️  未设置 SURICATA_CONFIG 环境变量")
        print("   建议设置: export SURICATA_CONFIG=/etc/suricata/suricata.yaml")
        # 自动设置环境变量
        os.environ['SURICATA_CONFIG'] = '/etc/suricata/suricata.yaml'
        print("   ✓ 已临时设置 SURICATA_CONFIG=/etc/suricata/suricata.yaml")
    else:
        print(f"✓ SURICATA_CONFIG 已设置为: {suricata_config}")
    
    # 2. 验证配置文件存在性和可读性
    print("\n2. 验证配置文件...")
    config_path = os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml')
    
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        return False
    
    if not os.access(config_path, os.R_OK):
        print(f"✗ 配置文件不可读: {config_path}")
        print("  建议修复权限: chmod 644 /etc/suricata/suricata.yaml")
        return False
    
    print(f"✓ 配置文件存在且可读: {config_path}")
    
    # 3. 检查配置文件内容
    print("\n3. 检查配置文件内容...")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 基本配置检查
        required_sections = ['vars:', 'af-packet:', 'outputs:']
        missing_sections = []
        
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  配置文件缺少以下基本部分: {', '.join(missing_sections)}")
        else:
            print("✓ 配置文件包含基本必需部分")
            
    except Exception as e:
        print(f"✗ 读取配置文件时出错: {e}")
        return False
    
    # 4. 测试Suricata配置验证
    print("\n4. 测试Suricata配置验证...")
    
    # 查找suricata命令
    suricata_cmd = None
    for cmd in ['suricata', '/usr/bin/suricata', '/usr/local/bin/suricata']:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                suricata_cmd = cmd
                break
        except:
            continue
    
    if not suricata_cmd:
        print("✗ 未找到Suricata命令")
        return False
    
    print(f"✓ 找到Suricata命令: {suricata_cmd}")
    
    # 执行配置验证
    try:
        result = subprocess.run([
            suricata_cmd, '-T', '-c', config_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ Suricata配置验证通过")
            return True
        else:
            print("✗ Suricata配置验证失败")
            print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ 配置验证超时")
        return False
    except Exception as e:
        print(f"✗ 配置验证出错: {e}")
        return False

def create_env_file():
    """创建或更新.env文件"""
    print("\n5. 创建/更新环境变量配置...")
    
    env_content = """# Suricata配置
SURICATA_CONFIG=/etc/suricata/suricata.yaml
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_LOG_DIR=/var/log/suricata

# 其他配置
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
"""
    
    env_file = '.env'
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✓ 已创建 {env_file} 文件")
        print("请重启应用使环境变量生效")
        return True
    except Exception as e:
        print(f"✗ 创建 {env_file} 文件失败: {e}")
        return False

def main():
    """主函数"""
    print("开始Suricata配置诊断和修复...\n")
    
    # 执行检查和修复
    config_ok = check_and_fix_config()
    
    if config_ok:
        print("\n🎉 配置检查通过！")
        print("Suricata应该能够正常识别配置文件")
    else:
        print("\n❌ 配置存在问题，需要进一步修复")
        
        # 尝试创建环境变量文件
        create_env_file()
        
        print("\n建议的手动修复步骤:")
        print("1. 检查文件权限: ls -la /etc/suricata/suricata.yaml")
        print("2. 修复权限问题: chmod 644 /etc/suricata/suricata.yaml")
        print("3. 验证配置文件内容完整性")
        print("4. 重启应用服务")

if __name__ == "__main__":
    main()