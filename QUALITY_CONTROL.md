# Navision Database - Quality Control Protocol

## CRITICAL: NAV vs BC Distinction

**MÅL:** Kun virksomheder der bruger **Dynamics NAV (2009-2018)** - IKKE Business Central!

### ✅ Acceptable Evidence (NAV-specifik)
- Job postings mentioning: "C/AL", "NAV 2009", "NAV 2013", "NAV 2015", "NAV 2016", "NAV 2017", "NAV 2018"
- Partner references stating "Navision" or "Dynamics NAV" (not just "Business Central")
- Technology stack showing "Microsoft Dynamics NAV" with version 14 or earlier
- Forum posts from employees discussing NAV-specific features

### ❌ Reject (Likely BC, not NAV)
- Only mentions "Business Central" or "BC"
- "Dynamics 365 Business Central" without NAV reference
- Job postings only mentioning "AL" language (BC uses AL, NAV uses C/AL)
- TheirStack alone (doesn't distinguish NAV vs BC)

### Quality Score System
```
5 = Definitive NAV (C/AL + NAV version mentioned)
4 = Strong NAV evidence (Navision/Dynamics NAV named)
3 = Likely NAV (partner reference, context suggests NAV)
2 = Unclear (could be NAV or BC)
1 = Likely BC (reject)
0 = Confirmed BC (reject)
```

## Sources by Quality

### Tier 1 (Highest Quality)
- **Job postings with C/AL** - Definitive NAV
- **mibuso.com forum** - NAV community, version discussions
- **NAV-specific partner references** - Partners listing NAV customers

### Tier 2 (Good Quality)
- **LinkedIn profiles** mentioning "Dynamics NAV Developer"
- **Partner case studies** specifying NAV version
- **Technology surveys** distinguishing NAV from BC

### Tier 3 (Use with Caution)
- **TheirStack** - Must verify manually or cross-reference
- **General job boards** - Must check for C/AL vs AL
- **Company websites** - Often say "Business Central" even if on NAV

## Verification Process

1. **Initial scrape** - Gather candidates
2. **Evidence check** - Does it mention NAV specifically?
3. **Version check** - NAV 2009-2018? Or BC?
4. **Language check** - C/AL (NAV) or AL (BC)?
5. **Confidence score** - Assign 0-5
6. **Database insert** - Only if score ≥ 3

## Detective Feedback Loop

Detective subagent should:
1. Review low-confidence entries weekly
2. Find NEW sources with better NAV/BC distinction
3. Validate random samples from each source
4. Report data quality metrics, not just quantity

## Metrics That Matter

- **NAV-confidence ≥4**: Target 5,000+ companies
- **Source diversity**: 10+ independent sources
- **False positive rate**: <5% (BC companies marked as NAV)
- **Geographic coverage**: 20+ countries

---

**Last Updated:** 2026-03-26
**Status:** ACTIVE - All scrapers must follow this protocol
