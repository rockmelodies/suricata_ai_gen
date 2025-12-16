#!/bin/bash

# Suricata Rule Generator - Frontend Startup Script (Linux)

echo "========================================"
echo "  Starting Suricata Rule Generator Frontend"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/frontend"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed!"
    echo "Please install Python3 first."
    exit 1
fi

echo "Frontend server starting..."
echo ""
echo "========================================"
echo "  Frontend URL: http://localhost:8080"
echo "  Remote access: http://<your-ip>:8080"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Bind to 0.0.0.0 to allow remote access
# Redirect output to log file to reduce console clutter
python3 -m http.server 8080 --bind 0.0.0.0 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

echo "Frontend PID: $FRONTEND_PID"
echo "Log file: frontend.log"
echo "To view logs: tail -f frontend.log"
