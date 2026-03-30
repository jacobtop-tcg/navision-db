# Navision Global Database

**Automatisk database over virksomheder der bruger Microsoft Navision/Dynamics 365 Business Central**

---

## 🎯 Formål

At opbygge og vedligeholde en **global database** over alle identificerbare virksomheder der bruger Microsoft Navision eller Dynamics 365 Business Central (on-premise).

---

## 📊 Nu Status

- **Totalt i database:** 343 virksomheder
- **Land:** DK (Danmark)
- **Kilder:** navision-sandheden-db
- **Dato:** 2026-03-20

---

## 🏗️ System Arkitektur

```
navision-db/
├── database/
│   ├── navision-global.db          # ÉN SQLite database (sand kilde)
│   ├── navision-global.json        # JSON eksport
│   └── navision-global.csv         # CSV eksport
├── scripts/
│   ├── scraper.py                  # Hovedscraper (kør selvstændigt)
│   ├── sources/                    # Kilde-specifikke scrapere
│   │   ├── theirstack.py           # TheirStack teknologi-scraping
│   │   ├── jobportals.py           # Jobportal scraping
│   │   ├── partners.py             # Partner website scraping
│   │   └── ...                     # Flere kilder
│   └── utils/                      # Utility funktioner
├── state/
│   ├── progress.json               # Hvilke kilder er færdige
│   ├── queue.json                  # Hvad skal scrapes næste
│   ├── errors.log                  # Fejllog
│   └── last-run.txt                # Tidspunkt for sidste kørsel
├── config/
│   ├── sources.json                # Hvilke kilder er aktive
│   ├── countries.json              # Hvilke lande skal scrapes
│   └── rate-limits.json            # Rate limiting konfiguration
├── documentation/                  # Dokumentation
└── archive/                        # Gamle data arkiveres her
```

---

## 🚀 Hurtig Start

### 1. Kør scraper (manuel)

```bash
cd navision-db
python3 scripts/scraper.py --status
```

### 2. Kør alle pending scrapes

```bash
python3 scripts/scraper.py --auto
```

### 3. Kør specifik kilde

```bash
python3 scripts/scraper.py --source theirstack --country NO
```

### 4. Tjek status

```bash
python3 scripts/scraper.py --status
```

---

## 🤖 Automatisk Kørsel (Set & Forget)

### Cron Job (Linux)

Tilføj til crontab (`crontab -e`):

```bash
# Kør hver 6. time
0 */6 * * * cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db && python3 scripts/scraper.py --auto >> logs/scraper.log 2>&1
```

### Heartbeat Task (OpenClaw)

Tilføj til `HEARTBEAT.md`:

```
# Navision Database Scraping
Check navision-db status and run pending scrapes
```

---

## 📋 Database Skema

### Tabel: `companies`

| Felt | Type | Beskrivelse |
|------|------|-------------|
| `id` | INTEGER | Auto-increment ID |
| `company_name` | TEXT | Virksomhedsnavn |
| `country` | TEXT | Land (DK, NO, SE, etc.) |
| `website` | TEXT | Virksomheds hjemmeside |
| `industry` | TEXT | Branche |
| `employees` | TEXT | Antal medarbejdere |
| `revenue` | TEXT | Omsætning |
| `evidence_type` | TEXT | Type bevis (job_posting, case_study, etc.) |
| `evidence_text` | TEXT | HVORFOR tror vi de bruger NAV |
| `confidence_score` | INTEGER | 1-5 stjerner |
| `source` | TEXT | Hvilken kilde fandt dette |
| `source_url` | TEXT | URL til bevis |
| `discovered_at` | TEXT | Hvornår fundet |
| `created_at` | TEXT | Database timestamp |
| `is_verified` | BOOLEAN | Er verificeret |

---

## 🔧 Udvid Systemet

### Tilføj ny kilde

1. Opret `scripts/sources/my_source.py`

```python
def scrape(country='DK'):
    # Din scraping logik
    return [
        {
            'company_name': 'Company A',
            'country': country,
            'evidence_type': 'my_source',
            'evidence_text': 'Found via...',
            'confidence_score': 4,
            'source_url': 'https://...'
        }
    ]
```

2. Tilføj til `config/sources.json`

```json
{
  "my_source": {
    "enabled": true,
    "priority": 6,
    "rate_limit": {...}
  }
}
```

3. Kør: `python3 scripts/scraper.py --source my_source --country DK`

### Tilføj nyt land

1. Tilføj til `config/countries.json`

```json
{
  "code": "US",
  "name": "United States",
  "language": "en",
  "job_portals": ["indeed.com", "linkedin.com"],
  "partner_websites": true,
  "priority": 9
}
```

2. Kør: `python3 scripts/scraper.py --source theirstack --country US`

---

## 📊 Data Kvalitet

### Confidence Score (1-5)

- ⭐⭐⭐⭐⭐ (5): Direkte bevis (case study, kundecitat)
- ⭐⭐⭐⭐ (4): Teknologisk detektion (TheirStack)
- ⭐⭐⭐ (3): Jobopslag (virksomhed søger NAV-folk)
- ⭐⭐ (2): Indirekte bevis (partner reference)
- ⭐ (1): Estimeret/markedsdata

### Verification

- `is_verified = 1`: Direkte bevis fra officiel kilde
- `is_verified = 0`: Indirekte bevis

---

## 🗂️ Filstruktur

```
navision-db/
├── database/                    # Produksjonsdata
├── scripts/                     # Scrapere
├── state/                       # System tilstand (overlever resets)
├── config/                      # Konfiguration
├── documentation/               # Dokumentasjon
└── archive/                     # Arkiverte versjoner
```

---

## 🔄 Surviving Session Resets

Systemet er designet til at overleve session resets:

1. **State er fil-baseret** - `state/progress.json` gemmer hvad der er gjort
2. **Database er permanent** - `database/navision-global.db` er altid tilgængelig
3. **Queue er eksisterende** - `state/queue.json` gemmer pending opgaver
4. **Logs er persistente** - Fejl og status logges til filer

Når en ny session starter, kan den bare:
```bash
python3 scripts/scraper.py --status  # Se hvad der er gjort
python3 scripts/scraper.py --auto    # Fortsæt hvor du stoppede
```

---

## 📈 Fremtidige Forbedringer

- [ ] Browser automation (Playwright) for JavaScript sites
- [ ] API integration (LinkedIn, Jobindex)
- [ ] Multi-threaded scraping
- [ ] Web UI for visualisering
- [ ] Email alerts for nye fund
- [ ] Automatic deduplication
- [ ] Confidence score machine learning

---

## 🆘 Fejlfinding

### Database kan ikke åbnes

```bash
# Tjek filen eksisterer
ls -la database/navision-global.db

# Reparér database
sqlite3 database/navision-global.db "PRAGMA integrity_check"
```

### Scraper kører ikke

```bash
# Kør med debug output
python3 scripts/scraper.py --auto --verbose

# Tjek logs
cat state/errors.log
```

### Duplikater i database

```bash
sqlite3 database/navision-global.db "
DELETE FROM companies 
WHERE rowid NOT IN (
    SELECT MAX(rowid) 
    FROM companies 
    GROUP BY company_name, country, source
)"
```

---

## 📞 Support

Spørgsmål? Tjek dokumentationen eller koden.

---

**System oprettet:** 2026-03-20  
**Version:** 1.0.0  
**Status:** Production Ready ✅
