#!/usr/bin/env python
# encoding: utf-8
# 诊断Suricata配置文件识别问题

import os
import platform
import subprocess
import json

def diagnose_config_issue():
    """诊断配置文件识别问题"""
    print("=== Suricata配置文件诊断 ===\n")
    
    # 1. 检查环境变量
    print("1. 环境变量检查:")
    env_vars = ['SURICATA_CONFIG', 'SURICATA_CONFIG_PATH', 'SURICATA_RULES_DIR', 'SURICATA_LOG_DIR']
    for var in env_vars:
        value = os.getenv(var, '未设置')
        print(f"   {var}: {value}")
    
    # 2. 检查配置文件路径
    print("\n2. 配置文件路径检查:")
    possible_configs = [
        "/etc/suricata/suricata.yaml",
        "/usr/local/etc/suricata/suricata.yaml",
        "/etc/default/suricata",
        os.getenv('SURICATA_CONFIG', '/etc/suricata/suricata.yaml')
    ]
    
    # 去重
    unique_configs = list(dict.fromkeys(possible_configs))
    
    for config_path in unique_configs:
        exists = os.path.exists(config_path)
        readable = os.access(config_path, os.R_OK) if exists else False
        print(f"   {config_path}: {'✓ 存在' if exists else '✗ 不存在'} {'(可读)' if readable else '(不可读)' if exists else ''}")
        
        # 如果文件存在，检查内容
        if exists and readable:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    print(f"     - 文件大小: {len(content)} 字节")
                    print(f"     - 行数: {lines}")
                    # 检查是否包含基本配置
                    if 'vars:' in content or 'af-packet:' in content:
                        print(f"     - ✓ 包含基本配置")
                    else:
                        print(f"     - ? 配置内容可能不完整")
            except Exception as e:
                print(f"     - ✗ 读取文件时出错: {e}")
    
    # 3. 检查当前工作目录
    print(f"\n3. 当前工作目录: {os.getcwd()}")
    print(f"   操作系统: {platform.system()}")
    print(f"   Python版本: {platform.python_version()}")
    
    # 4. 检查Suricata命令
    print("\n4. Suricata命令检查:")
    suricata_cmd = None
    for cmd in ['suricata', '/usr/bin/suricata', '/usr/local/bin/suricata']:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                suricata_cmd = cmd
                print(f"   ✓ 找到Suricata: {cmd}")
                print(f"   版本信息: {result.stdout.strip()}")
                break
        except:
            pass
    
    if not suricata_cmd:
        print("   ✗ 未找到Suricata命令")
        return
    
    # 5. 测试Suricata配置验证
    print("\n5. Suricata配置验证测试:")
    for config_path in unique_configs:
        if os.path.exists(config_path) and os.access(config_path, os.R_OK):
            try:
                result = subprocess.run([
                    suricata_cmd, '-T', '-c', config_path
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"   ✓ {config_path}: 配置验证通过")
                else:
                    print(f"   ✗ {config_path}: 配置验证失败")
                    print(f"     错误信息: {result.stderr[:200]}...")
            except subprocess.TimeoutExpired:
                print(f"   ✗ {config_path}: 验证超时")
            except Exception as e:
                print(f"   ✗ {config_path}: 验证出错: {e}")

def container_specific_check():
    """容器特定检查"""
    print("\n=== 容器环境检查 ===")
    
    # 检查是否在容器中运行
    try:
        with open('/proc/1/cgroup', 'r') as f:
            cgroup = f.read()
            if 'docker' in cgroup or 'containerd' in cgroup:
                print("✓ 检测到在容器环境中运行")
            else:
                print("? 可能在容器环境中运行")
    except:
        print("? 无法确定是否在容器中")
    
    # 检查挂载点
    try:
        with open('/proc/mounts', 'r') as f:
            mounts = f.read()
            suricata_mounts = [line for line in mounts.split('\n') if 'suricata' in line.lower()]
            if suricata_mounts:
                print("找到的Suricata相关挂载:")
                for mount in suricata_mounts:
                    print(f"  {mount}")
            else:
                print("未找到Suricata相关挂载")
    except:
        print("无法检查挂载信息")

if __name__ == "__main__":
    diagnose_config_issue()
    container_specific_check()
    
    print("\n=== 建议解决方案 ===")
    print("1. 确保设置了正确的环境变量:")
    print("   export SURICATA_CONFIG=/etc/suricata/suricata.yaml")
    print("2. 检查文件权限:")
    print("   ls -la /etc/suricata/suricata.yaml")
    print("3. 验证配置文件内容完整性")
    print("4. 确认容器正确挂载了配置文件目录")