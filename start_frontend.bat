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
echo Remote access: http://<your-ip>:8080
echo.
echo Press Ctrl+C to stop the server
echo.

REM Bind to 0.0.0.0 to allow remote access
python -m http.server 8080 --bind 0.0.0.0

pause
