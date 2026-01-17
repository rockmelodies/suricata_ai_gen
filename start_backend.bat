@echo off
echo Starting Suricata Rule Generator Backend...
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please create it first: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies if needed
echo Installing/Updating dependencies...
pip install -r backend\requirements.txt

REM Start Flask backend
echo.
echo Starting Flask backend on http://localhost:5000
echo.
python backend\start_app.py

pause
