#!/usr/bin/env python3
"""
Export Navision Database to JSON for Web Dashboard
Kører automatisk hvert 5. minut via daemon
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'
EXPORT_DIR = SCRIPT_DIR.parent / 'web-export'
EXPORT_JSON = EXPORT_DIR / 'companies.json'
EXPORT_META = EXPORT_DIR / 'metadata.json'

# Sikr export mappe eksisterer
EXPORT_DIR.mkdir(exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def export_companies():
    """Exporter alle virksomheder til JSON"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter export...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Hent alle virksomheder
    cur.execute('''
        SELECT 
            company_name,
            country,
            industry,
            evidence_type,
            evidence_text,
            confidence_score,
            source,
            website,
            source_url,
            discovered_at,
            employees,
            headquarters_address,
            linkedin_url
        FROM companies
        ORDER BY confidence_score DESC, discovered_at DESC
    ''')
    
    rows = cur.fetchall()
    
    # Konverter til liste af dicts
    companies = []
    for row in rows:
        companies.append({
            'name': row['company_name'],
            'country': row['country'],
            'industry': row['industry'] or '',
            'evidence_type': row['evidence_type'] or '',
            'evidence': row['evidence_text'] or '',
            'confidence': row['confidence_score'],
            'source': row['source'] or '',
            'website': row['website'] or '',
            'source_url': row['source_url'] or '',
            'discovered': row['discovered_at'] or '',
            'employees': row['employees'] or '',
            'address': row['headquarters_address'] or '',
            'linkedin': row['linkedin_url'] or ''
        })
    
    # Hent statistik
    cur.execute('SELECT COUNT(*) FROM companies')
    total = cur.fetchone()[0]
    
    cur.execute('SELECT confidence_score, COUNT(*) FROM companies GROUP BY confidence_score ORDER BY confidence_score DESC')
    by_confidence = {str(row[0]): row[1] for row in cur.fetchall()}
    
    cur.execute('SELECT country, COUNT(*) FROM companies GROUP BY country ORDER BY COUNT(*) DESC LIMIT 20')
    top_countries = {row[0]: row[1] for row in cur.fetchall()}
    
    cur.execute('SELECT source, COUNT(*) FROM companies GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10')
    top_sources = {row[0]: row[1] for row in cur.fetchall()}
    
    cur.execute('SELECT MIN(discovered_at), MAX(discovered_at) FROM companies')
    date_range = cur.fetchone()
    
    conn.close()
    
    # Lav metadata
    metadata = {
        'total_companies': total,
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'by_confidence': by_confidence,
        'top_countries': top_countries,
        'top_sources': top_sources,
        'date_range': {
            'first': date_range[0] or 'N/A',
            'latest': date_range[1] or 'N/A'
        }
    }
    
    # Gem JSON filer
    with open(EXPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    
    with open(EXPORT_META, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Lav også CSV for nem download
    df = pd.DataFrame(companies)
    csv_path = EXPORT_DIR / 'companies.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"[{datetime.utcnow().isoformat()}Z] Export færdig!")
    print(f"  Total: {total} virksomheder")
    print(f"  JSON: {EXPORT_JSON}")
    print(f"  CSV: {csv_path}")
    print(f"  Meta: {EXPORT_META}")
    
    return total

if __name__ == '__main__':
    try:
        export_companies()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
