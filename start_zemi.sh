#!/bin/bash

# Zemi Auto-start Script
# Waits for dependencies then starts Zemi

echo "=== Zemi starting at $(date) ===" 

# Wait for network
echo "Waiting for network..."
sleep 10

# Wait for Colima/Docker
echo "Checking Docker..."
until docker ps &> /dev/null; do
    echo "Waiting for Docker..."
    sleep 5
done
echo "✓ Docker is ready"

# Wait for Matrix container
echo "Checking Matrix..."
until docker ps | grep zemi_matrix | grep healthy &> /dev/null; do
    echo "Waiting for Matrix..."
    sleep 5
done
echo "✓ Matrix is ready"

# Start Ollama if not running
echo "Checking Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    /opt/homebrew/bin/ollama serve &
    sleep 5
fi
echo "✓ Ollama is ready"

# Start Zemi
echo "Starting Zemi orchestrator..."
cd /Users/zemi/ZemiV1/core
source ../venv/bin/activate
python zemi_main.py >> /Users/zemi/ZemiV1/logs/zemi_startup.log 2>&1
