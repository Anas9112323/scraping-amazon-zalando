"""Notification Slack optionnelle (Incoming Webhook)."""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import requests

logger = logging.getLogger("cours_scraping.slack")


def send_slack_message(webhook_url: str, text: str) -> bool:
    """
    Envoie un message texte simple (Incoming Webhook).
    Ne lève pas si le webhook échoue — log WARNING et False.
    """
    try:
        r = requests.post(
            webhook_url,
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        r.raise_for_status()
        logger.info("Notification Slack envoyée")
        return True
    except (requests.RequestException, OSError) as e:
        logger.warning("Slack non envoyé : %s", e)
        return False


_SLACK_MAX_LEN = 3000


def format_run_summary(
    *,
    success: bool,
    rows_written: int,
    rows_skipped: int,
    pages: int,
    duration_sec: float,
    csv_path: str,
    error: Optional[str] = None,
    failure_samples: Optional[List[Tuple[str, str]]] = None,
) -> str:
    status = "OK" if success else "ÉCHEC"
    lines = [
        f"*Scrape books.toscrape* — {status}",
        f"Lignes CSV : {rows_written} | ignorées : {rows_skipped} | pages liste : {pages}",
        f"Durée : {duration_sec:.1f}s",
        f"Fichier : `{csv_path}`",
    ]
    if error:
        lines.append(f"Erreur : {error[:500]}")
    if failure_samples:
        lines.append("*Échecs (extrait) :*")
        for i, (url, msg) in enumerate(failure_samples, start=1):
            line = f"{i}. `{url[:120]}` — {msg[:120]}"
            lines.append(line)
        if rows_skipped > len(failure_samples):
            lines.append(f"… et {rows_skipped - len(failure_samples)} autre(s)")
    text = "\n".join(lines)
    if len(text) > _SLACK_MAX_LEN:
        text = text[: _SLACK_MAX_LEN - 3] + "..."
    return text
