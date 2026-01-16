#!/usr/bin/env bash

# Test script to verify start_all.sh fixes

echo "Testing start_all.sh fixes..."

# Test 1: Check if script can be executed with bash
echo "Test 1: Checking bash execution..."
if bash start_all.sh --help 2>/dev/null; then
    echo "✓ Script can be executed with bash"
else
    echo "✗ Script cannot be executed with bash"
fi

# Test 2: Check if shebang is correct
echo ""
echo "Test 2: Checking shebang..."
head -n 1 start_all.sh | grep -q "bash" && echo "✓ Shebang is correct" || echo "✗ Shebang is incorrect"

# Test 3: Check if tmux command uses bash -c
echo ""
echo "Test 3: Checking tmux command format..."
grep -q "bash -c" start_all.sh && echo "✓ tmux commands use bash -c" || echo "✗ tmux commands don't use bash -c"

# Test 4: Check if screen command uses bash -c
echo ""
echo "Test 4: Checking screen command format..."
grep -q "bash -c" start_all.sh && echo "✓ screen commands use bash -c" || echo "✗ screen commands don't use bash -c"

# Test 5: Check if backend script has wait command
echo ""
echo "Test 5: Checking backend script wait command..."
grep -q "wait" start_backend.sh && echo "✓ Backend script has wait command" || echo "✗ Backend script missing wait command"

# Test 6: Check if frontend script has wait command
echo ""
echo "Test 6: Checking frontend script wait command..."
grep -q "wait" start_frontend.sh && echo "✓ Frontend script has wait command" || echo "✗ Frontend script missing wait command"

echo ""
echo "Test completed. Please run start_all.sh normally to verify the fix."
