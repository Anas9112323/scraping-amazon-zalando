"""Paramètres centralisés (URLs, délais, chemins)."""
from pathlib import Path

# Racine du projet (parent de src/)
ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
LOG_DIR = ROOT / "logs"

# Site de démo conçu pour l'apprentissage du scraping (légal / éthique)
DEFAULT_URL = "https://quotes.toscrape.com/"

# books.toscrape.com — catalogue utilisé pour le projet « livres »
BOOKS_BASE_URL = "https://books.toscrape.com/"

# Identifie poliment le client ; à adapter pour ton cours
USER_AGENT = (
    "Mozilla/5.0 (compatible; CoursScraping/1.0; +https://example.org/cours)"
)

# Pause minimale entre requêtes (secondes) — augmente si tu enchaînes plusieurs pages
REQUEST_DELAY_SEC = 1.0

# Retry HTTP (fetch_html_with_retry)
FETCH_MAX_RETRIES = 4
FETCH_BACKOFF_BASE_SEC = 2.0
FETCH_TIMEOUT_SEC = 30

# Variable d'environnement pour notifier Slack (optionnel)
SLACK_WEBHOOK_ENV = "SLACK_WEBHOOK_URL"
