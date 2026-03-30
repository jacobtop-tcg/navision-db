#!/usr/bin/env python3
"""
Generate COMPLETE database HTML with ALL companies + search + sort
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) as count FROM companies")
total = cursor.fetchone()['count']

cursor.execute("SELECT company_name, country, industry, confidence_score, source, discovered_at FROM companies ORDER BY discovered_at DESC")
all_companies = cursor.fetchall()

conn.close()

# Generate HTML with ALL companies
html = f'''<!DOCTYPE html>
<html lang="da">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAV Database - {total} Virksomheder</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f1a;
            color: #fff;
            padding: 20px;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ 
            text-align: center; 
            margin-bottom: 30px; 
            font-size: 2.5em;
            color: #00d4ff;
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
            border: 1px solid #00d4ff;
        }}
        .stat-value {{ font-size: 2em; color: #00d4ff; font-weight: bold; }}
        .stat-label {{ color: #888; margin-top: 5px; }}
        .controls {{ 
            margin-bottom: 20px; 
            display: flex; 
            gap: 10px; 
            flex-wrap: wrap;
        }}
        #search {{ 
            flex: 1; 
            min-width: 300px;
            padding: 12px 20px; 
            border: 2px solid #00d4ff; 
            border-radius: 8px; 
            background: #1a1a2e; 
            color: #fff; 
            font-size: 16px;
        }}
        #search::placeholder {{ color: #666; }}
        .info {{ color: #888; margin-bottom: 20px; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            background: #1a1a2e;
            border-radius: 10px;
            overflow: hidden;
        }}
        th {{ 
            background: #00d4ff; 
            color: #000; 
            padding: 15px; 
            text-align: left;
            cursor: pointer;
            user-select: none;
            font-weight: 600;
        }}
        th:hover {{ background: #00a8cc; }}
        td {{ 
            padding: 12px 15px; 
            border-bottom: 1px solid #2a2a4e;
        }}
        tr:hover {{ background: #2a2a4e; }}
        .conf {{ 
            display: inline-block; 
            padding: 4px 12px; 
            border-radius: 15px; 
            font-size: 0.85em; 
            font-weight: bold;
        }}
        .conf-5 {{ background: #00ff88; color: #000; }}
        .conf-4 {{ background: #00d4ff; color: #000; }}
        .conf-3 {{ background: #ffaa00; color: #000; }}
        .conf-2 {{ background: #ff6600; color: #fff; }}
        .conf-1 {{ background: #ff3333; color: #fff; }}
        .count {{ color: #888; margin-bottom: 10px; }}
        .sort-indicator {{ margin-left: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 NAV Database - HELE DATABASEN</h1>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total:,}</div>
                <div class="stat-label">Virksomheder</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(set(c['country'] for c in all_companies))}</div>
                <div class="stat-label">Lande</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(set(c['industry'] for c in all_companies))}</div>
                <div class="stat-label">Industrier</div>
            </div>
            <div class="stat">
                <div class="stat-value">{datetime.now().strftime('%H:%M')}</div>
                <div class="stat-label">Opdateret</div>
            </div>
        </div>

        <div class="controls">
            <input type="text" id="search" placeholder="🔍 Søg i alle {total:,} virksomheder (navn, land, industri, kilde...)" onkeyup="filterTable()">
        </div>
        
        <div class="count">Viser <span id="visibleCount">{total}</span> af {total:,} virksomheder</div>

        <table id="companyTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Virksomhed <span class="sort-indicator">↕</span></th>
                    <th onclick="sortTable(1)">Land <span class="sort-indicator">↕</span></th>
                    <th onclick="sortTable(2)">Industri <span class="sort-indicator">↕</span></th>
                    <th onclick="sortTable(3)">Conf <span class="sort-indicator">↕</span></th>
                    <th onclick="sortTable(4)">Kilde <span class="sort-indicator">↕</span></th>
                    <th onclick="sortTable(5)">Dato <span class="sort-indicator">↕</span></th>
                </tr>
            </thead>
            <tbody>
'''

for c in all_companies:
    conf_class = f"conf-{c['confidence_score']}"
    html += f'''                <tr>
                    <td><strong>{c['company_name']}</strong></td>
                    <td>{c['country']}</td>
                    <td>{c['industry'] or '-'}</td>
                    <td><span class="conf {conf_class}">{c['confidence_score']}/5</span></td>
                    <td>{c['source'] or '-'}</td>
                    <td>{c['discovered_at'][:10] if c['discovered_at'] else '-'}</td>
                </tr>
'''

html += '''            </tbody>
        </table>
    </div>
    
    <script>
    let sortDirection = [];
    
    function filterTable() {
        var input, filter, table, tr, td, i, j, txtValue, visibleCount = 0;
        input = document.getElementById("search");
        filter = input.value.toUpperCase();
        table = document.getElementById("companyTable");
        tr = table.getElementsByTagName("tr");
        
        for (i = 1; i < tr.length; i++) {
            var showRow = false;
            tds = tr[i].getElementsByTagName("td");
            for (j = 0; j < tds.length; j++) {
                if (tds[j]) {
                    txtValue = tds[j].textContent || tds[j].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        showRow = true;
                        break;
                    }
                }
            }
            tr[i].style.display = showRow ? "" : "none";
            if (showRow) visibleCount++;
        }
        document.getElementById("visibleCount").textContent = visibleCount;
    }
    
    function sortTable(columnIndex) {
        var table, tr, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
        table = document.getElementById("companyTable");
        switching = true;
        dir = sortDirection[columnIndex] === 'asc' ? 'desc' : 'asc';
        sortDirection[columnIndex] = dir;
        
        // Update sort indicators
        var headers = table.getElementsByTagName("th");
        for (var h = 0; h < headers.length; h++) {
            headers[h].querySelector('.sort-indicator').textContent = h === columnIndex ? (dir === 'asc' ? '↑' : '↓') : '↕';
        }
        
        while (switching) {
            switching = false;
            rows = table.rows;
            for (i = 1; i < (rows.length - 1); i++) {
                shouldSwitch = false;
                x = rows[i].getElementsByTagName("TD")[columnIndex];
                y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
                
                var xContent = x.textContent || x.innerText;
                var yContent = y.textContent || y.innerText;
                
                // Handle confidence scores (extract number)
                if (columnIndex === 3) {
                    xContent = xContent.replace('/5', '');
                    yContent = yContent.replace('/5', '');
                }
                
                if (dir === 'asc') {
                    if (xContent.toLowerCase() > yContent.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir === 'desc') {
                    if (xContent.toLowerCase() < yContent.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount ++;
            }
        }
    }
    </script>
</body>
</html>'''

# Save to file
output_path = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/complete-database.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Generated complete database HTML!")
print(f"📊 Total companies: {total:,}")
print(f"📁 File: {output_path}")
print(f"📏 Size: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
print(f"📋 Table rows: {html.count('<tr>') - 1}")  # Subtract header row
