"""
Google Sheets integration — push les résultats vers une feuille partagée.

SETUP (une seule fois) :
1. Va sur https://console.cloud.google.com/
2. Crée un projet (ou utilise un existant)
3. Active l'API Google Sheets + Google Drive
4. Crée un compte de service (Service Account)
5. Télécharge le JSON des credentials → pipeline/google_creds.json
6. Partage ta Google Sheet avec l'email du service account (en éditeur)
"""

import json
from pathlib import Path
from typing import Optional

import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_OK = True
except ImportError:
    GSPREAD_OK = False

from config import GOOGLE_SHEETS_CREDS, SPREADSHEET_NAME


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _get_client() -> Optional["gspread.Client"]:
    if not GSPREAD_OK:
        print("  [WARN] gspread non installé. pip install gspread google-auth")
        return None
    if not GOOGLE_SHEETS_CREDS.exists():
        print(f"  [WARN] Fichier creds introuvable : {GOOGLE_SHEETS_CREDS}")
        print("  → Voir le SETUP dans pipeline/sheets.py pour configurer Google Sheets.")
        return None

    creds = Credentials.from_service_account_file(str(GOOGLE_SHEETS_CREDS), scopes=SCOPES)
    return gspread.authorize(creds)


def push_to_sheets(df: pd.DataFrame, sheet_name: str = "Leads") -> bool:
    """Pousse le DataFrame vers Google Sheets. Crée le spreadsheet si besoin."""
    client = _get_client()
    if not client:
        return False

    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        print(f"  Création du spreadsheet : {SPREADSHEET_NAME}")
        spreadsheet = client.create(SPREADSHEET_NAME)
        spreadsheet.share("", perm_type="anyone", role="writer")

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

    existing = worksheet.get_all_records()
    existing_brands = {r.get("Brand", "") for r in existing}

    new_rows = df[~df["Brand"].isin(existing_brands)]
    update_rows = df[df["Brand"].isin(existing_brands)]

    if not new_rows.empty:
        if not existing:
            worksheet.update([new_rows.columns.tolist()] + new_rows.values.tolist())
        else:
            for _, row in new_rows.iterrows():
                worksheet.append_row(row.tolist())
        print(f"  ✅ {len(new_rows)} nouvelles marques ajoutées à Google Sheets")

    if not update_rows.empty:
        all_data = worksheet.get_all_values()
        if all_data:
            header = all_data[0]
            brand_col = header.index("Brand") if "Brand" in header else 0
            for _, row in update_rows.iterrows():
                for i, data_row in enumerate(all_data[1:], start=2):
                    if data_row[brand_col] == row["Brand"]:
                        worksheet.update(f"A{i}", [row.tolist()])
                        break
        print(f"  🔄 {len(update_rows)} marques mises à jour dans Google Sheets")

    url = spreadsheet.url
    print(f"  📊 Sheet URL : {url}")
    return True


def push_leads_and_all(df_all: pd.DataFrame) -> bool:
    """Push 2 onglets : 'Leads' (filtrées) et 'Toutes les marques'."""
    client = _get_client()
    if not client:
        print("  [INFO] Google Sheets non configuré — export CSV uniquement.")
        return False

    df_leads = df_all[df_all["LEAD"] == "OUI"].copy()

    push_to_sheets(df_all, sheet_name="Toutes les marques")
    if not df_leads.empty:
        push_to_sheets(df_leads, sheet_name="LEADS")

    return True
