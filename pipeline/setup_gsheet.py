#!/usr/bin/env python3
"""
Setup rapide Google Sheets — crée un spreadsheet partagé et synced.

ÉTAPES (2 minutes) :
  1. Va sur https://console.cloud.google.com/
  2. Crée un projet (ou utilise un existant)
  3. Active : "Google Sheets API" + "Google Drive API"
  4. Menu → Identifiants → Créer identifiants → Compte de service
  5. Nom : "scraping-pipeline" → Créer
  6. Clique sur le compte → Onglet Clés → Ajouter clé → JSON
  7. Renomme le fichier téléchargé en google_creds.json
  8. Mets-le dans : pipeline/google_creds.json
  9. Lance ce script : python3 pipeline/setup_gsheet.py

Le script va :
  - Créer un Google Sheet "Leads Marques FR - Amazon vs Zalando"
  - Y injecter toutes les données du CSV master
  - Générer un lien partageable (tout le monde peut voir)
  - Afficher le lien à envoyer à ton collègue
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import GOOGLE_SHEETS_CREDS, SPREADSHEET_NAME, RESULTS_CSV

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Installe d'abord : pip3 install gspread google-auth")
    sys.exit(1)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def setup():
    if not GOOGLE_SHEETS_CREDS.exists():
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  FICHIER GOOGLE CREDS MANQUANT                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Va sur https://console.cloud.google.com/                 ║
║  2. Crée un projet                                           ║
║  3. Active "Google Sheets API" + "Google Drive API"          ║
║  4. Identifiants → Compte de service → Créer                ║
║  5. Onglet Clés → Ajouter clé → JSON                        ║
║  6. Renomme → google_creds.json                              ║
║  7. Place dans : {GOOGLE_SHEETS_CREDS}
║                                                              ║
║  Puis relance : python3 pipeline/setup_gsheet.py             ║
╚══════════════════════════════════════════════════════════════╝
""")
        sys.exit(1)

    if not RESULTS_CSV.exists():
        print("Pas de données. Lance d'abord : python3 pipeline/seed_data.py")
        sys.exit(1)

    print("Connexion à Google Sheets...")
    creds = Credentials.from_service_account_file(str(GOOGLE_SHEETS_CREDS), scopes=SCOPES)
    client = gspread.authorize(creds)

    print(f"Création du spreadsheet : {SPREADSHEET_NAME}")
    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
        print("  (déjà existant, mise à jour)")
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(SPREADSHEET_NAME)

    spreadsheet.share("", perm_type="anyone", role="reader")

    df = pd.read_csv(RESULTS_CSV, encoding="utf-8-sig")
    df = df.fillna("")

    df_leads = df[df["LEAD"] == "OUI"].copy()
    df_all = df.copy()

    # Onglet LEADS
    try:
        ws_leads = spreadsheet.worksheet("LEADS")
        ws_leads.clear()
    except gspread.WorksheetNotFound:
        ws_leads = spreadsheet.add_worksheet(title="LEADS", rows=500, cols=20)

    ws_leads.update([df_leads.columns.tolist()] + df_leads.values.tolist())
    ws_leads.format("1:1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.1, "green": 0.1, "blue": 0.18}})

    # Onglet Toutes les marques
    try:
        ws_all = spreadsheet.worksheet("Toutes les marques")
        ws_all.clear()
    except gspread.WorksheetNotFound:
        ws_all = spreadsheet.add_worksheet(title="Toutes les marques", rows=500, cols=20)

    ws_all.update([df_all.columns.tolist()] + df_all.values.tolist())
    ws_all.format("1:1", {"textFormat": {"bold": True}})

    # Supprimer Sheet1 par défaut si elle existe
    try:
        default = spreadsheet.worksheet("Sheet1")
        spreadsheet.del_worksheet(default)
    except (gspread.WorksheetNotFound, Exception):
        pass

    url = spreadsheet.url

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  GOOGLE SHEET CRÉÉ ET PARTAGÉ !                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 URL : {url:<48s} ║
║                                                              ║
║  Onglets :                                                   ║
║    - LEADS             : {len(df_leads):>3d} marques (Amazon OUI, Zalando NON)  ║
║    - Toutes les marques: {len(df_all):>3d} marques                            ║
║                                                              ║
║  Partage : lien public en lecture                            ║
║  → Envoie ce lien à ton collègue pour Supabase              ║
║                                                              ║
║  Le cron job met à jour ce sheet chaque jour à 8h.           ║
╚══════════════════════════════════════════════════════════════╝
""")

    link_file = Path(__file__).resolve().parent / "GSHEET_LINK.txt"
    link_file.write_text(f"Google Sheet Leads Marques FR\n{url}\n\nCréé le {pd.Timestamp.now()}\n")
    print(f"  Lien sauvegardé dans : {link_file}")


if __name__ == "__main__":
    setup()
