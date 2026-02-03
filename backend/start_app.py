#!/usr/bin/env python3
# encoding: utf-8
# Application startup script for Kali Linux

import os
import sys
import subprocess
from pathlib import Path


def ensure_directories():
    """Ensure necessary directories exist"""
    upload_dir = os.getenv('UPLOAD_DIR', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    print(f"确保上传目录存在: {upload_dir}")
    
    # Set proper permissions for upload directory
    try:
        os.chmod(upload_dir, 0o755)
        print(f"设置上传目录权限: {upload_dir}")
    except PermissionError:
        print(f"警告: 无法修改 {upload_dir} 的权限")


def check_and_create_database():
    """Check and create database file with proper permissions"""
    from database import Database
    
    # Get the database path from environment or default
    db_path_env = os.getenv('DB_PATH')
    if db_path_env:
        db_path = db_path_env
    else:
        # Use default path relative to backend directory
        backend_dir = Path(__file__).parent.resolve()
        db_path = backend_dir / 'suricata_rules.db'
    
    print(f"数据库路径: {db_path}")
    
    # Create database instance and initialize
    db = Database(str(db_path))
    
    try:
        # This will trigger the creation of the database file
        db.init_db()
        print("数据库初始化成功!")
        return str(db_path)
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise

def main():
    """Main startup function"""
    print("=== Suricata规则生成工具启动脚本 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python 版本: {sys.version}")
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent.resolve()
    os.chdir(backend_dir)
    print(f"切换到后端目录: {backend_dir}")
    
    # Check if .env file exists
    env_file = backend_dir.parent / '.env'
    if not env_file.exists():
        print(f"警告: .env 文件不存在于 {env_file}")
        print("请确保已创建 .env 文件并配置了 AI_API_KEY")
    else:
        print(f"找到 .env 文件: {env_file}")
        
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=str(env_file))
        print("已加载 .env 文件中的环境变量")
    
    # Ensure necessary directories exist
    ensure_directories()
    
    # Check and create database
    try:
        db_path = check_and_create_database()
        print(f"使用数据库: {db_path}")
    except Exception as e:
        print(f"数据库设置失败: {e}")
        sys.exit(1)
    
    # Set environment variables for the Flask app
    os.environ['PYTHONPATH'] = str(backend_dir)
    os.environ['FLASK_APP'] = 'app_v2.py'
    
    # Import and run the Flask app
    try:
        from app_v2 import app  # Updated to use app_v2.py
        
        print("\n启动 Flask 应用...")
        print("应用将在 http://0.0.0.0:5000 上运行")
        print("按 Ctrl+C 停止服务\n")
        
        # Run the Flask app
        app.run(
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        )
        
    except KeyboardInterrupt:
        print("\n收到中断信号，正在关闭...")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()