#!/bin/bash
# Auto-export script - kører hvert 5. minut
# Exporterer SQLite database til JSON for web dashboard

set -e

cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting auto-export..."

# Kør export script
python3 scripts/export-for-web.py

# Gem timestamp
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > state/last-export.txt

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Export complete!"
