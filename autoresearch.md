# Navision Data Detective - Autoresearch Setup

## MÅL
Optimer strategier til at finde **Navision/Dynamics NAV** virksomheder (IKKE Business Central)

## METRIC
```
METRIC navision_companies_found=NUMBER
```
**Direction:** higher = better

## TEST INPUTS (5 scenarier)

### Test 1: USA Job Search
```
Find 10 virksomheder i USA der bruger Navision/Dynamics NAV
Kilder: Indeed, Glassdoor, LinkedIn
Signaturer: "Navision Developer", "Dynamics NAV", "C/AL"
```

### Test 2: Tyskland Partner Sites
```
Find 10 virksomheder i Tyskland fra partner kundelister
Kilder: COSMO CONSULT, Reply, lokale partnere
Signaturer: "Dynamics NAV Kunde", "Navision implementation"
```

### Test 3: mibuso.com Forum
```
Find 10 aktive Navision brugere fra mibuso.com forum
Kilder: Forum profiler, diskussioner
Signaturer: "NAV 2013/2015/2016/2017/2018", "C/AL"
```

### Test 4: UK Job Market
```
Find 10 virksomheder i UK med Navision jobopslag
Kilder: Reed, TotalJobs, LinkedIn UK
Signaturer: "Navision Consultant", "Dynamics NAV Developer"
```

### Test 5: Nordic (udenfor DK)
```
Find 10 virksomheder i Norge/Sverige med Navision
Kilder: LinkedIn SE/NO, lokale job sites
Signaturer: "Navision", "Dynamics NAV" (ikke kun "Business Central")
```

## EVAL KRITERIER (Binary Pass/Fail)

1. **found_5_plus** = Fundet mindst 5 virksomheder?
2. **navision_proof** = Alle har Navision-bevis (ikke kun BC)?
3. **no_duplicates** = Ingen dupliker i resultater?
4. **source_documented** = Alle kilder dokumenteret?
5. **contact_info** = Mindst 50% har website/email?
6. **country_correct** = Alle i korrekt land?

## RUNS PER EXPERIMENT
5 (for statistisk signifikans)

## BUDGET CAP
50 eksperimenter

## FILES IN SCOPE
- navision-db/scripts/sources/*.py
- navision-db/config/sources.json
- navision-db/state/queue.json

## CONSTRAINTS
- Må KUN finde Navision/Dynamics NAV (2009-2018)
- Må IKKE kun finde "Business Central" uden NAV reference
- Skal undgå dupliker
- Skal dokumentere kilder

## START COMMAND
```bash
cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db
python3 scripts/detective_runner.py --test
```
