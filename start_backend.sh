#!/bin/bash

# Suricata Rule Generator - Backend Startup Script (Linux)

echo "========================================"
echo "  Starting Suricata Rule Generator Backend"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment!"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment!"
    exit 1
fi

# Install/Update dependencies
echo ""
echo "Installing/Updating dependencies..."
pip install -r backend/requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies!"
    exit 1
fi

# Start Flask backend
# Disable debug mode to reduce verbose output
export FLASK_DEBUG=0
export FLASK_ENV=production

echo ""
echo "========================================"
echo "  Backend is starting..."
echo "  URL: http://localhost:5000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Redirect output to log file to reduce console clutter
python backend/app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

echo "Backend PID: $BACKEND_PID"
echo "Log file: backend.log"
echo "To view logs: tail -f backend.log"
