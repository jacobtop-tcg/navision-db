#!/usr/bin/env python3
"""
Add VERIFIED NAV customers with PROOF
These are REAL companies using NAV (not BC!)
"""

import sqlite3
from datetime import datetime

VERIFIED_NAV_CUSTOMERS = [
    # From InfoClutch research
    {
        "name": "Louis Dreyfus Company",
        "country": "NL",
        "industry": "Agriculture",
        "employees": "~100,000",
        "revenue": "USD 50B+",
        "confidence": 5,
        "source": "infoclutch_verified",
        "proof": "Job posting: Using NAV for financial management, accounting and reporting"
    },
    {
        "name": "Arrow Electronics",
        "country": "US",
        "industry": "Distribution/Electronics",
        "employees": "~20,000",
        "revenue": "USD 37B",
        "confidence": 5,
        "source": "infoclutch_verified",
        "proof": "Job posting: Using MS Dynamics NAV as ERP system"
    },
    {
        "name": "MET Group",
        "country": "CH",
        "industry": "Energy",
        "employees": "985",
        "revenue": "EUR 17.9B",
        "confidence": 5,
        "source": "infoclutch_verified",
        "proof": "LinkedIn: Dynamics NAV implementation project"
    },
    {
        "name": "Universal Music Group",
        "country": "NL",
        "industry": "Entertainment/Music",
        "employees": "18,315",
        "revenue": "EUR 11.8B",
        "confidence": 5,
        "source": "infoclutch_verified",
        "proof": "Job posting: NAV essential for production system, purchase orders, inventory"
    },
    {
        "name": "Heineken",
        "country": "NL",
        "industry": "Beverages/Brewing",
        "employees": "88,497",
        "revenue": "EUR 35.9B",
        "confidence": 5,
        "source": "infoclutch_verified",
        "proof": "Careers page: Uses NAV alongside SAP S/4HANA"
    },
    
    # From previous verified searches
    {
        "name": "ACS Group",
        "country": "ES",
        "industry": "Construction",
        "employees": "157,284",
        "revenue": "USD 47B",
        "confidence": 5,
        "source": "appsruntheworld_verified",
        "proof": "Listed in Apps Run The World NAV customer database"
    },
    {
        "name": "Spar International",
        "country": "NL",
        "industry": "Retail",
        "employees": "50,000",
        "revenue": "USD 32B",
        "confidence": 5,
        "source": "appsruntheworld_verified",
        "proof": "Listed in Apps Run The World NAV customer database"
    },
    {
        "name": "Puma Energy",
        "country": "CH",
        "industry": "Energy/Oil",
        "employees": "3,137",
        "revenue": "USD 18.5B",
        "confidence": 5,
        "source": "appsruntheworld_verified",
        "proof": "Listed in Apps Run The World NAV customer database"
    },
]

if __name__ == "__main__":
    conn = sqlite3.connect('database/navision-global.db')
    cursor = conn.cursor()
    
    # Drop old table and recreate with correct schema
    cursor.execute('DROP TABLE IF EXISTS verified_nav_customers')
    cursor.execute('''
        CREATE TABLE verified_nav_customers (
            company_name TEXT PRIMARY KEY,
            country TEXT,
            industry TEXT,
            employee_count TEXT,
            revenue TEXT,
            confidence_score INTEGER,
            source TEXT,
            proof TEXT,
            verified_at TEXT
        )
    ''')
    
    inserted = 0
    for company in VERIFIED_NAV_CUSTOMERS:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO verified_nav_customers
                (company_name, country, industry, employee_count, revenue, confidence_score, source, proof, verified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company["name"],
                company["country"],
                company["industry"],
                company.get("employees", ""),
                company.get("revenue", ""),
                company["confidence"],
                company["source"],
                company["proof"],
                datetime.utcnow().isoformat()
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print(f"✅ {company['name']} ({company['country']})")
                print(f"   📊 {company.get('employees', '?')} employees, {company.get('revenue', '?')}")
                print(f"   📝 Proof: {company['proof'][:80]}...")
                print()
        except Exception as e:
            print(f"❌ {company['name']}: {e}")
    
    conn.commit()
    
    # Count verified
    cursor.execute("SELECT COUNT(*) FROM verified_nav_customers")
    verified_count = cursor.fetchone()[0]
    
    # Show all verified
    print(f"\n{'='*60}")
    print(f"✅ VERIFIED NAV CUSTOMERS: {verified_count}")
    print(f"{'='*60}")
    
    cursor.execute("SELECT company_name, country, industry, employee_count FROM verified_nav_customers ORDER BY confidence_score DESC")
    for row in cursor.fetchall():
        print(f"  • {row[0]} ({row[1]}) - {row[2]}")
    
    conn.close()
