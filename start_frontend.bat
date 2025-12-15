@echo off
echo Starting Suricata Rule Generator Frontend...
echo.

cd /d "%~dp0\frontend"

REM Check if Python HTTP server is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo Frontend will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server 8080

pause
