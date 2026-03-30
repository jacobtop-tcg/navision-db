# Navision Global Database

Live dashboard over virksomheder der bruger Microsoft Dynamics NAV/Navision.

## 🚀 Live Dashboard

**URL:** https://navision-db.streamlit.app

## 📊 Database Stats

- **Total virksomheder:** 37,660+
- **Lande:** 50+
- **Kvalitet:** 94% (4-5 stjerner)
- **Opdatering:** Hvert 5. minut

## 🔍 Features

- 🔎 **Søg** i alle virksomheder
- 🌍 **Filtre** på land, kvalitet, kilde
- 📊 **Dashboard** med statistik
- 📥 **Download** som CSV
- ⭐ **Kvalitetsfilter** (1-5 stjerner)

## 🛠️ Setup

### Lokalt

```bash
# Installér dependencies
pip install streamlit plotly pandas requests

# Kør export
python3 scripts/export-for-web.py

# Kør Streamlit app
streamlit run streamlit_app.py
```

### Deployment

```bash
# Push til GitHub
git push origin main

# Streamlit Cloud auto-deployer
```

## 📁 Struktur

```
navision-db/
├── database/
│   └── navision-global.db    # SQLite database
├── web-export/
│   ├── companies.json        # Exported data
│   ├── companies.csv         # CSV export
│   └── metadata.json         # Statistics
├── scripts/
│   ├── export-for-web.py     # Export script
│   └── auto-export-daemon.py # Auto-export daemon
├── streamlit_app.py          # Main app
└── web-deploy/
    ├── streamlit_app.py      # Deploy version
    └── requirements.txt      # Dependencies
```

## 🔄 Auto-Updates

Export daemon kører hvert 5. minut og opdaterer JSON filer automatisk.

## 📧 Kontakt

Jacob - @jacob_top

---

Built with ❤️ using Streamlit, Plotly, and SQLite
