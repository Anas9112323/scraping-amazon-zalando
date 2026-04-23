#!/usr/bin/env python3
"""
Compile les résultats du POC scraping — 5 marques françaises.
Données récoltées via WebSearch + WebFetch.
"""

from datetime import datetime
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

results = [
    {
        "Brand": "Petit Bateau",
        "Origine": "France (Troyes)",
        "Catégorie": "Sous-vêtements / prêt-à-porter",
        "Genre": "Mixte (femme + homme + enfant)",
        "Style": "Basique, marin, coton, familial",
        "Positionnement": "Milieu de gamme",
        "Fourchette prix (€)": "16-90 €",
        "Avis (est. Amazon)": "~500+",
        "Note Amazon": "4.5",
        "Description courte": "Marque française historique (1893). Sous-vêtements en coton, marinières, basiques durables. Iconique chez enfants et adultes.",
        "Mot-clé principal": "petit bateau femme",
        "Lien site web": "https://www.petit-bateau.fr",
        "Page contact (commercial)": "https://www.petit-bateau.fr/nous-contacter",
        "Email (Général)": "N/A (formulaire)",
        "Page RGPD / mentions légales": "https://www.petit-bateau.fr/mentions-legales",
        "Présence Amazon.fr": "Oui — boutique officielle + resellers (~6 000 résultats)",
        "Présence Zalando.fr": "Oui — ~547 articles (85 femme), prix dès 29 €",
    },
    {
        "Brand": "Jacquemus",
        "Origine": "France (Paris)",
        "Catégorie": "Prêt-à-porter / accessoires",
        "Genre": "Mixte (femme + homme)",
        "Style": "Minimaliste provençal, avant-garde, solaire",
        "Positionnement": "Premium / luxe accessible",
        "Fourchette prix (€)": "200-2 000 €",
        "Avis (est. Amazon)": "N/A",
        "Note Amazon": "N/A",
        "Description courte": "Maison française (2009) par Simon Porte Jacquemus. Mode solaire, minimaliste, silhouettes épurées, mini-sacs cultes.",
        "Mot-clé principal": "jacquemus",
        "Lien site web": "https://www.jacquemus.com",
        "Page contact (commercial)": "N/A (pas de page contact publique)",
        "Email (Général)": "N/A",
        "Page RGPD / mentions légales": "N/A",
        "Présence Amazon.fr": "Non — aucun produit officiel trouvé",
        "Présence Zalando.fr": "Non — pas de page marque dédiée",
    },
    {
        "Brand": "Sézane",
        "Origine": "France (Paris)",
        "Catégorie": "Prêt-à-porter",
        "Genre": "Femme",
        "Style": "Parisien chic, bohème, vintage",
        "Positionnement": "Milieu / premium accessible",
        "Fourchette prix (€)": "50-300 €",
        "Avis (est. Amazon)": "N/A",
        "Note Amazon": "N/A",
        "Description courte": "Marque digitale parisienne (2013). Mode responsable, bohème-chic, collections capsules, modèle DNVB.",
        "Mot-clé principal": "sezane",
        "Lien site web": "https://www.sezane.com",
        "Page contact (commercial)": "N/A (DNVB, vente directe uniquement)",
        "Email (Général)": "N/A (formulaire)",
        "Page RGPD / mentions légales": "N/A",
        "Présence Amazon.fr": "Non — vente exclusivement sur sezane.com",
        "Présence Zalando.fr": "Non — pas disponible sur Zalando",
    },
    {
        "Brand": "Aigle",
        "Origine": "France (Ingrandes-sur-Vienne)",
        "Catégorie": "Outdoor / bottes / prêt-à-porter",
        "Genre": "Mixte (femme + homme + enfant)",
        "Style": "Outdoor élégant, bottes caoutchouc, imperméable",
        "Positionnement": "Milieu / premium",
        "Fourchette prix (€)": "56-188 €",
        "Avis (est. Amazon)": "~11 000+",
        "Note Amazon": "4.4",
        "Description courte": "Marque française (1853) spécialisée outdoor. Bottes caoutchouc fabriquées en France, vêtements imperméables.",
        "Mot-clé principal": "aigle bottes femme",
        "Lien site web": "https://www.aigle.com",
        "Page contact (commercial)": "https://www.aigle.com/contact",
        "Email (Général)": "N/A (formulaire)",
        "Page RGPD / mentions légales": "N/A",
        "Présence Amazon.fr": "Oui — boutique officielle + resellers (~1 000 résultats). Modèles phares : Parcours 2 (4.6★, 4700 avis), Benyl (4.5★, 997 avis), Chambord Pro (4.3★, 109 avis)",
        "Présence Zalando.fr": "Oui — ~270 articles (139 femme), prix 35-440 €, promos jusqu'à -50%",
    },
    {
        "Brand": "Lacoste",
        "Origine": "France (Paris)",
        "Catégorie": "Prêt-à-porter / sportswear",
        "Genre": "Mixte (femme + homme)",
        "Style": "Sportswear chic, polo, preppy, tennis",
        "Positionnement": "Premium",
        "Fourchette prix (€)": "40-130 €",
        "Avis (est. Amazon)": "~1 000+",
        "Note Amazon": "4.5",
        "Description courte": "Marque française iconique (1933). Polo au crocodile, sportswear chic, heritage tennis.",
        "Mot-clé principal": "lacoste polo homme",
        "Lien site web": "https://www.lacoste.com/fr/",
        "Page contact (commercial)": "N/A",
        "Email (Général)": "N/A (formulaire)",
        "Page RGPD / mentions légales": "N/A",
        "Présence Amazon.fr": "Oui — boutique officielle + resellers (~40 résultats polos). L1212 classique, PH4012 stretch",
        "Présence Zalando.fr": "Oui — ~4 500 articles (2 715 homme, 1 895 femme), prix dès 27 €",
    },
]

df = pd.DataFrame(results)

csv_path = OUTPUT_DIR / f"poc_5_marques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("=" * 80)
print("  POC SCRAPING — RÉSULTATS FINAUX — 5 MARQUES FRANÇAISES")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

for _, row in df.iterrows():
    print(f"\n{'─'*70}")
    for col in df.columns:
        val = row[col] if pd.notna(row[col]) and row[col] != "" else "—"
        print(f"  {col:35s} │ {val}")

print(f"\n\n✅ CSV exporté → {csv_path}")
print(f"   {len(results)} marques traitées.\n")
