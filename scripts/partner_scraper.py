#!/usr/bin/env python3
"""
Partner Site Direct Scraper - No API Required
==============================================
Scrapes Microsoft Dynamics partner sites directly for customer references.

Targets:
- Abakion (abakion.dk)
- Logos Consult (logosconsult.dk)
- NAV24 (nav24.com)
- Dynamics Danmark (dynamicsdanmark.dk)
- Evexo (evexo.dk)
- NaviLogic (navilogic.dk)
- JCD (jcd.dk)
- Consortio (consortio.dk)
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

SCRIPT_DIR = Path(__file__).parent.resolve()
NAVISION_DB = SCRIPT_DIR.parent
DB_PATH = NAVISION_DB / 'database' / 'navision-global.db'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Partner sites to scrape - each with customer reference URLs
PARTNER_SITES = {
    'abakion': {
        'base': 'https://abakion.dk',
        'references': ['/kunder/', '/case/', '/referencer/'],
        'country': 'DK'
    },
    'logos': {
        'base': 'https://logosconsult.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
    'nav24': {
        'base': 'https://nav24.com',
        'references': ['/customers/', '/cases/', '/references/'],
        'country': 'DK'
    },
    'dynamics_danmark': {
        'base': 'https://dynamicsdanmark.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
    'evexo': {
        'base': 'https://evexo.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
    'navilogic': {
        'base': 'https://navilogic.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
    'jcd': {
        'base': 'https://jcd.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
    'consortio': {
        'base': 'https://consortio.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
    'webcenter': {
        'base': 'https://webcenter.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
    'bornerups': {
        'base': 'https://bornerups.dk',
        'references': ['/kunder/', '/cases/', '/referencer/'],
        'country': 'DK'
    },
}

def save_companies(companies, source):
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
            (company_name, country, website, evidence_type, evidence_text, 
             confidence_score, source, source_url, discovered_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company.get('company_name', ''),
                company.get('country', 'DK'),
                company.get('website', ''),
                'partner_reference',
                company.get('evidence_text', ''),
                4,
                source,
                company.get('source_url', ''),
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

def scrape_partner_site(name, config):
    """Scrape a single partner site for customer references."""
    print(f"  🕷️  Scraping {name}...")
    
    companies = []
    base_url = config['base']
    seen = set()
    
    for ref_path in config['references']:
        try:
            url = urljoin(base_url, ref_path)
            resp = requests.get(url, headers=HEADERS, timeout=10)
            
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find customer links/cards
            # Look for common patterns in customer listing pages
            customer_links = []
            
            # Pattern 1: Links in article/post lists
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Skip non-customer pages
                if any(x in href.lower() for x in ['login', 'kontakt', 'om', 'job', 'privacy']):
                    continue
                
                # Look for customer indicators
                if any(x in href.lower() for x in ['/case/', '/kunde/', '/referenc', '/customer/', '/success']):
                    customer_links.append((urljoin(base_url, href), text))
            
            # Pattern 2: Customer cards/divs
            for card in soup.find_all(['div', 'article'], class_=lambda x: x and any(c in x.lower() for c in ['case', 'kunde', 'customer', 'reference'])):
                title_elem = card.find(['h2', 'h3', 'h4'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link_elem = card.find('a', href=True)
                    if link_elem and len(title) > 3:
                        customer_links.append((urljoin(base_url, link_elem['href']), title))
            
            # Process customer pages
            for customer_url, customer_title in customer_links[:20]:  # Limit per page
                if customer_url in seen:
                    continue
                seen.add(customer_url)
                
                try:
                    customer_resp = requests.get(customer_url, headers=HEADERS, timeout=10)
                    if customer_resp.status_code == 200:
                        company = extract_company_from_page(customer_resp.text, customer_url, customer_title, config['country'])
                        if company and company['company_name'].lower() not in [c['company_name'].lower() for c in companies]:
                            companies.append(company)
                except:
                    pass
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            continue
    
    return companies

def extract_company_from_page(html, url, title, country):
    """Extract company info from a customer reference page."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find company name
    company_name = None
    
    # Pattern 1: H1 heading
    h1 = soup.find('h1')
    if h1:
        company_name = h1.get_text(strip=True)
    
    # Pattern 2: Meta title
    if not company_name:
        title_tag = soup.find('title')
        if title_tag:
            company_name = title_tag.get_text(strip=True).split(' - ')[0]
    
    # Pattern 3: Use the title we got
    if not company_name:
        company_name = title
    
    # Clean up company name
    if company_name:
        # Remove common suffixes
        for suffix in [' - Case', ' | Case', ' - Kunde', ' | Kunde', 'Referenc', 'Customer']:
            company_name = company_name.replace(suffix, '')
        company_name = company_name.strip()
    
    if not company_name or len(company_name) < 3:
        return None
    
    # Skip if it looks like a partner name
    partner_names = ['abakion', 'logos', 'nav24', 'dynamics', 'evexo', 'navilogic', 'jcd', 'consortio']
    if any(p in company_name.lower() for p in partner_names):
        return None
    
    # Extract domain from URL
    try:
        domain = urlparse(url).netloc.replace('www.', '')
    except:
        domain = ''
    
    return {
        'company_name': company_name[:100],
        'country': country,
        'website': domain,
        'evidence_text': f"Partner reference: {title[:80]}",
        'source_url': url,
    }

def scrape_all():
    """Scrape all partner sites."""
    print("🚀 Starting partner site scraping...")
    
    all_companies = []
    
    for name, config in PARTNER_SITES.items():
        companies = scrape_partner_site(name, config)
        print(f"  ✅ {name}: Found {len(companies)} companies")
        all_companies.extend(companies)
        time.sleep(1)  # Rate limiting between sites
    
    # Save to database
    inserted = save_companies(all_companies, 'partner_scraper')
    
    print(f"\n📊 Total: {len(all_companies)} companies found, {inserted} inserted")
    
    # Get total count
    conn = sqlite3.connect(str(DB_PATH))
    total = conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
    conn.close()
    
    print(f"📈 Database total: {total}")
    
    return inserted

if __name__ == '__main__':
    scrape_all()
