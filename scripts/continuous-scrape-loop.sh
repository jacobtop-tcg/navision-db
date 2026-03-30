#!/bin/bash
# Continuous job board scraping loop
# Adds companies to database automatically

cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

echo "🚀 Starting continuous job board scraping..."
echo "💾 Adding companies to database automatically"
echo "📊 Current count: $(python3 -c "import sqlite3; conn=sqlite3.connect('database/navision-global.db'); print(conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]); conn.close()")"
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Running job board scrape..."
    
    # Run scraping scripts
    python3 scripts/add-linkedin-nav-companies.py 2>&1 | tail -5
    
    # Update dashboard
    python3 generate-master-list.py 2>&1 | tail -3
    
    # Upload to here.now
    python3 << 'EOF'
import requests
from pathlib import Path

API_KEY = '467d824a26824b6d6aa2745e18ac76b599e0a11eec3f9a1cdd1f231eab4902b4'

try:
    with open('master-list.html', 'rb') as f:
        content = f.read()
    
    resp = requests.post('https://here.now/api/v1/publish',
        headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
        json={'files': [{'path': 'master.html', 'size': len(content), 'contentType': 'text/html; charset=utf-8'}]})
    
    data = resp.json()
    print(f"✅ Dashboard updated: https://{data['slug']}.here.now/master.html")
except Exception as e:
    print(f"⚠️ Upload skipped: {e}")
EOF
    
    echo ""
    echo "⏳ Waiting 60 seconds before next scrape..."
    echo ""
    sleep 60
done
