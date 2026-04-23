#!/usr/bin/env python3
"""Point d'entrée : scraping livres (défaut) ou démo citations."""
from __future__ import annotations

import argparse
import sys

from pathlib import Path

from src.config import DATA_PROCESSED, LOG_DIR
from src.logging_setup import setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline scraping — books.toscrape.com par défaut",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Étape 3 : analyser le CSV (pas de scrape) — stats par catégorie + tops",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="CSV à analyser avec --analyze (défaut : data/processed/books.csv)",
    )
    parser.add_argument(
        "--demo-quotes",
        action="store_true",
        help="Ancienne démo quotes.toscrape.com → data/processed/quotes.csv",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limiter le nombre de pages catalogue (liste)",
    )
    parser.add_argument(
        "--max-books",
        type=int,
        default=None,
        help="Limiter le nombre de livres réussis dans le CSV",
    )
    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="Sauver le HTML des pages liste dans data/raw/",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Chemin du CSV (défaut : data/processed/books.csv)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Logs détaillés dans le terminal (sinon : console = erreurs seulement + bloc PROCESS DONE)",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Ajouter au CSV existant sans répéter l'en-tête (nouvelles lignes en fin de fichier)",
    )
    args = parser.parse_args()

    setup_logging(LOG_DIR, verbose_console=args.verbose)

    if args.analyze:
        from src.analyze_books import run_analysis

        csv_in = Path(args.input) if args.input else DATA_PROCESSED / "books.csv"
        run_analysis(csv_in)
        return 0

    if args.demo_quotes:
        from src.pipeline import run as run_quotes

        p = run_quotes()
        print(f"CSV écrit : {p}")
        return 0

    from src.books_pipeline import run_books_scrape

    run_books_scrape(
        output_csv=args.output,
        save_raw=args.save_raw,
        max_pages=args.max_pages,
        max_books=args.max_books,
        verbose=args.verbose,
        append_csv=args.append,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
