#!/usr/bin/env python3
"""
Tilføj SMOKING GUNS til databasen
Rigtige kunder med verificerede beviser
"""

import sqlite3
from datetime import datetime

DB_PATH = '/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db'

# SMOKING GUNS - Rigtige kunder med beviser
SMOKING_GUNS = [
    # Danmark
    ('Kaufmann ApS', 'DK', 'Kundecase: NAV er økonomisk rygrad for 45 butikker', 'https://9altitudes.com/dk/kundereferencer/kaufmann'),
    ('Bramidan A/S', 'DK', 'CEO: "Go-live gik bedre end forventet - fungerede dagen efter"', 'https://elbek-vejrup.dk/vidensbank/wiki/navision/'),
    ('BKI Foods A/S', 'DK', 'CFO: "Forbedrede planlægning og indkøb med NAV"', 'https://elbek-vejrup.dk/vidensbank/wiki/navision/'),
    ('Lomax', 'DK', 'Tilfreds NAV kunde (obtain.dk)', 'https://obtain.dk/'),
    ('Dana Lim', 'DK', 'Tilfreds NAV kunde (obtain.dk)', 'https://obtain.dk/'),
    ('Matas', 'DK', 'Tilfreds NAV kunde (obtain.dk)', 'https://obtain.dk/'),
    ('Novenco Marine & Offshore', 'DK', 'Tilfreds NAV kunde (obtain.dk)', 'https://obtain.dk/'),
    ('inco', 'DK', 'Gået live med Dynamics NAV integreret med LS Retail', 'https://jcd.dk/cases/pos-hardware-microsoft-dynamics-nav-med-integration-til-ls-retail-hos-inco/'),
    ('Hospidana', 'DK', 'Opgraderede fra NAV 2009 til BC Cloud (jan 2025)', 'https://www.vektus.dk/hospidana/'),
    ('Georg Berg A/S', 'DK', 'CEO: "Gik live - kørte løn 4 dage efter skift"', 'https://dynamicsinspire.dk/dynamics-nav/'),
    
    # International
    ('Cranswick', 'UK', 'Bruger Microsoft Dynamics NAV MRP (Consumer Packaged Goods)', 'https://www.appsruntheworld.com/customers-database/products/view/microsoft-dynamics-nav-mrp'),
    ('RS Medical', 'US', 'Bruger Microsoft Dynamics NAV MRP (Manufacturing)', 'https://www.appsruntheworld.com/customers-database/products/view/microsoft-dynamics-nav-mrp'),
    ('Wentworth Laboratories', 'UK', 'Bruger Microsoft Dynamics NAV MRP (Manufacturing)', 'https://www.appsruntheworld.com/customers-database/products/view/microsoft-dynamics-nav-mrp'),
    ('Wakou USA', 'US', 'Implemented Microsoft Dynamics NAV (Food & Beverage manufacturer)', 'https://www.calsoft.com/examples-different-industries-using-erp/'),
    ('Vipp', 'DK', 'Bruger Microsoft Dynamics NAV som ERP (integrated with WMS)', 'https://www.scm.dk/vipp-sikre-højt-kvalitetsniveau-med-ny-wms-løsning'),
]

def add_smoking_guns():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    added = 0
    existing = 0
    
    for company_name, country, evidence, url in SMOKING_GUNS:
        # Check if exists
        cur.execute('SELECT id FROM companies WHERE company_name = ? AND source_url = ?', 
                  (company_name, url))
        
        if cur.fetchone():
            existing += 1
        else:
            # Insert new
            cur.execute('''
                INSERT INTO companies 
                (company_name, country, evidence_type, evidence_text, 
                 confidence_score, source, source_url, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name,
                country,
                'smoking_gun',
                evidence,
                5,  # Maximum confidence - verified smoking gun
                'smoking_gun_hunt',
                url,
                datetime.utcnow().isoformat() + 'Z'
            ))
            added += 1
    
    conn.commit()
    conn.close()
    
    print(f'✅ TILFØJET: {added} smoking guns')
    print(f'⏭️  Allerede eksisterende: {existing}')
    print(f'📊 Total smoking guns: {added + existing}')
    
    return added

if __name__ == '__main__':
    add_smoking_guns()
