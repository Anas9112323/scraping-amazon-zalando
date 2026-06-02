"""Pipeline : liste catalogue → fiches livres → CSV + logs + Slack optionnel."""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from src.config import DATA_PROCESSED, SLACK_WEBHOOK_ENV
from src.fetch import fetch_html_with_retry
from src.notify_slack import format_run_summary, send_slack_message
from src.parse_books import (
    book_urls_from_listing_page,
    next_listing_page_url,
    parse_book_detail,
)

logger = logging.getLogger("cours_scraping.books")


def _print_process_done(
    *,
    started_at: datetime,
    duration_sec: float,
    rows: int,
    skipped: int,
    pages: int,
    csv_path: Path,
    last_error: Optional[str],
    limits: str,
) -> None:
    """Résumé final visible dans le terminal (cron / 3h du mat)."""
    if rows > 0 and last_error is None:
        status = "OK"
    elif rows > 0:
        status = "PARTIAL"
    else:
        status = "FAILED"

    lines = [
        "",
        "=" * 72,
        "PROCESS DONE — books.toscrape",
        f"  début (UTC)   : {started_at.isoformat()}",
        f"  durée         : {duration_sec:.1f}s",
        f"  lignes CSV    : {rows}  |  ignorés : {skipped}  |  pages catalogue : {pages}",
        f"  fichier       : {csv_path}",
        f"  statut        : {status}",
        f"  limites       : {limits}",
    ]
    if last_error:
        lines.append(f"  erreur liste  : {last_error[:280]}")
    lines.append("=" * 72)
    print("\n".join(lines), flush=True)


_MAX_FAILURE_SAMPLES = 8


def run_books_scrape(
    *,
    start_url: Optional[str] = None,
    output_csv: Optional[Union[str, Path]] = None,
    save_raw: bool = False,
    max_pages: Optional[int] = None,
    max_books: Optional[int] = None,
    slack_webhook: Optional[str] = None,
    verbose: bool = False,
    append_csv: bool = False,
) -> Path:
    """
    Parcourt toutes les pages « All products » (pagination), puis chaque fiche livre.
    Continue en cas d'erreur sur un livre (skip + log). Ajoute scraped_at (UTC).

    Si append_csv=True et que le fichier CSV existe déjà : ajoute les lignes sans
    réécrire l'en-tête (historique multi-runs ; doublons possibles pour un même
    livre avec scraped_at différent — pas d'upsert par UPC).
    """
    from src.config import BOOKS_BASE_URL, DATA_RAW

    t0 = time.perf_counter()
    started_at = datetime.now(timezone.utc)
    start = start_url or BOOKS_BASE_URL

    lim_parts = ["catalogue complet"]
    if max_pages is not None:
        lim_parts.append(f"max {max_pages} page(s) liste")
    if max_books is not None:
        lim_parts.append(f"max {max_books} livre(s)")
    limits_str = " | ".join(lim_parts)

    rows: List[Dict[str, Any]] = []
    failure_samples: List[tuple[str, str]] = []
    skipped = 0
    pages = 0
    current_url: Optional[str] = start
    last_error: Optional[str] = None

    log = logger.info if verbose else logger.debug
    print(
        f"\n→ START scrape books.toscrape | {started_at.isoformat()} UTC\n"
        f"  source: {start}\n"
        f"  limites: {limits_str}\n",
        flush=True,
    )
    logger.debug("Démarrage scrape livres — %s | %s", start, limits_str)

    while current_url:
        if max_pages is not None and pages >= max_pages:
            logger.debug("Arrêt : limite pages atteinte (%s)", max_pages)
            break
        pages += 1
        log("Page liste %s — %s", pages, current_url)

        try:
            html = fetch_html_with_retry(current_url)
        except Exception as e:
            last_error = str(e)
            logger.error("Impossible de charger la page liste %s : %s", current_url, e)
            break

        if save_raw:
            raw_path = DATA_RAW / f"listing_{pages}.html"
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_text(html, encoding="utf-8")
            logger.debug("HTML liste sauvegardé %s", raw_path)

        book_urls = book_urls_from_listing_page(html, current_url)
        log("%s lien(s) catalogue sur cette page", len(book_urls))

        stop_scrape = False
        for book_url in book_urls:
            if max_books is not None and len(rows) >= max_books:
                logger.debug("Arrêt : limite livres atteinte (%s)", max_books)
                stop_scrape = True
                break

            try:
                detail_html = fetch_html_with_retry(book_url)
                rec = parse_book_detail(detail_html, book_url)
                rec["scraped_at"] = datetime.now(timezone.utc).isoformat()
                rows.append(rec)
                log(
                    "OK livre — %s | %s | note=%s prix=%s",
                    rec.get("title", "")[:60],
                    rec.get("category") or "?",
                    rec.get("rating"),
                    rec.get("price_gbp"),
                )
            except Exception as e:
                skipped += 1
                err_short = str(e)[:120]
                if len(failure_samples) < _MAX_FAILURE_SAMPLES:
                    failure_samples.append((book_url, err_short))
                logger.warning(
                    "SKIP livre | %s | %s",
                    book_url,
                    e,
                    exc_info=logger.isEnabledFor(logging.DEBUG),
                )

            if max_books is not None and len(rows) >= max_books:
                stop_scrape = True
                break

        if stop_scrape:
            break

        nxt = next_listing_page_url(html, current_url)
        if not nxt:
            logger.debug("Fin du catalogue (pas de page suivante)")
            break
        if nxt == current_url:
            logger.warning("Pagination boucle sur la même URL — arrêt")
            break
        current_url = nxt

    out = Path(output_csv) if output_csv else DATA_PROCESSED / "books.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    if df.empty:
        logger.warning("Aucune ligne écrite — CSV vide")
    else:
        file_exists = out.exists() and out.stat().st_size > 0
        use_append = append_csv and file_exists
        df.to_csv(
            out,
            mode="a" if use_append else "w",
            index=False,
            header=not use_append,
            encoding="utf-8",
        )
        if use_append:
            logger.debug("CSV : lignes ajoutées sans nouvel en-tête — %s", out)

    duration = time.perf_counter() - t0
    success = len(rows) > 0
    logger.debug(
        "Terminé — %s lignes, %s ignorés, %s pages liste, %.1fs → %s",
        len(rows),
        skipped,
        pages,
        duration,
        out,
    )

    _print_process_done(
        started_at=started_at,
        duration_sec=duration,
        rows=len(rows),
        skipped=skipped,
        pages=pages,
        csv_path=out,
        last_error=last_error,
        limits=limits_str,
    )

    webhook = slack_webhook or os.environ.get(SLACK_WEBHOOK_ENV)
    if webhook:
        msg = format_run_summary(
            success=bool(success),
            rows_written=len(rows),
            rows_skipped=skipped,
            pages=pages,
            duration_sec=duration,
            csv_path=str(out),
            error=last_error,
            failure_samples=failure_samples if failure_samples else None,
        )
        send_slack_message(webhook, msg)

    return out
