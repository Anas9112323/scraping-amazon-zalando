"""Téléchargement HTTP (pages HTML ou réponses API)."""
from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from src.config import (
    FETCH_BACKOFF_BASE_SEC,
    FETCH_MAX_RETRIES,
    FETCH_TIMEOUT_SEC,
    REQUEST_DELAY_SEC,
    USER_AGENT,
)

logger = logging.getLogger("cours_scraping.fetch")


def fetch_html(url: str, delay_sec: Optional[float] = None) -> str:
    """Récupère le corps HTML d'une URL."""
    delay = REQUEST_DELAY_SEC if delay_sec is None else delay_sec
    if delay > 0:
        time.sleep(delay)

    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=FETCH_TIMEOUT_SEC)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def fetch_html_with_retry(
    url: str,
    *,
    delay_sec: Optional[float] = None,
    max_retries: Optional[int] = None,
    backoff_base: Optional[float] = None,
) -> str:
    """
    GET avec pause (REQUEST_DELAY), retries sur erreurs réseau / 5xx.
    Ne retry pas sur 4xx (client). Lève la dernière exception si échec total.
    """
    delay = REQUEST_DELAY_SEC if delay_sec is None else delay_sec
    retries = FETCH_MAX_RETRIES if max_retries is None else max_retries
    backoff = FETCH_BACKOFF_BASE_SEC if backoff_base is None else backoff_base

    if delay > 0:
        time.sleep(delay)

    headers = {"User-Agent": USER_AGENT}
    last_exc: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=FETCH_TIMEOUT_SEC)
            if resp.status_code >= 500 and attempt < retries:
                wait = backoff ** (attempt - 1)
                logger.debug(
                    "HTTP %s pour %s — réessai %s/%s dans %.1fs",
                    resp.status_code,
                    url,
                    attempt,
                    retries,
                    wait,
                )
                time.sleep(wait)
                continue
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            logger.debug("GET OK %s (%s octets)", url, len(resp.text))
            return resp.text
        except (requests.RequestException, OSError) as e:
            last_exc = e
            if attempt >= retries:
                logger.error("Échec définitif GET %s : %s", url, e)
                raise
            wait = backoff ** (attempt - 1)
            logger.debug(
                "Erreur réseau %s (%s) — tentative %s/%s dans %.1fs",
                url,
                e,
                attempt,
                retries,
                wait,
            )
            time.sleep(wait)

    assert last_exc is not None
    raise last_exc


def save_raw_html(path: str, html: str) -> None:
    """Optionnel : sauvegarder le HTML brut pour debug."""
    from pathlib import Path

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
