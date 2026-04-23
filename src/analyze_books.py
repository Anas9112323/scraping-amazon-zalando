"""
Étape « analyse » : lecture du CSV livres, stats par catégorie, tops.
À lancer après un scrape complet (ou un CSV partiel).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from src.config import DATA_PROCESSED

logger = logging.getLogger("cours_scraping.analyze")


def load_books_csv(path: Union[str, Path]) -> pd.DataFrame:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"CSV introuvable : {p}")
    df = pd.read_csv(p, encoding="utf-8")
    return df


def summary_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Prix moyen / médian et nombre de livres par catégorie."""
    work = df.copy()
    if "price_gbp" not in work.columns:
        raise ValueError("Colonne price_gbp absente")
    work = work.dropna(subset=["category"])
    work["price_gbp"] = pd.to_numeric(work["price_gbp"], errors="coerce")
    g = (
        work.groupby("category", dropna=False)["price_gbp"]
        .agg(["count", "mean", "median"])
        .rename(columns={"count": "nb_livres", "mean": "prix_moyen", "median": "prix_mediane"})
        .sort_values("prix_moyen", ascending=False)
        .round(2)
    )
    return g.reset_index()


def top_rated_books(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Livres les mieux notés (rating décroissant, puis titre)."""
    work = df.copy()
    if "rating" not in work.columns:
        raise ValueError("Colonne rating absente")
    work["rating"] = pd.to_numeric(work["rating"], errors="coerce")
    work = work.dropna(subset=["rating", "title"])
    cols = [c for c in ["title", "category", "rating", "price_gbp", "url"] if c in work.columns]
    out = work.sort_values(["rating", "title"], ascending=[False, True]).head(n)
    return out[cols].reset_index(drop=True)


def run_analysis(
    csv_path: Union[str, Path],
    *,
    export_category_csv: Optional[Union[str, Path]] = None,
    top_n: int = 15,
) -> None:
    df = load_books_csv(csv_path)
    logger.info("Lignes chargées : %s", len(df))

    by_cat = summary_by_category(df)
    out_cat = Path(export_category_csv) if export_category_csv else DATA_PROCESSED / "summary_by_category.csv"
    out_cat.parent.mkdir(parents=True, exist_ok=True)
    by_cat.to_csv(out_cat, index=False, encoding="utf-8")
    logger.info("Résumé par catégorie écrit : %s", out_cat)

    top = top_rated_books(df, n=top_n)

    print("\n--- Prix par catégorie (aperçu, 10 premières lignes) ---")
    print(by_cat.head(10).to_string(index=False))
    print(f"\n... ({len(by_cat)} catégories au total — voir {out_cat})")

    print(f"\n--- Top {top_n} livres les mieux notés ---")
    print(top.to_string(index=False))


if __name__ == "__main__":
    import sys

    from src.logging_setup import setup_logging
    from src.config import LOG_DIR

    setup_logging(LOG_DIR)
    path = sys.argv[1] if len(sys.argv) > 1 else DATA_PROCESSED / "books.csv"
    run_analysis(path)
