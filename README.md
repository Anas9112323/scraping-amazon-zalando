# Cours — Scraping + Pipeline (Python)

Projet de scraping web avec Python : extraction de données depuis [books.toscrape.com](https://books.toscrape.com/), parsing HTML, export CSV, analyse de données, scheduling automatique (cron/Docker), et notifications Slack.

---

## Fonctionnalités

- **Scraping quotes** — extraction de citations depuis [quotes.toscrape.com](https://quotes.toscrape.com/)
- **Scraping books** — catalogue complet de 1000 livres avec pagination, fiche détail, catégories
- **Analyse** — stats par catégorie (prix moyen/médian), top livres par note
- **Logging** — fichier rotatif + console configurable
- **Notification Slack** — webhook optionnel pour alerter en fin de scrape
- **Scheduling** — cron job + Docker pour automatisation quotidienne

---

## Structure

```
├── src/                        # Code source
│   ├── config.py               # URLs, délais, chemins
│   ├── fetch.py                # HTTP client + retry exponentiel
│   ├── parse.py                # Parser quotes.toscrape
│   ├── parse_books.py          # Parser books.toscrape (fiches + pagination)
│   ├── pipeline.py             # Pipeline quotes → CSV
│   ├── books_pipeline.py       # Pipeline books → CSV complet
│   ├── analyze_books.py        # Analyse : stats par catégorie, top rated
│   ├── logging_setup.py        # Logging rotatif fichier + console
│   └── notify_slack.py         # Notification Slack (webhook)
│
├── session_2/                  # Session 2 : Docker + cron
│   ├── Dockerfile              # Image Python pour le scraping
│   ├── docker-compose.yml      # Orchestration conteneur
│   ├── crontab.sh              # Script cron quotidien
│   └── ...
│
├── data/
│   ├── raw/                    # HTML brut (debug)
│   └── processed/              # CSV générés (books.csv, quotes.csv)
│
├── logs/                       # Logs d'exécution
├── run.py                      # Point d'entrée principal
└── requirements.txt            # Dépendances Python
```

---

## Installation

```bash
git clone https://github.com/Anas9112323/scraping-amazon-zalando.git
cd scraping-amazon-zalando

python3 -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Usage

### 1. Scraping Quotes (démo rapide)

```bash
python run.py
```

Résultat : `data/processed/quotes.csv`

### 2. Scraping Books (complet)

```bash
python -c "
from src.logging_setup import setup_logging
from src.config import LOG_DIR
from src.books_pipeline import run_books_scrape
setup_logging(LOG_DIR)
run_books_scrape()
"
```

Options :
```python
run_books_scrape(
    max_pages=5,        # Limiter le nombre de pages catalogue
    max_books=50,       # Limiter le nombre de livres
    save_raw=True,      # Sauvegarder le HTML brut
    append_csv=True,    # Ajouter au CSV existant (multi-runs)
    verbose=True,       # Logs détaillés en console
)
```

Résultat : `data/processed/books.csv`

### 3. Analyse des données

```bash
python -m src.analyze_books data/processed/books.csv
```

Affiche :
- Prix moyen/médian par catégorie
- Top 15 livres les mieux notés
- Export : `data/processed/summary_by_category.csv`

---

## Cron job — Scraping automatique

### Avec crontab (Linux/macOS)

```bash
crontab -e
# Ajouter :
0 3 * * * /chemin/vers/scripts/cron_scrape_3h.sh
```

### Avec Docker (session 2)

```bash
cd session_2
docker compose run --rm app
```

---

## Données extraites (books.csv)

| Colonne | Description |
|---------|-------------|
| `title` | Titre du livre |
| `category` | Catégorie (Travel, Mystery, etc.) |
| `price_gbp` | Prix en £ |
| `rating` | Note (1 à 5) |
| `availability` | Disponibilité |
| `upc` | Code produit unique |
| `num_reviews` | Nombre d'avis |
| `description_short` | Description (200 car.) |
| `url` | Lien vers la fiche |
| `scraped_at` | Date/heure du scraping (UTC) |

---

## Stack technique

- **Python 3.9+**
- **requests** — HTTP client
- **BeautifulSoup4 + lxml** — parsing HTML
- **pandas** — manipulation données + export CSV
- **Docker** — conteneurisation (session 2)
- **cron / launchd** — scheduling

---

## Éthique / légal

Les sites utilisés ([quotes.toscrape.com](https://quotes.toscrape.com/), [books.toscrape.com](https://books.toscrape.com/)) sont des **sites d'entraînement** conçus pour l'apprentissage du scraping. Vérifie toujours `robots.txt` et les conditions d'utilisation avant de scraper un site réel.
