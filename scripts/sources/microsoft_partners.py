#!/usr/bin/env python3
"""
Microsoft Dynamics Partner Finder
==================================
Finds Microsoft Dynamics partners and their customer references.
This is a GOLD MINE - partners list their customers with case studies.

FREE - Uses local SearXNG instance
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from urllib.parse import urlparse, quote

SEARXNG_URL = "http://127.0.0.1:8080"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Partner-focused queries - these find customer lists
PARTNER_QUERIES = {
    'DK': [
        'site:linkedin.com/company "Microsoft Dynamics" partner Danmark kunder',
        'site:facebook.com "Dynamics 365" partner Danmark kunde',
        '"Microsoft Dynamics partner" Danmark referencer',
        '"Business Central partner" Danmark kunder',
        'site:navision.dk kunde case',
        'Abakion kunder referencer',
        'Logos Dynamics kunder',
        'NAV24 kunder Danmark',
        'ERP-Gruppen kunder case',
        'Microsoft Dynamics 365 partner liste Danmark',
    ],
    'NO': [
        'site:linkedin.com/company "Microsoft Dynamics" partner Norge kunder',
        '"Microsoft Dynamics partner" Norge referanser',
        'NAV24 kunder Norge',
        'Business Central partner Norge',
    ],
    'SE': [
        'site:linkedin.com/company "Microsoft Dynamics" partner Sverige kunder',
        '"Microsoft Dynamics partner" Sverige referenser',
        'NAV24 kunder Sverige',
        'Business Central partner Sverige',
    ],
    'DE': [
        'site:linkedin.com/company "Microsoft Dynamics" partner Deutschland',
        '"Microsoft Dynamics Partner" Deutschland Kunden',
        'Business Central Partner Deutschland',
    ],
    'UK': [
        'site:linkedin.com/company "Microsoft Dynamics" partner UK customers',
        '"Microsoft Dynamics partner" United Kingdom customers',
        'Business Central partner UK references',
    ],
    'US': [
        'site:linkedin.com/company "Microsoft Dynamics" partner USA customers',
        '"Microsoft Dynamics partner" United States customers',
        'Business Central partner America references',
    ],
    'NL': [
        'site:linkedin.com/company "Microsoft Dynamics" partner Nederland',
        '"Microsoft Dynamics partner" Nederland klanten',
    ],
    'BE': [
        'site:linkedin.com/company "Microsoft Dynamics" partner België',
        '"Microsoft Dynamics partner" België klanten',
    ],
    'FI': [
        'site:linkedin.com/company "Microsoft Dynamics" partner Suomi',
        '"Microsoft Dynamics partner" Suomi asiakkaat',
    ],
}

# Domains to skip (partner sites themselves)
PARTNER_DOMAINS = [
    'linkedin.com', 'facebook.com', 'twitter.com', 'youtube.com',
    'microsoft.com', 'navision.dk', 'abakion.dk', 'logos.dk',
]

def scrape(country='DK'):
    """Find companies via partner references."""
    print(f"  📍 Searching partner references for {country}")
    
    companies = find_partners_via_searxng(country)
    
    if companies:
        print(f"  ✅ Found {len(companies)} companies via partners")
        return companies
    
    print(f"  ⚠️  No partner references found for {country}")
    return []

def find_partners_via_searxng(country='DK'):
    """
    Search SearXNG for partner customer references.
    
    Returns list of company dictionaries.
    """
    companies = []
    seen = set()
    
    queries = PARTNER_QUERIES.get(country, PARTNER_QUERIES['DK'])
    print(f"  🔍 Using {len(queries)} partner queries")
    
    for query in queries:
        try:
            url = f"{SEARXNG_URL}/search"
            params = {
                'q': query,
                'pageno': 1,
                'format': 'html',
            }
            
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('article', class_='result')
            
            for result in results[:20]:  # Max 20 per query
                try:
                    title_elem = result.find('h3').find('a') if result.find('h3') else None
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    content = result.get_text(strip=True)[:200]
                    
                    # Skip partner domains themselves
                    if any(partner in url.lower() for partner in PARTNER_DOMAINS):
                        continue
                    
                    # Extract company from result
                    company = extract_company_from_partner_result(title, url, content, country)
                    
                    if company and company.lower() not in seen:
                        if looks_like_company(company):
                            seen.add(company.lower())
                            companies.append({
                                'company_name': company,
                                'country': country,
                                'website': extract_domain(url),
                                'industry': '',
                                'employees': '',
                                'revenue': '',
                                'evidence_type': 'partner_reference',
                                'evidence_text': f"Partner reference: {title[:100]}",
                                'confidence_score': 4,
                                'source_url': url,
                                'is_verified': 0,
                            })
                            
                except Exception as e:
                    continue
            
            time.sleep(0.3)  # Rate limiting
            
        except Exception as e:
            continue
    
    return companies

def extract_company_from_partner_result(title, url, content, country):
    """Extract company name from partner search result."""
    domain = extract_domain(url)
    
    # Try to extract from title
    # Patterns like "Company X - Dynamics Implementation" or "Company X chooses Navision"
    patterns = [
        ' - ',
        ' implements ',
        ' chooses ',
        ' customer ',
        ' reference ',
        ' case study ',
    ]
    
    for pattern in patterns:
        if pattern.lower() in title.lower():
            parts = title.lower().split(pattern.lower())
            if parts:
                candidate = parts[0].strip()
                if 3 < len(candidate) < 50:
                    return candidate.title()
    
    # Try from domain
    if domain and len(domain) > 3:
        if domain not in ['google', 'bing', 'yahoo', 'facebook']:
            return domain.replace('-', ' ').replace('.', ' ').title()
    
    return None

def looks_like_company(name):
    """Check if string looks like a company name."""
    if not name or len(name) < 3 or len(name) > 60:
        return False
    
    # Skip if mostly numbers
    if sum(c.isdigit() for c in name) > len(name) / 2:
        return False
    
    # Skip generic terms
    generic = ['microsoft', 'dynamics', 'navision', 'partner', 'consulting', 
               'group', 'solutions', 'services', 'linkedin', 'facebook']
    if name.lower() in generic:
        return False
    
    # Should have at least one capital letter or be all caps (common for company names)
    has_capital = any(c.isupper() for c in name)
    is_all_caps = name.isupper()
    
    return has_capital or is_all_caps

def extract_domain(url):
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain.split('/')[0]
    except:
        return ''

if __name__ == '__main__':
    print("Testing Microsoft partner finder for DK...")
    result = scrape('DK')
    print(f"\nFound {len(result)} companies")
    for company in result[:15]:
        print(f"  - {company['company_name']}: {company['website']}")
