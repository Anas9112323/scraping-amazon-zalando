#!/usr/bin/env python3
"""
Injecte les données seed (déjà vérifiées manuellement) dans le CSV master.
À lancer une seule fois pour initialiser la base.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RESULTS_CSV, DATA_DIR

SEED_DATE = "2026-04-22 17:21:00"

VERIFIED_DATA = [
    # ═══ LEADS : Amazon OUI, Zalando NON ═══
    {
        "Brand": "Geographical Norway", "Mot-clé": "geographical norway softshell",
        "Amazon présent": "Oui", "Amazon détail": "Oui — boutique officielle, 1K+ clients, 87% positif",
        "Amazon note": "4.2", "Amazon avis": "1000+", "Amazon prix": "30-120 €",
        "Zalando présent (neuf)": "Non", "Zalando type": "absent",
        "Zalando détail": "Non — aucune page marque trouvée",
        "Site web": "https://geographicalnorway.fr/",
        "Page contact": "https://www.geographicalnorway.com/pages/contact",
        "Page RGPD": "", "LEAD": "OUI", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Naf Naf", "Mot-clé": "naf naf robe femme",
        "Amazon présent": "Oui", "Amazon détail": "Oui — produits neufs, robes, manteaux, 1000+ résultats",
        "Amazon note": "4.0", "Amazon avis": "1000+", "Amazon prix": "28-160 €",
        "Zalando présent (neuf)": "Non", "Zalando type": "seconde_main",
        "Zalando détail": "Seconde main uniquement — pas de boutique neuve",
        "Site web": "https://www.nafnaf.com/fr/",
        "Page contact": "https://serviceclient.nafnaf.com/hc/fr/requests/new",
        "Page RGPD": "", "LEAD": "OUI", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Celio", "Mot-clé": "celio jeans homme",
        "Amazon présent": "Oui", "Amazon détail": "Oui — produits neufs (jeans, basiques)",
        "Amazon note": "4.0", "Amazon avis": "", "Amazon prix": "15-80 €",
        "Zalando présent (neuf)": "Non", "Zalando type": "seconde_main",
        "Zalando détail": "Seconde main uniquement — pas de boutique neuve",
        "Site web": "https://www.celio.com/fr-fr",
        "Page contact": "https://www.celio.com/contact",
        "Page RGPD": "", "LEAD": "OUI", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Chevignon", "Mot-clé": "chevignon blouson cuir",
        "Amazon présent": "Oui", "Amazon détail": "Oui — blousons cuir, 111+ résultats",
        "Amazon note": "4.2", "Amazon avis": "", "Amazon prix": "60-300 €",
        "Zalando présent (neuf)": "Non", "Zalando type": "seconde_main",
        "Zalando détail": "Seconde main uniquement — quelques articles d'occasion",
        "Site web": "https://www.chevignon.fr",
        "Page contact": "https://www.chevignon.fr/pages/contact",
        "Page RGPD": "https://chevignon.com/fr/pages/cgv", "LEAD": "OUI", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Eric Bompard", "Mot-clé": "eric bompard cachemire",
        "Amazon présent": "Oui", "Amazon détail": "Oui — écharpes et accessoires cachemire",
        "Amazon note": "", "Amazon avis": "", "Amazon prix": "80-500 €",
        "Zalando présent (neuf)": "Non", "Zalando type": "absent",
        "Zalando détail": "Non — aucune page marque trouvée",
        "Site web": "https://www.eric-bompard.com",
        "Page contact": "https://www.eric-bompard.com/pages/contact",
        "Page RGPD": "", "LEAD": "OUI", "Date scan": SEED_DATE,
    },
    # ═══ DÉJÀ SUR LES DEUX (NON leads) ═══
    {
        "Brand": "Petit Bateau", "Mot-clé": "petit bateau femme",
        "Amazon présent": "Oui", "Amazon détail": "Oui (~6 000 résultats)", "Amazon note": "4.5",
        "Amazon avis": "500+", "Amazon prix": "16-90 €",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~547 articles (85 femme), prix dès 29 €",
        "Site web": "https://www.petit-bateau.fr",
        "Page contact": "https://www.petit-bateau.fr/nous-contacter",
        "Page RGPD": "https://www.petit-bateau.fr/mentions-legales",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Aigle", "Mot-clé": "aigle bottes femme",
        "Amazon présent": "Oui", "Amazon détail": "Oui (~1 000 résultats, Parcours 2: 4.6★ 4700 avis)",
        "Amazon note": "4.4", "Amazon avis": "11000+", "Amazon prix": "56-188 €",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~270 articles (139 femme), prix 35-440 €",
        "Site web": "https://www.aigle.com",
        "Page contact": "https://www.aigle.com/contact", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Lacoste", "Mot-clé": "lacoste polo homme",
        "Amazon présent": "Oui", "Amazon détail": "Oui (~40 résultats polos)", "Amazon note": "4.5",
        "Amazon avis": "1000+", "Amazon prix": "40-130 €",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~4 500 articles (2 715 homme, 1 895 femme)",
        "Site web": "https://www.lacoste.com/fr/",
        "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Armor Lux", "Mot-clé": "armor lux marinière",
        "Amazon présent": "Oui", "Amazon détail": "Oui — boutique officielle, 94% positif",
        "Amazon note": "4.5", "Amazon avis": "200+", "Amazon prix": "49-149 €",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~468 articles",
        "Site web": "https://www.armorlux.com", "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Kaporal", "Mot-clé": "kaporal jeans",
        "Amazon présent": "Oui", "Amazon détail": "Oui — boutique dédiée, jeans",
        "Amazon note": "", "Amazon avis": "", "Amazon prix": "",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~330 articles",
        "Site web": "", "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Oxbow", "Mot-clé": "oxbow t-shirt homme",
        "Amazon présent": "Oui", "Amazon détail": "Oui — t-shirts, shorts, 95% positif",
        "Amazon note": "4.3", "Amazon avis": "500+", "Amazon prix": "16-110 €",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~742 articles",
        "Site web": "", "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Le Coq Sportif", "Mot-clé": "le coq sportif",
        "Amazon présent": "Oui", "Amazon détail": "Oui — vêtements sport",
        "Amazon note": "", "Amazon avis": "", "Amazon prix": "",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~230 articles",
        "Site web": "", "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Le Slip Français", "Mot-clé": "le slip français",
        "Amazon présent": "Oui", "Amazon détail": "Oui — boutique officielle",
        "Amazon note": "", "Amazon avis": "", "Amazon prix": "",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — underwear + pyjamas",
        "Site web": "", "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Veja", "Mot-clé": "veja sneakers",
        "Amazon présent": "Oui", "Amazon détail": "Oui — sneakers",
        "Amazon note": "", "Amazon avis": "", "Amazon prix": "",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~281 articles",
        "Site web": "https://www.veja-store.com", "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
    {
        "Brand": "Aubade", "Mot-clé": "aubade lingerie",
        "Amazon présent": "Oui", "Amazon détail": "Oui — boutique officielle Aubade Paris",
        "Amazon note": "", "Amazon avis": "", "Amazon prix": "",
        "Zalando présent (neuf)": "Oui", "Zalando type": "officiel",
        "Zalando détail": "Oui — ~500+ articles lingerie",
        "Site web": "", "Page contact": "", "Page RGPD": "",
        "LEAD": "NON", "Date scan": SEED_DATE,
    },
]


def seed():
    df = pd.DataFrame(VERIFIED_DATA)
    df.to_csv(RESULTS_CSV, index=False, encoding="utf-8-sig")

    leads = df[df["LEAD"] == "OUI"]
    non_leads = df[df["LEAD"] == "NON"]

    print("=" * 60)
    print("  SEED DATA INJECTÉ")
    print("=" * 60)
    print(f"  Total marques     : {len(df)}")
    print(f"  🎯 LEADS           : {len(leads)}")
    print(f"  ❌ Déjà sur les 2   : {len(non_leads)}")
    print(f"\n  🎯 Leads :")
    for _, r in leads.iterrows():
        print(f"     • {r['Brand']:25s} | Amazon: {r['Amazon détail'][:40]}")
        print(f"       {'':25s} | Zalando: {r['Zalando détail'][:50]}")
    print(f"\n  CSV → {RESULTS_CSV}")


if __name__ == "__main__":
    seed()
