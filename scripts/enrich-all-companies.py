#!/usr/bin/env python3
"""
MASS ENRICHMENT - Alle virksomheder mangler data
Bruger deresStack + LinkedIn + web scraping til at tilføje:
- Website (hvis mangler)
- Industry (hvis mangler)
- Bedre source_url (hvis kun generisk LinkedIn search)
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
import requests

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def extract_company_from_url(url):
    """Udtræk virksomhedsnavn fra URL"""
    if not url:
        return None
    # Fjern protocol og www
    url = re.sub(r'https?://', '', url)
    url = re.sub(r'www\.', '', url)
    # Tag første del af domain
    domain = url.split('/')[0].split('.')[0]
    return domain.lower()

def guess_industry_from_evidence(evidence):
    """Gæt branche baseret på evidence tekst"""
    if not evidence:
        return None
    
    evidence_lower = evidence.lower()
    
    # IT/Software
    if any(word in evidence_lower for word in ['developer', 'udvikler', 'software', 'it', 'erp', 'dynamics', 'navision']):
        return 'IT Services'
    
    # Retail
    if any(word in evidence_lower for word in ['retail', 'butik', 'shop', 'ecommerce', 'webshop']):
        return 'Retail'
    
    # Manufacturing
    if any(word in evidence_lower for word in ['manufacturing', 'produktion', 'factory', 'industrial']):
        return 'Manufacturing'
    
    # Finance
    if any(word in evidence_lower for word in ['finance', 'bank', 'insurance', 'finans', 'forsikring']):
        return 'Finance'
    
    # Healthcare
    if any(word in evidence_lower for word in ['health', 'hospital', 'clinic', 'sundhed', 'hospital', 'pharma']):
        return 'Healthcare'
    
    # Logistics
    if any(word in evidence_lower for word in ['logistics', 'shipping', 'transport', 'fragt', 'levering']):
        return 'Logistics'
    
    # Construction
    if any(word in evidence_lower for word in ['construction', 'byggeri', 'entreprenør', 'builder']):
        return 'Construction'
    
    # Energy
    if any(word in evidence_lower for word in ['energy', 'energi', 'oil', 'gas', 'renewable']):
        return 'Energy'
    
    # Food & Beverage
    if any(word in evidence_lower for word in ['food', 'beverage', 'fødevarer', 'restaurant', 'catering']):
        return 'Food & Beverages'
    
    return None

def enrich_all():
    """Enrich ALLE virksomheder der mangler data"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter MASS ENRICHMENT...")
    print("=" * 80)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Find virksomheder der mangler website ELLER industry
    cur.execute('''
        SELECT id, company_name, country, industry, evidence_text, source_url, website
        FROM companies
        WHERE 
            (website IS NULL OR website = '')
            OR (industry IS NULL OR industry = '')
        LIMIT 10000
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Fundet {len(rows)} virksomheder der mangler data")
    print()
    
    updated_websites = 0
    updated_industries = 0
    batch_size = 100
    
    for i, row in enumerate(rows):
        company_id = row['id']
        company_name = row['company_name']
        current_industry = row['industry']
        current_website = row['website']
        evidence = row['evidence_text']
        source_url = row['source_url']
        
        updates = {}
        
        # 1. Gæt industry fra evidence
        if not current_industry and evidence:
            guessed_industry = guess_industry_from_evidence(evidence)
            if guessed_industry:
                updates['industry'] = guessed_industry
                updated_industries += 1
        
        # 2. Ekstraher website fra source_url hvis det er en virksomheds-side
        if not current_website and source_url:
            # Hvis source_url indeholder virksomhedens navn, brug det som website
            company_domain = extract_company_from_url(source_url)
            if company_domain and company_domain.lower() in company_name.lower():
                # Dette er sandsynligvis virksomhedens eget website
                updates['website'] = source_url
                updated_websites += 1
        
        # 3. Hvis source_url er LinkedIn search, prøv at finde rigtig website
        if not current_website and source_url and 'linkedin.com' in source_url:
            # Prøv at gætte website fra company name
            # Fjern specialtegn fra navn
            clean_name = re.sub(r'[^\w\s-]', '', company_name.lower())
            clean_name = re.sub(r'\s+', '-', clean_name)
            
            # Gem til senere verificering (ikke automatisk)
            pass
        
        # Opdater hvis vi har changes
        if updates:
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [company_id]
            
            cur.execute(f'''
                UPDATE companies
                SET {set_clause}
                WHERE id = ?
            ''', values)
        
        # Commit i batches
        if (i + 1) % batch_size == 0:
            conn.commit()
            print(f"  ⏳ Progress: {i+1}/{len(rows)} (websites: {updated_websites}, industries: {updated_industries})")
    
    # Final commit
    conn.commit()
    conn.close()
    
    print()
    print("=" * 80)
    print(f"✅ MASS ENRICHMENT FÆRDIG!")
    print(f"   Websites tilføjet: {updated_websites}")
    print(f"   Industries gættet: {updated_industries}")
    print(f"   Total opdateret: {updated_websites + updated_industries}")
    print()
    print(f"💡 Kør: python3 scripts/export-verified.py")
    
    return updated_websites, updated_industries

if __name__ == '__main__':
    try:
        enrich_all()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
