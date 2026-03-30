#!/usr/bin/env python3
"""
Auto-upload NAV database to here.now every minute
Shows ALL companies with search functionality
"""

import sqlite3
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

DB_PATH = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')
API_KEY = '467d824a26824b6d6aa2745e18ac76b599e0a11eec3f9a1cdd1f231eab4902b4'
HERE_NOW_API = 'https://here.now/api/v1/publish'
SLUG = 'astral-kernel-4cf3'

FLAGS = {'DK':'🇩🇰','US':'🇺🇸','GB':'🇬🇧','DE':'🇩🇪','NL':'🇳🇱','SE':'🇸🇪','NO':'🇳🇴','FI':'🇫🇮','BE':'🇧🇪','FR':'🇫🇷','ES':'🇪🇸','IT':'🇮🇹','CH':'🇨🇭','AT':'🇦🇹','PL':'🇵🇱','CA':'🇨🇦','AU':'🇦🇺','IN':'🇮🇳','JP':'🇯🇵','CN':'🇨🇳','SG':'🇸🇬','NZ':'🇳🇿','IE':'🇮🇪','PT':'🇵🇹','GR':'🇬🇷','CZ':'🇨🇿','HU':'🇭🇺','RO':'🇷🇴','BG':'🇧🇬','HR':'🇭🇷','SK':'🇸🇰','SI':'🇸🇮','LT':'🇱🇹','LV':'🇱🇻','EE':'🇪🇪','MX':'🇲🇽','BR':'🇧🇷','AR':'🇦🇷','CL':'🇨🇱','CO':'🇨🇴','ZA':'🇿🇦','AE':'🇦🇪','SA':'🇸🇦','IL':'🇮🇱','TR':'🇹🇷','RU':'🇷🇺','UA':'🇺🇦','TH':'🇹🇭','MY':'🇲🇾','ID':'🇮🇩','PH':'🇵🇭','VN':'🇻🇳','KR':'🇰🇷','TW':'🇹🇼','HK':'🇭🇰','XX':'🌍','EU':'🇪🇺','LU':'🇱🇺','QA':'🇶🇦'}

def get_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM companies")
    total = cursor.fetchone()['count']
    
    cursor.execute("SELECT country, COUNT(*) as count FROM companies GROUP BY country ORDER BY count DESC LIMIT 10")
    countries = [{'name': r['country'], 'count': r['count']} for r in cursor.fetchall()]
    
    cursor.execute("SELECT industry, COUNT(*) as count FROM companies GROUP BY industry ORDER BY count DESC LIMIT 10")
    industries = [{'name': r['industry'], 'count': r['count']} for r in cursor.fetchall()]
    
    cursor.execute("SELECT company_name, country, industry, confidence_score, source FROM companies ORDER BY discovered_at DESC")
    all_companies = [{'name': r['company_name'], 'country': r['country'], 'industry': r['industry'], 'confidence': r['confidence_score'], 'source': r['source']} for r in cursor.fetchall()]
    
    cursor.execute("SELECT source, COUNT(*) as count FROM companies GROUP BY source ORDER BY count DESC")
    sources = [{'name': r['source'], 'count': r['count']} for r in cursor.fetchall()]
    
    conn.close()
    
    avg_conf = sum(r['confidence'] for r in all_companies) / len(all_companies) if all_companies else 0
    
    return {
        'total': total,
        'countries': countries,
        'industries': industries,
        'all_companies': all_companies,
        'sources': sources,
        'avg_conf': round(avg_conf, 1),
        'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generate_html(data):
    countries_html = ''.join([f'<div class="country-item"><span><span class="country-flag">{FLAGS.get(c["name"],"🌍")}</span>{c["name"]}</span><span class="country-count">{c["count"]}</span></div>' for c in data['countries']])
    industries_html = ''.join([f'<tr><td>{i["name"]}</td><td><strong>{i["count"]}</strong></td></tr>' for i in data['industries']])
    all_companies_html = ''.join([f'<tr><td><strong>{r["name"]}</strong></td><td>{r["country"]}</td><td>{r["industry"]}</td><td><span class="confidence conf-{r["confidence"]}>{r["confidence"]}/5</span></td><td>{r["source"]}</td></tr>' for r in data['all_companies']])
    sources_html = ''.join([f'<tr><td>{s["name"]}</td><td><strong>{s["count"]}</strong></td></tr>' for s in data['sources']])
    
    return f'''<!DOCTYPE html>
<html lang="da">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 NAV Database Dashboard - HELE DATABASEN</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ text-align: center; margin-bottom: 30px; font-size: 2.5em; text-shadow: 0 0 20px rgba(0,150,255,0.5); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }}
        .stat-number {{ font-size: 3em; font-weight: bold; color: #00d4ff; text-shadow: 0 0 20px rgba(0,212,255,0.5); }}
        .stat-label {{ font-size: 1.1em; color: #aaa; margin-top: 10px; }}
        .section {{ background: rgba(255,255,255,0.05); border-radius: 15px; padding: 25px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.1); }}
        .section h2 {{ margin-bottom: 20px; color: #00d4ff; font-size: 1.5em; }}
        .country-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
        .country-item {{ background: rgba(255,255,255,0.08); padding: 15px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; }}
        .country-flag {{ font-size: 1.5em; margin-right: 10px; }}
        .country-count {{ background: #00d4ff; color: #000; padding: 5px 12px; border-radius: 20px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; overflow-x: auto; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ background: rgba(0,212,255,0.2); color: #00d4ff; font-weight: 600; }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}
        .confidence {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; }}
        .conf-5 {{ background: #00ff88; color: #000; }}
        .conf-4 {{ background: #00d4ff; color: #000; }}
        .conf-3 {{ background: #ffaa00; color: #000; }}
        .refresh-info {{ text-align: center; color: #666; margin-top: 30px; font-size: 0.9em; }}
        .last-updated {{ text-align: center; color: #00d4ff; margin-bottom: 20px; }}
        #search {{ width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; background: rgba(255,255,255,0.1); color: #fff; font-size: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 NAV Database Dashboard - HELE DATABASEN</h1>
        <div class="last-updated">Sidst opdateret: {data['updated']}</div>
        
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-number">{data['total']}</div><div class="stat-label">Samlet Antal</div></div>
            <div class="stat-card"><div class="stat-number">{len(data['countries'])}</div><div class="stat-label">Lande</div></div>
            <div class="stat-card"><div class="stat-number">{len(data['industries'])}</div><div class="stat-label">Industrier</div></div>
            <div class="stat-card"><div class="stat-number">{data['avg_conf']}</div><div class="stat-label">Avg Confidence</div></div>
        </div>

        <div class="section">
            <h2>🌍 Top Lande</h2>
            <div class="country-grid">{countries_html}</div>
        </div>

        <div class="section">
            <h2>🏭 Top Industrier</h2>
            <table><thead><tr><th>Industri</th><th>Antal</th></tr></thead><tbody>{industries_html}</tbody></table>
        </div>

        <div class="section">
            <h2>🏢 HELE DATABASEN - {data['total']} Virksomheder</h2>
            <input type="text" id="search" onkeyup="searchTable()" placeholder="🔍 Søg efter navn, land, industri...">
            <table id="companyTable"><thead><tr><th>Virksomhed</th><th>Land</th><th>Industri</th><th>Conf</th><th>Kilde</th></tr></thead><tbody>{all_companies_html}</tbody></table>
        </div>

        <div class="section">
            <h2>📊 Kilder</h2>
            <table><thead><tr><th>Kilde</th><th>Antal</th></tr></thead><tbody>{sources_html}</tbody></table>
        </div>

        <div class="refresh-info">🔄 Auto-opdateres hvert minut • Daemon kører 24/7 • Viser ALLE {data['total']} virksomheder</div>
    </div>
    
    <script>
    function searchTable() {{
        var input, filter, table, tr, tdName, tdCountry, tdIndustry, txtName, txtCountry, txtIndustry;
        input = document.getElementById("search");
        filter = input.value.toUpperCase();
        table = document.getElementById("companyTable");
        tr = table.getElementsByTagName("tr");
        for (i = 1; i < tr.length; i++) {{
            tdName = tr[i].getElementsByTagName("td")[0];
            tdCountry = tr[i].getElementsByTagName("td")[1];
            tdIndustry = tr[i].getElementsByTagName("td")[2];
            if (tdName || tdCountry || tdIndustry) {{
                txtName = tdName.textContent || tdName.innerText;
                txtCountry = tdCountry.textContent || tdCountry.innerText;
                txtIndustry = tdIndustry.textContent || tdIndustry.innerText;
                if (txtName.toUpperCase().indexOf(filter) > -1 || txtCountry.toUpperCase().indexOf(filter) > -1 || txtIndustry.toUpperCase().indexOf(filter) > -1) {{
                    tr[i].style.display = "";
                }} else {{
                    tr[i].style.display = "none";
                }}
            }}       
        }}
    }}
    </script>
</body>
</html>'''

def upload_to_herenow(html_content):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    files = [{'path': f'navision-database-{timestamp}.html', 'size': len(html_content), 'contentType': 'text/html; charset=utf-8'}]
    
    resp = requests.post(HERE_NOW_API, 
        headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json', 'X-HereNow-Client': 'orion/auto'},
        json={'files': files})
    
    if resp.status_code != 200:
        print(f"❌ Step 1 failed: {resp.text}")
        return False
    
    data = resp.json()
    slug = data['slug']
    upload_info = data['upload']
    
    upload_url = upload_info['uploads'][0]['url']
    resp = requests.put(upload_url, 
        headers={'Content-Type': 'text/html; charset=utf-8'},
        data=html_content.encode('utf-8'))
    
    if resp.status_code != 200:
        print(f"❌ Step 2 failed: {resp.text}")
        return False
    
    resp = requests.post(f"https://here.now/api/v1/publish/{slug}/finalize",
        headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
        json={'versionId': upload_info['versionId']})
    
    if resp.status_code != 200:
        print(f"❌ Step 3 failed: {resp.text}")
        return False
    
    # Get the actual uploaded filename from response
    manifest = resp.json().get('manifest', [])
    uploaded_file = manifest[0]['path'] if manifest else f'navision-database-{timestamp}.html'
    
    print(f"✅ Uploaded to https://{slug}.here.now/{uploaded_file}")
    return True

if __name__ == '__main__':
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] Generating dashboard...")
    data = get_data()
    html = generate_html(data)
    
    print(f"📊 Total: {data['total']} virksomheder (ALLE)")
    print(f"📤 Uploading to here.now...")
    
    if upload_to_herenow(html):
        print(f"✅ Success! Live at: https://astral-kernel-4cf3.here.now/")
    else:
        print("❌ Upload failed!")
