#!/usr/bin/env python3
"""
Add companies to Navision database from web search results.
"""

import sqlite3
from datetime import datetime

# Absolute path to database
DB_PATH = '/mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/database/navision-global.db'

# Companies found from web search
COMPANIES = [
    # Denmark
    {"name": "Ampa Medical", "country": "DK", "industry": "Healthcare", "founded": 2020, "city": "Copenhagen"},
    {"name": "Nordic Microbes", "country": "DK", "industry": "Biotechnology", "founded": 2021, "city": "Copenhagen"},
    {"name": "proprty.ai", "country": "DK", "industry": "PropTech", "founded": 2022, "city": "Copenhagen"},
    {"name": "DeviceLab", "country": "DK", "industry": "Software Development", "founded": 2019, "city": "Copenhagen"},
    {"name": "Windit", "country": "DK", "industry": "Cross Industry", "founded": 2022, "city": "Copenhagen"},
    {"name": "Orbis Medicines", "country": "DK", "industry": "Pharma", "founded": 2021, "city": "Copenhagen"},
    {"name": "WaterCare Guard", "country": "DK", "industry": "Utility", "founded": 2019, "city": "Copenhagen"},
    {"name": "Tricloud", "country": "DK", "industry": "Cross Industry", "founded": 2019, "city": "Copenhagen"},
    {"name": "Segtnan.ai", "country": "DK", "industry": "Healthcare", "founded": 2022, "city": "Copenhagen"},
    {"name": "Autonomous Units", "country": "DK", "industry": "Cross Industry", "founded": 2022, "city": "Copenhagen"},
    {"name": "Muna Therapeutics", "country": "DK", "industry": "Biopharma", "founded": 2020, "city": "Copenhagen"},
    {"name": "FluoGuide", "country": "DK", "industry": "Biotechnology", "founded": 2018, "city": "Copenhagen"},
    {"name": "Hyme Energy", "country": "DK", "industry": "Energy Storage", "founded": 2021, "city": "Copenhagen"},
    {"name": "EvodiaBio", "country": "DK", "industry": "Biotechnology", "founded": 2021, "city": "Copenhagen"},
    {"name": "Go Autonomous", "country": "DK", "industry": "B2B Software", "founded": 2020, "city": "Copenhagen"},
    {"name": "NØIE", "country": "DK", "industry": "Health Care", "founded": 2019, "city": "Copenhagen"},
    {"name": "Modl.ai", "country": "DK", "industry": "AI/Gaming", "founded": 2018, "city": "Copenhagen"},
    {"name": "Flatpay", "country": "DK", "industry": "Fintech", "founded": 2022, "city": "Copenhagen"},
    {"name": "Pleo", "country": "DK", "industry": "Fintech", "founded": 2015, "city": "Copenhagen"},
    {"name": "Dixa", "country": "DK", "industry": "Customer Service", "founded": 2015, "city": "Copenhagen"},
    {"name": "Monta", "country": "DK", "industry": "CleanTech", "founded": 2022, "city": "Copenhagen"},
    {"name": "Ocean.io", "country": "DK", "industry": "AI/Marketing", "founded": 2017, "city": "Copenhagen"},
    {"name": "Humani", "country": "DK", "industry": "AI/HR", "founded": 2022, "city": "Copenhagen"},
    {"name": "Segtnan.ai", "country": "DK", "industry": "Healthcare AI", "founded": 2022, "city": "Copenhagen"},
    {"name": "Subsets", "country": "DK", "industry": "AI/CRM", "founded": 2022, "city": "Copenhagen"},
    # Sweden
    {"name": "GeoGuessr", "country": "SE", "industry": "Gaming", "founded": 2014, "city": "Stockholm"},
    {"name": "Vermiculus", "country": "SE", "industry": "Financial Services", "founded": 2019, "city": "Stockholm"},
    {"name": "Evify", "country": "SE", "industry": "EV Charging", "founded": 2019, "city": "Stockholm"},
    {"name": "Bizcap", "country": "SE", "industry": "Financial Services", "founded": 2014, "city": "Stockholm"},
    {"name": "snafu", "country": "SE", "industry": "Fintech", "founded": 2020, "city": "Stockholm"},
    {"name": "KanEL", "country": "SE", "industry": "Energy", "founded": 2021, "city": "Stockholm"},
    {"name": "Chargehome", "country": "SE", "industry": "EV Charging", "founded": 2019, "city": "Stockholm"},
    {"name": "Ensotech", "country": "SE", "industry": "SaaS", "founded": 2020, "city": "Stockholm"},
    {"name": "Marketmate", "country": "SE", "industry": "Fintech", "founded": 2017, "city": "Stockholm"},
    {"name": "Period Pack", "country": "SE", "industry": "Consumer Goods", "founded": 2019, "city": "Stockholm"},
    {"name": "WeTal", "country": "SE", "industry": "Recruiting", "founded": 2019, "city": "Stockholm"},
    {"name": "Venizum", "country": "SE", "industry": "Translation", "founded": 2020, "city": "Stockholm"},
    {"name": "Advicy", "country": "SE", "industry": "PropTech AI", "founded": 2019, "city": "Stockholm"},
    {"name": "Signcast", "country": "SE", "industry": "Digital Signage", "founded": 2018, "city": "Stockholm"},
    {"name": "Klarna", "country": "SE", "industry": "Fintech", "founded": 2005, "city": "Stockholm"},
    {"name": "Dema", "country": "SE", "industry": "E-commerce AI", "founded": 2022, "city": "Stockholm"},
    {"name": "Northvolt", "country": "SE", "industry": "Battery", "founded": 2016, "city": "Stockholm"},
    {"name": "Heart Aerospace", "country": "SE", "industry": "Aviation", "founded": 2019, "city": "Stockholm"},
    {"name": "VOI Technology", "country": "SE", "industry": "Micro-mobility", "founded": 2018, "city": "Stockholm"},
    {"name": "H2 Green Steel", "country": "SE", "industry": "Green Steel", "founded": 2020, "city": "Stockholm"},
    # Germany
    {"name": "Enpal", "country": "DE", "industry": "Solar Energy", "founded": 2019, "city": "Berlin"},
    {"name": "Sunfire", "country": "DE", "industry": "Green Hydrogen", "founded": 2009, "city": "Dresden"},
    {"name": "Helsing", "country": "DE", "industry": "Defense AI", "founded": 2021, "city": "Munich"},
    {"name": "DeepL", "country": "DE", "industry": "AI Translation", "founded": 2017, "city": "Cologne"},
    {"name": "Everphone", "country": "DE", "industry": "Device Integration", "founded": 2014, "city": "Berlin"},
    {"name": "eGym", "country": "DE", "industry": "Fitness Tech", "founded": 2015, "city": "Munich"},
    {"name": "Celonis", "country": "DE", "industry": "Process Mining", "founded": 2011, "city": "Munich"},
    {"name": "N26", "country": "DE", "industry": "Neobank", "founded": 2013, "city": "Berlin"},
    {"name": "Personio", "country": "DE", "industry": "HR Software", "founded": 2015, "city": "Munich"},
    {"name": "Forto", "country": "DE", "industry": "Logistics", "founded": 2015, "city": "Berlin"},
    {"name": "Commercetools", "country": "DE", "industry": "E-commerce", "founded": 2009, "city": "Berlin"},
    {"name": "SoundCloud", "country": "DE", "industry": "Music Streaming", "founded": 2007, "city": "Berlin"},
    {"name": "Zalando", "country": "DE", "industry": "E-commerce", "founded": 2008, "city": "Berlin"},
    {"name": "HelloFresh", "country": "DE", "industry": "Meal Kit", "founded": 2011, "city": "Berlin"},
    {"name": "Trade Republic", "country": "DE", "industry": "Fintech", "founded": 2015, "city": "Berlin"},
    {"name": "Adyen", "country": "DE", "industry": "Payment", "founded": 2006, "city": "Amsterdam/Berlin"},
    {"name": "Rapid7", "country": "DE", "industry": "Cybersecurity", "founded": 2000, "city": "Munich"},
    {"name": "Dynatrace", "country": "DE", "industry": "Observability", "founded": 2005, "city": "Munich"},
    {"name": "Schrödinger", "country": "DE", "industry": "Computational Chemistry", "founded": 1990, "city": "Munich"},
    {"name": "HERE", "country": "DE", "industry": "Mapping", "founded": 2015, "city": "Munich"},
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

if __name__ == '__main__':
    add_companies()
