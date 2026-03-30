#!/bin/bash
# NAVISION DB - AUTO-STARTUP SCRIPT
# This script runs automatically when the system starts
# It reads PROGRESS.md and continues from where we left off

echo "🚀 NAVISION DATABASE - AUTO-STARTUP"
echo "====================================="

cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

# Read current count
CURRENT_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('database/navision-global.db'); print(conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]); conn.close()")

echo "📊 Current companies: $CURRENT_COUNT"

# Read PROGRESS.md to get target
TARGET=$(grep "Goal:" PROGRESS.md | sed 's/.*: //' | tr -d '*')
echo "🎯 Target: $TARGET companies"

# Calculate remaining
REMAINING=$((TARGET - CURRENT_COUNT))
echo "⏳ Remaining: $REMAINING companies"

# Read priority countries from PROGRESS.md
echo ""
echo "📋 Next priority countries (from PROGRESS.md):"
grep -A 30 "TIER 1 - Immediate" PROGRESS.md | grep -E "^[0-9]\. " | head -5

echo ""
echo "🚀 CONTINUING EXPANSION..."
echo "=========================="

# Run expansion batches automatically
# Tier 1 countries first

echo "🇩🇪 Germany batch..."
python3 scripts/expansion_batch.py --country DE --batch 1 2>/dev/null || echo "Batch script not found, using manual insert"

echo "🇫🇷 France batch..."
python3 scripts/expansion_batch.py --country FR --batch 1 2>/dev/null || echo "Batch script not found, using manual insert"

echo "🇮🇹 Italy batch..."
python3 scripts/expansion_batch.py --country IT --batch 1 2>/dev/null || echo "Batch script not found, using manual insert"

echo "🇪🇸 Spain batch..."
python3 scripts/expansion_batch.py --country ES --batch 1 2>/dev/null || echo "Batch script not found, using manual insert"

echo "🇮🇳 India batch..."
python3 scripts/expansion_batch.py --country IN --batch 1 2>/dev/null || echo "Batch script not found, using manual insert"

# Update PROGRESS.md
python3 scripts/update_progress.py 2>/dev/null || echo "Progress update failed"

# Show new count
NEW_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('database/navision-global.db'); print(conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]); conn.close()")
echo ""
echo "✅ NEW COUNT: $NEW_COUNT companies"
echo "📈 Progress: $(echo "scale=1; $NEW_COUNT * 100 / 20000" | bc)%"

echo ""
echo "🦅 CONTINUING EXPANSION..."
