#!/usr/bin/env python3
"""
Generate page showing ALL verified NAV companies from job postings + profiles
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get job posting verified
cursor.execute("SELECT * FROM nav_job_postings ORDER BY confidence_score DESC")
job_postings = cursor.fetchall()

# Get verified customers
cursor.execute("SELECT * FROM verified_nav_customers ORDER BY revenue DESC")
verified_customers = cursor.fetchall()

conn.close()

html = f'''<!DOCTYPE html>
<html lang="da">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 NAV MIGRATION TARGETS - Verificerede Virksomheder</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f1a;
            color: #fff;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ 
            text-align: center; 
            margin-bottom: 10px; 
            font-size: 2.5em;
            color: #00ff88;
        }}
        .subtitle {{
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 50px;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #00ff88;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .stats {{ 
            display: flex; 
            gap: 20px; 
            margin-bottom: 30px; 
            flex-wrap: wrap;
        }}
        .stat {{ 
            background: #1a1a2e; 
            padding: 20px 30px; 
            border-radius: 10px;
            border: 2px solid #00ff88;
        }}
        .stat-value {{ font-size: 2em; color: #00ff88; font-weight: bold; }}
        .stat-label {{ color: #888; margin-top: 5px; }}
        
        .company-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }}
        .company-card {{
            background: #1a1a2e;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #00ff88;
        }}
        .company-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        }}
        .company-meta {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}
        .meta-tag {{
            background: #2a2a4e;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
        }}
        .proof {{
            background: #0f0f1a;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.9em;
            color: #ccc;
            margin-top: 10px;
        }}
        .proof-label {{
            color: #00ff88;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .urgent {{
            border-left-color: #ff6600;
            background: linear-gradient(135deg, rgba(255,102,0,0.1) 0%, #1a1a2e 100%);
        }}
        .urgent-badge {{
            display: inline-block;
            background: #ff6600;
            color: #000;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: bold;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 NAV MIGRATION TARGETS</h1>
        <p class="subtitle">Virksomheder der BEVISLIGT bruger Microsoft Dynamics NAV - perfekte emner til Business Central migration</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(job_postings)}</div>
                <div class="stat-label">🔥 Job Postings (Lige nu!)</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(verified_customers)}</div>
                <div class="stat-label">⭐ Verificerede Kunder</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(job_postings) + len(verified_customers)}</div>
                <div class="stat-label">📊 Total Verificerede</div>
            </div>
        </div>

        <!-- JOB POSTINGS - HOTTEST LEADS -->
        <div class="section">
            <h2 class="section-title">🔥 AKTIVE JOB POSTINGS - HØJESTE PRIORITET</h2>
            <p style="color: #888; margin-bottom: 20px;">
                Disse virksomheder søger LIGE NU efter NAV-folk! De bruger NAV i dag og er perfekte migrationsemner.
            </p>
            <div class="company-grid">
'''

for c in job_postings:
    html += f'''
                <div class="company-card urgent">
                    <span class="urgent-badge">🔥 HØJ PRIORITET</span>
                    <div class="company-name">{c['company_name']}</div>
                    <div class="company-meta">
                        <span class="meta-tag">🌍 {c['country']}</span>
                        <span class="meta-tag">🏭 {c['industry']}</span>
                        <span class="meta-tag">⭐ {c['confidence_score']}/5</span>
                    </div>
                    <div class="proof">
                        <div class="proof-label">📋 BEVIS:</div>
                        {c['proof']}
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 0.85em;">
                        📊 Kilde: {c['source']}
                    </div>
                </div>
'''

html += '''
            </div>
        </div>

        <!-- VERIFIED CUSTOMERS -->
        <div class="section">
            <h2 class="section-title">⭐ VERIFICEREDE NAV-KUNDER</h2>
            <p style="color: #888; margin-bottom: 20px;">
                Store virksomheder med offentlige beviser for NAV-brug (case studies, kundelister, etc.)
            </p>
            <div class="company-grid">
'''

for c in verified_customers:
    html += f'''
                <div class="company-card">
                    <div class="company-name">{c['company_name']}</div>
                    <div class="company-meta">
                        <span class="meta-tag">🌍 {c['country']}</span>
                        <span class="meta-tag">🏭 {c['industry']}</span>
                        {f'<span class="meta-tag">👥 {c["employee_count"]}</span>' if c['employee_count'] else ''}
                    </div>
                    <div class="proof">
                        <div class="proof-label">📋 BEVIS:</div>
                        {c['proof']}
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 0.85em;">
                        📊 Kilde: {c['source']}
                    </div>
                </div>
'''

html += '''
            </div>
        </div>
    </div>
</body>
</html>
'''

# Save to file
output_path = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/nav-targets.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Generated NAV targets page!")
print(f"🔥 Job postings: {len(job_postings)}")
print(f"⭐ Verified customers: {len(verified_customers)}")
print(f"📊 Total: {len(job_postings) + len(verified_customers)}")
print(f"📁 File: {output_path}")
print(f"📏 Size: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
