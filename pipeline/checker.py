"""
Moteur de vérification : check Amazon.fr + Zalando.fr pour une marque donnée.

Backends supportés :
  - "serpapi" : SerpAPI (fiable, 100 recherches/mois gratuites)
  - "manual"  : vérification directe par HEAD/GET requests (fallback)

Configure SERPAPI_KEY dans .env pour le mode SerpAPI.
"""

import os
import re
import time
import random
from typing import Optional
from urllib.parse import quote_plus

import requests

HEADERS_BROWSER = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}

PAUSE_MIN, PAUSE_MAX = 2, 5
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")


def _pause():
    time.sleep(random.uniform(PAUSE_MIN, PAUSE_MAX))


def _head(url: str, timeout: int = 10) -> Optional[int]:
    try:
        r = requests.head(url, headers=HEADERS_BROWSER, timeout=timeout, allow_redirects=True)
        return r.status_code
    except requests.RequestException:
        return None


def _serpapi_search(query: str, num: int = 10) -> list:
    """SerpAPI Google search. Returns list of organic results."""
    if not SERPAPI_KEY:
        return []
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "gl": "fr",
            "hl": "fr",
            "num": num,
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = r.json()
        return data.get("organic_results", [])
    except Exception as e:
        print(f"    [SerpAPI warn] {e}")
        return []


# ─────────────────────────────────────────────────────────
# Amazon.fr check
# ─────────────────────────────────────────────────────────
def check_amazon(brand_name: str, mot_cle: str) -> dict:
    result = {
        "amazon_present": False,
        "amazon_results": 0,
        "amazon_detail": "Non trouvé sur Amazon.fr",
        "amazon_note": "",
        "amazon_avis": "",
        "amazon_prix_range": "",
    }

    if SERPAPI_KEY:
        query = f'site:amazon.fr "{brand_name}" {mot_cle}'
        serp_results = _serpapi_search(query)
        amazon_hits = [r for r in serp_results if "amazon.fr" in r.get("link", "")]
        n = len(amazon_hits)

        if n > 0:
            result["amazon_present"] = True
            result["amazon_results"] = n
            result["amazon_detail"] = f"Oui ({n} résultats SerpAPI)"

            prices, ratings, reviews = [], [], []
            for hit in amazon_hits:
                text = f"{hit.get('title', '')} {hit.get('snippet', '')}"
                for m in re.finditer(r"(\d{1,3}[,\.]\d{2})\s*€", text):
                    try:
                        prices.append(float(m.group(1).replace(",", ".")))
                    except ValueError:
                        pass
                rating_info = hit.get("rich_snippet", {}).get("top", {})
                detected = rating_info.get("detected_extensions", {}) if isinstance(rating_info, dict) else {}
                if detected.get("rating"):
                    try:
                        ratings.append(float(str(detected["rating"]).replace(",", ".")))
                    except (ValueError, TypeError):
                        pass
                if detected.get("reviews"):
                    try:
                        reviews.append(int(str(detected["reviews"]).replace(",", "").replace(" ", "")))
                    except (ValueError, TypeError):
                        pass
                for m in re.finditer(r"(\d[\d\s\u202f]*)\s*(?:évaluation|avis|note|commentaire)", text):
                    try:
                        reviews.append(int(m.group(1).replace(" ", "").replace("\u202f", "")))
                    except ValueError:
                        pass

            if ratings:
                result["amazon_note"] = f"{sum(ratings)/len(ratings):.1f}"
            if reviews:
                result["amazon_avis"] = str(sum(reviews))
            if prices:
                result["amazon_prix_range"] = f"{min(prices):.0f}-{max(prices):.0f} €"
    else:
        # Fallback: direct Amazon.fr search URL check
        search_url = f"https://www.amazon.fr/s?k={quote_plus(brand_name)}&i=fashion"
        try:
            r = requests.get(search_url, headers=HEADERS_BROWSER, timeout=15)
            if r.status_code == 200 and brand_name.lower() in r.text.lower():
                result["amazon_present"] = True
                result["amazon_detail"] = "Oui (détecté via recherche directe)"
            elif r.status_code == 200:
                result["amazon_detail"] = "Page chargée mais marque non détectée"
        except requests.RequestException:
            result["amazon_detail"] = "Impossible de vérifier (blocage Amazon)"

    return result


# ─────────────────────────────────────────────────────────
# Zalando.fr check
# ─────────────────────────────────────────────────────────
def _make_slugs(brand_name: str) -> list:
    clean = brand_name.lower().strip()
    slugs = set()
    for s in [
        clean.replace(" ", "-").replace("&", "").replace("'", "").replace(".", ""),
        clean.replace(" ", "-"),
        clean.replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace(" ", "-").replace("&", "").replace(".", ""),
    ]:
        if s:
            slugs.add(s)
    return list(slugs)


def check_zalando(brand_name: str) -> dict:
    result = {
        "zalando_present": False,
        "zalando_type": "absent",
        "zalando_detail": "Non trouvé sur Zalando.fr",
        "zalando_articles": 0,
    }

    if SERPAPI_KEY:
        query = f'site:zalando.fr "{brand_name}"'
        serp_results = _serpapi_search(query)
        zalando_hits = [r for r in serp_results if "zalando.fr" in r.get("link", "")]
        n = len(zalando_hits)

        if n == 0:
            return result

        all_text = " ".join(f"{h.get('title','')} {h.get('snippet','')} {h.get('link','')}" for h in zalando_hits).lower()
        brand_lower = brand_name.lower()

        is_secondhand = "seconde main" in all_text or "seconde-main" in all_text
        has_catalog = any(
            f"zalando.fr/{s}/" in h.get("link", "").lower() and "seconde" not in h.get("link", "").lower()
            for h in zalando_hits
            for s in _make_slugs(brand_name)
        )

        article_match = re.search(r"(\d+)\s*article", all_text)
        if article_match:
            result["zalando_articles"] = int(article_match.group(1))

        if has_catalog:
            result["zalando_present"] = True
            result["zalando_type"] = "officiel"
            detail = f"Oui — catalogue officiel ({n} pages SerpAPI)"
            if result["zalando_articles"]:
                detail += f", ~{result['zalando_articles']} articles"
            result["zalando_detail"] = detail
        elif is_secondhand:
            result["zalando_type"] = "seconde_main"
            result["zalando_detail"] = "Seconde main uniquement"
        elif any(brand_lower in f"{h.get('title','')} {h.get('snippet','')}".lower() for h in zalando_hits):
            result["zalando_present"] = True
            result["zalando_type"] = "probable"
            result["zalando_detail"] = f"Probablement oui ({n} résultats)"
        else:
            result["zalando_detail"] = f"Résultats non pertinents ({n})"
    else:
        # Fallback: direct slug check (souvent bloqué 403, mais on essaie)
        for slug in _make_slugs(brand_name):
            url = f"https://www.zalando.fr/{slug}/"
            status = _head(url, timeout=10)
            if status == 200:
                result["zalando_present"] = True
                result["zalando_type"] = "officiel"
                result["zalando_detail"] = f"Oui — page /{slug}/ accessible"
                return result
            elif status == 301 or status == 302:
                result["zalando_present"] = True
                result["zalando_type"] = "probable"
                result["zalando_detail"] = f"Redirection depuis /{slug}/"
                return result

        result["zalando_detail"] = "Impossible de vérifier (blocage Zalando 403)"

    return result


# ─────────────────────────────────────────────────────────
# Site officiel enrichment
# ─────────────────────────────────────────────────────────
def enrich_website(brand_name: str) -> dict:
    result = {"site_web": "", "page_contact": "", "page_rgpd": ""}

    clean = brand_name.lower().replace("&", "").replace("'", "").replace(".", "").strip()
    for base in [
        f"https://www.{clean.replace(' ', '')}.fr",
        f"https://www.{clean.replace(' ', '')}.com",
        f"https://www.{clean.replace(' ', '-')}.fr",
        f"https://www.{clean.replace(' ', '-')}.com",
    ]:
        status = _head(base)
        if status and status < 400:
            result["site_web"] = base
            break

    if not result["site_web"]:
        return result

    base = result["site_web"].rstrip("/")
    for path in ["/contact", "/nous-contacter", "/pages/contact", "/fr/contact"]:
        status = _head(base + path)
        if status and status < 400:
            result["page_contact"] = base + path
            break

    for path in ["/mentions-legales", "/pages/mentions-legales", "/legal", "/cgv"]:
        status = _head(base + path)
        if status and status < 400:
            result["page_rgpd"] = base + path
            break

    return result


# ─────────────────────────────────────────────────────────
# Pipeline complet
# ─────────────────────────────────────────────────────────
def process_brand(brand_name: str, mot_cle: str) -> dict:
    mode = "SerpAPI" if SERPAPI_KEY else "fallback"
    print(f"  [1/3] Check Amazon ({mode}) : {brand_name}")
    amazon = check_amazon(brand_name, mot_cle)
    _pause()

    print(f"  [2/3] Check Zalando ({mode}) : {brand_name}")
    zalando = check_zalando(brand_name)
    _pause()

    print(f"  [3/3] Enrichissement site : {brand_name}")
    website = enrich_website(brand_name)

    is_lead = amazon["amazon_present"] and not zalando["zalando_present"]

    return {
        "Brand": brand_name,
        "Mot-clé": mot_cle,
        "Amazon présent": "Oui" if amazon["amazon_present"] else "Non",
        "Amazon détail": amazon["amazon_detail"],
        "Amazon note": amazon["amazon_note"],
        "Amazon avis": amazon["amazon_avis"],
        "Amazon prix": amazon["amazon_prix_range"],
        "Zalando présent (neuf)": "Oui" if zalando["zalando_present"] else "Non",
        "Zalando type": zalando["zalando_type"],
        "Zalando détail": zalando["zalando_detail"],
        "Site web": website["site_web"],
        "Page contact": website["page_contact"],
        "Page RGPD": website["page_rgpd"],
        "LEAD": "OUI" if is_lead else "NON",
        "Date scan": "",
    }
