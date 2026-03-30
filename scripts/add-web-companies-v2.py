#!/usr/bin/env python3
"""
Add companies to Navision database from web search results.
"""

import sqlite3
from datetime import datetime

# Absolute path to database
DB_PATH = '/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db'

# Companies found from web search - Norway, Finland, Netherlands, Belgium
COMPANIES = [
    # NORWAY (NO)
    {"name": "Noteless", "country": "NO", "industry": "Healthcare AI"},
    {"name": "SportAI", "country": "NO", "industry": "Sports Technology"},
    {"name": "WeWillWrite", "country": "NO", "industry": "Education"},
    {"name": "Sensor Globe", "country": "NO", "industry": "Agriculture AI"},
    {"name": "Spoor", "country": "NO", "industry": "AI"},
    {"name": "Sonair", "country": "NO", "industry": "Hardware Sensors"},
    {"name": "Two", "country": "NO", "industry": "Commerce"},
    {"name": "K33", "country": "NO", "industry": "Financial Services"},
    {"name": "ONiO", "country": "NO", "industry": "Energy"},
    {"name": "Attensi", "country": "NO", "industry": "Education VR"},
    {"name": "Plaace", "country": "NO", "industry": "Analytics"},
    {"name": "Iris.ai", "country": "NO", "industry": "AI Science"},
    {"name": "Glint Solar", "country": "NO", "industry": "AI Solar"},
    {"name": "Actithera", "country": "NO", "industry": "Biotechnology"},
    {"name": "Pistachio", "country": "NO", "industry": "AI Cybersecurity"},
    {"name": "Vind AI", "country": "NO", "industry": "AI Wind"},
    {"name": "Sloyd", "country": "NO", "industry": "3D Technology"},
    {"name": "Telescope", "country": "NO", "industry": "Real Estate AI"},
    {"name": "Völur", "country": "NO", "industry": "AI Meat Processing"},
    {"name": "SportAI", "country": "NO", "industry": "Computer Vision"},
    {"name": "Vespa.ai", "country": "NO", "industry": "AI"},
    {"name": "Calluna Pharma", "country": "NO", "industry": "Pharmaceuticals"},
    {"name": "Tings", "country": "NO", "industry": "Marketplace"},
    {"name": "Ignite", "country": "NO", "industry": "Supply Chain"},
    {"name": "Laiout", "country": "NO", "industry": "PropTech"},
    {"name": "Enode", "country": "NO", "industry": "Energy Tech"},
    
    # FINLAND (FI)
    {"name": "Donut Lab", "country": "FI", "industry": "Transportation"},
    {"name": "SelfHack AI", "country": "FI", "industry": "AI"},
    {"name": "Pauhu", "country": "FI", "industry": "Software"},
    {"name": "Flatta", "country": "FI", "industry": "Software"},
    {"name": "Untuvia", "country": "FI", "industry": "Software"},
    {"name": "Cronvall", "country": "FI", "industry": "Marketplace"},
    {"name": "CHAOS", "country": "FI", "industry": "AI"},
    {"name": "Perkly", "country": "FI", "industry": "AI FinTech"},
    {"name": "ReOrbit", "country": "FI", "industry": "Aerospace"},
    {"name": "ONEiO", "country": "FI", "industry": "IT"},
    {"name": "DataCrunch.io", "country": "FI", "industry": "Cloud Computing"},
    {"name": "Varjo", "country": "FI", "industry": "VR/AR Hardware"},
    {"name": "Spacent", "country": "FI", "industry": "Real Estate"},
    {"name": "CloEE", "country": "FI", "industry": "AI"},
    {"name": "Inven", "country": "FI", "industry": "AI M&A"},
    {"name": "Verge Motorcycles", "country": "FI", "industry": "Electric Vehicles"},
    {"name": "Klu", "country": "FI", "industry": "Legal Tech"},
    {"name": "Woima", "country": "FI", "industry": "Energy"},
    {"name": "Measurlabs", "country": "FI", "industry": "Testing"},
    {"name": "StayingBee", "country": "FI", "industry": "Software"},
    
    # NETHERLANDS (NL)
    {"name": "Runnr.ai", "country": "NL", "industry": "AI Hospitality"},
    {"name": "Floepp", "country": "NL", "industry": "Infrastructure Monitoring"},
    {"name": "Edgeway", "country": "NL", "industry": "Surveillance AI"},
    {"name": "Agurotech", "country": "NL", "industry": "AgriTech"},
    {"name": "LUMABS", "country": "NL", "industry": "Healthcare Diagnostics"},
    {"name": "daisys.ai", "country": "NL", "industry": "AI Voice"},
    {"name": "InConnect.io", "country": "NL", "industry": "Safety Platform"},
    {"name": "Ore Energy", "country": "NL", "industry": "Energy Storage"},
    {"name": "Farmless", "country": "NL", "industry": "Fermentation"},
    {"name": "Lapsi Health", "country": "NL", "industry": "HealthTech"},
    {"name": "Naya", "country": "NL", "industry": "Hardware"},
    {"name": "Neople", "country": "NL", "industry": "AI Customer Support"},
    {"name": "Solvimon", "country": "NL", "industry": "Billing Platform"},
    {"name": "Monumental", "country": "NL", "industry": "Autonomous Vehicles"},
    {"name": "Insify", "country": "NL", "industry": "Insurance Tech"},
    {"name": "Source.ag", "country": "NL", "industry": "E-commerce"},
    {"name": "Finom", "country": "NL", "industry": "Fintech"},
    {"name": "Fero", "country": "NL", "industry": "Fintech"},
    {"name": "Leyden Labs", "country": "NL", "industry": "Biotech"},
    {"name": "Carbon Equity", "country": "NL", "industry": "Climate Tech"},
    {"name": "Workwize", "country": "NL", "industry": "IT Hardware"},
    {"name": "Carv", "country": "NL", "industry": "AI Recruiting"},
    {"name": "Cradle", "country": "NL", "industry": "AI Protein Engineering"},
    {"name": "Quatt", "country": "NL", "industry": "Heat Pump Tech"},
    {"name": "Next Sense", "country": "NL", "industry": "Smart Building AI"},
    {"name": "CarbonX", "country": "NL", "industry": "Battery Materials"},
    
    # BELGIUM (BE)
    {"name": "Collibra", "country": "BE", "industry": "Data Intelligence"},
    {"name": "Simera Sense", "country": "BE", "industry": "Space Technology"},
    {"name": "Aikido Security", "country": "BE", "industry": "Cybersecurity"},
    {"name": "Cowboy", "country": "BE", "industry": "Urban Mobility"},
    {"name": "Qover", "country": "BE", "industry": "InsurTech"},
    {"name": "Voxel Sensors", "country": "BE", "industry": "Sensors"},
    {"name": "Greenomy", "country": "BE", "industry": "Sustainability"},
    {"name": "Protealis", "country": "BE", "industry": "Biotech"},
    {"name": "Vaultspeed", "country": "BE", "industry": "Cybersecurity"},
    {"name": "Raito", "country": "BE", "industry": "Legal Tech"},
    {"name": "Dualyx", "country": "BE", "industry": "Biotech"},
    {"name": "Timefold", "country": "BE", "industry": "AI Optimization"},
    {"name": "TechWolf", "country": "BE", "industry": "Tech Recruiting"},
    {"name": "BelGaN", "country": "BE", "industry": "Semiconductors"},
    {"name": "Swave Photonics", "country": "BE", "industry": "Photonics"},
    {"name": "Astrivax", "country": "BE", "industry": "Biotech Vaccines"},
]

def add_companies():
    """Add companies to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    added = 0
    skipped = 0
    
    for company in COMPANIES:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO companies 
                (company_name, country, industry, evidence_type, source, discovered_at, created_at, updated_at)
                VALUES (?, ?, ?, 'web_search', ?, ?, ?, ?)
            """, (
                company['name'],
                company['country'],
                company['industry'],
                'web_search',
                datetime.now(),
                datetime.now(),
                datetime.now()
            ))
            added += 1
        except Exception as e:
            skipped += 1
            print(f"Error adding {company['name']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {added} companies to database")
    print(f"⚠️  Skipped {skipped} (likely duplicates)")
    
    # Show new totals
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM companies')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT country, COUNT(*) FROM companies GROUP BY country ORDER BY COUNT(*) DESC')
    print("\n📊 Database by country:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    conn.close()
    
    print(f"\n🎯 Total: {total} companies")
    print(f"📈 Next threshold: 1001 (need {1001 - total} more)")

if __name__ == '__main__':
    add_companies()
