"""Chaîne fetch → parse → nettoyer → sauvegarder."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from src.config import DATA_PROCESSED, DATA_RAW, DEFAULT_URL
from src.fetch import fetch_html, save_raw_html
from src.parse import parse_quotes_toscrape


def run(
    url: Optional[str] = None,
    save_raw: bool = True,
    output_csv: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Exécute le pipeline démo sur quotes.toscrape.com.
    Retourne le chemin du CSV produit.
    """
    target = url or DEFAULT_URL
    html = fetch_html(target)

    if save_raw:
        raw_path = DATA_RAW / "last_page.html"
        save_raw_html(str(raw_path), html)

    rows = parse_quotes_toscrape(html)
    df = pd.DataFrame(rows)

    out = output_csv or (DATA_PROCESSED / "quotes.csv")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    return out


if __name__ == "__main__":
    path = run()
    print(f"OK — {path} ({path.stat().st_size} octets)")
