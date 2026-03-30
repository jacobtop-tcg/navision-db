# 🚀 Streamlit Cloud Deployment - NEM GUIDE

## ✅ GitHub er KLAR!

Repo: https://github.com/jacobtop-tcg/navision-db

---

## 📋 Sådan Deployer du (2 minutter)

### 1. Gå til Streamlit Cloud

👉 **https://streamlit.io/cloud**

### 2. Log ind med GitHub

- Klik **"Log in"**
- Vælg **"Sign in with GitHub"**
- Godkend adgang til `jacobtop-tcg/navision-db`

### 3. Opret App

- Klik **"+ New app"**
- Vælg repo: **`jacobtop-tcg/navision-db`**
- Branch: **`master`**
- Main file path: **`streamlit_app.py`**

### 4. Klik "Deploy"!

⏱️ **Ventetid:** ~1-2 minutter

---

## 🎉 Din App URL

Når deploy er færdig:

```
https://navision-db-jacobtop-tcg.streamlit.app
```

---

## 🔄 Auto-Updates

Når du pusher til GitHub, deployer Streamlit automatisk!

```bash
# Eksempel: Opdater data og push
cd /mnt/data/openclaw/workspace/.openclaw/workspace/navision-db
python3 scripts/export-for-web.py
git add web-export/
git commit -m "Update data: 37,832 companies"
git push
```

Streamlit Cloud gen-deployer automatisk! 🚀

---

## 📊 Hvad Appen Viser

- **37.832+ virksomheder** der bruger Navision
- **50+ lande** dækket
- **Søg & filtrer** på navn, land, kvalitet
- **Download** som CSV
- **Live charts** og statistik

---

## 🐛 Hvis Noget Går Gale

**App viser ingen data?**
- Tjek at `web-export/companies.json` findes i repo
- Kør export: `python3 scripts/export-for-web.py`
- Push igen

**Deploy fejler?**
- Tjek logs på: https://streamlit.io/cloud
- Tjek at `requirements.txt` findes

---

**KLAR TIL DEPLOY!** 🎨

Gå til https://streamlit.io/cloud og følg trinene ovenfor.
