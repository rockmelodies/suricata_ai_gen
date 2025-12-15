@echo off
echo ============================================
echo   Suricata Rule Generator - Start All
echo ============================================
echo.

cd /d "%~dp0"

echo Starting Backend Server...
start "Backend - Flask" cmd /k "call start_backend.bat"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend - Vue3" cmd /k "call start_frontend.bat"

timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo   All services are starting...
echo ============================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:8080
echo.
echo   Open your browser and go to:
echo   http://localhost:8080
echo.
echo ============================================

timeout /t 5

start http://localhost:8080

echo.
echo Press any key to exit...
pause >nul
