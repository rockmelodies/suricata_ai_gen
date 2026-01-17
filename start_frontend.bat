@echo off
echo Starting Suricata Rule Generator Frontend...
echo.

cd /d "%~dp0\frontend-vue3"

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed or not in PATH!
    echo Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo npm is not installed or not in PATH!
    echo Please install Node.js first.
    pause
    exit /b 1
)

echo Installing dependencies...
npm install

echo Frontend will be available at: http://localhost:5173
Remote access: http://<your-ip>:5173
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Vite development server with host binding
npm run dev -- --host 0.0.0.0

pause