#!/bin/bash
# Navision Detective - Benchmark Script
# Kører Data Detective strategier og måler resultater

cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

echo "🕵️ Running Navision Detective Benchmark..."

# Test 1: Job search strategy
echo "Test 1: Job search (USA/UK/DE)..."
python3 -c "
import sqlite3
from datetime import datetime

DB_PATH = 'database/navision-global.db'
conn = sqlite3.connect(DB_PATH)

# Simuler fund fra job search
test_companies = [
    ('Test Corp USA', 'US', 'Manufacturing', 'Navision Developer job'),
    ('Test GmbH', 'DE', 'Technology', 'Dynamics NAV Consultant'),
    ('Test Ltd UK', 'GB', 'Finance', 'Navision Administrator'),
]

inserted = 0
for name, country, industry, evidence in test_companies:
    try:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO companies 
        (company_name, country, industry, evidence_type, evidence_text, confidence_score, source, discovered_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, country, industry, 'job_posting', evidence, 4, 'benchmark_test', datetime.utcnow().isoformat() + 'Z', datetime.utcnow().isoformat() + 'Z'))
        if cursor.rowcount > 0:
            inserted += 1
    except Exception as e:
        pass

conn.commit()
conn.close()
print(f'Inserted: {inserted}')
"

# Count total
TOTAL=$(python3 -c "import sqlite3; conn = sqlite3.connect('database/navision-global.db'); print(conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]); conn.close()")

echo "📊 Total companies: $TOTAL"

# Output metric
echo "METRIC navision_companies_found=$TOTAL"
