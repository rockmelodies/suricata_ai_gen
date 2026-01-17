#!/bin/bash

# Suricata Rule Generator - Stop All Services (Linux)

echo "============================================"
echo "   Stopping Suricata Rule Generator"
echo "============================================"
echo ""

# Stop tmux session
if command -v tmux &> /dev/null; then
    if tmux has-session -t suricata_rule_gen 2>/dev/null; then
        echo "Stopping tmux session..."
        tmux kill-session -t suricata_rule_gen
        echo "✓ Tmux session stopped"
    fi
fi

# Stop screen sessions
if command -v screen &> /dev/null; then
    if screen -list | grep -q "suricata_rule_gen_backend"; then
        echo "Stopping backend screen session..."
        screen -S suricata_rule_gen_backend -X quit
        echo "✓ Backend screen session stopped"
    fi
    
    if screen -list | grep -q "suricata_rule_gen_frontend"; then
        echo "Stopping frontend screen session..."
        screen -S suricata_rule_gen_frontend -X quit
        echo "✓ Frontend screen session stopped"
    fi
fi

# Kill processes by port
# Also check for PID files

echo ""
echo "Checking for processes on ports 5000 and 8080..."

# Kill process by PID file (backend)
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Killing backend process (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
        echo "✓ Backend stopped"
    else
        echo "  Backend PID file exists but process not running"
    fi
    rm -f backend.pid
else
    # Fallback to port-based killing
    BACKEND_PID=$(lsof -ti:5000 2>/dev/null)
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Killing backend process (PID: $BACKEND_PID)..."
        kill -9 $BACKEND_PID 2>/dev/null
        echo "✓ Backend stopped"
    else
        echo "  No process found on port 5000"
    fi
fi

# Kill process by PID file (frontend)
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Killing frontend process (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
        echo "✓ Frontend stopped"
    else
        echo "  Frontend PID file exists but process not running"
    fi
    rm -f frontend.pid
else
    # Fallback to port-based killing
    FRONTEND_PID=$(lsof -ti:5173 2>/dev/null)
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Killing frontend process (PID: $FRONTEND_PID)..."
        kill -9 $FRONTEND_PID 2>/dev/null
        echo "✓ Frontend stopped"
    else
        echo "  No process found on port 5173"
    fi
fi

echo ""
echo "============================================"
echo "   All services stopped"
echo "============================================"
