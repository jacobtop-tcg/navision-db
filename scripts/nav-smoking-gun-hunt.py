#!/usr/bin/env python3
"""
NAVISION SMOKING GUN HUNT - Aggressiv indsamling af NAV kunder
================================================================
Finder VIRKELIGE Navision kunder via multiple kilder

Kilder:
1. Job postings (søger NAV folk = bruger NAV)
2. Navision Stat (offentlige institutioner)
3. TheirStack (teknologi-stack detektion)
4. Partner kundelister (hvis NAV eksplicit nævnt)
5. Case studies (kundenavn + NAV)
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'
SEARXNG_URL = "http://127.0.0.1:8080"

# NAVISION KEYWORDS (ikke BC!)
NAV_KEYWORDS = [
    "Dynamics NAV", "Navision", "Microsoft Dynamics NAV",
    "NAV 2009", "NAV 2013", "NAV 2015", "NAV 2016", "NAV 2017", 
    "NAV 2018", "NAV 2019", "NAV 2020",
    "Dynamics NAV 2009", "Dynamics NAV 2013", "Dynamics NAV 2015",
    "Dynamics NAV 2016", "Dynamics NAV 2017", "Dynamics NAV 2018",
    "Dynamics NAV 2019", "Dynamics NAV 2020",
    "Navision Stat", "C/AL", "NAV on-premise"
]

# Filtrer BC væk
BC_FILTERS = [
    "Business Central", "BC Cloud", "Dynamics 365 BC",
    "migrated to BC", "gået live med BC"
]

def search_searxng(query, country=""):
    """Search via SearXNG"""
    try:
        url = f"{SEARXNG_URL}/search"
        q = query
        if country:
            q = f"{query} site:.{country.lower()}"
        
        params = {
            "q": q,
            "format": "json",
            "language": "en",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('results', [])
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
    return []

def extract_company_name(text, url=""):
    """Extract company name from text"""
    # Simple extraction - first capitalized phrase
    # Can be improved with NLP
    return text[:100].strip()

def add_company(cursor, company_name, country, evidence_type, evidence_text, source_url, confidence=4):
    """Add company to database if not exists"""
    # Check exists
    cursor.execute("SELECT id FROM companies WHERE company_name = ? AND source_url = ?", 
                  (company_name[:200], source_url[:500] if source_url else ""))
    if cursor.fetchone():
        return False
    
    # Insert
    cursor.execute("""
        INSERT INTO companies 
        (company_name, country, evidence_type, evidence_text, confidence_score, source, source_url, discovered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_name[:200],
        country,
        evidence_type,
        evidence_text[:2000],
        confidence,
        "smoking_gun_hunt",
        source_url[:500] if source_url else "",
        datetime.utcnow().isoformat() + 'Z'
    ))
    return True

def hunt_job_postings():
    """Find companies hiring NAV people = they use NAV!"""
    print("\n" + "="*80)
    print("🔍 HUNT #1: JOB POSTINGS (søger NAV folk = bruger NAV)")
    print("="*80)
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Job queries per country
    job_queries = {
        'DK': [
            '"Dynamics NAV" udvikler',
            '"Navision" udvikler',
            '"Dynamics NAV" økonomi',
            '"Navision" regnskab',
            '"Dynamics NAV" support',
            '"Navision" konsulent intern',
        ],
        'DE': [
            '"Dynamics NAV" Entwickler',
            '"Navision" Entwickler',
            '"Dynamics NAV" Berater intern',
        ],
        'SE': [
            '"Dynamics NAV" utvecklare',
            '"Navision" utvecklare',
        ],
        'NO': [
            '"Dynamics NAV" utvikler',
            '"Navision" utvikler',
        ],
        'UK': [
            '"Dynamics NAV" developer',
            '"Navision" developer',
        ],
        'US': [
            '"Dynamics NAV" developer',
            '"Navision" developer',
        ],
    }
    
    added = 0
    
    for country, queries in job_queries.items():
        print(f"\n📍 {country}")
        
        for query in queries:
            results = search_searxng(query, country)
            
            for result in results[:10]:
                title = result.get('title', '')
                url = result.get('url', '')
                content = result.get('content', '')
                
                # Skip if BC
                if any(bc in title.lower() or bc in content.lower() for bc in BC_FILTERS):
                    continue
                
                # Check if has NAV keyword
                if not any(nav.lower() in title.lower() or nav.lower() in content.lower() for nav in NAV_KEYWORDS):
                    continue
                
                # Extract company (simplified)
                company = extract_company_name(title, url)
                if len(company) < 3:
                    continue
                
                evidence = f"Job posting: {title[:200]}"
                
                if add_company(cur, company, country, 'job_posting_nav', evidence, url, confidence=5):
                    added += 1
                    print(f"  ✅ {company} ({country})")
            
            time.sleep(0.5)
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 JOB POSTINGS: +{added} virksomheder")
    return added

def hunt_navision_stat():
    """Find Navision Stat institutioner (offentlige bruger gammelt NAV)"""
    print("\n" + "="*80)
    print("🔍 HUNT #2: NAVISION STAT (offentlige institutioner)")
    print("="*80)
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Search for Navision Stat institutions
    results = search_searxng('"Navision Stat" institution', 'dk')
    
    added = 0
    for result in results[:50]:
        title = result.get('title', '')
        url = result.get('url', '')
        content = result.get('content', '')
        
        # Extract institution name
        company = extract_company_name(title, url)
        if len(company) < 3:
            continue
        
        evidence = f"Navision Stat institution: {title[:200]} + {content[:200]}"
        
        if add_company(cur, company, 'DK', 'navision_stat', evidence, url, confidence=5):
            added += 1
            print(f"  ✅ {company}")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 NAVISION STAT: +{added} institutioner")
    return added

def hunt_theirstack():
    """TheirStack has 36,000+ NAV companies"""
    print("\n" + "="*80)
    print("🔍 HUNT #3: THEIRSTACK (teknologi detektion)")
    print("="*80)
    
    # TheirStack URLs per country
    theirstack_urls = {
        'DE': 'https://theirstack.com/de/technology/navision',
        'NL': 'https://theirstack.com/nl/technology/navision',
        'UK': 'https://theirstack.com/en/technology/navision',
        'US': 'https://theirstack.com/en/technology/navision',
        'DK': 'https://theirstack.com/da/technology/navision',
        'SE': 'https://theirstack.com/sv/technology/navision',
        'NO': 'https://theirstack.com/no/technology/navision',
        'FR': 'https://theirstack.com/fr/technology/navision',
    }
    
    print("📋 TheirStack URLs til scraping:")
    for country, url in theirstack_urls.items():
        print(f"  {country}: {url}")
    
    # Note: Actual scraping would need browser automation
    # For now, just log the URLs
    print("\n⚠️  TheirStack kræver browser scraping - tilføjes til queue")
    return 0

def hunt_partner_customers():
    """Find partner customer lists that mention NAV"""
    print("\n" + "="*80)
    print("🔍 HUNT #4: PARTNER KUNDELISTER (hvis NAV nævnt)")
    print("="*80)
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # Search for partner customer pages
    partner_queries = [
        '"vores kunder" "Dynamics NAV"',
        '"vores kunder" "Navision"',
        '"kundereference" "Dynamics NAV"',
        '"case" "Dynamics NAV" kunde',
        '"reference" "Navision"',
    ]
    
    added = 0
    for query in partner_queries:
        results = search_searxng(query, 'dk')
        
        for result in results[:10]:
            title = result.get('title', '')
            url = result.get('url', '')
            content = result.get('content', '')
            
            # Skip if BC
            if any(bc in title.lower() or bc in content.lower() for bc in BC_FILTERS):
                continue
            
            company = extract_company_name(title, url)
            if len(company) < 3:
                continue
            
            evidence = f"Partner customer: {title[:200]}"
            
            if add_company(cur, company, 'DK', 'partner_customer_nav', evidence, url, confidence=4):
                added += 1
                print(f"  ✅ {company}")
        
        time.sleep(0.5)
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 PARTNER KUNDER: +{added} virksomheder")
    return added

def main():
    print("="*80)
    print("🎯 NAVISION SMOKING GUN HUNT")
    print(f"Start: {datetime.utcnow().isoformat()}Z")
    print("="*80)
    
    total = 0
    
    # Run hunts
    total += hunt_job_postings()
    total += hunt_navision_stat()
    total += hunt_theirstack()
    total += hunt_partner_customers()
    
    print("\n" + "="*80)
    print(f"✅ TOTAL TILFØJET: {total} virksomheder")
    print("="*80)
    
    return total

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
