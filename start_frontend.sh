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
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 8080
