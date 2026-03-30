#!/usr/bin/env python3
"""
TheirStack Navision Scraper - GRATIS
=====================================
Scraper TheirStack.com for Navision virksomheder
Ingen API key nødvendig - bruger web scraping

TheirStack har:
- 36.597 Navision virksomheder globalt
- 2.789 i USA alene
- 658 i Tyskland
- 825 i Holland

Bruger: web_search + web_fetch tools
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
NAVISION_DB = SCRIPT_DIR.parent
DB_PATH = NAVISION_DB / 'database' / 'navision-global.db'

# TheirStack URLs for different countries
THEIRSTACK_URLS = {
    'global': 'https://theirstack.com/en/technology/navision',
    'us': 'https://theirstack.com/en/technology/navision/us',
    'de': 'https://theirstack.com/en/technology/navision/de',
    'nl': 'https://theirstack.com/en/technology/navision/nl',
    'uk': 'https://theirstack.com/en/technology/navision/gb',
    'dk': 'https://theirstack.com/en/technology/navision/dk',
    'se': 'https://theirstack.com/en/technology/navision/se',
    'fr': 'https://theirstack.com/en/technology/navision/fr',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def scrape_theirstack_country(country_code='global'):
    """Scrape TheirStack for a specific country"""
    print(f"🕷️  Scraping TheirStack for {country_code}...")
    
    url = THEIRSTACK_URLS.get(country_code, THEIRSTACK_URLS['global'])
    companies = []
    
    try:
        # Fetch the page
        resp = requests.get(url, headers=HEADERS, timeout=15)
        
        if resp.status_code != 200:
            print(f"  ⚠️  HTTP {resp.status_code}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find company cards on TheirStack
        # TheirStack uses a specific structure for company listings
        company_cards = soup.find_all('div', class_=lambda x: x and 'company' in x.lower())
        
        for card in company_cards[:50]:  # Limit per page
            try:
                name_elem = card.find(['h3', 'h4', 'a'], class_=lambda x: x and 'name' in x.lower())
                if not name_elem:
                    continue
                
                name = name_elem.get_text(strip=True)
                if not name or len(name) < 2:
                    continue
                
                # Extract industry
                industry_elem = card.find('div', class_=lambda x: x and 'industry' in x.lower())
                industry = industry_elem.get_text(strip=True) if industry_elem else ''
                
                # Extract employee count
                size_elem = card.find('div', class_=lambda x: x and ('size' in x.lower() or 'employee' in x.lower()))
                size = size_elem.get_text(strip=True) if size_elem else ''
                
                # Extract location
                location_elem = card.find('div', class_=lambda x: x and 'location' in x.lower())
                location = location_elem.get_text(strip=True) if location_elem else ''
                
                companies.append({
                    'company_name': name,
                    'country': country_code.upper() if country_code != 'global' else '',
                    'industry': industry,
                    'employees': size,
                    'location': location,
                    'evidence_type': 'theirstack',
                    'evidence_text': f'TheirStack Navision user - {country_code}',
                    'confidence_score': 3,
                    'source': 'theirstack_scrape',
                })
                
            except Exception as e:
                continue
        
        print(f"  ✅ Found {len(companies)} companies")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return companies

def save_companies(companies):
    """Save companies to database"""
    if not companies:
        return 0
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    inserted = 0
    for company in companies:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO companies 
            (company_name, country, industry, employees, evidence_type, evidence_text, 
             confidence_score, source, discovered_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company.get('company_name', ''),
                company.get('country', ''),
                company.get('industry', ''),
                company.get('employees', ''),
                company.get('evidence_type', 'theirstack'),
                company.get('evidence_text', ''),
                company.get('confidence_score', 3),
                company.get('source', 'theirstack_scrape'),
                datetime.utcnow().isoformat() + 'Z',
                datetime.utcnow().isoformat() + 'Z',
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            pass
    
    conn.commit()
    conn.close()
    return inserted

def scrape_all_countries():
    """Scrape all countries"""
    print("🚀 Starting TheirStack global scrape...")
    
    all_companies = []
    
    # Scrape each country
    for country in ['global', 'us', 'de', 'nl', 'uk', 'dk', 'se', 'fr']:
        companies = scrape_theirstack_country(country)
        all_companies.extend(companies)
        time.sleep(2)  # Rate limiting
    
    # Save to database
    inserted = save_companies(all_companies)
    
    print(f"\n📊 Total: {len(all_companies)} companies found, {inserted} inserted")
    
    # Get total count
    conn = sqlite3.connect(str(DB_PATH))
    total = conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
    conn.close()
    
    print(f"📈 Database total: {total}")
    
    return inserted

if __name__ == '__main__':
    scrape_all_countries()
