# Global Expansion Strategy - Navision Database

## Status: 2026-03-29

### Ændringer Implementeret

#### 1. Udvidet Countries Config
- **Fra:** 8 lande til **40 lande**
- **Nye lande:** RU, TR, ID, TH, MY, VN, AR, CL, CO, PE og flere

#### 2. Udvidede Search Queries
- **Fra:** 9 lande med queries til **42 lande** (40 + GLOBAL)
- **Localiserede queries** på 15+ sprog (da, no, sv, fi, de, en, nl, fr, it, es, pl, pt, ja, ko, tr, ru, vi, th, id, ar)

#### 3. Scraping Logic Opdateret
- Systemet tjekker nu: `COMPANY_QUERIES` → `ADDITIONAL_QUERIES` → `GLOBAL`
- Sikrer at alle 40 lande får specialiserede queries

### Nuværende Database Status
```
Total: 24,720+ virksomheder
Lande: 70+ (fra alle kilder)
Top lande: DK (6,887), SE (2,743), DE (2,124), US (1,704), NO (1,569)
```

### Forventet Vækst
Med den nye globale strategi forventes:
- **Kort sigt (1-2 uger):** +2,000-5,000 virksomheder fra FR, IT, ES, PL, IN
- **Mellemlangt (1-2 måneder):** +10,000+ virksomheder fra APAC og Latinamerika
- **Langt sigt:** Mere均衡 fordeling mellem regioner

### Prioritering (1-40)
1-10: Nordics + EU (DK, NO, SE, FI, DE, UK, NL, BE, US, FR)
11-20: Europa + APAC (IT, ES, PL, IN, CA, AU, JP, BR, MX, SG)
21-30: Mellemøsten + Asien (AE, ZA, KR, CH, AT, IE, NZ, PT, GR, CZ)
31-40: Emerging Markets (RU, TR, ID, TH, MY, VN, AR, CL, CO, PE)

### Kører Nu
Daemon kører 24/7 med 60 sekunders interval.
Systemet vil automatisk begynde at finde virksomheder fra de nye markeder.

### Næste Skridn
- Monitorere vækst i underrepræsenterede lande
- Tilføje flere queries til lande med lav dækning
- Overveje at øge side-grænser (15 → 25 per query) for højere volumen
