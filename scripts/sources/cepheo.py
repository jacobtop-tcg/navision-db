#!/usr/bin/env python3
"""
Cepheo Customer Scraper - Nordic Dynamics 365 Partner
======================================================
Scrapes customer cases from Cepheo.com - a leading Nordic Microsoft partner.

URL: https://cepheo.com/our-customers/
Focus: Nordic companies (DK, SE, NO, FI) using Dynamics 365/NAV

This finds END USERS (companies using the system), not developers.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict

CEPHEO_URL = "https://cepheo.com/our-customers/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

def extract_customers_from_html(html: str) -> List[Dict]:
    """Extract customer names and details from Cepheo HTML"""
    customers = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Cepheo uses cards/sections for each customer
    # Look for customer cards with company names
    for card in soup.find_all(['div', 'article'], class_=lambda x: x and any(k in x for k in ['customer', 'case', 'client', 'card'])):
        try:
            # Try to find company name
            name_elem = card.find(['h1', 'h2', 'h3', 'h4'], class_=lambda x: x and any(k in x for k in ['title', 'name', 'heading']))
            if not name_elem:
                # Fallback: look for links
                link = card.find('a', href=lambda x: x and '/customer' in x)
                if link:
                    name_elem = link
            
            if not name_elem:
                continue
            
            company_name = name_elem.get_text(strip=True)
            if not company_name or len(company_name) < 3:
                continue
            
            # Skip if it's just generic text
            if company_name.lower() in ['our customers', 'view all', 'learn more']:
                continue
            
            # Extract clean company name from title
            # Pattern: "Company Name does something" -> "Company Name"
            clean_name = company_name
            for sep in [' shapes ', ' frees ', ' gears ', ' is ready ', ' went from ', ' with ', ' at ']:
                if sep in clean_name:
                    clean_name = clean_name.split(sep)[0].strip()
                    break
            
            company_name = clean_name
            if len(company_name) < 2:
                continue
            
            # Get additional info if available
            description = ''
            desc_elem = card.find(['p', 'div'], class_=lambda x: x and any(k in x for k in ['desc', 'summary', 'text']))
            if desc_elem:
                description = desc_elem.get_text(strip=True)[:200]
            
            # Determine country from context or URL
            country = 'DK'  # Default, Cepheo is DK-based
            if 'sweden' in company_name.lower() or 'sverige' in description.lower():
                country = 'SE'
            elif 'norway' in company_name.lower() or 'norge' in description.lower():
                country = 'NO'
            elif 'finland' in company_name.lower() or 'suomi' in description.lower():
                country = 'FI'
            
            customers.append({
                'company_name': company_name,
                'country': country,
                'industry': '',
                'employees': '',
                'evidence_type': 'partner_customer',
                'evidence_text': f'Cepheo customer case - {description[:100]}' if description else 'Listed on Cepheo customer page',
                'confidence_score': 4,  # High - partner customer references
                'source_url': CEPHEO_URL,
            })
            
        except Exception as e:
            continue
    
    return customers

def scrape(country: str = 'DK') -> List[Dict]:
    """
    Scrape Cepheo customer page.
    Country parameter is ignored - we scrape all Nordic customers.
    """
    print(f"🔍 Cepheo customer scraper (Nordic partner)")
    
    try:
        resp = requests.get(CEPHEO_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        
        if resp.status_code == 403:
            print(f"  ⚠️  Blocked by Cepheo")
            return []
        
        customers = extract_customers_from_html(resp.text)
        
        # Deduplicate
        seen = set()
        unique = []
        for c in customers:
            key = c['company_name'].lower()
            if key not in seen:
                seen.add(key)
                unique.append(c)
        
        print(f"✅ Cepheo: Found {len(unique)} unique customers")
        return unique
        
    except requests.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []

if __name__ == '__main__':
    result = scrape('DK')
    print(f"\nFound {len(result)} customers")
    for c in result[:10]:
        print(f"  - {c['company_name']} ({c['country']})")
