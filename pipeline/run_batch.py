#!/usr/bin/env python3
"""
Pipeline quotidien : traite un batch de marques FR, check Amazon/Zalando,
exporte CSV + Google Sheets.

Usage :
  python3 pipeline/run_batch.py              # batch normal (BATCH_SIZE marques)
  python3 pipeline/run_batch.py --all        # toutes les marques pending
  python3 pipeline/run_batch.py --reset      # remet tout en pending
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import QUEUE_FILE, RESULTS_CSV, BATCH_SIZE, DATA_DIR, LOGS_DIR
from checker import process_brand
from sheets import push_leads_and_all


def load_queue() -> list:
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["brands"]


def save_queue(brands: list):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump({"brands": brands}, f, ensure_ascii=False, indent=2)


def load_results() -> pd.DataFrame:
    if RESULTS_CSV.exists():
        return pd.read_csv(RESULTS_CSV, encoding="utf-8-sig")
    return pd.DataFrame()


def save_results(df: pd.DataFrame):
    df.to_csv(RESULTS_CSV, index=False, encoding="utf-8-sig")


def run_batch(process_all: bool = False):
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 70)
    print(f"  PIPELINE SCRAPING — Batch quotidien")
    print(f"  {ts}")
    print("=" * 70)

    brands = load_queue()
    pending = [b for b in brands if b["status"] == "pending"]

    if not pending:
        print("\n  Aucune marque en attente. Utilisez --reset pour relancer.")
        return

    batch = pending if process_all else pending[:BATCH_SIZE]
    print(f"\n  Marques en attente : {len(pending)}")
    print(f"  Batch du jour      : {len(batch)}")

    df_existing = load_results()
    new_results = []

    for i, brand_info in enumerate(batch, 1):
        name = brand_info["name"]
        mot_cle = brand_info["mot_cle"]

        print(f"\n{'─'*60}")
        print(f"  [{i}/{len(batch)}] {name}")
        print(f"{'─'*60}")

        try:
            row = process_brand(name, mot_cle)
            row["Date scan"] = ts
            new_results.append(row)

            for b in brands:
                if b["name"] == name:
                    b["status"] = "done"
                    b["last_scan"] = ts
                    break

            lead_tag = " 🎯 LEAD!" if row["LEAD"] == "OUI" else ""
            print(f"  → Amazon: {row['Amazon présent']} | Zalando: {row['Zalando présent (neuf)']} | {row['Zalando type']}{lead_tag}")

        except Exception as e:
            print(f"  [ERREUR] {name} : {e}")
            for b in brands:
                if b["name"] == name:
                    b["status"] = "error"
                    b["error"] = str(e)
                    break

    save_queue(brands)

    if new_results:
        df_new = pd.DataFrame(new_results)

        if not df_existing.empty:
            existing_brands = set(df_existing["Brand"].tolist())
            df_insert = df_new[~df_new["Brand"].isin(existing_brands)]
            df_update = df_new[df_new["Brand"].isin(existing_brands)]

            # Only overwrite existing rows if the new scan has real data
            # (don't overwrite seed/verified data with weaker fallback results)
            if not df_update.empty:
                rows_to_replace = []
                for _, new_row in df_update.iterrows():
                    old_row = df_existing[df_existing["Brand"] == new_row["Brand"]].iloc[0]
                    old_amazon = old_row.get("Amazon présent", "") == "Oui"
                    new_amazon = new_row.get("Amazon présent", "") == "Oui"
                    if new_amazon or not old_amazon:
                        rows_to_replace.append(new_row["Brand"])

                if rows_to_replace:
                    df_existing = df_existing[~df_existing["Brand"].isin(rows_to_replace)]
                    df_update = df_update[df_update["Brand"].isin(rows_to_replace)]
                else:
                    df_update = pd.DataFrame()

            df_all = pd.concat([df_existing, df_update, df_insert], ignore_index=True)
        else:
            df_all = df_new

        save_results(df_all)

        daily_csv = DATA_DIR / f"batch_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        df_new.to_csv(daily_csv, index=False, encoding="utf-8-sig")

        print(f"\n{'='*70}")
        print(f"  RÉSUMÉ DU BATCH")
        print(f"{'='*70}")

        leads = df_new[df_new["LEAD"] == "OUI"]
        non_leads = df_new[df_new["LEAD"] == "NON"]
        print(f"  Marques traitées  : {len(df_new)}")
        print(f"  🎯 LEADS trouvés  : {len(leads)}")
        print(f"  ❌ Déjà sur les 2  : {len(non_leads)}")

        if not leads.empty:
            print(f"\n  🎯 LEADS du jour :")
            for _, row in leads.iterrows():
                print(f"     • {row['Brand']} — {row['Amazon détail']} | Zalando: {row['Zalando détail']}")

        remaining = len([b for b in brands if b["status"] == "pending"])
        print(f"\n  Marques restantes : {remaining}")
        print(f"  CSV batch         : {daily_csv}")
        print(f"  CSV master        : {RESULTS_CSV}")

        print(f"\n  → Push Google Sheets...")
        push_leads_and_all(df_all)

    log_file = LOGS_DIR / f"batch_{now.strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] Batch: {len(batch)} marques, "
                f"{len([r for r in new_results if r['LEAD'] == 'OUI'])} leads\n")

    print(f"\n✅ Pipeline terminé.\n")


def reset_queue():
    brands = load_queue()
    for b in brands:
        b["status"] = "pending"
        b.pop("last_scan", None)
        b.pop("error", None)
    save_queue(brands)
    print(f"✅ {len(brands)} marques remises en pending.")


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_queue()
    elif "--all" in sys.argv:
        run_batch(process_all=True)
    else:
        run_batch()
