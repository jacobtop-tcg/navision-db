#!/usr/bin/env python3
"""
Generate standalone HTML dashboard for here.now upload
"""

import sqlite3
from datetime import datetime
import json

DB_PATH = '/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db'

def get_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Total
    cursor.execute("SELECT COUNT(*) as count FROM companies")
    total = cursor.fetchone()['count']
    
    # Top countries
    cursor.execute("SELECT country, COUNT(*) as count FROM companies GROUP BY country ORDER BY count DESC LIMIT 10")
    countries = [{'name': r['country'], 'count': r['count']} for r in cursor.fetchall()]
    
    # Top industries
    cursor.execute("SELECT industry, COUNT(*) as count FROM companies GROUP BY industry ORDER BY count DESC LIMIT 10")
    industries = [{'name': r['industry'], 'count': r['count']} for r in cursor.fetchall()]
    
    # Recent companies
    cursor.execute("SELECT company_name, country, industry, confidence_score, source FROM companies ORDER BY discovered_at DESC LIMIT 50")
    recent = [{'name': r['company_name'], 'country': r['country'], 'industry': r['industry'], 'confidence': r['confidence_score'], 'source': r['source']} for r in cursor.fetchall()]
    
    # Sources
    cursor.execute("SELECT source, COUNT(*) as count FROM companies GROUP BY source ORDER BY count DESC")
    sources = [{'name': r['source'], 'count': r['count']} for r in cursor.fetchall()]
    
    conn.close()
    
    return {
        'total': total,
        'countries': countries,
        'industries': industries,
        'recent': recent,
        'sources': sources,
        'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

HTML = """
<!DOCTYPE html>
<html lang="da">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 NAV Database Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(0,150,255,0.5);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .stat-number {
            font-size: 3em;
            font-weight: bold;
            color: #00d4ff;
            text-shadow: 0 0 20px rgba(0,212,255,0.5);
        }
        .stat-label { font-size: 1.1em; color: #aaa; margin-top: 10px; }
        .section {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .section h2 { margin-bottom: 20px; color: #00d4ff; font-size: 1.5em; }
        .country-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        .country-item {
            background: rgba(255,255,255,0.08);
            padding: 15px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .country-flag { font-size: 1.5em; margin-right: 10px; }
        .country-count {
            background: #00d4ff;
            color: #000;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        th { background: rgba(0,212,255,0.2); color: #00d4ff; font-weight: 600; }
        tr:hover { background: rgba(255,255,255,0.05); }
        .confidence {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .conf-5 { background: #00ff88; color: #000; }
        .conf-4 { background: #00d4ff; color: #000; }
        .conf-3 { background: #ffaa00; color: #000; }
        .refresh-info { text-align: center; color: #666; margin-top: 30px; font-size: 0.9em; }
        .last-updated { text-align: center; color: #00d4ff; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 NAV Database Dashboard</h1>
        <div class="last-updated">Sidst opdateret: <span id="updated">-</span></div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="total">0</div>
                <div class="stat-label">Samlet Antal</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="countries-count">0</div>
                <div class="stat-label">Lande</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="industries-count">0</div>
                <div class="stat-label">Industrier</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="avg-conf">0</div>
                <div class="stat-label">Avg Confidence</div>
            </div>
        </div>

        <div class="section">
            <h2>🌍 Top Lande</h2>
            <div class="country-grid" id="countries"></div>
        </div>

        <div class="section">
            <h2>🏭 Top Industrier</h2>
            <table><thead><tr><th>Industri</th><th>Antal</th></tr></thead><tbody id="industries"></tbody></table>
        </div>

        <div class="section">
            <h2>🆕 Seneste 50</h2>
            <table><thead><tr><th>Virksomhed</th><th>Land</th><th>Industri</th><th>Conf</th><th>Kilde</th></tr></thead><tbody id="recent"></tbody></table>
        </div>

        <div class="section">
            <h2>📊 Kilder</h2>
            <table><thead><tr><th>Kilde</th><th>Antal</th></tr></thead><tbody id="sources"></tbody></table>
        </div>

        <div class="refresh-info">🔄 Daemon kører 24/7 • Opdateret hvert minut</div>
    </div>

    <script>
        const data = DATA_PLACEHOLDER;
        
        document.getElementById('total').textContent = data.total;
        document.getElementById('countries-count').textContent = data.countries.length;
        document.getElementById('industries-count').textContent = data.industries.length;
        document.getElementById('updated').textContent = data.updated;
        
        // Calculate avg confidence
        let totalConf = 0;
        data.recent.forEach(r => totalConf += r.confidence);
        document.getElementById('avg-conf').textContent = (totalConf / data.recent.length).toFixed(1);
        
        // Countries
        const flags = {'DK':'🇩🇰','US':'🇺🇸','GB':'🇬🇧','DE':'🇩🇪','NL':'🇳🇱','SE':'🇸🇪','NO':'🇳🇴','FI':'🇫🇮','BE':'🇧🇪','FR':'🇫🇷','ES':'🇪🇸','IT':'🇮🇹','CH':'🇨🇭','AT':'🇦🇹','PL':'🇵🇱','CA':'🇨🇦','AU':'🇦🇺','IN':'🇮🇳','JP':'🇯🇵','CN':'🇨🇳','SG':'🇸🇬','NZ':'🇳🇿','IE':'🇮🇪','PT':'🇵🇹','GR':'🇬🇷','CZ':'🇨🇿','HU':'🇭🇺','RO':'🇷🇴','BG':'🇧🇬','HR':'🇭🇷','SK':'🇸🇰','SI':'🇸🇮','LT':'🇱🇹','LV':'🇱🇻','EE':'🇪🇪','MX':'🇲🇽','BR':'🇧🇷','AR':'🇦🇷','CL':'🇨🇱','CO':'🇨🇴','ZA':'🇿🇦','AE':'🇦🇪','SA':'🇸🇦','IL':'🇮🇱','TR':'🇹🇷','RU':'🇷🇺','UA':'🇺🇦','TH':'🇹🇭','MY':'🇲🇾','ID':'🇮🇩','PH':'🇵🇭','VN':'🇻🇳','KR':'🇰🇷','TW':'🇹🇼','HK':'🇭🇰','XX':'🌍','EU':'🇪🇺','LU':'🇱🇺','QA':'🇶🇦'};
        document.getElementById('countries').innerHTML = data.countries.map(c => 
            `<div class="country-item"><span><span class="country-flag">${flags[c.name]||'🌍'}</span>${c.name}</span><span class="country-count">${c.count}</span></div>`
        ).join('');
        
        // Industries
        document.getElementById('industries').innerHTML = data.industries.map(i => 
            `<tr><td>${i.name}</td><td><strong>${i.count}</strong></td></tr>`
        ).join('');
        
        // Recent
        document.getElementById('recent').innerHTML = data.recent.map(r => 
            `<tr><td><strong>${r.name}</strong></td><td>${r.country}</td><td>${r.industry}</td><td><span class="confidence conf-${r.confidence}">${r.confidence}/5</span></td><td>${r.source}</td></tr>`
        ).join('');
        
        // Sources
        document.getElementById('sources').innerHTML = data.sources.map(s => 
            `<tr><td>${s.name}</td><td><strong>${s.count}</strong></td></tr>`
        ).join('');
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    data = get_data()
    html = HTML.replace('DATA_PLACEHOLDER', json.dumps(data))
    
    with open('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-database-live.html', 'w') as f:
        f.write(html)
    
    print(f"✅ HTML genereret! {len(html)} bytes")
    print(f"📊 Total: {data['total']} virksomheder")
    print(f"📁 Fil: navision-database-live.html")
