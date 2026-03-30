#!/usr/bin/env python3
"""
Navision Partner Customer Scraper
==================================
Scrapes customer lists from Navision/Business Central partner websites.

Partners:
- ERPgruppen (DK) - erpgruppen.dk
- NAV-Vision (DK) - nav-vision.dk
- Nav24 (EU) - nav24.eu
- Abakion (DK) - abakion.dk
- Columbus (Global) - columbusglobal.com
- Logos Consult (DK) - logosconsult.dk
- Many more...

This finds ACTUAL companies using Navision - not job boards!
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import time

# Partner websites with customer references
PARTNERS = {
    'erpgruppen': {
        'url': 'https://erpgruppen.dk/inspiration/kundecases/',
        'country': 'DK',
        'selector': 'a[href*="kundecases"]',
    },
    'nav-vision': {
        'url': 'https://nav-vision.dk/',
        'country': 'DK',
        'selector': 'a:contains("kunder"), a:contains("cases")',
    },
    'nav24': {
        'url': 'https://nav24.eu/case-studies/',
        'country': 'EU',
        'selector': '.case-study, article',
    },
    'abakion': {
        'url': 'https://abakion.dk/cases/',
        'country': 'DK',
        'selector': '.case, article',
    },
    'logos': {
        'url': 'https://logosconsult.dk/cases/',
        'country': 'DK',
        'selector': '.case-study, article',
    },
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def scrape(country='DK'):
    """Scrape partner websites for customer references."""
    print(f"  📍 Scraping partners for {country}")
    
    companies = []
    
    for partner_name, partner_info in PARTNERS.items():
        if partner_info['country'] not in [country, 'EU', 'GLOBAL']:
            continue
        
        print(f"    Partner: {partner_name}")
        try:
            partner_companies = scrape_partner(partner_name, partner_info)
            companies.extend(partner_companies)
            print(f"      ✅ Found {len(partner_companies)} companies")
        except Exception as e:
            print(f"      ⚠️  Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    if companies:
        print(f"  ✅ Total: {len(companies)} companies from partners")
    
    return companies

def scrape_partner(partner_name, partner_info):
    """Scrape a single partner website for customers."""
    companies = []
    
    url = partner_info['url']
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        
        if resp.status_code != 200:
            print(f"      HTTP {resp.status_code}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find all customer/company links or mentions
        # Look for patterns in the HTML
        
        # Strategy 1: Find case study links
        case_links = soup.find_all('a', href=re.compile(r'case|kunde|reference|success', re.I))
        
        for link in case_links:
            text = link.get_text(strip=True)
            if text and len(text) > 3 and len(text) < 100:
                # Check if it looks like a company name
                if looks_like_company(text):
                    companies.append({
                        'company_name': text,
                        'country': partner_info['country'],
                        'website': '',
                        'industry': '',
                        'employees': '',
                        'revenue': '',
                        'evidence_type': 'partner_customer',
                        'evidence_text': f"Customer of {partner_name}",
                        'confidence_score': 4,
                        'source_url': urljoin(url, link.get('href', '')),
                        'is_verified': 0,
                    })
        
        # Strategy 2: Find company names in text
        # Look for patterns like "Company X chose Navision"
        text_content = soup.get_text()
        
        # Extract potential company names from headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for heading in headings:
            text = heading.get_text(strip=True)
            if text and len(text) > 3 and len(text) < 80:
                # Clean up
                text = re.sub(r'\s+', ' ', text)
                if looks_like_company(text) and not any(x in text.lower() for x in ['case', 'story', 'customer', 'kunde']):
                    companies.append({
                        'company_name': text,
                        'country': partner_info['country'],
                        'website': '',
                        'industry': '',
                        'employees': '',
                        'revenue': '',
                        'evidence_type': 'partner_customer',
                        'evidence_text': f"Mentioned by {partner_name}: {text[:50]}",
                        'confidence_score': 3,
                        'source_url': url,
                        'is_verified': 0,
                    })
        
        # Strategy 3: Find logo grids (partners often display customer logos)
        logo_imgs = soup.find_all('img', alt=re.compile(r'.+', re.I))
        for img in logo_imgs[:30]:  # Limit to first 30
            alt = img.get('alt', '').strip()
            if alt and len(alt) > 2 and len(alt) < 50:
                if looks_like_company(alt):
                    companies.append({
                        'company_name': alt,
                        'country': partner_info['country'],
                        'website': '',
                        'industry': '',
                        'employees': '',
                        'revenue': '',
                        'evidence_type': 'partner_customer_logo',
                        'evidence_text': f"Logo on {partner_name} website",
                        'confidence_score': 3,
                        'source_url': urljoin(url, img.get('src', '')),
                        'is_verified': 0,
                    })
        
    except Exception as e:
        print(f"      Error scraping {partner_name}: {e}")
    
    # Deduplicate
    seen = set()
    unique = []
    for c in companies:
        if c['company_name'].lower() not in seen:
            seen.add(c['company_name'].lower())
            unique.append(c)
    
    return unique

def looks_like_company(name):
    """Check if string looks like a company name."""
    if len(name) < 3 or len(name) > 60:
        return False
    
    # Skip generic terms
    generic = [
        'home', 'contact', 'about', 'cases', 'cases study', 'cases',
        'kunden', 'references', 'partners', 'services', 'products',
        'navision', 'dynamics', 'business central', 'microsoft',
        'case study', 'success story', 'customer story',
        'kontakt', 'om os', 'ydelser', 'løsninger',
    ]
    
    if name.lower() in generic:
        return False
    
    # Skip if mostly numbers
    if sum(c.isdigit() for c in name) > len(name) / 2:
        return False
    
    # Should have at least one capital letter or be all caps
    if not any(c.isupper() for c in name) and not name.isupper():
        # Allow Danish company names that might be lowercase
        pass
    
    return True

if __name__ == '__main__':
    print("Testing partner scraper for DK...")
    result = scrape('DK')
    print(f"\nFound {len(result)} companies from partners")
    for company in result[:15]:
        print(f"  - {company['company_name']} ({company['evidence_type']})")
