"""Téléchargement HTTP (pages HTML ou réponses API)."""
from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from src.config import REQUEST_DELAY_SEC, USER_AGENT

logger = logging.getLogger("cours_scraping.fetch")


def fetch_html(url: str, delay_sec: Optional[float] = None) -> str:
    """Récupère le corps HTML d'une URL."""
    delay = REQUEST_DELAY_SEC if delay_sec is None else delay_sec
    if delay > 0:
        time.sleep(delay)

    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def fetch_html_with_retry(
    url: str,
    *,
    max_retries: int = 3,
    delay_sec: Optional[float] = None,
    backoff: float = 2.0,
) -> str:
    """fetch_html avec retry exponentiel en cas d'erreur réseau."""
    last_err: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            return fetch_html(url, delay_sec=delay_sec)
        except requests.RequestException as e:
            last_err = e
            if attempt < max_retries:
                wait = backoff ** attempt
                logger.warning("Retry %s/%s pour %s (attente %.1fs) : %s", attempt, max_retries, url, wait, e)
                time.sleep(wait)
    raise last_err  # type: ignore[misc]


def save_raw_html(path: str, html: str) -> None:
    """Optionnel : sauvegarder le HTML brut pour debug."""
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
