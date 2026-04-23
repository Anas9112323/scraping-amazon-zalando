"""
Configuration du pipeline scraping marques FR.
"""
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PIPELINE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PIPELINE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

QUEUE_FILE = PIPELINE_DIR / "brands_queue.json"
RESULTS_CSV = DATA_DIR / "leads_master.csv"

BATCH_SIZE = 10

GOOGLE_SHEETS_CREDS = PIPELINE_DIR / "google_creds.json"
SPREADSHEET_NAME = "Leads Marques FR - Amazon vs Zalando"
