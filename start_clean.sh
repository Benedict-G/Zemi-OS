#!/bin/bash
echo "Killing all Zemi instances..."
pkill -9 -f zemi_main 2>/dev/null
sleep 2
echo "Cleaning up screen sessions..."
screen -wipe > /dev/null 2>&1
echo "Starting fresh Zemi instance..."
cd ~/ZemiV1
source venv/bin/activate
screen -dmS zemi bash -c "python core/zemi_main.py; exec bash"
sleep 2
echo "? Zemi started in background"
screen -ls
