#!/bin/bash

# Suricata Rule Generator - Frontend Startup Script (Linux)

echo "========================================"
echo "  Starting Suricata Rule Generator Frontend"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/frontend-vue3"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed!"
    echo "Please install Node.js first."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "npm is not installed!"
    echo "Please install Node.js first."
    exit 1
fi

echo "Installing dependencies..."
npm install

echo "Frontend server starting..."
echo ""
echo "========================================"
echo "  Frontend URL: http://localhost:5173"
echo "  Remote access: http://<your-ip>:5173"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Vite development server with host binding
npm run dev -- --host 0.0.0.0
