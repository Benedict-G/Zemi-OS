#!/bin/bash
echo "Killing all Zemi instances..."
pkill -9 -f zemi_main
sleep 2
echo "Cleaning up screen sessions..."
screen -wipe > /dev/null 2>&1
echo "Starting fresh Zemi instance..."
cd ~/ZemiV1
source venv/bin/activate
screen -S zemi python core/zemi_main.py
