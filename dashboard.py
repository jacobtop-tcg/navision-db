#!/usr/bin/env python3
"""
NAV Database Live Dashboard
Viser Navision database status i real-time
"""

from flask import Flask, render_template_string
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'navision-global.db')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="da">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAV Database Dashboard</title>
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-number {
            font-size: 3em;
            font-weight: bold;
            color: #00d4ff;
            text-shadow: 0 0 20px rgba(0,212,255,0.5);
        }
        .stat-label {
            font-size: 1.1em;
            color: #aaa;
            margin-top: 10px;
        }
        .section {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .section h2 {
            margin-bottom: 20px;
            color: #00d4ff;
            font-size: 1.5em;
        }
        .country-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
        .country-name { flex: 1; }
        .country-count {
            background: #00d4ff;
            color: #000;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        th {
            background: rgba(0,212,255,0.2);
            color: #00d4ff;
            font-weight: 600;
        }
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
        .conf-2 { background: #ff6600; color: #fff; }
        .conf-1 { background: #ff3333; color: #fff; }
        .refresh-info {
            text-align: center;
            color: #666;
            margin-top: 30px;
            font-size: 0.9em;
        }
        .last-updated {
            text-align: center;
            color: #00d4ff;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 NAV Database Dashboard</h1>
        
        <div class="last-updated">
            Sidst opdateret: {{ last_updated }}
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ total_companies }}</div>
                <div class="stat-label">Samlet Antal Virksomheder</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_countries }}</div>
                <div class="stat-label">Lande</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_industries }}</div>
                <div class="stat-label">Industrier</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ avg_confidence }}</div>
                <div class="stat-label">Gennemsnitlig Confidence</div>
            </div>
        </div>

        <div class="section">
            <h2>🌍 Top 10 Lande</h2>
            <div class="country-grid">
                {% for country in top_countries %}
                <div class="country-item">
                    <span>
                        <span class="country-flag">{{ country.flag }}</span>
                        <span class="country-name">{{ country.name }}</span>
                    </span>
                    <span class="country-count">{{ country.count }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="section">
            <h2>🏭 Top 10 Industrier</h2>
            <table>
                <thead>
                    <tr>
                        <th>Industri</th>
                        <th>Antal</th>
                    </tr>
                </thead>
                <tbody>
                    {% for industry in top_industries %}
                    <tr>
                        <td>{{ industry.name }}</td>
                        <td><strong>{{ industry.count }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>🆕 Seneste 20 Tilføjelser</h2>
            <table>
                <thead>
                    <tr>
                        <th>Virksomhed</th>
                        <th>Land</th>
                        <th>Industri</th>
                        <th>Confidence</th>
                        <th>Kilde</th>
                    </tr>
                </thead>
                <tbody>
                    {% for company in recent_companies %}
                    <tr>
                        <td><strong>{{ company.name }}</strong></td>
                        <td>{{ company.country }}</td>
                        <td>{{ company.industry }}</td>
                        <td><span class="confidence conf-{{ company.confidence }}">{{ company.confidence }}/5</span></td>
                        <td>{{ company.source }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📊 Kilde Fordeling</h2>
            <table>
                <thead>
                    <tr>
                        <th>Kilde</th>
                        <th>Antal</th>
                    </tr>
                </thead>
                <tbody>
                    {% for source in sources %}
                    <tr>
                        <td>{{ source.name }}</td>
                        <td><strong>{{ source.count }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="refresh-info">
            🔄 Opdater siden for at se nyeste data • Daemon kører 24/7
        </div>
    </div>
</body>
</html>
"""

FLAGS = {
    'DK': '🇩🇰', 'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷',
    'NL': '🇳🇱', 'SE': '🇸🇪', 'NO': '🇳🇴', 'FI': '🇫🇮', 'ES': '🇪🇸',
    'IT': '🇮🇹', 'BE': '🇧🇪', 'CH': '🇨🇭', 'AT': '🇦🇹', 'PL': '🇵🇱',
    'CA': '🇨🇦', 'AU': '🇦🇺', 'IN': '🇮🇳', 'JP': '🇯🇵', 'CN': '🇨🇳',
    'SG': '🇸🇬', 'NZ': '🇳🇿', 'IE': '🇮🇪', 'PT': '🇵🇹', 'GR': '🇬🇷',
    'CZ': '🇨🇿', 'HU': '🇭🇺', 'RO': '🇷🇴', 'BG': '🇧🇬', 'HR': '🇭🇷',
    'SK': '🇸🇰', 'SI': '🇸🇮', 'LT': '🇱🇹', 'LV': '🇱🇻', 'EE': '🇪🇪',
    'MX': '🇲🇽', 'BR': '🇧🇷', 'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴',
    'ZA': '🇿🇦', 'AE': '🇦🇪', 'SA': '🇸🇦', 'IL': '🇮🇱', 'TR': '🇹🇷',
    'RU': '🇷🇺', 'UA': '🇺🇦', 'TH': '🇹🇭', 'MY': '🇲🇾', 'ID': '🇮🇩',
    'PH': '🇵🇭', 'VN': '🇻🇳', 'KR': '🇰🇷', 'TW': '🇹🇼', 'HK': '🇭🇰',
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total companies
    cursor.execute("SELECT COUNT(*) as count FROM companies")
    total_companies = cursor.fetchone()['count']
    
    # Countries count
    cursor.execute("SELECT COUNT(DISTINCT country) as count FROM companies")
    total_countries = cursor.fetchone()['count']
    
    # Industries count
    cursor.execute("SELECT COUNT(DISTINCT industry) as count FROM companies")
    total_industries = cursor.fetchone()['count']
    
    # Average confidence
    cursor.execute("SELECT ROUND(AVG(confidence_score), 1) as avg FROM companies")
    avg_confidence = cursor.fetchone()['avg'] or 0
    
    # Top countries
    cursor.execute("""
        SELECT country, COUNT(*) as count 
        FROM companies 
        GROUP BY country 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_countries = []
    for row in cursor.fetchall():
        country = row['country']
        flag = FLAGS.get(country, '🌍')
        top_countries.append({
            'name': country,
            'count': row['count'],
            'flag': flag
        })
    
    # Top industries
    cursor.execute("""
        SELECT industry, COUNT(*) as count 
        FROM companies 
        GROUP BY industry 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_industries = [{'name': row['industry'], 'count': row['count']} 
                      for row in cursor.fetchall()]
    
    # Recent companies
    cursor.execute("""
        SELECT company_name, country, industry, confidence_score, source
        FROM companies 
        ORDER BY discovered_at DESC 
        LIMIT 20
    """)
    recent_companies = [{
        'name': row['company_name'],
        'country': row['country'],
        'industry': row['industry'],
        'confidence': row['confidence_score'],
        'source': row['source']
    } for row in cursor.fetchall()]
    
    # Sources
    cursor.execute("""
        SELECT source, COUNT(*) as count 
        FROM companies 
        GROUP BY source 
        ORDER BY count DESC
    """)
    sources = [{'name': row['source'], 'count': row['count']} 
               for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template_string(HTML_TEMPLATE,
        total_companies=total_companies,
        total_countries=total_countries,
        total_industries=total_industries,
        avg_confidence=avg_confidence,
        top_countries=top_countries,
        top_industries=top_industries,
        recent_companies=recent_companies,
        sources=sources,
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starter NAV Dashboard...")
    print(f"📊 Åbn: http://localhost:{port}")
    print("🔄 Dashboard opdateres automatisk ved refresh")
    app.run(host='0.0.0.0', port=port, debug=False)
