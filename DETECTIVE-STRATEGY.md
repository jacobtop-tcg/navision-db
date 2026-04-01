# 🕵️ DETECTIVE STRATEGY - Smoking Gun Hunt

**Filosofi:** Kvalitet over kvantitet. Ingen blind scraping. Kun RIGTIGE beviser.

---

## 🎯 Hvad er en "Smoking Gun"?

En **smoking gun** er et **ubestrideligt bevis** for at en virksomhed bruger Navision/Dynamics 365 Business Central.

### ✅ SMOKING GUNS (Høj kvalitet - 5 stjerner)

| Type | Eksempel | Hvorfor det er bevis |
|------|----------|---------------------|
| **Internt jobopslag** | "Vi søger Dynamics NAV udvikler til vores team" | Virksomheden ansætter NAV folk = de bruger det |
| **Kundecase skrevet AF kunden** | "Sådan bruger vi Dynamics NAV i vores produktion" | Kunden fortæller selv om deres brug |
| **Go-live pressemeddelelse** | "X A/S går live med Dynamics NAV" | Offentlig annoncering af implementering |
| **Konference oplæg AF kunde** | "Customer story: How Company Y uses NAV" | Kunde præsenterer deres erfaringer |
| **Tech stack side** | "Our ERP: Microsoft Dynamics NAV" | Virksomheden lister det som deres system |
| **Partner kundeliste** | "Vores kunder: Company A, Company B" | Partner bekræfter kundeforhold |
| **Executive quote** | "CFO: Dynamics NAV har forbedret..." | Leder bekræfter brug |

### ❌ IKKE Smoking Guns (Lav kvalitet - 1-3 stjerner)

| Type | Hvorfor det er svagt |
|------|---------------------|
| Partner nævner kunde | Kan være gammelt, ukonkret |
| Job consultant skal ud til kunde | Konsulenten bruger det, ikke nødvendigvis kunden |
| Generel omtale uden konkret brug | "Vi kender NAV" ≠ "Vi bruger NAV" |
| Ukonkrete lister | Uden kildeangivelse eller bevis |

---

## 🔍 Detective Methods

### Method 1: Job Posting Detective

**Mål:** Find virksomheder der aktivt søger NAV folk

**Search queries:**
```
"Dynamics NAV developer" "our company" site:linkedin.com/jobs
"Business Central" "we are looking" site:indeed.com
"NAV udvikler" "vores team" site:jobindex.dk
"Dynamics NAV" "internal" developer
```

**Hvorfor det virker:**
- Virksomheder søger ikke NAV udviklere hvis de ikke bruger NAV
- Job postings er offentlige og verificerbare
- Indeholder ofte konkret info om hvordan de bruger systemet

**Detektiv arbejde:**
1. Find job posting
2. Verificer det er fra virksomheden selv (ikke konsulenthus)
3. Extract company name
4. Gem URL som bevis
5. Tilføj med 5-stjernet confidence

---

### Method 2: Customer Story Detective

**Mål:** Find kunder der fortæller om deres NAV rejse

**Search queries:**
```
"sådan bruger vi" "Dynamics NAV" site:.dk
"how we use" "Dynamics NAV" site:.com
"vores rejse med" "Navision"
"our journey with" "Dynamics NAV"
"gik live med" "Dynamics NAV"
"went live with" "Microsoft Dynamics NAV"
```

**Hvorfor det virker:**
- Kunder deler deres success stories
- Ofte detaljeret info om implementation og brug
- Skrevet AF kunden selv (høj troværdighed)

**Detektiv arbejde:**
1. Find customer story
2. Verificer det er skrevet af kunden (ikke partner)
3. Extract konkrete citater/beviser
4. Gem URL og evidence
5. Tilføj med 5-stjernet confidence

---

### Method 3: Partner Customer List Detective

**Mål:** Find partneres bekræftede kundelister

**Target partners (DK):**
- 9altitudes.com (største NAV partner i DK)
- elbek-vejrup.dk
- obtain.dk
- jcd.dk
- vektus.dk
- dynamicsinspire.dk

**Target partners (International):**
- appsruntheworld.com (global ERP database)
- calsoft.com (implementation partner)
- Various Microsoft Gold Partners

**Hvorfor det virker:**
- Partnere viser stolt deres kunder frem
- Ofte med cases og referencer
- Bekræftet kundeforhold

**Detektiv arbejde:**
1. Find partner customer page
2. Extract customer names
3. Verificer med case study hvis muligt
4. Gem partner URL som kilde
5. Tilføj med 4-5 stjerner (afhængig af bevisstyrke)

---

### Method 4: Conference & Event Detective

**Mål:** Find kunder der præsenterer på konferencer

**Search queries:**
```
"Dynamics NAV" "customer story" site:youtube.com
"Business Central" "customer" site:community.dynamics.com
"NAV user conference" presentation
"Dynamics 365" "customer success" site:microsoft.com
```

**Hvorfor det virker:**
- Kunder præsenterer deres erfaringer offentligt
- Ofte med konkret info om brug og resultater
- Microsoft/community validerer indholdet

**Detektiv arbejde:**
1. Find conference presentation
2. Identificer kundevirksomhed
3. Extract key points fra præsentation
4. Gem URL/video som bevis
5. Tilføj med 5-stjernet confidence

---

### Method 5: Tech Stack Detective

**Mål:** Find virksomheder der lister NAV som deres ERP

**Search queries:**
```
"our ERP" "Microsoft Dynamics NAV" site:.com
"vores ERP" "Dynamics NAV" site:.dk
"technology stack" "Dynamics NAV"
"systems we use" "Navision"
"IT landscape" "Dynamics"
```

**Hvorfor det virker:**
- Virksomheder dokumenterer deres IT stack
- Ofte på careers/about/tech pages
- Direkte bevis for systembrug

**Detektiv arbejde:**
1. Find tech stack page
2. Verificer det er virksomhedens egen side
3. Extract konkret ERP info
4. Gem URL som bevis
5. Tilføj med 5-stjernet confidence

---

### Method 6: Historical Detective (Wayback Machine)

**Mål:** Find historiske beviser fra de sidste 2 år

**Target:**
- Jobindex.dk arkiverede job postings
- Partner websites med gamle kundelister
- Pressemeddelelser der er blevet fjernet

**Værktøjer:**
- Wayback Machine: archive.org/web
- Google Cache: `cache:url`
- CDX API for bulk lookup

**Hvorfor det virker:**
- Mange beviser forsvinder fra live sites
- Arkiverede sider er stadig gyldige beviser
- Giver historisk dybde (2+ år tilbage)

**Detektiv arbejde:**
1. Find URL der ikke længere eksisterer
2. Lookup i Wayback Machine
3. Fetch arkiveret version
4. Extract evidence
5. Gem både original og arkiv-URL
6. Tilføj med 4-5 stjerner

---

## 📊 Kvalitetskrav

### 5-stjernet (Smoking Gun - Ubestrideligt)
- ✅ Direkte citat fra kunde/executive
- ✅ Job posting fra virksomhed selv
- ✅ Case study skrevet AF kunden
- ✅ Go-live pressemeddelelse
- ✅ Tech stack side fra virksomhed

### 4-stjernet (Stærkt bevis)
- ✅ Partner kundeliste med case link
- ✅ Conference presentation af kunde
- ✅ Job posting via tredjepart (verificeret)
- ✅ Customer reference på partner site

### 3-stjernet (Moderat bevis)
- ⚠️ Partner nævner kunde (uden case)
- ⚠️ Job consultant skal til kunde
- ⚠️ Indirekte omtale

### 1-2 stjernet (Svagt bevis)
- ❌ Ukonkret liste uden kilde
- ❌ Generel omtale uden brug
- ❌ Forældet info (>3 år gammel)

---

## 🛠️ Scripts

### `smoking-gun-hunter.py` (V2)
**Formål:** Systematisk jagt på smoking guns via søgemaskiner

**Kategorier:**
1. `job_internal` - Interne jobopslag
2. `customer_case` - Kundecases
3. `go_live` - Go-live annonceringer
4. `conference` - Konference oplæg
5. `tech_stack` - Tech stack sider
6. `partner_customers` - Partner kundelister

**Output:**
- Kun virksomheder med confidence ≥ 4
- Automatisk company name extraction
- Evidence tekst gemmes
- URL som bevis

---

## 📈 Mål

**Nuværende status:**
- 43 virksomheder med 5 stjerner
- 4.441 virksomheder med 4 stjerner
- 37.140 virksomheder med 1 stjerne

**Mål om 30 dage:**
- 500+ virksomheder med 5 stjerner (smoking guns)
- 10.000+ virksomheder med 4 stjerner (stærke beviser)
- Reducer 1-stjernet til <50% (kvalitetsfokus)

**Fokus:**
- Kvalitet > Kvantitet
- Verificerbare beviser
- Ingen blind scraping

---

## 🚀 Execution Plan

### Uge 1: Job Posting Detective
- Kør `smoking-gun-hunter.py` med fokus på jobs
- Target: DK, NO, SE, DE, UK, NL
- Forventet: 200-500 smoking guns

### Uge 2: Customer Story Detective
- Find kundecases på tværs af lande
- Target: Partner websites + customer blogs
- Forventet: 100-300 smoking guns

### Uge 3: Partner Detective
- Systematisk gennemgang af partner sites
- Target: 50+ partnere globalt
- Forventet: 300-500 smoking guns

### Uge 4: Historical Detective
- Wayback Machine for historiske beviser
- Target: Jobindex, partner sites 2024-2026
- Forventet: 100-200 smoking guns

---

## ⚠️ Vigtige Principper

1. **Ingen blind scraping** - Hver entry skal have et bevis
2. **Verificer kilde** - Er det virksomheden selv eller en tredjepart?
3. **Gem URL** - Altid gemme kilde-URL som bevis
4. **Evidence tekst** - Gem konkret citat/bevis i database
5. **Kvalitet over kvantitet** - Hellere 100 verificerede end 10.000 usikre

---

**"Detektivarbejde handler ikke om at finde mest data - det handler om at finde de RIGTIGE beviser."**
