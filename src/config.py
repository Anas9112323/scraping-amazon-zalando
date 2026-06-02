"""Paramètres centralisés (URLs, délais, chemins)."""
from pathlib import Path

# Racine du projet (parent de src/)
ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
LOG_DIR = ROOT / "logs"

# Sites de démo conçus pour l'apprentissage du scraping (légal / éthique)
DEFAULT_URL = "https://quotes.toscrape.com/"
BOOKS_BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"

# Identifie poliment le client
USER_AGENT = (
    "Mozilla/5.0 (compatible; CoursScraping/1.0; +https://example.org/cours)"
)

# Pause minimale entre requêtes (secondes)
REQUEST_DELAY_SEC = 1.0

# Slack (optionnel) — nom de la variable d'environnement contenant le webhook URL
SLACK_WEBHOOK_ENV = "SLACK_WEBHOOK_URL"
