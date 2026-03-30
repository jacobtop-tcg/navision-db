#!/usr/bin/env python3
"""
TheirStack Country Scraper - FREE Public Pages
===============================================
Scrapes TheirStack's public country pages for Navision companies.
No API key needed - uses public web pages.

URLs:
- Germany: https://theirstack.com/en/technology/microsoft-dynamics-nav/de
- Spain: https://theirstack.com/en/technology/microsoft-dynamics-365-business-central/es
- Italy: https://theirstack.com/en/technology/navision/it
- France: https://theirstack.com/en/technology/microsoft-dynamics-nav/fr
- India: https://theirstack.com/en/technology/microsoft-dynamics-nav/in

Each page shows companies with:
- Company name
- Country
- Industry
- Employee count
- Technologies used
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional

BASE_URLS = {
    'DE': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/de',
    'ES': 'https://theirstack.com/en/technology/microsoft-dynamics-365-business-central/es',
    'IT': 'https://theirstack.com/en/technology/navision/it',
    'FR': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/fr',
    'IN': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/in',
    'GB': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/gb',
    'NL': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/nl',
    'US': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/us',
    'CA': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/ca',
    'SE': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/se',
    'NO': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/no',
    'DK': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/dk',
    'FI': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/fi',
    'BE': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/be',
    'PL': 'https://theirstack.com/en/technology/microsoft-dynamics-nav/pl',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

def extract_companies_from_html(html: str, country_code: str) -> List[Dict]:
    """Extract company data from TheirStack HTML"""
    companies = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all company rows in the table
    # TheirStack uses tr elements with data attributes
    for tr in soup.find_all('tr', class_=lambda x: x and 'border-b' in x):
        try:
            # Extract company name
            name_elem = tr.find('a', class_=lambda x: x and 'font-medium' in x and 'text-blue-700' in x)
            if not name_elem:
                continue
            
            company_name = name_elem.get('title', '').strip()
            if not company_name:
                company_name = name_elem.get_text(strip=True)
            
            if not company_name or len(company_name) < 2:
                continue
            
            # Extract industry
            industry_elem = tr.find('td')
            industry = ''
            if industry_elem:
                # Find the industry column (usually 3rd td)
                tds = tr.find_all('td')
                if len(tds) >= 3:
                    industry = tds[2].get_text(strip=True) if tds[2] else ''
            
            # Extract employee count
            employees = ''
            if len(tds) >= 4:
                employees = tds[3].get_text(strip=True) if tds[3] else ''
            
            # Extract revenue (if available)
            revenue = ''
            if len(tds) >= 5:
                revenue = tds[4].get_text(strip=True) if tds[4] else ''
            
            company = {
                'company_name': company_name,
                'country': country_code,
                'industry': industry,
                'employees': employees,
                'revenue': revenue,
                'evidence_type': 'technology_stack',
                'evidence_text': f'Listed on TheirStack as Microsoft Dynamics NAV user',
                'confidence_score': 4,  # High confidence - TheirStack is reliable
                'source_url': f'https://theirstack.com/en/technology/microsoft-dynamics-nav/{country_code.lower()}',
                'website': '',  # Would need additional lookup
            }
            
            companies.append(company)
            
        except Exception as e:
            print(f"  ⚠️  Error parsing row: {e}")
            continue
    
    return companies

def scrape_country(country_code: str, max_pages: int = 5) -> List[Dict]:
    """
    Scrape a single country page with pagination.
    
    TheirStack shows 10 companies per page.
    max_pages limits how many pages we scrape (to avoid rate limiting).
    """
    base_url = BASE_URLS.get(country_code)
    if not base_url:
        print(f"  ❌ No URL configured for {country_code}")
        return []
    
    all_companies = []
    
    for page in range(1, max_pages + 1):
        # Build paginated URL
        # TheirStack uses query params for pagination
        url = f"{base_url}?page={page}"
        
        print(f"  📍 Scraping {country_code} page {page}/{max_pages}")
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            
            # Check if we got blocked
            if resp.status_code == 403 or 'captcha' in resp.text.lower():
                print(f"  ⚠️  Blocked by captcha/rate limit on page {page}")
                break
            
            companies = extract_companies_from_html(resp.text, country_code)
            
            if not companies:
                print(f"  ℹ️  No more companies on page {page}")
                break
            
            all_companies.extend(companies)
            print(f"  ✅ Page {page}: {len(companies)} companies (total: {len(all_companies)})")
            
            # Be nice - delay between requests
            time.sleep(3)
            
        except requests.RequestException as e:
            print(f"  ❌ Request failed on page {page}: {e}")
            break
    
    return all_companies

def scrape(country: str, **kwargs) -> List[Dict]:
    """Main scrape function called by scraper.py"""
    country_code = country.upper()
    
    if country_code not in BASE_URLS:
        print(f"  ❌ TheirStack not configured for {country}")
        return []
    
    print(f"🕷️  TheirStack scraper for {country}")
    
    companies = scrape_country(country_code)
    
    # Deduplicate by company name
    seen = set()
    unique_companies = []
    for c in companies:
        key = c['company_name'].lower()
        if key not in seen:
            seen.add(key)
            unique_companies.append(c)
    
    print(f"✅ TheirStack/{country}: {len(unique_companies)} unique companies")
    return unique_companies

def scrape_all_countries() -> Dict[str, int]:
    """Scrape all configured countries"""
    results = {}
    
    for country_code in BASE_URLS.keys():
        companies = scrape_country(country_code)
        results[country_code] = len(companies)
        time.sleep(2)  # Be nice to their server
    
    return results

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Scrape specific country
        country = sys.argv[1].upper()
        companies = scrape(country)
        print(f"\nTotal: {len(companies)} companies")
        
        # Show first 5
        for c in companies[:5]:
            print(f"  - {c['company_name']} ({c['country']}) - {c['industry']}")
    else:
        # Scrape all
        print("Scraping all TheirStack country pages...")
        results = scrape_all_countries()
        print("\nResults:")
        for country, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
            print(f"  {country}: {count} companies")
        print(f"\nTotal: {sum(results.values())} companies")
