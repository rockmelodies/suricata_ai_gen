#!/bin/bash

# Suricata Rule Generator - Start All Services (Linux)

echo "============================================"
echo "   Suricata Rule Generator - Start All"
echo "============================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Make scripts executable
chmod +x start_backend.sh
chmod +x start_frontend.sh

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Using tmux to manage multiple terminals..."
    echo ""
    
    # Create new tmux session
    SESSION_NAME="suricata_rule_gen"
    
    # Kill existing session if it exists
    tmux kill-session -t $SESSION_NAME 2>/dev/null
    
    # Create new session with backend
    # Redirect output to log file to reduce console clutter
    tmux new-session -d -s $SESSION_NAME -n "Backend" "./start_backend.sh > /dev/null 2>&1"
    
    # Create new window for frontend
    # Redirect output to log file to reduce console clutter
    tmux new-window -t $SESSION_NAME -n "Frontend" "./start_frontend.sh > /dev/null 2>&1"
    
    # Select backend window
    tmux select-window -t $SESSION_NAME:0
    
    echo "============================================"
    echo "   Services are starting in tmux..."
    echo "============================================"
    echo ""
    echo "   Backend:  http://localhost:5000"
    echo "   Frontend: http://localhost:8080"
    echo ""
    echo "   To attach to session: tmux attach -t $SESSION_NAME"
    echo "   To switch windows: Ctrl+B then 0/1"
    echo "   To detach: Ctrl+B then D"
    echo "   To kill session: tmux kill-session -t $SESSION_NAME"
    echo ""
    echo "============================================"
    echo ""
    
    # Wait a moment
    sleep 2
    
    # Try to open browser
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8080 &> /dev/null &
    elif command -v sensible-browser &> /dev/null; then
        sensible-browser http://localhost:8080 &> /dev/null &
    fi
    
    # Attach to tmux session
    tmux attach -t $SESSION_NAME
    
else
    echo "tmux not found, using screen instead..."
    echo ""
    
    if command -v screen &> /dev/null; then
        SESSION_NAME="suricata_rule_gen"
        
        # Kill existing session if exists
        screen -S $SESSION_NAME -X quit 2>/dev/null
        
        # Start backend in screen
        screen -dmS "${SESSION_NAME}_backend" bash -c "./start_backend.sh > /dev/null 2>&1"
        
        # Wait a moment
        sleep 2
        
        # Start frontend in another screen
        screen -dmS "${SESSION_NAME}_frontend" bash -c "./start_frontend.sh > /dev/null 2>&1"
        
        echo "============================================"
        echo "   Services are starting in screen..."
        echo "============================================"
        echo ""
        echo "   Backend:  http://localhost:5000"
        echo "   Frontend: http://localhost:8080"
        echo ""
        echo "   To view backend:  screen -r ${SESSION_NAME}_backend"
        echo "   To view frontend: screen -r ${SESSION_NAME}_frontend"
        echo "   To detach: Ctrl+A then D"
        echo "   To kill: screen -S <session_name> -X quit"
        echo ""
        echo "============================================"
        echo ""
        
        # Try to open browser
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:8080 &> /dev/null &
        elif command -v sensible-browser &> /dev/null; then
            sensible-browser http://localhost:8080 &> /dev/null &
        fi
        
        echo "Servers are running in background."
        echo "Press Enter to continue..."
        read
        
    else
        echo "Neither tmux nor screen is available!"
        echo "Please install one of them for better experience:"
        echo "  sudo apt install tmux"
        echo "  or"
        echo "  sudo apt install screen"
        echo ""
        echo "Starting services manually..."
        echo ""
        
        # Start backend in background
        ./start_backend.sh > /dev/null 2>&1 &
        BACKEND_PID=$!
        
        # Wait for backend to start
        sleep 3
        
        # Start frontend in background
        ./start_frontend.sh > /dev/null 2>&1 &
        FRONTEND_PID=$!
        
        echo ""
        echo "============================================"
        echo "   Services Started"
        echo "============================================"
        echo ""
        echo "   Backend PID:  $BACKEND_PID"
        echo "   Frontend PID: $FRONTEND_PID"
        echo ""
        echo "   Backend:  http://localhost:5000"
        echo "   Frontend: http://localhost:8080"
        echo ""
        echo "   To stop services:"
        echo "   kill $BACKEND_PID $FRONTEND_PID"
        echo ""
        echo "============================================"
        echo ""
        
        # Try to open browser
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:8080 &> /dev/null &
        elif command -v sensible-browser &> /dev/null; then
            sensible-browser http://localhost:8080 &> /dev/null &
        fi
        
        # Wait for user interrupt
        echo "Press Ctrl+C to stop all services..."
        trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
        wait
    fi
fi
