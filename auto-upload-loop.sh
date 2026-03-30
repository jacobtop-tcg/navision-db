#!/bin/bash
# Auto-upload loop for here.now dashboard

cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running auto-upload..."
    python3 auto-upload-herenow.py
    echo ""
    sleep 60
done
