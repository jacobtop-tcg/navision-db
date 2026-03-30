#!/usr/bin/env python3
"""
Scrape ALL TheirStack NAV customers (8,345 companies)
Pages 1-835, ~10 companies per page
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import time

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

BASE_URL = "https://theirstack.com/en/technology/microsoft-dynamics-nav"
TOTAL_PAGES = 835

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def scrape_theirstack_all():
    """Scrape all TheirStack pages"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter THEIRSTACK EXPANSION...")
    print("=" * 80)
    print(f"Total pages: {TOTAL_PAGES}")
    print(f"Expected companies: ~8,345")
    print()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    companies_added = 0
    companies_existing = 0
    
    for page in range(1, TOTAL_PAGES + 1):
        url = f"{BASE_URL}?page={page}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"  ❌ Page {page}: {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find company list
            # Based on the page structure, companies are in a table or list
            companies = []
            
            # Try to find company names in the page
            # Looking for patterns like company name + country + industry
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # First column usually has company name with link
                    company_link = row.find('a')
                    if company_link and 'href' in company_link.attrs:
                        company_name = company_link.get_text(strip=True)
                        
                        # Get country from next column or nearby
                        country = ''
                        if len(cols) > 1:
                            country = cols[1].get_text(strip=True)
                        
                        # Get industry
                        industry = ''
                        if len(cols) > 2:
                            industry = cols[2].get_text(strip=True)
                        
                        if company_name and len(company_name) > 2:
                            companies.append({
                                'name': company_name,
                                'country': country,
                                'industry': industry,
                                'url': f"https://theirstack.com/en/technology/microsoft-dynamics-nav?page={page}"
                            })
            
            if companies:
                print(f"  📄 Page {page}: Found {len(companies)} companies")
                
                for comp in companies:
                    # Check if already exists
                    cur.execute('SELECT id FROM companies WHERE company_name = ? AND source = ?', 
                              (comp['name'], 'theirstack'))
                    
                    if cur.fetchone():
                        companies_existing += 1
                    else:
                        # Insert new
                        cur.execute('''
                            INSERT INTO companies 
                            (company_name, country, industry, evidence_type, evidence_text, 
                             confidence_score, source, source_url, discovered_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            comp['name'],
                            comp['country'],
                            comp['industry'],
                            'theirstack',
                            f'Listed on TheirStack as Microsoft Dynamics NAV user',
                            5,  # Maximum confidence - tech stack verified
                            'theirstack',
                            comp['url'],
                            datetime.utcnow().isoformat() + 'Z'
                        ))
                        companies_added += 1
            
            # Rate limiting - be nice to TheirStack
            if page % 10 == 0:
                print(f"  ⏳ Progress: {page}/{TOTAL_PAGES} (added: {companies_added}, existing: {companies_existing})")
                time.sleep(1)
            
            conn.commit()
            
        except Exception as e:
            print(f"  ❌ Error on page {page}: {e}")
            break
    
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ THEIRSTACK EXPANSION FÆRDIG!")
    print(f"   Nytilføjet: {companies_added:,} virksomheder")
    print(f"   Allerede eksisterende: {companies_existing:,}")
    print(f"   Total TheirStack i DB: {companies_added + companies_existing:,}")
    print("=" * 80)
    
    return companies_added

if __name__ == '__main__':
    try:
        scrape_theirstack_all()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
