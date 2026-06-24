#!/bin/bash
echo "[start.sh] Killing old bot instances..."
pkill -9 -f "python main.py" 2>/dev/null || true
sleep 4
echo "[start.sh] Starting FITNESS AI BOT..."
cd "$(dirname "$0")"
exec python main.py
