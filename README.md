# Pipeline Scraping — Marques FR : Amazon vs Zalando

Pipeline automatisé qui identifie les marques françaises de vêtements présentes sur **Amazon.fr** mais **absentes de Zalando.fr**, pour les rediriger vers Zalando via **Mirakl**.

---

## Objectif business

> Trouver des **leads** : marques qui vendent sur Amazon.fr mais ne sont pas (encore) sur Zalando.fr → leur proposer de s'y inscrire via Mirakl.

**Critère LEAD :**
- Amazon.fr = **OUI** (produits neufs en vente)
- Zalando.fr = **NON** (absent ou seconde main uniquement)

---

## Architecture du pipeline

```
pipeline/
├── run_batch.py          # Script principal — batch quotidien (10 marques/jour)
├── checker.py            # Moteur de vérification Amazon.fr + Zalando.fr
├── sheets.py             # Export automatique vers Google Sheets
├── config.py             # Configuration (paths, batch size, credentials)
├── seed_data.py          # Données seed vérifiées (15 marques)
├── brands_queue.json     # File d'attente des marques à scanner (50 marques FR)
├── cron_pipeline.sh      # Script bash exécuté par le cron job
├── export_excel.py       # Export Excel formaté (.xlsx) avec couleurs
├── setup_gsheet.py       # Setup one-time Google Sheets
├── requirements.txt      # Dépendances Python
└── .env.example          # Template de configuration
```

---

## Données collectées

| Colonne | Description |
|---------|-------------|
| `Brand` | Nom de la marque |
| `Mot-clé` | Mot-clé de recherche Amazon |
| `Amazon présent` | Oui/Non — présence produits neufs sur Amazon.fr |
| `Amazon détail` | Détails (nb résultats, boutique officielle, % positif) |
| `Amazon note` | Note moyenne (ex: 4.2/5) |
| `Amazon avis` | Nombre d'avis estimé |
| `Amazon prix` | Fourchette de prix en € |
| `Zalando présent (neuf)` | Oui/Non — présence catalogue neuf sur Zalando.fr |
| `Zalando type` | `officiel` / `seconde_main` / `absent` / `probable` |
| `Zalando détail` | Détails (nb articles, type de présence) |
| `Site web` | URL du site officiel de la marque |
| `Page contact` | URL page contact / commercial |
| `Page RGPD` | URL mentions légales / CGV |
| `LEAD` | **OUI** = cible commerciale / **NON** = déjà sur les 2 |
| `Date scan` | Date du dernier scan |

---

## Installation

```bash
# Cloner le repo
git clone https://github.com/<username>/cours-scraping-pipeline.git
cd cours-scraping-pipeline

# Installer les dépendances
pip install -r pipeline/requirements.txt

# Configurer l'environnement
cp pipeline/.env.example pipeline/.env
# Éditer pipeline/.env avec ta clé SerpAPI (optionnel mais recommandé)
```

---

## Usage

### Lancer un batch manuellement

```bash
# Batch normal (10 marques)
python3 pipeline/run_batch.py

# Traiter TOUTES les marques d'un coup
python3 pipeline/run_batch.py --all

# Remettre toutes les marques en attente
python3 pipeline/run_batch.py --reset
```

### Exporter les données

```bash
# Export Excel formaté (s'ouvre automatiquement)
python3 pipeline/export_excel.py

# Injecter les données seed (première fois)
python3 pipeline/seed_data.py
```

### Google Sheets (auto-sync)

```bash
# Setup one-time (après avoir configuré les credentials)
python3 pipeline/setup_gsheet.py
```

---

## Cron job — Exécution quotidienne à 8h

### macOS (launchd) — recommandé

```bash
# Charger le job
launchctl load ~/Library/LaunchAgents/com.scraping.pipeline.plist

# Vérifier qu'il est actif
launchctl list | grep scraping

# Désactiver
launchctl unload ~/Library/LaunchAgents/com.scraping.pipeline.plist
```

### Linux (crontab)

```bash
crontab -e
# Ajouter :
0 8 * * * /chemin/vers/pipeline/cron_pipeline.sh
```

---

## Configuration

### SerpAPI (recommandé pour la fiabilité)

Sans SerpAPI, le pipeline fonctionne en mode dégradé (Amazon OK, Zalando souvent bloqué 403).

1. Crée un compte gratuit sur [serpapi.com](https://serpapi.com/) (100 recherches/mois)
2. Copie ta clé API
3. Ajoute dans `pipeline/.env` :

```
SERPAPI_KEY=ta_cle_api_ici
```

### Google Sheets (partage automatique)

Pour que le cron job mette à jour un Google Sheet partagé automatiquement :

1. Va sur [Google Cloud Console](https://console.cloud.google.com/)
2. Crée un projet → active **Google Sheets API** + **Google Drive API**
3. Crée un **Service Account** → télécharge la clé JSON
4. Place le fichier dans `pipeline/google_creds.json`
5. Lance `python3 pipeline/setup_gsheet.py`

Le script crée le spreadsheet, injecte les données, et génère un lien partageable.

---

## Résultats actuels (POC)

### 5 LEADS identifiés

| Marque | Amazon | Zalando | Statut |
|--------|--------|---------|--------|
| Geographical Norway | Oui — boutique officielle | Absent | **LEAD** |
| Naf Naf | Oui — robes, manteaux | Seconde main uniquement | **LEAD** |
| Celio | Oui — jeans, basiques | Seconde main uniquement | **LEAD** |
| Chevignon | Oui — blousons cuir | Seconde main uniquement | **LEAD** |
| Eric Bompard | Oui — cachemire | Absent | **LEAD** |

### 10 marques déjà sur les 2 plateformes (référence)

Petit Bateau, Aigle, Lacoste, Armor Lux, Kaporal, Oxbow, Le Coq Sportif, Le Slip Français, Veja, Aubade

### 40 marques restantes dans la queue

À traiter par le batch quotidien (10/jour → 4 jours pour tout couvrir).

---

## Workflow quotidien

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Cron 8h    │────▶│  run_batch   │────▶│  checker.py     │
│  (launchd)  │     │  (10 marques)│     │  Amazon+Zalando │
└─────────────┘     └──────┬───────┘     └────────┬────────┘
                           │                       │
                    ┌──────▼───────┐        ┌──────▼────────┐
                    │  CSV master  │        │  Google Sheet │
                    │  + Excel     │        │  (auto-sync)  │
                    └──────────────┘        └───────────────┘
```

---

## Stack technique

- **Python 3.9+**
- **requests** — HTTP client
- **BeautifulSoup4** — parsing HTML
- **pandas** — manipulation données
- **openpyxl** — export Excel formaté
- **gspread** — Google Sheets API
- **SerpAPI** — recherche Google fiable (optionnel)
- **launchd/cron** — scheduling quotidien

---

## Auteurs

Projet réalisé dans le cadre d'un cours de scraping.
