#!/usr/bin/env python3
"""
Company Data Enrichment Script
===============================
Updates existing companies with:
- Real company website (not source URL)
- Headquarters address
- LinkedIn URL

Usage:
    python3 scripts/enrich-companies.py --batch 100    # Process 100 companies
    python3 scripts/enrich-companies.py --all          # Process all (SLOW!)
"""

import argparse
import sqlite3
import requests
from pathlib import Path
from datetime import datetime
import time
import re

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def extract_company_name_from_url(url):
    """Try to extract company name from URL"""
    if not url:
        return None
    # Remove protocol and www
    clean = re.sub(r'^https?://(www\.)?', '', url)
    # Get domain
    domain = clean.split('/')[0]
    # Remove TLD
    name = domain.split('.')[0]
    return name.replace('-', ' ').replace('_', ' ').title()

def search_company_info(company_name, country):
    """
    Search for company website and address using SearXNG
    Returns: dict with website, address, linkedin_url
    """
    base_url = "http://127.0.0.1:8080"
    
    # Sites to exclude (not official company websites)
    exclude_sites = [
        'jobindex', 'linkedin.com', 'indeed', 'glassdoor', 'emply', 
        'cepheo', 'logosconsult', 'microsoft.com', 'navision',
        'dynamics.com', 'facebook', 'twitter', 'youtube',
        'wikipedia', 'crunchbase', 'zoominfo', 'rocketreach',
        'forbes', 'bloomberg', 'reuters', 'finance.yahoo',
        '.pdf', 'viewforum', 'njacs', 'usmc.mil'
    ]
    
    results = {
        'website': None,
        'headquarters_address': None,
        'linkedin_url': None
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Search for official website
    try:
        query = f"{company_name} official website"
        url = f"{base_url}/search?q={requests.utils.quote(query)}&format=json"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for result in data.get('results', [])[:10]:
                result_url = result.get('url', '').lower()
                
                # Skip excluded sites
                if any(exclude in result_url for exclude in exclude_sites):
                    continue
                
                # Prefer short, clean domains
                if not results['website']:
                    results['website'] = result.get('url', '')
                    print(f"  ✅ Website: {results['website']}")
                    break
                    
    except Exception as e:
        print(f"  ⚠️  Website search failed: {e}")
    
    time.sleep(0.3)
    
    # Search for LinkedIn
    try:
        query = f"{company_name} LinkedIn"
        url = f"{base_url}/search?q={requests.utils.quote(query)}&format=json"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for result in data.get('results', [])[:5]:
                result_url = result.get('url', '')
                if 'linkedin.com/company' in result_url.lower():
                    results['linkedin_url'] = result_url
                    print(f"  💼 LinkedIn: {results['linkedin_url']}")
                    break
                    
    except Exception as e:
        print(f"  ⚠️  LinkedIn search failed: {e}")
    
    time.sleep(0.3)
    
    # Search for headquarters address
    try:
        query = f"{company_name} headquarters address" if country != "DK" else f"{company_name} hovedkvarter adresse"
        url = f"{base_url}/search?q={requests.utils.quote(query)}&format=json"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for result in data.get('results', [])[:5]:
                result_content = result.get('content', '')
                
                # Look for address patterns
                address_patterns = [
                    r'(\d{3,5}\s+[A-Z][a-z]+\s+(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Vej|Gade|Stræde|Allé)[,\s]+)',
                    r'([A-Z][a-z]+\s+(?:Vej|Gade|Stræde|Allé)\s+\d+[A-Z]?(?:\s*,?\s*\d{4}\s*[A-Z][a-z]*)?)',
                ]
                for pattern in address_patterns:
                    match = re.search(pattern, result_content)
                    if match:
                        results['headquarters_address'] = match.group(1).strip()
                        print(f"  📍 Address: {results['headquarters_address']}")
                        break
                        
    except Exception as e:
        print(f"  ⚠️  Address search failed: {e}")
    
    return results

def update_company(conn, company_id, updates):
    """Update a company record"""
    cursor = conn.cursor()
    
    # Add updated_at to updates
    updates['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values()) + [company_id]
    
    cursor.execute(f'''
        UPDATE companies 
        SET {set_clause}
        WHERE id = ?
    ''', values)
    
    conn.commit()
    return cursor.rowcount > 0

def enrich_companies(batch_size=100, process_all=False):
    """Enrich company data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find companies without proper website (currently has source URL instead)
    if process_all:
        cursor.execute('''
            SELECT id, company_name, country, website, source_url
            FROM companies
            WHERE website IS NULL OR website = ''
            ORDER BY created_at DESC
            LIMIT ?
        ''', (batch_size,))
    else:
        # Prioritize high-confidence companies without website
        cursor.execute('''
            SELECT id, company_name, country, website, source_url
            FROM companies
            WHERE (website IS NULL OR website = '' OR website LIKE '%jobindex%' OR website LIKE '%linkedin%')
            AND confidence_score >= 4
            ORDER BY confidence_score DESC, created_at DESC
            LIMIT ?
        ''', (batch_size,))
    
    companies = cursor.fetchall()
    print(f"📊 Found {len(companies)} companies to enrich\n")
    
    updated = 0
    skipped = 0
    
    for i, company in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] {company['company_name']} ({company['country']})")
        
        # Search for info
        info = search_company_info(company['company_name'], company['country'])
        
        updates = {}
        if info['website'] and info['website'] != company['source_url']:
            updates['website'] = info['website']
            print(f"  ✅ Website: {info['website']}")
        
        if info['headquarters_address']:
            updates['headquarters_address'] = info['headquarters_address']
            print(f"  📍 Address: {info['headquarters_address']}")
        
        if info['linkedin_url']:
            updates['linkedin_url'] = info['linkedin_url']
            print(f"  💼 LinkedIn: {info['linkedin_url']}")
        
        if updates:
            if update_company(conn, company['id'], updates):
                updated += 1
        else:
            skipped += 1
            print(f"  ⏭️  No new info found")
        
        # Small delay to avoid overwhelming SearXNG
        time.sleep(0.3)
        
        # Progress update every 10
        if i % 10 == 0:
            print(f"\n  📈 Progress: {updated} updated, {skipped} skipped\n")
    
    print(f"\n{'='*60}")
    print(f"✅ Enrichment complete!")
    print(f"   Updated: {updated}")
    print(f"   Skipped: {skipped}")
    
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enrich company data')
    parser.add_argument('--batch', type=int, default=50, help='Number of companies to process')
    parser.add_argument('--all', action='store_true', help='Process all companies (slow)')
    args = parser.parse_args()
    
    enrich_companies(batch_size=args.batch, process_all=args.all)
