# Cours — Scraping + Pipeline (Python)

Projet de scraping web avec Python : extraction de données, parsing HTML, export CSV, scheduling automatique (cron), et notifications Slack.

---

## Contenu du projet

### 1. Pipeline Quotes (démo)
Scraping de [quotes.toscrape.com](https://quotes.toscrape.com/) — extraction de citations.

```bash
python run.py
```

### 2. Pipeline Books to Scrape
Scraping complet de [books.toscrape.com](https://books.toscrape.com/) — catalogue de 1000 livres avec pagination, détail produit, analyse par catégorie.

```bash
python -c "
from src.logging_setup import setup_logging
from src.config import LOG_DIR
from src.books_pipeline import run_books_scrape
setup_logging(LOG_DIR)
run_books_scrape(max_pages=3, max_books=20)
"
```

### 3. Pipeline Amazon vs Zalando (business)
Identification de marques FR présentes sur Amazon.fr mais absentes de Zalando.fr → leads pour redirection Mirakl.

```bash
python pipeline/run_batch.py
```

### 4. Scheduling (cron / launchd)
Automatisation quotidienne des scrapes via cron job et Docker.

---

## Structure

```
├── src/                        # Code source principal
│   ├── config.py               # URLs, délais, chemins
│   ├── fetch.py                # HTTP client + retry
│   ├── parse.py                # Parser quotes.toscrape
│   ├── parse_books.py          # Parser books.toscrape (fiches + pagination)
│   ├── pipeline.py             # Pipeline quotes → CSV
│   ├── books_pipeline.py       # Pipeline books → CSV + Slack
│   ├── analyze_books.py        # Analyse : stats par catégorie, top rated
│   ├── logging_setup.py        # Logging rotatif fichier + console
│   └── notify_slack.py         # Notification Slack (webhook)
│
├── pipeline/                   # Pipeline Amazon vs Zalando
│   ├── run_batch.py            # Batch quotidien (10 marques/jour)
│   ├── checker.py              # Check Amazon.fr + Zalando.fr
│   ├── sheets.py               # Export Google Sheets
│   ├── export_excel.py         # Export Excel formaté
│   ├── seed_data.py            # Données seed vérifiées
│   ├── brands_queue.json       # File d'attente (50 marques FR)
│   ├── config.py               # Config pipeline
│   ├── cron_pipeline.sh        # Script cron
│   ├── setup_gsheet.py         # Setup Google Sheets
│   └── .env.example            # Template config
│
├── scripts/                    # Scripts utilitaires
│   └── cron_scrape_3h.sh       # Cron books à 3h du mat
│
├── session_2/                  # Session 2 : Docker + cron
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── crontab.sh
│   └── ...
│
├── data/
│   ├── raw/                    # HTML brut (debug)
│   └── processed/              # CSV générés
│
├── logs/                       # Logs d'exécution
├── run.py                      # Point d'entrée quotes
└── requirements.txt            # Dépendances Python
```

---

## Installation

```bash
git clone https://github.com/Anas9112323/scraping-amazon-zalando.git
cd scraping-amazon-zalando

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Pour le pipeline Amazon/Zalando :
```bash
pip install -r pipeline/requirements.txt
```

---

## Stack technique

- **Python 3.9+**
- **requests** — HTTP client
- **BeautifulSoup4 + lxml** — parsing HTML
- **pandas** — manipulation données + export CSV
- **openpyxl** — export Excel
- **gspread** — Google Sheets API
- **Docker** — conteneurisation (session 2)
- **cron / launchd** — scheduling

---

## Pipeline Amazon vs Zalando — Détail

### Objectif business

Identifier les marques FR de vêtements sur **Amazon.fr** mais **absentes de Zalando.fr** → leads pour Mirakl.

### Résultats POC

| Marque | Amazon | Zalando | Statut |
|--------|--------|---------|--------|
| Geographical Norway | Boutique officielle | Absent | **LEAD** |
| Naf Naf | 1000+ résultats | Seconde main | **LEAD** |
| Celio | Jeans, basiques | Seconde main | **LEAD** |
| Chevignon | Blousons cuir | Seconde main | **LEAD** |
| Eric Bompard | Cachemire | Absent | **LEAD** |

### Usage

```bash
python3 pipeline/run_batch.py            # Batch 10 marques
python3 pipeline/run_batch.py --all      # Toutes les marques
python3 pipeline/run_batch.py --reset    # Reset la queue
python3 pipeline/export_excel.py         # Export Excel
python3 pipeline/setup_gsheet.py        # Setup Google Sheets
```

### Config (optionnel)

```bash
cp pipeline/.env.example pipeline/.env
# SERPAPI_KEY=...     (recherche Google fiable)
# SLACK_WEBHOOK_URL=  (notifications)
```
