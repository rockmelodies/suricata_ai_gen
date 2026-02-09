#!/usr/bin/env python
# encoding: utf-8
# Docker容器Suricata配置权限修复工具

import os
import subprocess
import sys
import json

def check_docker_environment():
    """检查是否在Docker环境中"""
    print("=== Docker环境检查 ===")
    
    # 检查是否在容器中
    in_container = False
    container_type = "unknown"
    
    # 方法1: 检查 /.dockerenv 文件
    if os.path.exists('/.dockerenv'):
        in_container = True
        container_type = "Docker"
        print("✓ 检测到Docker容器环境 (/.dockerenv存在)")
    
    # 方法2: 检查 /proc/1/cgroup
    try:
        with open('/proc/1/cgroup', 'r') as f:
            cgroup_content = f.read()
            if 'docker' in cgroup_content:
                in_container = True
                container_type = "Docker"
                print("✓ 检测到Docker容器环境 (cgroup包含docker)")
            elif 'containerd' in cgroup_content:
                in_container = True
                container_type = "Containerd"
                print("✓ 检测到Containerd容器环境")
    except:
        pass
    
    # 方法3: 检查环境变量
    if 'container' in os.environ:
        in_container = True
        print(f"✓ 检测到容器环境 (CONTAINER={os.environ.get('container')})")
    
    return in_container, container_type

def docker_specific_solutions():
    """Docker特定的解决方案"""
    print("\n=== Docker容器解决方案 ===")
    
    # 1. 检查当前用户
    try:
        uid = os.getuid()
        user_name = subprocess.check_output(['whoami'], text=True).strip()
        print(f"当前用户: {user_name} (UID: {uid})")
    except:
        print("无法确定当前用户")
        uid = 1000  # 默认用户ID
    
    # 2. 提供Docker运行建议
    print("\nDocker运行建议:")
    
    if uid == 0:
        print("✓ 当前是root用户，权限应该足够")
    else:
        print("⚠ 当前是非root用户，可能需要权限调整")
        print("\n解决方案选项:")
        print("1. 以root用户运行容器:")
        print("   docker run --user 0:0 ...")
        print("\n2. 在docker-compose.yml中设置:")
        print("   services:")
        print("     app:")
        print("       user: '0:0'  # root用户")
        print("\n3. 挂载时设置正确的权限:")
        print("   volumes:")
        print("     - ./suricata-config:/etc/suricata:rw")
        print("\n4. 构建时复制配置文件:")
        print("   COPY suricata.yaml /etc/suricata/suricata.yaml")
        print("   RUN chmod 644 /etc/suricata/suricata.yaml")

def create_docker_compose_fix():
    """创建修复的docker-compose配置"""
    print("\n=== 创建Docker Compose修复配置 ===")
    
    docker_compose_content = '''version: '3.8'

services:
  suricata-app:
    # 使用你的应用镜像
    image: your-suricata-app:latest
    container_name: suricata-app
    
    # 以root用户运行确保权限
    user: "0:0"
    
    # 环境变量配置
    environment:
      - SURICATA_CONFIG=/etc/suricata/suricata.yaml
      - SURICATA_RULES_DIR=/var/lib/suricata/rules
      - SURICATA_LOG_DIR=/var/log/suricata
    
    # 挂载配置文件（读写权限）
    volumes:
      - ./suricata-config:/etc/suricata:rw
      - ./rules:/var/lib/suricata/rules:rw
      - ./logs:/var/log/suricata:rw
    
    # 端口映射
    ports:
      - "5000:5000"
    
    # 重启策略
    restart: unless-stopped
    
    # 健康检查
    healthcheck:
      test: ["CMD", "python", "-c", "import os; exit(0 if os.path.exists('/etc/suricata/suricata.yaml') and os.access('/etc/suricata/suricata.yaml', os.R_OK) else 1)"]
      interval: 30s
      timeout: 10s
      retries: 3
'''
    
    try:
        with open('docker-compose.fixed.yml', 'w') as f:
            f.write(docker_compose_content)
        print("✓ 已创建修复的docker-compose配置: docker-compose.fixed.yml")
        print("使用方法:")
        print("  docker-compose -f docker-compose.fixed.yml up -d")
        return True
    except Exception as e:
        print(f"✗ 创建docker-compose文件失败: {e}")
        return False

def create_dockerfile_fix():
    """创建修复的Dockerfile"""
    print("\n=== 创建修复的Dockerfile ===")
    
    dockerfile_content = '''# 使用Python基础镜像
FROM python:3.9-slim

# 安装Suricata
RUN apt-get update && apt-get install -y \\
    suricata \\
    && rm -rf /var/lib/apt/lists/*

# 创建Suricata目录
RUN mkdir -p /etc/suricata /var/lib/suricata/rules /var/log/suricata

# 复制配置文件到镜像中（确保权限正确）
COPY suricata.yaml /etc/suricata/suricata.yaml

# 设置正确的权限
RUN chmod 644 /etc/suricata/suricata.yaml && \\
    chown root:root /etc/suricata/suricata.yaml

# 创建应用目录
WORKDIR /app

# 复制应用代码
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV SURICATA_CONFIG=/etc/suricata/suricata.yaml
ENV SURICATA_RULES_DIR=/var/lib/suricata/rules
ENV SURICATA_LOG_DIR=/var/log/suricata

# 暴露端口
EXPOSE 5000

# 以root用户运行（确保权限）
USER root

# 启动应用
CMD ["python", "app.py"]
'''
    
    try:
        with open('Dockerfile.fixed', 'w') as f:
            f.write(dockerfile_content)
        print("✓ 已创建修复的Dockerfile: Dockerfile.fixed")
        print("使用方法:")
        print("  docker build -t suricata-app-fixed -f Dockerfile.fixed .")
        return True
    except Exception as e:
        print(f"✗ 创建Dockerfile失败: {e}")
        return False

def test_container_access():
    """测试容器内文件访问"""
    print("\n=== 容器文件访问测试 ===")
    
    config_path = '/etc/suricata/suricata.yaml'
    
    # 检查文件存在性
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        return False
    
    print(f"✓ 配置文件存在: {config_path}")
    
    # 检查权限
    try:
        # 检查各种访问权限
        can_read = os.access(config_path, os.R_OK)
        can_write = os.access(config_path, os.W_OK)
        can_execute = os.access(config_path, os.X_OK)
        
        print(f"访问权限 - 读:{can_read} 写:{can_write} 执行:{can_execute}")
        
        # 尝试实际读取
        if can_read:
            with open(config_path, 'r') as f:
                first_line = f.readline().strip()
                print(f"✓ 成功读取文件，第一行: {first_line[:50]}")
                return True
        else:
            print("✗ 没有读取权限")
            return False
            
    except Exception as e:
        print(f"✗ 访问文件时出错: {e}")
        return False

def main():
    """主函数"""
    print("开始Docker容器权限诊断和修复...\n")
    
    # 检查Docker环境
    in_container, container_type = check_docker_environment()
    
    if not in_container:
        print("⚠ 未检测到容器环境，可能在宿主机上运行")
        print("请在容器内运行此脚本")
        return
    
    print(f"✓ 确认在{container_type}容器环境中运行\n")
    
    # 测试文件访问
    access_ok = test_container_access()
    
    # 提供解决方案
    docker_specific_solutions()
    
    # 创建修复配置文件
    if not access_ok:
        print("\n=== 创建修复配置 ===")
        create_docker_compose_fix()
        create_dockerfile_fix()
        
        print("\n=== 紧急修复命令 ===")
        print("# 如果急需修复，可以尝试:")
        print("chmod 644 /etc/suricata/suricata.yaml")
        print("chown root:root /etc/suricata/suricata.yaml")
        print("# 或者在容器外:")
        print("docker exec -u 0 <container_name> chmod 644 /etc/suricata/suricata.yaml")

if __name__ == "__main__":
    main()