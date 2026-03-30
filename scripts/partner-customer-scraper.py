#!/usr/bin/env python3
"""
Scraper customer lists directly from partner websites
No SearXNG dependency - direct HTTP requests
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re

# Partner websites with known customer lists
PARTNER_SITES = [
    {
        "name": "abakion",
        "url": "https://www.abakion.dk/kunder/",
        "country": "DK",
        "selector": "customer"
    },
    {
        "name": "conscia",
        "url": "https://www.conscia.dk/cases",
        "country": "DK", 
        "selector": "case"
    },
    {
        "name": " Columbus",
        "url": "https://www.columbusglobal.com/customers",
        "country": "DK",
        "selector": "customer"
    },
    {
        "name": "evry",
        "url": "https://www.evry.com/no/cases/",
        "country": "NO",
        "selector": "case"
    },
    {
        "name": "stonex",
        "url": "https://www.stonex.dk/referencer/",
        "country": "DK",
        "selector": "reference"
    }
]

def fetch_customers_from_site(site):
    """Fetch customer names from partner website"""
    customers = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml"
        }
        
        print(f"  📄 Fetching {site['url']}")
        resp = requests.get(site['url'], headers=headers, timeout=20)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Try to find company names in various patterns
            # Look for h2, h3, a tags that might contain company names
            for tag in soup.find_all(['h2', 'h3', 'a'], class_=lambda x: x and any(word in x.lower() for word in ['customer', 'case', 'client', 'reference'])):
                text = tag.get_text(strip=True)
                if text and len(text) > 3 and len(text) < 100:
                    customers.append(text)
            
            # Also look for logo alt texts
            for img in soup.find_all('img', alt=True):
                alt = img['alt'].strip()
                if alt and len(alt) > 3 and len(alt) < 100:
                    if not any(word in alt.lower() for word in ['logo', 'icon', 'arrow', 'click']):
                        customers.append(alt)
                        
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    
    return customers

def main():
    conn = sqlite3.connect('database/navision-global.db')
    cursor = conn.cursor()
    
    total_inserted = 0
    
    print("🎯 PARTNER CUSTOMER SCRAPER\n")
    
    for site in PARTNER_SITES:
        print(f"\n📍 {site['name']} ({site['country']})")
        customers = fetch_customers_from_site(site)
        
        print(f"   Found {len(customers)} potential customers")
        
        for customer in customers[:20]:  # Limit per site
            # Clean up name
            name = customer.strip()
            if len(name) < 3 or len(name) > 80:
                continue
                
            # Skip common non-company words
            skip_words = ['home', 'contact', 'about', 'services', 'cases', 'customers', 'references', 'read more', 'learn more']
            if any(word in name.lower() for word in skip_words):
                continue
            
            # Check if exists
            cursor.execute("SELECT id FROM companies WHERE company_name = ?", (name,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO companies 
                    (company_name, country, industry, confidence_score, source, evidence_type, discovered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name[:100],
                    site['country'],
                    "Unknown",
                    3,
                    site['name'],
                    "partner_customer_list",
                    datetime.utcnow().isoformat()
                ))
                total_inserted += 1
                print(f"   ✅ NEW: {name}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Complete! Inserted: {total_inserted} new companies")

if __name__ == "__main__":
    main()
