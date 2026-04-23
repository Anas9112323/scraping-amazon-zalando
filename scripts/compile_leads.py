#!/usr/bin/env python3
"""
Pipeline final : marques FR sur Amazon.fr MAIS PAS sur Zalando.fr.
= Leads commerciaux pour les rediriger vers Zalando.
"""

from datetime import datetime
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# LEADS : Amazon OUI + Zalando NON (ou seconde main uniquement)
# ═══════════════════════════════════════════════════════════════════
leads = [
    {
        "Brand": "Geographical Norway",
        "Origine": "France (équipes, locaux et entrepôts en France)",
        "Catégorie": "Outdoor / softshell / sportswear",
        "Genre": "Mixte (femme + homme + enfant)",
        "Style": "Outdoor inspiré nordique, softshell, doudounes, ski",
        "Positionnement": "Mass market / accessible",
        "Fourchette prix (€)": "30-120 €",
        "Avis (est. Amazon)": "1 000+ clients, 87% positif",
        "Note Amazon": "~4.2",
        "Description courte": "Marque française d'outdoor au style nordique. Softshells, doudounes, vestes de ski. Très fort volume Amazon avec boutique officielle dédiée.",
        "Mot-clé principal": "geographical norway softshell homme",
        "Lien site web": "https://geographicalnorway.fr/",
        "Page contact (commercial)": "https://www.geographicalnorway.com/pages/contact",
        "Email (Général)": "Via formulaire (horaires: L-J 9h-17h, V 9h-15h30)",
        "Page RGPD / mentions légales": "https://geographicalnorway.fr/",
        "Présence Amazon.fr": "OUI — boutique officielle, vestes softshell, 1K+ clients, 87% positif",
        "Présence Zalando.fr": "NON — aucune page marque trouvée",
        "Statut lead": "🎯 CIBLE PRIORITAIRE — gros volume Amazon, absent de Zalando",
    },
    {
        "Brand": "Naf Naf",
        "Origine": "France (Épinay-sur-Seine, Groupe Beaumanoir)",
        "Catégorie": "Prêt-à-porter femme",
        "Genre": "Femme",
        "Style": "Féminin, robes, manteaux, casual chic",
        "Positionnement": "Milieu de gamme",
        "Fourchette prix (€)": "28-160 €",
        "Avis (est. Amazon)": "1 000+ résultats robes",
        "Note Amazon": "~4.0",
        "Description courte": "Marque française de PAP féminin (1973). Robes, manteaux, blouses. Rejoint Groupe Beaumanoir en 2024. Forte présence Amazon avec produits neufs.",
        "Mot-clé principal": "naf naf robe femme",
        "Lien site web": "https://www.nafnaf.com/fr/",
        "Page contact (commercial)": "https://serviceclient.nafnaf.com/hc/fr/requests/new",
        "Email (Général)": "communication@nafnaf.fr / serviceclient@eboutique.nafnaf.com",
        "Page RGPD / mentions légales": "https://www.nafnaf.com/fr/",
        "Présence Amazon.fr": "OUI — produits neufs, robes, manteaux, 1000+ résultats",
        "Présence Zalando.fr": "SECONDE MAIN UNIQUEMENT — pas de boutique officielle neuve",
        "Statut lead": "🎯 CIBLE PRIORITAIRE — produits neufs Amazon, seulement occasion Zalando",
    },
    {
        "Brand": "Celio",
        "Origine": "France (Saint-Ouen)",
        "Catégorie": "Prêt-à-porter homme",
        "Genre": "Homme",
        "Style": "Casual masculin, basiques, jeans, chemises",
        "Positionnement": "Mass market / accessible",
        "Fourchette prix (€)": "15-80 €",
        "Avis (est. Amazon)": "Présence confirmée (jeans, basiques)",
        "Note Amazon": "~4.0",
        "Description courte": "Marque française de PAP homme (1985). Basiques masculins, jeans, chemises. Réseau de 1000+ boutiques dans le monde.",
        "Mot-clé principal": "celio jeans homme",
        "Lien site web": "https://www.celio.com/fr-fr",
        "Page contact (commercial)": "https://www.celio.com/contact",
        "Email (Général)": "contact@celio.com / Tel: 09 69 32 34 20",
        "Page RGPD / mentions légales": "https://www.celio.com/fr-fr",
        "Présence Amazon.fr": "OUI — produits neufs (jeans, basiques)",
        "Présence Zalando.fr": "SECONDE MAIN UNIQUEMENT — pas de boutique officielle neuve",
        "Statut lead": "🎯 CIBLE — gros réseau physique, manque Zalando neuf",
    },
    {
        "Brand": "Chevignon",
        "Origine": "France (Paris, 36 rue du Faubourg Saint Antoine)",
        "Catégorie": "Prêt-à-porter / blousons cuir",
        "Genre": "Mixte (homme + femme)",
        "Style": "Américain vintage, cuir, aviateur, casual heritage",
        "Positionnement": "Milieu / premium",
        "Fourchette prix (€)": "60-300 €",
        "Avis (est. Amazon)": "111+ résultats blousons cuir",
        "Note Amazon": "~4.2",
        "Description courte": "Marque française iconique (1979). Blousons cuir, aviateurs, style américain vintage. 111 résultats Amazon pour blousons cuir.",
        "Mot-clé principal": "chevignon blouson cuir homme",
        "Lien site web": "https://www.chevignon.fr",
        "Page contact (commercial)": "https://www.chevignon.fr/pages/contact",
        "Email (Général)": "serviceclients@chevignon.fr / Tel: 01 85 78 63 75",
        "Page RGPD / mentions légales": "https://chevignon.com/fr/pages/cgv",
        "Présence Amazon.fr": "OUI — produits neufs, blousons cuir, 111+ résultats",
        "Présence Zalando.fr": "SECONDE MAIN UNIQUEMENT — quelques articles d'occasion",
        "Statut lead": "🎯 CIBLE — marque heritage, produits neufs Amazon, absent neuf Zalando",
    },
    {
        "Brand": "Eric Bompard",
        "Origine": "France (Neuilly-sur-Seine)",
        "Catégorie": "Cachemire / prêt-à-porter premium",
        "Genre": "Mixte (femme + homme)",
        "Style": "Cachemire haut de gamme, basiques luxe, écharpes, pulls",
        "Positionnement": "Premium / luxe accessible",
        "Fourchette prix (€)": "80-500 €",
        "Avis (est. Amazon)": "Écharpes & accessoires trouvés",
        "Note Amazon": "N/A",
        "Description courte": "Maison française de cachemire haut de gamme. Pulls, écharpes, accessoires en cachemire. Présence Amazon via accessoires.",
        "Mot-clé principal": "eric bompard cachemire",
        "Lien site web": "https://www.eric-bompard.com",
        "Page contact (commercial)": "https://www.eric-bompard.com/pages/contact",
        "Email (Général)": "contact@eric-bompard.com / Tel: +33 1 40 12 00 40",
        "Page RGPD / mentions légales": "https://www.eric-bompard.com",
        "Présence Amazon.fr": "OUI — écharpes et accessoires cachemire",
        "Présence Zalando.fr": "NON — aucune page marque trouvée",
        "Statut lead": "🎯 CIBLE — niche premium cachemire, absent de Zalando",
    },
]

# ═══════════════════════════════════════════════════════════════════
# MARQUES DÉJÀ SUR LES DEUX (référence)
# ═══════════════════════════════════════════════════════════════════
already_both = [
    {"Brand": "Petit Bateau", "Amazon": "OUI (~6000 résultats)", "Zalando": "OUI (~547 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Aigle", "Amazon": "OUI (~1000 résultats)", "Zalando": "OUI (~270 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Lacoste", "Amazon": "OUI (~40 polos)", "Zalando": "OUI (~4500 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Armor Lux", "Amazon": "OUI (boutique officielle)", "Zalando": "OUI (~468 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Saint James", "Amazon": "OUI (marinières)", "Zalando": "OUI (~9 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Kaporal", "Amazon": "OUI (boutique dédiée)", "Zalando": "OUI (~330 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Oxbow", "Amazon": "OUI (t-shirts, shorts)", "Zalando": "OUI (~742 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Le Coq Sportif", "Amazon": "OUI (vêtements sport)", "Zalando": "OUI (~230 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Le Slip Français", "Amazon": "OUI (boutique officielle)", "Zalando": "OUI (underwear)", "Statut": "Déjà sur les 2"},
    {"Brand": "Faguo", "Amazon": "OUI (chaussures)", "Zalando": "OUI (~114 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Veja", "Amazon": "OUI (sneakers)", "Zalando": "OUI (~281 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Aubade", "Amazon": "OUI (boutique officielle)", "Zalando": "OUI (~500 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Teddy Smith", "Amazon": "OUI (sweaters, t-shirts)", "Zalando": "OUI (~118 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Deeluxe", "Amazon": "OUI (boutique officielle)", "Zalando": "OUI (~53 femme)", "Statut": "Déjà sur les 2"},
    {"Brand": "Redskins", "Amazon": "OUI (blousons)", "Zalando": "OUI (chaussures, vêtements)", "Statut": "Déjà sur les 2"},
    {"Brand": "Caroll", "Amazon": "OUI (chemises)", "Zalando": "OUI (~40 blouses)", "Statut": "Déjà sur les 2"},
    {"Brand": "Von Dutch", "Amazon": "OUI (casquettes)", "Zalando": "OUI (~366 articles)", "Statut": "Déjà sur les 2"},
    {"Brand": "Banana Moon", "Amazon": "OUI (maillots)", "Zalando": "OUI (~22 articles)", "Statut": "Déjà sur les 2"},
]

df_leads = pd.DataFrame(leads)
df_both = pd.DataFrame(already_both)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")

leads_path = OUTPUT_DIR / f"LEADS_amazon_sans_zalando_{ts}.csv"
df_leads.to_csv(leads_path, index=False, encoding="utf-8-sig")

ref_path = OUTPUT_DIR / f"REF_deja_sur_les_deux_{ts}.csv"
df_both.to_csv(ref_path, index=False, encoding="utf-8-sig")

print("=" * 80)
print("  🎯 LEADS — MARQUES FR SUR AMAZON.FR MAIS PAS SUR ZALANDO.FR")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

for _, row in df_leads.iterrows():
    print(f"\n{'━'*70}")
    print(f"  {'Brand':35s} │ {row['Brand']}")
    print(f"  {'Présence Amazon.fr':35s} │ {row['Présence Amazon.fr']}")
    print(f"  {'Présence Zalando.fr':35s} │ {row['Présence Zalando.fr']}")
    print(f"  {'Statut lead':35s} │ {row['Statut lead']}")
    print(f"  {'Site web':35s} │ {row['Lien site web']}")
    print(f"  {'Contact':35s} │ {row['Email (Général)']}")
    print(f"  {'Fourchette prix':35s} │ {row['Fourchette prix (€)']}")

print(f"\n\n{'='*80}")
print(f"  📊 RÉSUMÉ")
print(f"{'='*80}")
print(f"  Marques scannées au total       : {len(leads) + len(already_both)}")
print(f"  Sur Amazon + Zalando (exclues)   : {len(already_both)}")
print(f"  🎯 LEADS (Amazon oui, Zalando non) : {len(leads)}")
print(f"\n  ✅ CSV leads     → {leads_path}")
print(f"  📋 CSV référence → {ref_path}\n")
