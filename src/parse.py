"""Extraction de données structurées depuis le HTML."""
from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup


def parse_quotes_toscrape(html: str) -> List[Dict[str, str]]:
    """
    Exemple : quotes.toscrape.com — chaque citation dans un div.quote.
    Retourne une liste de dicts {text, author, tags}.
    """
    soup = BeautifulSoup(html, "lxml")
    rows: list[dict[str, str]] = []

    for quote in soup.select("div.quote"):
        text_el = quote.select_one("span.text")
        author_el = quote.select_one("small.author")
        tag_els = quote.select("div.tags a.tag")

        text = text_el.get_text(strip=True) if text_el else ""
        author = author_el.get_text(strip=True) if author_el else ""
        tags = ", ".join(t.get_text(strip=True) for t in tag_els)

        rows.append({"text": text, "author": author, "tags": tags})

    return rows
