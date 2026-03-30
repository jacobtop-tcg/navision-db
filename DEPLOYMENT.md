# 🚀 Deployment Guide - Navision Database Dashboard

## ✅ Hvad der er klar

- ✅ **Export script** - Eksporterer database til JSON
- ✅ **Auto-export daemon** - Kører automatisk hvert 5. minut
- ✅ **Streamlit app** - Lækkert dashboard med filtre og søgning
- ✅ **Git repo** - Initialiseret med alle filer

---

## 📋 Trin-for-trin Deployment

### 1. Opret GitHub Repo

Gå til: https://github.com/new

**Repository name:** `navision-db`  
**Visibility:** Public (gratis Streamlit Cloud)  
**Don't initialize with README** (allerede lavet)

### 2. Push til GitHub

```bash
cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db

# Opret remote (skift <your-username> med dit GitHub username)
git remote add origin https://github.com/<your-username>/navision-db.git

# Push
git push -u origin master
```

### 3. Deploy til Streamlit Cloud

1. Gå til: https://streamlit.io/cloud
2. Log ind med GitHub
3. Klik **"New app"**
4. Vælg repo: `navision-db`
5. **Main file path:** `streamlit_app.py`
6. Klik **"Deploy"**

### 4. 🎉 Klar!

Din app er nu live på:
```
https://navision-db-<your-username>.streamlit.app
```

---

## 🔄 Auto-Updates

### Lokalt (nu)

Auto-export daemon kører allerede:
- Kører hvert 5. minut
- Eksporterer SQLite → JSON
- Appen læser JSON filer automatisk

### Streamlit Cloud (når deployet)

**Mulighed 1: Manual export** (simpelst)
- Kør export scriptet manuelt på GitHub hver gang du vil opdatere
- Push til GitHub
- Streamlit auto-redeployer

**Mulighed 2: GitHub Actions** (automatisk)
- Lav en GitHub Action der kører export
- Push JSON til repo
- Streamlit læser JSON

**Mulighed 3: Database som Git LFS** (bedst)
- Gem database i repo med Git LFS
- Streamlit appen query'r database direkte
- Ingen export needed

---

## 🎨 Features i Appen

### 🔍 Søgning
- Søg i virksomhedsnavn
- Søg i branche
- Søg i evidence (bevis)

### 🌍 Filtre
- **Lande:** Vælg flere lande (checkbox)
- **Kvalitet:** Slider 1-5 stjerner
- **Kilder:** Vælg datakilde (TheirStack, LinkedIn, etc.)

### 📊 Dashboard
- KPI cards: Total, høj kvalitet, lande, kilder
- Top 10 lande (pie chart)
- Kilde fordeling (bar chart)
- Kvalitetsfordeling (bar chart)

### 📥 Download
- Download filteret data som CSV
- Filnavn med timestamp

### ⚡ Auto-refresh
- Knap til manuel opdatering
- Data cache i 5 minutter

---

## 🛠️ Tekniske Detaljer

### Filstruktur
```
navision-db/
├── database/
│   └── navision-global.db    # SQLite database (37,660+ virksomheder)
├── web-export/
│   ├── companies.json        # Exported data (læst af app)
│   ├── companies.csv         # CSV export
│   └── metadata.json         # Statistik
├── scripts/
│   ├── export-for-web.py     # Eksporter SQLite → JSON
│   └── auto-export-daemon.py # Auto-run export
├── streamlit_app.py          # Main app
└── requirements.txt          # Python dependencies
```

### Dependencies
- `streamlit==1.55.0` - Web framework
- `plotly==6.6.0` - Charts
- `pandas==2.3.3` - Data handling
- `requests==2.32.3` - API calls

### Database Schema
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    company_name TEXT,
    country TEXT,
    industry TEXT,
    evidence_type TEXT,
    evidence_text TEXT,
    confidence_score INTEGER,
    source TEXT,
    website TEXT,
    source_url TEXT,
    discovered_at TEXT,
    employees INTEGER,
    headquarters_address TEXT,
    linkedin_url TEXT
);
```

---

## 🐛 Troubleshooting

### App viser "Kunne ikke indlæse data"

**Lokalt:**
```bash
# Kør export manuelt
cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db
python3 scripts/export-for-web.py
```

**Cloud:**
- Push JSON filer til GitHub
- Eller opret GitHub Action til auto-export

### Data opdateres ikke

Tjek auto-export daemon:
```bash
tail -f logs/auto-export-daemon.log
```

### Streamlit Cloud deploy fejler

Tjek `requirements.txt`:
```bash
cat web-deploy/requirements.txt
```

Og sørg for at main file path er korrekt: `streamlit_app.py`

---

## 📞 Support

Hvis du har problemer med deployment:

1. Tjek GitHub repo: https://github.com/<your-username>/navision-db
2. Tjek Streamlit logs: https://streamlit.io/cloud/apps
3. Kør export lokalt for at teste

---

## 🎯 Næste Skridt

1. ✅ Opret GitHub repo
2. ✅ Push til GitHub
3. ✅ Deploy til Streamlit Cloud
4. 🔄 Opsæt auto-updates (GitHub Actions eller manual)
5. 🎨 Tilføj features: Kort visning, virksomhedsdetaljer, eksport til API

**Tid:** ~15 minutter at deploye!
