#!/usr/bin/env python
# encoding: utf-8
"""
Suricata Engine Test Script
用于测试Suricata引擎在Windows或Linux上是否可以正常使用
"""

import os
import subprocess
import tempfile
import platform
import shutil


def test_suricata_availability():
    """测试Suricata是否可用"""
    print("=== 测试Suricata引擎可用性 ===")
    print(f"操作系统: {platform.system()}")
    
    # 查找Suricata命令
    suricata_cmd = shutil.which('suricata') or shutil.which('suricata.exe')
    
    if suricata_cmd:
        print(f"✓ 找到Suricata命令: {suricata_cmd}")
        return suricata_cmd
    else:
        print("✗ 未找到Suricata命令")
        print("  提示: 请确保Suricata已安装并添加到系统PATH中")
        print("  - Linux/Kali: sudo apt-get install suricata")
        print("  - Windows: 从 https://github.com/OISF/suricata/releases 下载并安装")
        return None


def test_suricata_version(suricata_cmd):
    """测试Suricata版本信息"""
    print("\n=== 测试Suricata版本 ===")
    try:
        result = subprocess.run([suricata_cmd, '--version'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✓ Suricata版本: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ 获取版本失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ 版本查询超时")
        return False
    except Exception as e:
        print(f"✗ 版本查询出错: {e}")
        return False


def test_suricata_syntax_check(suricata_cmd):
    """测试Suricata规则语法检查功能"""
    print("\n=== 测试Suricata规则语法检查 ===")
    
    # 创建一个简单的测试规则
    test_rule = 'alert tcp any any -> any 80 (msg:"Test rule"; content:"GET"; sid:1000001; rev:1;)'
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rules', delete=False) as f:
            f.write(test_rule)
            temp_rule_file = f.name
        
        # 使用默认配置文件测试语法
        default_config = "/etc/suricata/suricata.yaml" if platform.system() != "Windows" else "C:\\\\Program Files\\\\Suricata\\\\suricata.yaml"
        
        # 如果默认配置不存在，尝试查找
        if not os.path.exists(default_config):
            # 尝试常见位置
            possible_configs = [
                "/etc/suricata/suricata.yaml",
                "/usr/local/etc/suricata/suricata.yaml",
                "/etc/default/suricata",
                "C:\\Program Files\\Suricata\\suricata.yaml",
                "C:\\suricata\\suricata.yaml"
            ]
            for config in possible_configs:
                if os.path.exists(config):
                    default_config = config
                    break
            else:
                print("  ! 未找到Suricata配置文件，跳过语法检查测试")
                os.unlink(temp_rule_file)
                return False
        
        result = subprocess.run([
            suricata_cmd,
            '-T',  # 测试模式
            '-c', default_config,
            '-S', temp_rule_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ 规则语法检查通过")
            success = True
        else:
            print(f"✗ 规则语法检查失败: {result.stderr}")
            success = False
            
        # 清理临时文件
        os.unlink(temp_rule_file)
        return success
        
    except subprocess.TimeoutExpired:
        print("✗ 语法检查超时")
        if 'temp_rule_file' in locals():
            os.unlink(temp_rule_file)
        return False
    except Exception as e:
        print(f"✗ 语法检查出错: {e}")
        if 'temp_rule_file' in locals():
            os.unlink(temp_rule_file)
        return False


def test_suricata_config_validation(suricata_cmd):
    """测试Suricata配置文件验证"""
    print("\n=== 测试Suricata配置文件 ===")
    
    # 查找配置文件
    possible_configs = [
        "/etc/suricata/suricata.yaml",
        "/usr/local/etc/suricata/suricata.yaml",
        "/etc/default/suricata",
        "C:\\Program Files\\Suricata\\suricata.yaml",
        "C:\\suricata\\suricata.yaml"
    ]
    
    config_found = False
    for config in possible_configs:
        if os.path.exists(config):
            print(f"  找到配置文件: {config}")
            config_found = True
            try:
                result = subprocess.run([
                    suricata_cmd,
                    '-T',  # 测试模式
                    '-c', config
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("✓ 配置文件验证通过")
                    return True
                else:
                    print(f"✗ 配置文件验证失败: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                print("✗ 配置验证超时")
                return False
            except Exception as e:
                print(f"✗ 配置验证出错: {e}")
                return False
    
    if not config_found:
        print("  ! 未找到Suricata配置文件")
        print("  提示: 请确认Suricata已正确安装")
        return False


def test_suricata_with_sample_pcap(suricata_cmd):
    """测试Suricata与PCAP文件的基本功能"""
    print("\n=== 测试Suricata与PCAP文件处理 ===")
    
    # 检查是否存在示例PCAP文件
    sample_pcap = "sample.pcap"
    if not os.path.exists(sample_pcap):
        print("  ! 未找到示例PCAP文件，跳过此测试")
        print("  提示: 创建一个名为 'sample.pcap' 的文件来测试完整功能")
        return False
    
    try:
        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 查找配置文件
            possible_configs = [
                "/etc/suricata/suricata.yaml",
                "/usr/local/etc/suricata/suricata.yaml",
                "/etc/default/suricata",
                "C:\\Program Files\\Suricata\\suricata.yaml",
                "C:\\suricata\\suricata.yaml"
            ]
            
            config_found = False
            for config in possible_configs:
                if os.path.exists(config):
                    config_found = True
                    break
            
            if not config_found:
                print("  ! 未找到Suricata配置文件，跳过此测试")
                return False
            
            result = subprocess.run([
                suricata_cmd,
                '-c', config,
                '-r', sample_pcap,
                '-l', temp_dir
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✓ PCAP处理测试通过")
                # 检查输出日志
                fast_log = os.path.join(temp_dir, "fast.log")
                if os.path.exists(fast_log):
                    with open(fast_log, 'r') as f:
                        lines = f.readlines()
                        print(f"  - fast.log中有 {len(lines)} 条告警记录")
                return True
            else:
                print(f"✗ PCAP处理失败: {result.stderr}")
                return False
                
    except subprocess.TimeoutExpired:
        print("✗ PCAP处理超时")
        return False
    except Exception as e:
        print(f"✗ PCAP处理出错: {e}")
        return False


def main():
    """主测试函数"""
    print("Suricata引擎功能测试")
    print("="*50)
    
    # 测试1: 检查Suricata是否可用
    suricata_cmd = test_suricata_availability()
    if not suricata_cmd:
        print("\n由于未找到Suricata，其他测试将被跳过。")
        return False
    
    # 测试2: 检查版本
    version_ok = test_suricata_version(suricata_cmd)
    
    # 测试3: 配置验证
    config_ok = test_suricata_config_validation(suricata_cmd)
    
    # 测试4: 语法检查
    syntax_ok = test_suricata_syntax_check(suricata_cmd)
    
    # 测试5: PCAP处理（如果存在示例文件）
    pcap_ok = test_suricata_with_sample_pcap(suricata_cmd)
    
    # 总结
    print("\n" + "="*50)
    print("测试总结:")
    print(f"  Suricata可用性: {'✓' if suricata_cmd else '✗'}")
    print(f"  版本信息: {'✓' if version_ok else '✗'}")
    print(f"  配置验证: {'✓' if config_ok else '✗'}")
    print(f"  语法检查: {'✓' if syntax_ok else '✗'}")
    print(f"  PCAP处理: {'✓' if pcap_ok else '✗'}")
    
    success_count = sum([bool(suricata_cmd), version_ok, config_ok, syntax_ok, pcap_ok])
    total_tests = 5
    
    print(f"\n总体进度: {success_count}/{total_tests} 项测试通过")
    
    if success_count >= 3:  # 至少基础功能正常
        print("✓ Suricata引擎基本功能正常")
        return True
    else:
        print("✗ Suricata引擎存在问题，建议检查安装和配置")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)