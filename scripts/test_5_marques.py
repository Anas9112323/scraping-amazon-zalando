#!/usr/bin/env python3
"""
POC : scraping pipeline — test sur 5 marques françaises de vêtements.
Stratégie : Google search (site:amazon.fr / site:zalando.fr) + site officiel.
Utilise Playwright pour contourner les protections.
"""

import re
import time
import random
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
import pandas as pd
from playwright.sync_api import sync_playwright, Page, TimeoutError as PWTimeout

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REQ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}

PAUSE_MIN, PAUSE_MAX = 3, 6

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 5 marques françaises de test
# ---------------------------------------------------------------------------
TEST_BRANDS = [
    {
        "brand": "Petit Bateau",
        "origine": "France (Troyes)",
        "categorie": "Sous-vêtements / prêt-à-porter",
        "genre": "Mixte (femme + homme + enfant)",
        "style": "Basique, marin, coton, familial",
        "positionnement": "Milieu de gamme",
        "site_web": "https://www.petit-bateau.fr",
        "mot_cle_amazon": "petit bateau femme",
    },
    {
        "brand": "Jacquemus",
        "origine": "France (Paris)",
        "categorie": "Prêt-à-porter / accessoires",
        "genre": "Mixte (femme + homme)",
        "style": "Minimaliste provençal, avant-garde, solaire",
        "positionnement": "Premium / luxe accessible",
        "site_web": "https://www.jacquemus.com",
        "mot_cle_amazon": "jacquemus",
    },
    {
        "brand": "Sézane",
        "origine": "France (Paris)",
        "categorie": "Prêt-à-porter",
        "genre": "Femme",
        "style": "Parisien chic, bohème, vintage",
        "positionnement": "Milieu / premium accessible",
        "site_web": "https://www.sezane.com",
        "mot_cle_amazon": "sezane",
    },
    {
        "brand": "Aigle",
        "origine": "France (Ingrandes-sur-Vienne)",
        "categorie": "Outdoor / bottes / prêt-à-porter",
        "genre": "Mixte (femme + homme + enfant)",
        "style": "Outdoor élégant, bottes caoutchouc, imperméable",
        "positionnement": "Milieu / premium",
        "site_web": "https://www.aigle.com",
        "mot_cle_amazon": "aigle bottes femme",
    },
    {
        "brand": "Lacoste",
        "origine": "France (Paris)",
        "categorie": "Prêt-à-porter / sportswear",
        "genre": "Mixte (femme + homme)",
        "style": "Sportswear chic, polo, preppy, tennis",
        "positionnement": "Premium",
        "site_web": "https://www.lacoste.com/fr/",
        "mot_cle_amazon": "lacoste polo homme",
    },
]

DESCRIPTIONS = {
    "Petit Bateau": "Marque française historique (1893). Sous-vêtements en coton, marinières, basiques durables. Iconique chez enfants et adultes.",
    "Jacquemus": "Maison française (2009) par Simon Porte Jacquemus. Mode solaire, minimaliste, silhouettes épurées, mini-sacs cultes.",
    "Sézane": "Marque digitale parisienne (2013). Mode responsable, bohème-chic, collections capsules, modèle DNVB.",
    "Aigle": "Marque française (1853) spécialisée outdoor. Bottes caoutchouc fabriquées en France, vêtements imperméables.",
    "Lacoste": "Marque française iconique (1933). Polo au crocodile, sportswear chic, heritage tennis.",
}


def polite_pause(extra: float = 0):
    time.sleep(random.uniform(PAUSE_MIN, PAUSE_MAX) + extra)


# ---------------------------------------------------------------------------
# Google search helper
# ---------------------------------------------------------------------------
def google_search(page: Page, query: str, num: int = 10) -> list:
    """Search Google and return list of {title, url, snippet}."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.fr/search?q={encoded}&num={num}&hl=fr&gl=fr"

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        polite_pause()

        # Accept cookies if Google shows consent
        try:
            accept = page.locator("button:has-text('Tout accepter')")
            if accept.is_visible(timeout=2000):
                accept.click()
                time.sleep(2)
        except Exception:
            pass

        results = []
        items = page.locator("div.g")
        count = items.count()

        for i in range(min(count, num)):
            item = items.nth(i)
            try:
                link_el = item.locator("a").first
                title_el = item.locator("h3").first
                snippet_el = item.locator("div[data-sncf], div.VwiC3b, span.aCOpRe").first

                href = link_el.get_attribute("href") or ""
                title = title_el.inner_text() if title_el.count() > 0 else ""
                snippet = ""
                try:
                    snippet = snippet_el.inner_text() if snippet_el.is_visible(timeout=300) else ""
                except Exception:
                    pass

                if href.startswith("http"):
                    results.append({"title": title, "url": href, "snippet": snippet})
            except Exception:
                continue

        return results

    except Exception as e:
        print(f"    [ERREUR Google] {e}")
        return []


# ---------------------------------------------------------------------------
# Amazon.fr — via Google site:amazon.fr
# ---------------------------------------------------------------------------
def scrape_amazon_via_google(page: Page, brand_info: dict) -> dict:
    result = {
        "presence_amazon": "Non",
        "note_amazon": "",
        "avis_amazon": "",
        "fourchette_prix": "",
    }

    query = f'site:amazon.fr "{brand_info["brand"]}" {brand_info["mot_cle_amazon"]}'
    print(f"  → Google : « {query} »")

    hits = google_search(page, query)
    amazon_hits = [h for h in hits if "amazon.fr" in h["url"]]

    if not amazon_hits:
        print(f"    Aucun résultat Amazon via Google.")
        return result

    n = len(amazon_hits)
    result["presence_amazon"] = f"Oui ({n} résultats Google)"
    print(f"    ✓ {n} résultats Amazon trouvés via Google")

    # Extract price and rating from snippets
    prices = []
    ratings = []
    review_counts = []

    for h in amazon_hits:
        snippet = h["snippet"] + " " + h["title"]

        # Prices
        for m in re.finditer(r"(\d{1,3}[,\.]\d{2})\s*€", snippet):
            try:
                prices.append(float(m.group(1).replace(",", ".")))
            except ValueError:
                pass

        # Ratings
        for m in re.finditer(r"(\d[,\.]\d)\s*(?:sur\s*5|étoile|star)", snippet):
            try:
                ratings.append(float(m.group(1).replace(",", ".")))
            except ValueError:
                pass

        # Review counts
        for m in re.finditer(r"(\d[\d\s]*)\s*(?:évaluation|avis|note)", snippet):
            try:
                n_reviews = int(m.group(1).replace(" ", "").replace("\u202f", ""))
                review_counts.append(n_reviews)
            except ValueError:
                pass

    if ratings:
        result["note_amazon"] = f"{sum(ratings)/len(ratings):.1f}"
    if review_counts:
        result["avis_amazon"] = str(sum(review_counts))
    if prices:
        result["fourchette_prix"] = f"{min(prices):.0f}-{max(prices):.0f} €"

    # Now scrape the first actual Amazon product page for rating/reviews
    if not ratings or not review_counts:
        first_product = next(
            (h for h in amazon_hits if "/dp/" in h["url"] or "/gp/" in h["url"]),
            None
        )
        if first_product:
            print(f"    → Visite produit Amazon : {first_product['url'][:80]}...")
            try:
                page.goto(first_product["url"], wait_until="domcontentloaded", timeout=20000)
                polite_pause()

                # Accept cookies
                try:
                    accept_btn = page.locator("#sp-cc-accept")
                    if accept_btn.is_visible(timeout=2000):
                        accept_btn.click()
                        time.sleep(1)
                except Exception:
                    pass

                # Rating
                if not ratings:
                    try:
                        rating_el = page.locator("span.a-icon-alt").first
                        if rating_el.is_visible(timeout=3000):
                            m = re.search(r"([\d,]+)", rating_el.inner_text())
                            if m:
                                result["note_amazon"] = m.group(1).replace(",", ".")
                    except Exception:
                        pass

                # Review count
                if not review_counts:
                    try:
                        review_el = page.locator("#acrCustomerReviewText").first
                        if review_el.is_visible(timeout=3000):
                            m = re.search(r"([\d\s]+)", review_el.inner_text().replace("\u202f", ""))
                            if m:
                                result["avis_amazon"] = m.group(1).strip().replace(" ", "")
                    except Exception:
                        pass

                # Price
                if not prices:
                    try:
                        price_el = page.locator("span.a-price span.a-offscreen").first
                        if price_el.count() > 0:
                            m = re.search(r"([\d,]+)", price_el.inner_text())
                            if m:
                                p = float(m.group(1).replace(",", "."))
                                result["fourchette_prix"] = f"{p:.0f} €"
                    except Exception:
                        pass

            except Exception as e:
                print(f"    [WARN] Visite produit : {e}")

    return result


# ---------------------------------------------------------------------------
# Zalando.fr — via Google site:zalando.fr
# ---------------------------------------------------------------------------
def check_zalando_via_google(page: Page, brand_name: str) -> str:
    query = f'site:zalando.fr "{brand_name}"'
    print(f"  → Google : « {query} »")

    hits = google_search(page, query)
    zalando_hits = [h for h in hits if "zalando.fr" in h["url"]]

    if not zalando_hits:
        print(f"    Aucun résultat Zalando via Google.")
        return "Non trouvé"

    n = len(zalando_hits)
    brand_lower = brand_name.lower()

    relevant = [h for h in zalando_hits if brand_lower in h["title"].lower() or brand_lower in h["snippet"].lower()]

    if relevant:
        print(f"    ✓ {len(relevant)} résultats Zalando pertinents")
        return f"Oui ({len(relevant)} pages Google)"
    elif zalando_hits:
        print(f"    ~ {n} résultats Zalando (pertinence incertaine)")
        return f"Probablement oui ({n} pages)"

    return "Non trouvé"


# ---------------------------------------------------------------------------
# Enrichissement site officiel
# ---------------------------------------------------------------------------
def enrich_website(brand_info: dict) -> dict:
    result = {"page_contact": "", "email_general": "", "page_rgpd": ""}
    base = brand_info["site_web"].rstrip("/")

    contact_paths = ["/contact", "/nous-contacter", "/contactez-nous", "/pages/contact", "/fr/contact"]
    legal_paths = ["/mentions-legales", "/legal", "/pages/mentions-legales", "/fr/mentions-legales", "/cgv"]

    print(f"  → Site web : scan contact & mentions légales")

    for path in contact_paths:
        url = base + path
        try:
            r = requests.head(url, headers=REQ_HEADERS, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                result["page_contact"] = url
                break
        except requests.RequestException:
            continue

    for path in legal_paths:
        url = base + path
        try:
            r = requests.head(url, headers=REQ_HEADERS, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                result["page_rgpd"] = url
                break
        except requests.RequestException:
            continue

    return result


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def process_brand(page: Page, brand_info: dict) -> dict:
    brand_name = brand_info["brand"]
    print(f"\n{'='*60}")
    print(f"▸ Traitement : {brand_name}")
    print(f"{'='*60}")

    row = {
        "Brand": brand_name,
        "Origine": brand_info["origine"],
        "Catégorie": brand_info["categorie"],
        "Genre": brand_info["genre"],
        "Style": brand_info["style"],
        "Positionnement": brand_info["positionnement"],
    }

    amazon_data = scrape_amazon_via_google(page, brand_info)
    polite_pause(extra=2)

    row["Fourchette prix (€)"] = amazon_data["fourchette_prix"]
    row["Avis (est. Amazon)"] = amazon_data["avis_amazon"]
    row["Note Amazon"] = amazon_data["note_amazon"]
    row["Description courte"] = DESCRIPTIONS.get(brand_name, "")
    row["Mot-clé principal"] = brand_info["mot_cle_amazon"]
    row["Lien site web"] = brand_info["site_web"]

    web_data = enrich_website(brand_info)
    polite_pause()

    row["Page contact (commercial)"] = web_data["page_contact"]
    row["Email (Général)"] = web_data["email_general"] or "N/A (formulaire)"
    row["Page RGPD / mentions légales"] = web_data["page_rgpd"]
    row["Présence Amazon.fr"] = amazon_data["presence_amazon"]

    zalando = check_zalando_via_google(page, brand_name)
    polite_pause(extra=2)

    row["Présence Zalando.fr"] = zalando

    return row


def main():
    print("=" * 60)
    print("  POC Scraping — 5 marques françaises (via Google)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="fr-FR",
            viewport={"width": 1440, "height": 900},
            java_script_enabled=True,
        )

        # Hide webdriver flag
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        page = context.new_page()

        for brand_info in TEST_BRANDS:
            row = process_brand(page, brand_info)
            results.append(row)

        browser.close()

    df = pd.DataFrame(results)

    csv_path = OUTPUT_DIR / f"test_5_marques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print("\n\n" + "=" * 80)
    print("  RÉSULTATS")
    print("=" * 80)

    for _, row in df.iterrows():
        print(f"\n{'─'*60}")
        for col in df.columns:
            val = row[col] if pd.notna(row[col]) and row[col] != "" else "—"
            print(f"  {col:35s} │ {val}")

    print(f"\n\n✅ CSV exporté → {csv_path}")
    print(f"   {len(results)} marques traitées.\n")

    return df


if __name__ == "__main__":
    main()
