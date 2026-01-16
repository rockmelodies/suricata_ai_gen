@echo off
REM Start Frontend (Vue3) - Windows

cd /d "%~dp0"

echo ========================================
echo    Suricata Rule Generator - Frontend
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] 依赖未安装，正在安装...
    call npm install
    echo [OK] 依赖安装成功
    echo.
)

echo [INFO] 启动前端开发服务器...
echo.
echo ========================================
echo    访问地址: http://localhost:5173
echo    后端API: http://localhost:5000/api
echo ========================================
echo.

npm run dev

pause
