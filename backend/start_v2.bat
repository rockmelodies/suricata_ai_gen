@echo off
REM Start Backend API v2 (OpenAPI) - Windows

echo ========================================
echo    Suricata Rule Generator API v2.0
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo [WARNING] 虚拟环境不存在，正在创建...
    python -m venv venv
    echo [OK] 虚拟环境创建成功
    echo.
)

REM Activate virtual environment
echo [INFO] 激活虚拟环境...
call venv\Scripts\activate.bat

REM Install/Update dependencies
echo [INFO] 检查并安装依赖...
pip install -r requirements.txt >nul 2>&1

REM Run the API server
echo [INFO] 启动API服务器...
echo.
echo ========================================
echo   API文档: http://localhost:5000/api/docs
echo   默认管理员: admin / admin123
echo   服务地址: http://localhost:5000/api
echo ========================================
echo.

python app_with_auth.py

pause
