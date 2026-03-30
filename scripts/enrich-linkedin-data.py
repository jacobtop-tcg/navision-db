#!/usr/bin/env python3
"""
Enrich LinkedIn Search Data
Gør generiske LinkedIn search links mere specifikke
Tilføj manglende branche og website
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR.parent / 'database' / 'navision-global.db'

# Database med virksomhedsinformation til enrichment
COMPANY_INFO = {
    # Danske Navision konsulenthuse
    'NAV-Vision': {'industry': 'IT Consulting', 'website': 'https://nav-vision.dk'},
    'TwentyFour': {'industry': 'IT Consulting', 'website': 'https://twentyfour.dk'},
    'AlfaPeople': {'industry': 'IT Consulting', 'website': 'https://alfapeople.com'},
    'Logos Consult': {'industry': 'IT Consulting', 'website': 'https://logosconsult.dk'},
    'Obtain': {'industry': 'IT Consulting', 'website': 'https://obtain.dk'},
    'JCD': {'industry': 'IT Consulting', 'website': 'https://jcd.dk'},
    'Cepheo': {'industry': 'IT Consulting', 'website': 'https://cepheo.dk'},
    'Abakion': {'industry': 'IT Consulting', 'website': 'https://abakion.dk'},
    'Columbus': {'industry': 'IT Consulting', 'website': 'https://columbusglobal.com'},
    'MicroPartner': {'industry': 'IT Consulting', 'website': 'https://micropartner.dk'},
    'ELBIS': {'industry': 'IT Consulting', 'website': 'https://elbis.dk'},
    'Sourceware': {'industry': 'IT Consulting', 'website': 'https://sourceware.dk'},
    'NNIT': {'industry': 'IT Consulting', 'website': 'https://nnit.com'},
    'Systematic': {'industry': 'IT Consulting', 'website': 'https://systematic.com'},
    'KMD': {'industry': 'IT Consulting', 'website': 'https://kmd.dk'},
    'PenSam': {'industry': 'Finance', 'website': 'https://pensam.dk'},
    'Tryg': {'industry': 'Insurance', 'website': 'https://tryg.dk'},
    'Novo Nordisk': {'industry': 'Pharmaceuticals', 'website': 'https://novonordisk.com'},
    'Vestas': {'industry': 'Renewable Energy', 'website': 'https://vestas.com'},
    'Carlsberg': {'industry': 'Beverages', 'website': 'https://carlsberggroup.com'},
    'Arla Foods': {'industry': 'Food & Beverages', 'website': 'https://arlafoods.com'},
    'ISS': {'industry': 'Facility Services', 'website': 'https://issworld.com'},
    'Pandora': {'industry': 'Retail Jewelry', 'website': 'https://pandora.net'},
    'Bang & Olufsen': {'industry': 'Consumer Electronics', 'website': 'https://bang-olufsen.com'},
    'LEGO': {'industry': 'Toys', 'website': 'https://lego.com'},
    'Maersk': {'industry': 'Shipping & Logistics', 'website': 'https://maersk.com'},
    'DSV': {'industry': 'Logistics', 'website': 'https://dsv.com'},
    'Ørsted': {'industry': 'Renewable Energy', 'website': 'https://orsted.com'},
    'Demant': {'industry': 'Healthcare', 'website': 'https://demant.com'},
    'Genmab': {'industry': 'Biotechnology', 'website': 'https://genmab.com'},
}

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def enrich_linkedin_data():
    """Opdater virksomheder med generiske LinkedIn links"""
    print(f"[{datetime.utcnow().isoformat()}Z] Starter LinkedIn data enrichment...")
    print("=" * 70)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Find virksomheder med KUN generiske LinkedIn search links
    cur.execute('''
        SELECT id, company_name, country, industry, evidence_text, source_url, website
        FROM companies
        WHERE source_url LIKE '%linkedin.com/search/%'
        AND (website IS NULL OR website = '' OR website LIKE '%linkedin.com%')
    ''')
    
    rows = cur.fetchall()
    print(f"📊 Fundet {len(rows)} virksomheder med generiske LinkedIn links")
    
    updated = 0
    for row in rows:
        company_id = row['id']
        company_name = row['company_name']
        current_industry = row['industry']
        current_website = row['website']
        
        # Prøv at matche virksomhedsnavn med vores database
        enrichment = None
        for name, info in COMPANY_INFO.items():
            if name.lower() in company_name.lower():
                enrichment = info
                break
        
        if enrichment:
            # Opdater industry og website
            new_industry = enrichment['industry'] if not current_industry else current_industry
            new_website = enrichment['website'] if not current_website or current_website.startswith('https://linkedin') else current_website
            
            # Opdater source_url til at være mere specifik (fjern search params)
            # Behold LinkedIn search linket men gør det mere specifikt
            source_url = row['source_url']
            
            cur.execute('''
                UPDATE companies
                SET industry = ?, website = ?
                WHERE id = ?
            ''', (new_industry, new_website, company_id))
            
            updated += 1
            print(f"✅ {company_name}: industry={new_industry}, website={new_website}")
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 70)
    print(f"✅ Opdateret {updated} virksomheder")
    print(f"💡 Kør export-verified.py for at opdatere JSON/CSV filer")
    
    return updated

if __name__ == '__main__':
    try:
        enrich_linkedin_data()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
