# 🎯 Navision Database - Strategisk Udvidelsesplan

**Dato:** 2026-03-31  
**Mål:** Udvide database fra 44.500 → 100.000+ virksomheder  
**Fokus:** Job sites pr. land + LinkedIn deep-dive + Historiske data

---

## 📋 Executive Summary

Nuværende status:
- **44.500 virksomheder** i databasen
- **Kilder:** global_jobs, theirstack, linkedin_global, partners, microsoft_partners
- **Dækning:** 50+ lande, men overfladisk i mange

**Jacob's krav:**
1. ✅ De mest væsentlige job sites i hvert individuelt land
2. ✅ Historiske job opslag (sidste 2 år) via cached data
3. ✅ LinkedIn grundig gennemsøgning for personer der bruger Navision i nuværende job

---

## 🌍 DEL 1: Landespecifikke Job Portaler

### Prioritet 1: Nordics (DK, NO, SE, FI)

#### 🇩🇰 Danmark
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Jobindex | jobindex.dk | "Dynamics NAV", "Business Central", "Navision" | ✅ 2 år |
| Workable | workable.com | "Microsoft Dynamics" | ✅ 1 år |
| LinkedIn DK | linkedin.com/jobs | "Dynamics 365 BC" | ✅ 2 år |
| Glassdoor DK | glassdoor.dk | "NAV udvikler" | ⚠️ Begrænset |
| Karriere | karriere.dk | "ERP konsulent" | ✅ 1 år |
| Jobbank | jobbank.dk | "Navision support" | ❌ |

**Speciel kilde:**
- **Wayback Machine**: archive.org/web/*/jobindex.dk (gå tilbage til 2024)
- **Google Cache**: `cache:jobindex.dk "Dynamics NAV"`

#### 🇳🇴 Norge
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Jobbnorge | jobbnorge.no | "Dynamics NAV", "Business Central" | ✅ 2 år |
| Finn.no | finn.no/job | "Navision", "Microsoft Dynamics" | ✅ 1 år |
| LinkedIn NO | linkedin.com/jobs | "Dynamics 365" | ✅ 2 år |
| StepStone NO | stepstone.no | "ERP konsulent" | ⚠️ |
| Karriereco | karriereco.no | "NAV utvikler" | ❌ |

#### 🇸🇪 Sverige
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Blocket Jobb | blocketjobb.se | "Dynamics NAV", "Business Central" | ✅ 1 år |
| LinkedIn SE | linkedin.com/jobs | "Navision", "Dynamics 365" | ✅ 2 år |
| Indeed SE | indeed.se | "Microsoft Dynamics" | ⚠️ |
| Metrojobb | metrojobb.se | "NAV konsult" | ❌ |
| Jobbsafari | jobbsafari.se | "ERP system" | ❌ |

#### 🇫🇮 Finland
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| TE-palvelut | te-palvelut.fi | "Dynamics NAV", "Business Central" | ✅ 2 år |
| Oikotie Työpaikat | oikotie.fi/tyopaikat | "Navision", "Microsoft Dynamics" | ✅ 1 år |
| LinkedIn FI | linkedin.com/jobs | "Dynamics 365" | ✅ 2 år |
| Duunitori | duunitori.fi | "ERP asiantuntija" | ⚠️ |

---

### Prioritet 2: DACH (DE, AT, CH)

#### 🇩🇪 Tyskland
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| StepStone | stepstone.de | "Dynamics NAV", "Business Central" | ✅ 2 år |
| Indeed DE | indeed.de | "Microsoft Dynamics NAV" | ✅ 1 år |
| LinkedIn DE | linkedin.com/jobs | "Navision", "Dynamics 365 BC" | ✅ 2 år |
| XING | xing.com/jobs | "NAV Entwickler", "Dynamics Berater" | ✅ 2 år |
| Monster DE | monster.de | "ERP Consultant" | ⚠️ |
| Kimeta | kimeta.de | "Microsoft NAV" | ❌ |

**Speciel kilde:**
- **XING** er KÆMPE i Tyskland - mange Dynamics profiler
- **Kununu**: kununu.com (arbejdsgivervurderinger + jobs)

#### 🇦🇹 Østrig
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Karriere.at | karriere.at | "Dynamics NAV", "Business Central" |
| LinkedIn AT | linkedin.com/jobs | "Microsoft Dynamics" |
| XING AT | xing.com/jobs | "NAV Berater" |
| Der Standard | derstandard.at/stellenmarkt | "ERP" |

#### 🇨🇭 Schweiz
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Jobs.ch | jobs.ch | "Dynamics NAV", "Business Central" |
| LinkedIn CH | linkedin.com/jobs | "Dynamics 365" |
| Jobup.ch | jobup.ch | "Microsoft NAV" (fransk del) |
| XING CH | xing.com/jobs | "NAV Entwickler" |

---

### Prioritet 3: UK & Irland

#### 🇬🇧 United Kingdom
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Indeed UK | indeed.co.uk | "Dynamics NAV", "Business Central" | ✅ 2 år |
| LinkedIn UK | linkedin.com/jobs | "Microsoft Dynamics 365" | ✅ 2 år |
| Glassdoor UK | glassdoor.co.uk | "NAV Developer" | ⚠️ |
| Reed | reed.co.uk | "Dynamics Consultant" | ✅ 1 år |
| Totaljobs | totaljobs.com | "Business Central" | ✅ 1 år |
| CV-Library | cv-library.co.uk | "Navision" | ⚠️ |
| Monster UK | monster.co.uk | "ERP Consultant" | ❌ |

#### 🇮🇪 Irland
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| IrishJobs | irishjobs.ie | "Dynamics NAV", "Business Central" |
| LinkedIn IE | linkedin.com/jobs | "Microsoft Dynamics" |
| Jobs.ie | jobs.ie | "NAV Developer" |
| Indeed IE | indeed.ie | "Dynamics 365" |

---

### Prioritet 4: Benelux (NL, BE)

#### 🇳🇱 Holland
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Indeed NL | indeed.nl | "Dynamics NAV", "Business Central" | ✅ 2 år |
| LinkedIn NL | linkedin.com/jobs | "Microsoft Dynamics" | ✅ 2 år |
| Werk.nl | werk.nl | "NAV Ontwikkelaar" | ✅ 1 år |
| Glassdoor NL | glassdoor.nl | "Dynamics Consultant" | ⚠️ |
| Nationale Vacaturebank | nationalevacaturebank.nl | "ERP" | ❌ |

#### 🇧🇪 Belgien
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Indeed BE | indeed.be | "Dynamics NAV", "Business Central" |
| LinkedIn BE | linkedin.com/jobs | "Microsoft Dynamics" |
| StepStone BE | stepstone.be | "NAV Consultant" |
| Jobat | jobat.be | "Dynamics 365" (flamsk) |
| Le Soir Emploi | lesoiremploi.be | "Dynamics" (fransk) |

---

### Prioritet 5: Frankrig & Sydeuropa

#### 🇫🇷 Frankrig
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Indeed FR | indeed.fr | "Dynamics NAV", "Business Central" | ✅ 2 år |
| LinkedIn FR | linkedin.com/jobs | "Microsoft Dynamics 365" | ✅ 2 år |
| APEC | apec.fr | "Consultant Dynamics" | ✅ 1 år |
| Monster FR | monster.fr | "NAV Développeur" | ⚠️ |
| RégionJob | regionjob.com | "ERP Microsoft" | ❌ |
| Pole Emploi | pole-emploi.fr | "Gestionnaire PAIE" (offentlig) | ✅ 2 år |

#### 🇮🇹 Italien
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Indeed IT | indeed.it | "Dynamics NAV", "Business Central" |
| LinkedIn IT | linkedin.com/jobs | "Microsoft Dynamics" |
| Monster IT | monster.it | "Sviluppatore NAV" |
| InfoJobs | infojobs.it | "Consulente ERP" |
| Lavoropiu | lavoropiu.it | "Dynamics 365" |

#### 🇪🇸 Spanien
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Indeed ES | indeed.es | "Dynamics NAV", "Business Central" |
| LinkedIn ES | linkedin.com/jobs | "Microsoft Dynamics" |
| InfoJobs | infojobs.net | "Consultor Dynamics" |
| Monster ES | monster.es | "Desarrollador NAV" |
| Tecnoempleo | tecnoempleo.com | "ERP Microsoft" (tech focus) |

---

### Prioritet 6: Polen & Centraleuropa

#### 🇵🇱 Polen
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Pracuj.pl | pracuj.pl | "Dynamics NAV", "Business Central" | ✅ 2 år |
| LinkedIn PL | linkedin.com/jobs | "Microsoft Dynamics" | ✅ 2 år |
| OLX Praca | olx.pl/praca | "NAV Programista" | ⚠️ |
| Indeed PL | indeed.pl | "Dynamics 365" | ✅ 1 år |
| GoldenLine | goldenline.pl | "Konsultant Dynamics" (profiler) | ✅ 2 år |

#### 🇨🇿 Tjekkiet
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Jobs.cz | jobs.cz | "Dynamics NAV", "Business Central" |
| LinkedIn CZ | linkedin.com/jobs | "Microsoft Dynamics" |
| Prace.cz | prace.cz | "Vývojář NAV" |

#### 🇭🇺 Ungarn
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Profession.hu | profession.hu | "Dynamics NAV", "Business Central" |
| LinkedIn HU | linkedin.com/jobs | "Microsoft Dynamics" |
| Indeed HU | indeed.hu | "NAV Fejlesztő" |

---

### Prioritet 7: Nordamerika

#### 🇺🇸 USA
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Indeed US | indeed.com | "Dynamics NAV", "Business Central" | ✅ 2 år |
| LinkedIn US | linkedin.com/jobs | "Microsoft Dynamics 365 BC" | ✅ 2 år |
| Glassdoor | glassdoor.com | "NAV Developer" | ✅ 1 år |
| Monster | monster.com | "Dynamics Consultant" | ⚠️ |
| CareerBuilder | careerbuilder.com | "Business Central" | ⚠️ |
| Dice | dice.com | "Dynamics NAV" (tech focus) | ✅ 2 år |
| SimplyHired | simplyhired.com | "Microsoft ERP" | ❌ |

**Specielle kilder:**
- **Wayback Machine**: archive.org for gamle job postings
- **Google Cache**: `cache:indeed.com "Dynamics NAV" 2024..2026`

#### 🇨🇦 Canada
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Indeed CA | indeed.ca | "Dynamics NAV", "Business Central" |
| LinkedIn CA | linkedin.com/jobs | "Microsoft Dynamics" |
| Job Bank | jobbank.gc.ca | "ERP Consultant" (offentlig) |
| Workopolis | workopolis.com | "Dynamics 365" |
| Monster CA | monster.ca | "NAV Developer" |

---

### Prioritet 8: Asien-Pacific

#### 🇮🇳 Indien
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Naukri.com | naukri.com | "Dynamics NAV", "Business Central" | ✅ 2 år |
| LinkedIn IN | linkedin.com/jobs | "Microsoft Dynamics 365" | ✅ 2 år |
| Indeed IN | indeed.co.in | "NAV Developer" | ✅ 1 år |
| Glassdoor IN | glassdoor.co.in | "Dynamics Consultant" | ⚠️ |
| Monster IN | monsterindia.com | "Business Central" | ❌ |
| TimesJobs | timesjobs.com | "ERP Microsoft" | ⚠️ |

#### 🇯🇵 Japan
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Rikunabi | rikunabi.com | "Dynamics NAV", "Business Central" |
| LinkedIn JP | linkedin.com/jobs | "Microsoft Dynamics" |
| Doda | doda.jp | "ERP コンサルタント" |
| Indeed JP | indeed.co.jp | "Dynamics 365" |
| Mynavi | mynavi.jp | "NAV 開発者" |

#### 🇦🇺 Australien
| Portal | URL | Navision Keywords | Historisk |
|--------|-----|-------------------|-----------|
| Seek | seek.com.au | "Dynamics NAV", "Business Central" | ✅ 2 år |
| LinkedIn AU | linkedin.com/jobs | "Microsoft Dynamics" | ✅ 2 år |
| Indeed AU | indeed.com.au | "NAV Developer" | ✅ 1 år |
| Glassdoor AU | glassdoor.com.au | "Dynamics Consultant" | ⚠️ |
| Jora | jora.com | "Business Central" | ❌ |

#### 🇸🇬 Singapore
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| JobStreet | jobstreet.com.sg | "Dynamics NAV", "Business Central" |
| LinkedIn SG | linkedin.com/jobs | "Microsoft Dynamics" |
| Indeed SG | indeed.com.sg | "Dynamics 365" |
| MyCareersFuture | mycareersfuture.gov.sg | "ERP Consultant" (offentlig) |

---

### Prioritet 9: Mellemøsten

#### 🇦🇪 UAE (Dubai/Abu Dhabi)
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Bayt.com | bayt.com | "Dynamics NAV", "Business Central" |
| LinkedIn AE | linkedin.com/jobs | "Microsoft Dynamics" |
| Indeed AE | indeed.ae | "NAV Developer" |
| GulfTalent | gulftalent.com | "Dynamics Consultant" |
| Naukrigulf | naukrigulf.com | "Business Central" |

---

### Prioritet 10: Latinamerika

#### 🇧🇷 Brasilien
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Indeed BR | indeed.com.br | "Dynamics NAV", "Business Central" |
| LinkedIn BR | linkedin.com/jobs | "Microsoft Dynamics" |
| Catho | catho.com.br | "Consultor Dynamics" |
| Vagas | vagas.com.br | "Desenvolvedor NAV" |
| InfoJobs BR | infojobs.com.br | "ERP Microsoft" |

#### 🇲🇽 Mexico
| Portal | URL | Navision Keywords |
|--------|-----|-------------------|
| Indeed MX | indeed.com.mx | "Dynamics NAV", "Business Central" |
| LinkedIn MX | linkedin.com/jobs | "Microsoft Dynamics" |
| OCCMundial | occ.com.mx | "Consultor Dynamics" |
| Computrabajo | computrabajo.com.mx | "Desarrollador NAV" |

---

## 🔍 DEL 2: Historiske Data (Sidste 2 År)

### Strategi 1: Wayback Machine (archive.org)

**Script:** `scripts/historical-wayback.py`

```python
# Eksempel: Jobindex.dk historik
# https://web.archive.org/web/20240101000000*/jobindex.dk

import requests
from datetime import datetime, timedelta

def get_wayback_snapshots(url, from_date, to_date):
    """Hent alle snapshots af en URL i en periode"""
    cdx_url = f"http://web.archive.org/cdx/search/cdx?url={url}&from={from_date}&to={to_date}"
    response = requests.get(cdx_url)
    return response.text.split('\n')

# Brug: Hent job postings fra 2024-2026
# Extract company names from archived job pages
```

**Target URLs for arkivering:**
- jobindex.dk (DK) - 2 år tilbage
- jobbnorge.no (NO) - 2 år tilbage
- stepstone.de (DE) - 2 år tilbage
- indeed.com (US) - 2 år tilbage
- pracuj.pl (PL) - 2 år tilbage

### Strategi 2: Google Cache

**Script:** `scripts/google-cache-scraper.py`

```python
# Google Cache query eksempler:
# cache:jobindex.dk "Dynamics NAV"
# cache:linkedin.com/jobs "Business Central"

# Brug Google Custom Search API med date ranges
# date_after: 2024-01-01
# date_before: 2026-03-31
```

**Queries:**
```
site:jobindex.dk "Dynamics NAV" OR "Business Central" 2024..2026
site:linkedin.com/jobs "Microsoft Dynamics" 2024..2026
site:stepstone.de "Dynamics NAV" 2024..2026
```

### Strategi 3: Job Aggregator APIs

Nogle job sites har APIs der tillader historisk søgning:

| API | URL | Historisk | Rate Limit |
|-----|-----|-----------|------------|
| Adzuna | api.adzuna.com | ✅ 2 år | 500/day (free) |
| The Muse | themuse.com/api | ⚠️ 1 år | 100/day |
| USAJobs | data.usajobs.gov | ✅ 5 år | Unlimited (offentlig) |
| LinkedIn API | developer.linkedin.com | ❌ Kun aktuelle | 100/day |

**Script:** `scripts/job-api-historical.py`

---

## 👥 DEL 3: LinkedIn Deep-Dive (Personer)

### Strategi 1: LinkedIn Profil Søgning via Google Dorks

**Script:** `scripts/linkedin-people-deep.py`

```python
# Google Dorks for LinkedIn profiler:
queries = [
    'site:linkedin.com/in/ "Dynamics NAV" AND "current"',
    'site:linkedin.com/in/ "Business Central" AND "nuværende"',
    'site:linkedin.com/in/ "Microsoft Dynamics" AND "consultant"',
    'site:linkedin.com/in/ "Navision" AND "developer"',
    'site:linkedin.com/in/ "Dynamics 365" AND "ERP"',
    
    # Sprog-specifikke
    'site:linkedin.com/in/ "Dynamics NAV" AND "utvecklare"',  # SE
    'site:linkedin.com/in/ "Dynamics NAV" AND "Entwickler"',  # DE
    'site:linkedin.com/in/ "Dynamics NAV" AND "développeur"', # FR
    'site:linkedin.com/in/ "Dynamics NAV" AND "ontwikkelaar"', # NL
]
```

**Fordele:**
- Ingen LinkedIn login required
- Kan scrape via SearXNG
- Historiske profiler (cached af Google)

### Strategi 2: LinkedIn Company Pages → Employees

**Script:** `scripts/linkedin-company-employees.py`

```python
# Trin:
# 1. Find virksomheder der bruger Navision (allerede i DB)
# 2. Gå til deres LinkedIn company page
# 3. Scrap employees der nævner "Dynamics" i deres profil

# Eksempel URL:
# linkedin.com/company/MICROSOFT/people/?keywords=Dynamics
# linkedin.com/company/NAV-PARTNER/people/
```

### Strategi 3: LinkedIn Job Postings → Hiring Companies

**Script:** `scripts/linkedin-jobs-companies.py`

```python
# Find ALLE aktuelle Dynamics NAV jobs på LinkedIn
# Extract company name fra hvert job posting
# Tilføj til database med high confidence (de søger aktivt Navision folk!)

queries = [
    '"Dynamics NAV" developer',
    '"Business Central" consultant',
    '"Microsoft Dynamics" ERP',
    '"Navision" developer',
    '"Dynamics 365" Business Central',
]

countries = ['DK', 'NO', 'SE', 'DE', 'UK', 'NL', 'BE', 'US', 'FR', 'ES', 'IT', 'PL']
```

### Strategi 4: LinkedIn Groups

**Script:** `scripts/linkedin-groups.py`

```python
# Dynamics NAV / Business Central grupper:
groups = [
    "Microsoft Dynamics NAV User Group",
    "Dynamics 365 Business Central Professionals",
    "Navision Professionals",
    "Microsoft Dynamics ERP Community",
    "Dynamics NAV Developers",
]

# Scrap group member lists
# Extract company names from member profiles
```

---

## 🛠️ Implementeringsplan

### Fase 1: LinkedIn Deep-Dive (UGE 1)
**Mål:** +10.000 virksomheder fra LinkedIn

| Script | Prioritet | Estimeret Yield |
|--------|-----------|-----------------|
| `linkedin-people-deep.py` | 🔴 Høj | 5.000 virksomheder |
| `linkedin-jobs-companies.py` | 🔴 Høj | 3.000 virksomheder |
| `linkedin-company-employees.py` | 🟡 Medium | 2.000 virksomheder |
| `linkedin-groups.py` | 🟢 Lav | 500 virksomheder |

**Tidsestimat:** 3-4 dage

### Fase 2: Landespecifikke Job Portaler (UGE 2-3)
**Mål:** +25.000 virksomheder fra job sites

#### Uge 2: Nordics + DACH
- DK: jobindex.dk, karriere.dk (+2.000)
- NO: jobbnorge.no, finn.no (+1.500)
- SE: blocketjobb.se, metrojobb.se (+2.000)
- DE: stepstone.de, xing.com (+5.000)
- AT/CH: karriere.at, jobs.ch (+1.000)

#### Uge 3: UK + Benelux + Frankrig
- UK: reed.co.uk, totaljobs.com (+3.000)
- NL: werk.nl, nationalevacaturebank.nl (+2.000)
- BE: jobat.be, lesoiremploi.be (+1.000)
- FR: apec.fr, regionjob.com (+2.500)

**Tidsestimat:** 10 dage

### Fase 3: Historiske Data (UGE 4)
**Mål:** +10.000 virksomheder fra arkiver

| Kilde | Metode | Estimeret Yield |
|-------|--------|-----------------|
| Wayback Machine | jobindex.dk 2024-2025 | 3.000 |
| Wayback Machine | stepstone.de 2024-2025 | 4.000 |
| Google Cache | LinkedIn jobs 2024-2026 | 2.000 |
| Adzuna API | Historical jobs API | 1.000 |

**Tidsestimat:** 5-7 dage

### Fase 4: Resten af Europa + Asien (UGE 5-6)
**Mål:** +10.000 virksomheder

- PL, CZ, HU: 3.000
- IT, ES, PT: 3.000
- IN, JP, SG: 2.000
- AU, NZ: 1.000
- UAE, SA: 1.000

---

## 📊 Forventet Resultat

| Fase | Nye Virksomheder | Total Database |
|------|------------------|----------------|
| Start | - | 44.500 |
| Fase 1 (LinkedIn) | +10.000 | 54.500 |
| Fase 2 (Job Nordics+DACH) | +11.500 | 66.000 |
| Fase 3 (Job UK+Benelux+FR) | +8.500 | 74.500 |
| Fase 4 (Historisk) | +10.000 | 84.500 |
| Fase 5 (Resten) | +10.000 | 94.500 |

**Mål:** 100.000+ virksomheder inden 6 uger

---

## 🔧 Nye Scripts der skal laves

### 1. `scripts/linkedin-people-deep.py`
```python
# Google Dorks + SearXNG scraping
# Extract company names from LinkedIn profiles
# Keywords: "Dynamics NAV", "Business Central", etc.
# Languages: EN, DA, NO, SV, DE, FR, NL, ES, IT, PL
```

### 2. `scripts/historical-wayback.py`
```python
# Wayback Machine CDX API
# Fetch archived job pages
# Extract company names from historical postings
# Date range: 2024-01-01 to 2026-03-31
```

### 3. `scripts/job-portal-country.py`
```python
# Generic scraper for country-specific job portals
# Config-driven (config/job-portals.json)
# Supports: jobindex.dk, stepstone.de, reed.co.uk, etc.
# Historical data via site search with date filters
```

### 4. `scripts/google-cache-scraper.py`
```python
# Google Custom Search API
# Date-range queries for cached job postings
# Extract companies from search results
```

### 5. `scripts/adzuna-api-scraper.py`
```python
# Adzuna API integration
# Historical job postings (2 years)
# Country-specific searches
```

---

## 📝 Config Opdateringer

### `config/job-portals-expanded.json` (NY)
```json
{
  "portals": {
    "DK": [
      {"name": "jobindex", "url": "https://www.jobindex.dk", "keywords": ["Dynamics NAV", "Business Central", "Navision"], "historical": true},
      {"name": "karriere", "url": "https://www.karriere.dk", "keywords": ["Dynamics", "ERP"], "historical": false}
    ],
    "DE": [
      {"name": "stepstone", "url": "https://www.stepstone.de", "keywords": ["Dynamics NAV", "Business Central"], "historical": true},
      {"name": "xing", "url": "https://www.xing.com/jobs", "keywords": ["Dynamics", "NAV Entwickler"], "historical": true}
    ]
    // ... flere lande
  }
}
```

### `config/linkedin-queries.json` (NY)
```json
{
  "people_queries": [
    "\"Dynamics NAV\" AND current",
    "\"Business Central\" AND consultant",
    "\"Microsoft Dynamics\" AND ERP",
    "\"Navision\" AND developer"
  ],
  "job_queries": [
    "\"Dynamics NAV\" developer",
    "\"Business Central\" consultant"
  ],
  "languages": {
    "en": ["current", "consultant", "developer"],
    "da": ["nuværende", "konsulent", "udvikler"],
    "de": ["aktuell", "Berater", "Entwickler"],
    "fr": ["actuel", "consultant", "développeur"]
  }
}
```

---

## ⚠️ Risici & Udfordringer

### 1. Rate Limiting
- **LinkedIn:** Meget aggressiv bot detection
- **Løsning:** Brug Google Dorks + SearXNG istedet for direkte scraping
- **Løsning:** Respektfulde delays (2-5 sekunder mellem requests)

### 2. Data Kvalitet
- **Problem:** Gamle job postings = virksomheder der måske ikke bruger Navision længere
- **Løsning:** Tag kun postings fra sidste 2 år
- **Løsning:** Verificer med sekundære kilder (company website, LinkedIn)

### 3. Sprog Barrierer
- **Problem:** Job postings på lokale sprog (tysk, fransk, japansk, etc.)
- **Løsning:** Brug oversatte keywords i searches
- **Løsning:** NLP for company name extraction (flersproget)

### 4. Duplicate Entries
- **Problem:** Samme virksomhed fundet via multiple kilder
- **Løsning:** Existing deduplication logic i scraper.py
- **Løsning:** Fuzzy matching på company names

---

## ✅ Næste Skridt

1. **Godkend plan** → Jacob reviewer og godkender strategien
2. **Start med Fase 1** → LinkedIn deep-dive scripts
3. **Kør LinkedIn scripts** → Forvent +10.000 virksomheder
4. **Evaluer resultater** → Justér strategi hvis nødvendigt
5. **Fortsæt med Fase 2-5** → Rull ud gradvist

---

**Spørgsmål til Jacob:**
- Skal jeg starte med at kode LinkedIn deep-dive scripts først?
- Er der specifikke lande der skal prioriteres højere?
- Vil du have jeg laver en hurtig prototype (1-2 lande) før fuld udrulning?
