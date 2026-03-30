# NAVISION DATABASE - PROGRESS TRACKER
# This file survives context refreshes - READ IT EVERY SESSION

## CURRENT STATUS
- **Total Companies:** 4630
- **Goal:** 20000
- **Progress:** 23.1%
- **Remaining:** 15370

## LAST UPDATED
- **Timestamp:** 2026-03-25T21:45:00Z
- **Session:** Jacob's main session
- **Agent:** Orion

## EXPANSION PRIORITY (in order)

### TIER 1 - Immediate (next 1000)
1. **Germany** - Target: 2401 (currently 401, need +2000)
   - Focus: Manufacturing, Automotive, Industrial
   - Sources: Industry directories, company registries
   
2. **France** - Target: 1697 (currently 197, need +1500)
   - Focus: Retail, Luxury, Aerospace
   - Sources: Industry associations, chambers of commerce

3. **Italy** - Target: 1052 (currently 52, need +1000)
   - Focus: Fashion, Manufacturing, Food
   - Sources: Trade associations, export directories

4. **Spain** - Target: 1051 (currently 51, need +1000)
   - Focus: Retail, Tourism, Construction
   - Sources: Business registries, tourism boards

5. **India** - Target: 1138 (currently 138, need +1000)
   - Focus: IT Services, Manufacturing, Pharma
   - Sources: NASSCOM, industry directories

### TIER 2 - Next 5000
- Eastern Europe: Poland, Czech, Hungary, Romania (+2000)
- Asia: Japan, Korea, China, SEA (+2000)
- Latin America: Brazil, Mexico, Argentina (+1000)

### TIER 3 - Final 10000
- Middle East: Saudi Arabia, UAE, Israel (+1000)
- Africa: South Africa, Nigeria, Kenya (+1000)
- Oceania: Australia, New Zealand (+500)
- Nordics: Denmark, Norway, Sweden, Finland (+1500)
- Benelux: Belgium, Netherlands, Luxembourg (+1000)
- UK & Ireland: (+1500)
- USA & Canada: (+2000)
- Other Europe: (+1500)

## BATCH STRATEGY

**Batch Size:** 100-200 companies per batch
**Batches per Hour:** 3-4 batches
**Expected Rate:** 300-600 companies/hour

## SOURCES TO EXPLOIT

### High-Yield Sources (use first)
1. **TheirStack** - 36,240 companies available
   - URL: https://theirstack.com/en/technology/navision
   - By country: DE (1734), US (2789), NL (825), UK (1146)
   
2. **ThomsonData** - 32,821 companies
   - URL: thomsondata.com/customer-base/microsoft-dynamics-nav-customers-list.php
   - Paid but comprehensive

3. **EU Business Registries** - Free
   - Each country has public business registry
   - Search for ERP software users

4. **LinkedIn Sales Navigator** - Premium
   - Search by technology: "Microsoft Dynamics NAV"
   - Filter by company size, industry, location

5. **Industry Associations** - Free
   - Manufacturing associations
   - Retail associations
   - IT services associations

### Medium-Yield Sources
- Job boards (companies hiring NAV developers = using NAV)
- Partner directories (Microsoft partners list their customers)
- Conference attendee lists (NAV/BC conferences)
- Forum members (mibuso.com, dynamicsuser.net)

## SCRIPTS TO RUN

### Primary Expansion Script
```bash
cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db
python3 scripts/expansion_batch.py --country DE --batch 1
python3 scripts/expansion_batch.py --country FR --batch 1
python3 scripts/expansion_batch.py --country IT --batch 1
python3 scripts/expansion_batch.py --country ES --batch 1
python3 scripts/expansion_batch.py --country IN --batch 1
```

### Status Check
```bash
python3 scripts/check-threshold.py
python3 scripts/scraper.py --status
```

## THRESHOLDS

- ✅ 3002 - Reached 2026-03-25
- ✅ 3052 - Reached 2026-03-25
- ✅ 3277 - Reached 2026-03-25
- ✅ 4209 - Current threshold
- ⏳ 5000 - Next milestone (370 remaining)
- ⏳ 10000 - Mid-point
- ⏳ 15000 - Advanced
- 🎯 20000 - GOAL

## SESSION NOTES

### What Worked Today
- Manual batch inserts (100-200 companies per batch)
- Country-by-country approach
- Focus on major companies first (enterprise)
- Using TheirStack data as reference

### What Didn't Work
- Subagent collaboration (technical limitations)
- Relying only on daemon (SearXNG rate limited)
- Long pauses between batches

### Key Learnings
- Need to maintain momentum (no long pauses)
- Batch size of 100-200 is optimal
- Enterprise companies first (easier to find)
- Update progress file after each batch

## NEXT SESSION CHECKLIST

1. [ ] Read this file FIRST
2. [ ] Check current count: `python3 scripts/scraper.py --status`
3. [ ] Continue with Tier 1 countries (DE, FR, IT, ES, IN)
4. [ ] Add 500+ companies in first hour
5. [ ] Update this file with new count
6. [ ] Repeat until 20,000 reached

## CONTACT

If stuck or need guidance:
- Jacob: @jacob_top (Telegram)
- Documentation: /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db/COLLABORATION.md

---

**REMEMBER:** Momentum is key! Never stop for more than 5 minutes.
If context refreshes, read this file and CONTINUE WHERE YOU LEFT OFF.

**CURRENT TARGET:** 5000 companies (370 more needed)
**NEXT BATCH:** Germany +200 companies
