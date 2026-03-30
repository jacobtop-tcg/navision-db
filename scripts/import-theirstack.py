#!/usr/bin/env python3
"""
Import ALL companies from TheirStack into the database.

This script:
1. Scrapes all countries from TheirStack
2. Saves directly to navision-global.db
3. Reports progress

Run time: ~30-60 minutes for all countries
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from sources.theirstack_scraper import scrape, COUNTRIES

DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

def save_companies(companies):
    """Save companies to database."""
    if not companies:
        return 0
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    inserted = 0
    for company in companies:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO companies 
            (company_name, country, website, industry, employees, revenue,
             evidence_type, evidence_text, confidence_score, source, source_url,
             discovered_at, updated_at, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company.get('company_name', ''),
                company.get('country', ''),
                company.get('website', ''),
                company.get('industry', ''),
                company.get('employees', ''),
                company.get('revenue', ''),
                company.get('evidence_type', 'theirstack'),
                company.get('evidence_text', 'TheirStack listing'),
                company.get('confidence_score', 5),
                'TheirStack',
                company.get('source_url', ''),
                datetime.utcnow().isoformat() + 'Z',
                datetime.utcnow().isoformat() + 'Z',
                company.get('is_verified', 1)
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"  ⚠️  Failed to insert {company.get('company_name', 'Unknown')}: {e}")
    
    conn.commit()
    conn.close()
    return inserted

def main():
    print("="*70)
    print("THEIRSTACK FULL IMPORT - Microsoft Dynamics NAV Companies")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    total_companies = []
    total_inserted = 0
    
    # Skip GLOBAL, do individual countries
    countries_to_scrape = [c for c in COUNTRIES if c != 'GLOBAL']
    
    for i, country in enumerate(countries_to_scrape, 1):
        pages = COUNTRIES[country]['pages']
        print(f"\n{'='*70}")
        print(f"[{i}/{len(countries_to_scrape)}] {country} ({pages} pages)")
        print(f"{'='*70}")
        
        # Scrape
        companies = scrape(country)
        
        if companies:
            # Save to database
            inserted = save_companies(companies)
            total_inserted += inserted
            total_companies.extend(companies)
            
            print(f"  💾 Saved {inserted} new companies to database")
        
        print(f"\n📊 RUNNING TOTAL: {len(total_companies)} companies scraped, {total_inserted} new in DB")
        
        # Delay between countries
        if i < len(countries_to_scrape):
            print(f"  😴 Waiting 5 seconds...")
            import time
            time.sleep(5)
    
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print(f"Total companies scraped: {len(total_companies)}")
    print(f"New companies in database: {total_inserted}")
    print(f"Finished: {datetime.now().isoformat()}")
    
    # Show breakdown by country
    print("\n📊 BY COUNTRY:")
    country_counts = {}
    for c in total_companies:
        country = c.get('country', 'UNKNOWN')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    for country, count in sorted(country_counts.items(), key=lambda x: -x[1]):
        print(f"  {country}: {count}")

if __name__ == '__main__':
    main()
