#!/bin/bash 
# Zemi Goose Controller 
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null) 

case "$1" in
    start)
        echo "?? Starting Goose web server..." 
        echo "?? Connect from iPad Safari: http://$IP:3000" 
        echo "??  Press Ctrl+C to stop" 
        goose web --port 3000 
        ;;
    local)
        echo "??? Starting local Goose session..." 
        goose session start 
        ;;
    *)
        echo "Zemi Goose Control" 
        echo "  start - Start web server for iPad browser access" 
        echo "  local - Start local terminal session" 
        ;;
esac
