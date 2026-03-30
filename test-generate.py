#!/usr/bin/env python3
"""Generate HTML locally first to verify size"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) as count FROM companies")
total = cursor.fetchone()['count']

cursor.execute("SELECT company_name, country, industry, confidence_score, source FROM companies ORDER BY discovered_at DESC")
all_companies = cursor.fetchall()

conn.close()

print(f"Total companies: {total}")
print(f"Companies in list: {len(all_companies)}")

# Generate simple HTML
html = f"""<!DOCTYPE html>
<html>
<head><title>NAV Database - {total} Virksomheder</title>
<style>body{{font-family:sans-serif;padding:20px;background:#1a1a2e;color:#fff}}</style>
</head>
<body>
<h1>🚀 NAV Database - HELE DATABASEN</h1>
<p><strong>Total:</strong> {total} virksomheder</p>
<p><strong>Genereret:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<table border="1" style="width:100%;border-collapse:collapse;margin-top:20px;">
<thead><tr><th>Navn</th><th>Land</th><th>Industri</th><th>Conf</th><th>Kilde</th></tr></thead>
<tbody>
"""

for c in all_companies:
    html += f"<tr><td>{c['company_name']}</td><td>{c['country']}</td><td>{c['industry']}</td><td>{c['confidence_score']}</td><td>{c['source']}</td></tr>\n"

html += """</tbody></table>
</body></html>"""

# Save to file
output_path = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/test-full-database.html')
with open(output_path, 'w') as f:
    f.write(html)

print(f"HTML fil størrelse: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
print(f"Fil gemt: {output_path}")
print(f"Antal <tr> tags: {html.count('<tr>')}")
