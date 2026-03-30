#!/usr/bin/env python3
"""
Add all BC/NAV partners from ERP Software Blog list
Partners = Customers or potential customers!
"""

COMPANIES = [
    # US Partners from erpsoftwareblog.com/list-state/
    {"name": "DLD Business Solutions", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Dexpro Dynamics", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Calsoft Systems", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Technology Management Concepts", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Knaster Technology Group", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "CAL Business Solutions", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Custom Systems", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Caf2Code", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "ACE Micro", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Ternpoint Solutions", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Logan Consulting", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "OTT Inc", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "TrinSoft", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Dynamics Square USA", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "The TM Group", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "MetaOption", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Admiral Consulting Group", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Alpha Variance Solutions", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Citrin Cooperman", "country": "US", "industry": "Professional Services", "source": "erp_partners"},
    {"name": "360 Visibility", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Stoneridge Software", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Velosio", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Njevity", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "iCepts Technology Group", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Elliott Clark Consulting", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Custom Information Services", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Rand Group", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "JourneyTeam", "country": "US", "industry": "IT Services", "source": "erp_partners"},
    {"name": "JOVACO Solutions", "country": "CA", "industry": "IT Services", "source": "erp_partners"},
    {"name": "Kwixand Solutions", "country": "CA", "industry": "IT Services", "source": "erp_partners"},
    
    # UK Partners
    {"name": "Dynamics Square UK", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Azzure IT", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Technology Management", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Incremental Group", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "TVision Technology", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Xperience Group", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Kick ICT Group", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Chorus UK", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "m-hance", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Tecvia", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Synergy Technology", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Total Enterprise Solutions", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Enhanced", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    {"name": "Bam Boom Cloud", "country": "GB", "industry": "IT Services", "source": "uk_partners"},
    
    # Europe/Global Partners
    {"name": "Gestisoft", "country": "CA", "industry": "IT Services", "source": "global_partners"},
    {"name": "Alithya", "country": "CA", "industry": "IT Services", "source": "global_partners"},
    {"name": "Hitachi Solutions", "country": "JP", "industry": "IT Services", "source": "global_partners"},
    {"name": "BDO Digital", "country": "US", "industry": "Professional Services", "source": "global_partners"},
    {"name": "Avanade", "country": "US", "industry": "IT Services", "source": "global_partners"},
    {"name": "RSM", "country": "US", "industry": "Professional Services", "source": "global_partners"},
    {"name": "Deloitte", "country": "US", "industry": "Professional Services", "source": "global_partners"},
    {"name": "Columbus", "country": "DK", "industry": "IT Services", "source": "global_partners"},
    {"name": "WinfoSoft", "country": "US", "industry": "IT Services", "source": "global_partners"},
    {"name": "ScienceSoft", "country": "US", "industry": "IT Services", "source": "global_partners"},
    {"name": "Folio3 Dynamics", "country": "GB", "industry": "IT Services", "source": "global_partners"},
    {"name": "HSO", "country": "NL", "industry": "IT Services", "source": "global_partners"},
    {"name": "Nexer", "country": "SE", "industry": "IT Services", "source": "global_partners"},
    {"name": "Preact", "country": "GB", "industry": "IT Services", "source": "global_partners"},
    {"name": "K3 Business Technology", "country": "GB", "industry": "IT Services", "source": "global_partners"},
    {"name": "Prodware", "country": "FR", "industry": "IT Services", "source": "global_partners"},
    {"name": "Agilitas", "country": "SE", "industry": "IT Services", "source": "global_partners"},
]

if __name__ == "__main__":
    import sqlite3
    from datetime import datetime
    
    conn = sqlite3.connect('database/navision-global.db')
    cursor = conn.cursor()
    
    inserted = 0
    for company in COMPANIES:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO companies 
                (company_name, country, industry, confidence_score, source, evidence_type, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company["name"],
                company["country"],
                company["industry"],
                4,  # High confidence - verified partner
                company["source"],
                "partner_directory",
                datetime.utcnow().isoformat()
            ))
            if cursor.rowcount > 0:
                inserted += 1
                print(f"✅ Added: {company['name']} ({company['country']})")
        except Exception as e:
            print(f"❌ Error adding {company['name']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Complete! Inserted {inserted} new companies")
