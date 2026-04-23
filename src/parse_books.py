"""Parsing HTML pour books.toscrape.com (BeautifulSoup)."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def _parse_price_gbp(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"[\d.]+", text.replace(",", ""))
    if not m:
        return None
    return float(m.group())


def _rating_from_star_rating(star_el: Any) -> Optional[int]:
    if not star_el:
        return None
    for c in star_el.get("class", []):
        if c in RATING_MAP:
            return RATING_MAP[c]
    return None


def extract_category_from_breadcrumb(soup: BeautifulSoup) -> str:
    """Dernière entrée catégorie (dernier lien .../category/... avant le titre actif)."""
    last = ""
    for a in soup.select("ul.breadcrumb li a"):
        href = a.get("href") or ""
        if "category" in href:
            last = a.get_text(strip=True)
    return last


def parse_book_detail(html: str, url: str) -> Dict[str, Any]:
    """
    Parse une fiche produit. Lève ValueError si structure inattendue.
    """
    soup = BeautifulSoup(html, "lxml")
    main = soup.select_one("div.product_main")
    if not main:
        raise ValueError("div.product_main introuvable")

    h1 = main.select_one("h1")
    title = h1.get_text(strip=True) if h1 else ""

    price_el = main.select_one("p.price_color")
    price_raw = price_el.get_text(strip=True) if price_el else ""
    price_gbp = _parse_price_gbp(price_raw)

    rating_el = main.select_one("p.star-rating")
    rating = _rating_from_star_rating(rating_el)

    category = extract_category_from_breadcrumb(soup)

    upc = ""
    availability = ""
    num_reviews: Optional[int] = None
    table = soup.select_one("table.table")
    if table:
        for row in table.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if not th or not td:
                continue
            key = th.get_text(strip=True).lower()
            val = td.get_text(strip=True)
            if key == "upc":
                upc = val
            elif key == "availability":
                availability = val
            elif key == "number of reviews":
                try:
                    num_reviews = int(val)
                except ValueError:
                    num_reviews = None

    desc_el = soup.select_one("#product_description")
    description = ""
    if desc_el:
        description = desc_el.get_text(strip=True)
    description_short = description[:200] if description else ""

    author = ""

    return {
        "title": title,
        "category": category,
        "author": author,
        "price_gbp": price_gbp,
        "price_raw": price_raw,
        "rating": rating,
        "availability": availability,
        "upc": upc,
        "num_reviews": num_reviews,
        "description_short": description_short,
        "url": url,
    }


def book_urls_from_listing_page(html: str, base_url: str) -> List[str]:
    """Liens absolus vers les fiches depuis une page liste (index ou catalogue/page-N)."""
    soup = BeautifulSoup(html, "lxml")
    out: List[str] = []
    for a in soup.select("article.product_pod h3 a"):
        href = a.get("href")
        if href:
            out.append(urljoin(base_url, href))
    return out


def next_listing_page_url(html: str, base_url: str) -> Optional[str]:
    """URL absolue de la page suivante, ou None."""
    soup = BeautifulSoup(html, "lxml")
    next_a = soup.select_one("ul.pager li.next a")
    if not next_a:
        return None
    href = next_a.get("href")
    if not href:
        return None
    return urljoin(base_url, href)
