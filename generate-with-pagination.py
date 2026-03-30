#!/usr/bin/env python3
"""
Generate COMPLETE database with pagination, advanced filtering, and sorting
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) as count FROM companies")
total = cursor.fetchone()['count']

cursor.execute("SELECT DISTINCT country FROM companies ORDER BY country")
countries = [r['country'] for r in cursor.fetchall()]

cursor.execute("SELECT DISTINCT industry FROM companies WHERE industry IS NOT NULL AND industry != '' ORDER BY industry")
industries = [r['industry'] for r in cursor.fetchall()]

cursor.execute("SELECT company_name, country, industry, confidence_score, source, discovered_at FROM companies ORDER BY discovered_at DESC")
all_companies = cursor.fetchall()

conn.close()

# Convert to JSON for JavaScript
companies_json = json.dumps([dict(c) for c in all_companies])

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
        
        .filters {{ 
            background: #1a1a2e;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }}
        .filters h3 {{ margin-bottom: 15px; color: #00d4ff; }}
        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .filter-group {{ }}
        .filter-group label {{ display: block; margin-bottom: 5px; color: #888; font-size: 0.9em; }}
        .filter-group input, .filter-group select {{
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #333;
            border-radius: 6px;
            background: #0f0f1a;
            color: #fff;
            font-size: 14px;
        }}
        .filter-group input:focus, .filter-group select:focus {{
            outline: none;
            border-color: #00d4ff;
        }}
        .filter-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        button {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }}
        .btn-primary {{ background: #00d4ff; color: #000; }}
        .btn-primary:hover {{ background: #00a8cc; }}
        .btn-secondary {{ background: #333; color: #fff; }}
        .btn-secondary:hover {{ background: #444; }}
        
        .results-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            color: #888;
        }}
        
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
            white-space: nowrap;
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
        
        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .pagination button {{
            min-width: 40px;
        }}
        .pagination .active {{
            background: #00d4ff;
            color: #000;
        }}
        .pagination select {{
            padding: 8px 15px;
            background: #1a1a2e;
            color: #fff;
            border: 1px solid #333;
            border-radius: 6px;
        }}
        
        .sort-indicator {{ margin-left: 5px; opacity: 0.5; }}
        .sort-indicator.active {{ opacity: 1; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 NAV Database - {total:,} Virksomheder</h1>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total:,}</div>
                <div class="stat-label">Virksomheder</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(countries)}</div>
                <div class="stat-label">Lande</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(industries)}</div>
                <div class="stat-label">Industrier</div>
            </div>
            <div class="stat">
                <div class="stat-value">{datetime.now().strftime('%H:%M')}</div>
                <div class="stat-label">Opdateret</div>
            </div>
        </div>

        <div class="filters">
            <h3>🔍 Filtrering</h3>
            <div class="filter-grid">
                <div class="filter-group">
                    <label>Søg i alle felter</label>
                    <input type="text" id="searchText" placeholder="Søg efter navn, land...">
                </div>
                <div class="filter-group">
                    <label>Land</label>
                    <select id="filterCountry">
                        <option value="">Alle lande ({len(countries)})</option>
                        {''.join(f'<option value="{c}">{c}</option>' for c in countries)}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Industri</label>
                    <select id="filterIndustry">
                        <option value="">Alle industrier ({len(industries)})</option>
                        {''.join(f'<option value="{i}">{i}</option>' for i in industries)}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Confidence</label>
                    <select id="filterConf">
                        <option value="">Alle</option>
                        <option value="5">⭐⭐⭐⭐⭐ (5/5)</option>
                        <option value="4">⭐⭐⭐⭐ (4/5)</option>
                        <option value="3">⭐⭐⭐ (3/5)</option>
                        <option value="2">⭐⭐ (2/5)</option>
                        <option value="1">⭐ (1/5)</option>
                    </select>
                </div>
            </div>
            <div class="filter-actions">
                <button class="btn-primary" onclick="applyFilters()">🔍 Anvend filtre</button>
                <button class="btn-secondary" onclick="resetFilters()">↺ Nulstil</button>
                <span id="resultCount" style="margin-left: auto; align-self: center;"></span>
            </div>
        </div>

        <div class="results-info">
            <span id="showingInfo">Viser 0-0 af 0</span>
            <span id="sortInfo"></span>
        </div>

        <table id="companyTable">
            <thead>
                <tr>
                    <th onclick="sortTable('company_name')">Virksomhed <span class="sort-indicator" id="sort-company_name">↕</span></th>
                    <th onclick="sortTable('country')">Land <span class="sort-indicator" id="sort-country">↕</span></th>
                    <th onclick="sortTable('industry')">Industri <span class="sort-indicator" id="sort-industry">↕</span></th>
                    <th onclick="sortTable('confidence_score')">Conf <span class="sort-indicator" id="sort-confidence_score">↕</span></th>
                    <th onclick="sortTable('source')">Kilde <span class="sort-indicator" id="sort-source">↕</span></th>
                    <th onclick="sortTable('discovered_at')">Dato <span class="sort-indicator" id="sort-discovered_at">↕</span></th>
                </tr>
            </thead>
            <tbody id="tableBody">
            </tbody>
        </table>

        <div class="pagination">
            <button class="btn-secondary" onclick="changePage(-1)">← Forrige</button>
            <span id="pageInfo" style="min-width: 120px; text-align: center;">Side 1 af 1</span>
            <button class="btn-secondary" onclick="changePage(1)">Næste →</button>
            <select id="pageSize" onchange="changePageSize()">
                <option value="50">50 pr. side</option>
                <option value="100" selected>100 pr. side</option>
                <option value="200">200 pr. side</option>
                <option value="500">500 pr. side</option>
            </select>
        </div>
    </div>
    
    <script>
    // All companies data
    const allCompanies = {companies_json};
    
    // State
    let filteredCompanies = [...allCompanies];
    let currentPage = 1;
    let pageSize = 100;
    let currentSort = {{ column: 'discovered_at', direction: 'desc' }};
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {{
        applyFilters();
    }});
    
    // Filter function
    function applyFilters() {{
        const searchText = document.getElementById('searchText').value.toLowerCase();
        const country = document.getElementById('filterCountry').value;
        const industry = document.getElementById('filterIndustry').value;
        const conf = document.getElementById('filterConf').value;
        
        filteredCompanies = allCompanies.filter(c => {{
            // Text search
            if (searchText) {{
                const textMatch = 
                    c.company_name.toLowerCase().includes(searchText) ||
                    c.country.toLowerCase().includes(searchText) ||
                    (c.industry && c.industry.toLowerCase().includes(searchText)) ||
                    (c.source && c.source.toLowerCase().includes(searchText));
                if (!textMatch) return false;
            }}
            // Country filter
            if (country && c.country !== country) return false;
            // Industry filter
            if (industry && c.industry !== industry) return false;
            // Confidence filter
            if (conf && c.confidence_score != conf) return false;
            
            return true;
        }});
        
        // Sort
        sortData();
        
        // Reset to page 1
        currentPage = 1;
        
        // Update UI
        updateTable();
        updateResultCount();
    }}
    
    function resetFilters() {{
        document.getElementById('searchText').value = '';
        document.getElementById('filterCountry').value = '';
        document.getElementById('filterIndustry').value = '';
        document.getElementById('filterConf').value = '';
        applyFilters();
    }}
    
    function sortData() {{
        const {{ column, direction }} = currentSort;
        filteredCompanies.sort((a, b) => {{
            let aVal = a[column] || '';
            let bVal = b[column] || '';
            
            // Handle confidence scores as numbers
            if (column === 'confidence_score') {{
                aVal = Number(aVal);
                bVal = Number(bVal);
            }}
            
            if (aVal < bVal) return direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            return 0;
        }});
    }}
    
    function sortTable(column) {{
        if (currentSort.column === column) {{
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        }} else {{
            currentSort.column = column;
            currentSort.direction = 'asc';
        }}
        
        // Update sort indicators
        document.querySelectorAll('.sort-indicator').forEach(el => {{
            el.classList.remove('active');
            el.textContent = '↕';
        }});
        const activeIndicator = document.getElementById(`sort-${{column}}`);
        if (activeIndicator) {{
            activeIndicator.classList.add('active');
            activeIndicator.textContent = currentSort.direction === 'asc' ? '↑' : '↓';
        }}
        
        document.getElementById('sortInfo').textContent = `Sorteret: ${{column}} (${{currentSort.direction === 'asc' ? 'A-Å' : 'Å-A'}})`;
        
        sortData();
        updateTable();
    }}
    
    function updateTable() {{
        const tbody = document.getElementById('tableBody');
        const start = (currentPage - 1) * pageSize;
        const end = Math.min(start + pageSize, filteredCompanies.length);
        const pageData = filteredCompanies.slice(start, end);
        
        tbody.innerHTML = pageData.map(c => `
            <tr>
                <td><strong>${{c.company_name}}</strong></td>
                <td>${{c.country}}</td>
                <td>${{c.industry || '-'}}</td>
                <td><span class="conf conf-${{c.confidence_score}}">${{c.confidence_score}}/5</span></td>
                <td>${{c.source || '-'}}</td>
                <td>${{c.discovered_at ? c.discovered_at.substring(0, 10) : '-'}}</td>
            </tr>
        `).join('');
        
        // Update pagination
        const totalPages = Math.ceil(filteredCompanies.length / pageSize);
        document.getElementById('pageInfo').textContent = `Side ${{currentPage}} af ${{totalPages || 1}}`;
        document.getElementById('showingInfo').textContent = `Viser ${{start + 1}}-${{end}} af ${{filteredCompanies.length}}`;
    }}
    
    function changePage(delta) {{
        const totalPages = Math.ceil(filteredCompanies.length / pageSize);
        const newPage = currentPage + delta;
        if (newPage >= 1 && newPage <= totalPages) {{
            currentPage = newPage;
            updateTable();
        }}
    }}
    
    function changePageSize() {{
        pageSize = parseInt(document.getElementById('pageSize').value);
        currentPage = 1;
        updateTable();
    }}
    
    function updateResultCount() {{
        document.getElementById('resultCount').textContent = `📊 ${{filteredCompanies.length}} resultater`;
    }}
    </script>
</body>
</html>'''

# Save to file
output_path = Path('/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database-with-filters.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Generated database with pagination & filters!")
print(f"📊 Total companies: {total:,}")
print(f"📁 File: {output_path}")
print(f"📏 Size: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
