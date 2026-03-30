#!/usr/bin/env python3
"""
Scrape AppsRunTheWorld for Navision/ERP users
https://appsruntheworld.com/ has databases of ERP users
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

# AppsRunTheWorld Navision liste
URLS = [
    "https://appsruntheworld.com/microsoft-dynamics-nav-customers",
    "https://appsruntheworld.com/dynamics-nav-case-studies",
]

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def scrape_appsruntheworld():
    """Scrape AppsRunTheWorld for Navision customers"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter AppsRunTheWorld scrape...")
    print("=" * 80)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    companies_added = 0
    
    for url in URLS:
        print(f"\n📄 Scraping: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"  ❌ Status: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find tabel med virksomheder
            tables = soup.find_all('table')
            print(f"  📊 Fundet {len(tables)} tabeller")
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        company = cols[0].get_text(strip=True)
                        country = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                        
                        if company and len(company) > 3:
                            # Tjek om allerede i DB
                            cur.execute('SELECT id FROM companies WHERE company_name = ? AND source = ?', 
                                      (company, 'appsruntheworld'))
                            if not cur.fetchone():
                                # Indsæt
                                cur.execute('''
                                    INSERT INTO companies 
                                    (company_name, country, evidence_type, evidence_text, 
                                     confidence_score, source, source_url, discovered_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    company,
                                    country,
                                    'appsruntheworld_database',
                                    f'Listed on AppsRunTheWorld as Microsoft Dynamics NAV customer',
                                    4,  # Høj kvalitet - manuelt verificeret database
                                    'appsruntheworld',
                                    url,
                                    datetime.utcnow().isoformat() + 'Z'
                                ))
                                companies_added += 1
                                print(f"  ✅ {company} ({country})")
            
            conn.commit()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ Tilføjet {companies_added} virksomheder fra AppsRunTheWorld")
    
    return companies_added

if __name__ == '__main__':
    try:
        scrape_appsruntheworld()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
