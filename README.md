# Pipeline Scraping — Marques FR Amazon vs Zalando

Pipeline automatisé qui identifie les marques françaises de vêtements présentes sur **Amazon.fr** mais **absentes de Zalando.fr**, pour les rediriger vers Zalando via **Mirakl**.

## Objectif

Trouver des **leads** : marques qui vendent sur Amazon.fr mais ne sont pas (encore) sur Zalando.fr → leur proposer d'y aller via Mirakl.

## Architecture

```
pipeline/
├── run_batch.py          # Script principal — batch quotidien
├── checker.py            # Moteur de vérification Amazon + Zalando
├── sheets.py             # Export auto vers Google Sheets
├── config.py             # Configuration (paths, batch size)
├── seed_data.py          # Données vérifiées initiales (15 marques)
├── brands_queue.json     # File d'attente (50 marques FR)
├── cron_pipeline.sh      # Script bash pour le cron job
├── export_excel.py       # Export Excel formaté (.xlsx)
├── setup_gsheet.py       # Setup Google Sheets (one-time)
├── requirements.txt      # Dépendances Python
└── .env.example          # Template config
```

## Colonnes de données

| Colonne | Description |
|---------|-------------|
| Brand | Nom de la marque |
| Amazon présent | Oui/Non sur Amazon.fr |
| Amazon détail | Détails (nb résultats, boutique officielle) |
| Amazon note | Note moyenne Amazon |
| Amazon avis | Nombre d'avis estimé |
| Amazon prix | Fourchette de prix (€) |
| Zalando présent (neuf) | Oui/Non sur Zalando.fr (produits neufs) |
| Zalando type | officiel / seconde_main / absent |
| Zalando détail | Détails présence Zalando |
| Site web | URL du site officiel |
| Page contact | URL page contact/commercial |
| Page RGPD | URL mentions légales |
| LEAD | **OUI** = Amazon oui + Zalando non |
| Date scan | Date du dernier scan |

## Installation

```bash
cd pipeline
pip install -r requirements.txt
cp .env.example .env
# Édite .env avec ta clé SerpAPI (optionnel)
```

## Usage

```bash
# Lancer un batch (10 marques)
python3 pipeline/run_batch.py

# Traiter toutes les marques
python3 pipeline/run_batch.py --all

# Remettre la queue à zéro
python3 pipeline/run_batch.py --reset

# Exporter en Excel formaté
python3 pipeline/export_excel.py

# Setup Google Sheets (one-time)
python3 pipeline/setup_gsheet.py
```

## Cron Job (quotidien à 8h)

```bash
# macOS (launchd)
launchctl load ~/Library/LaunchAgents/com.scraping.pipeline.plist

# Linux (crontab)
crontab -e
0 8 * * * /chemin/vers/pipeline/cron_pipeline.sh
```

## Google Sheets (auto-sync)

1. Crée un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Active **Google Sheets API** + **Google Drive API**
3. Crée un **Service Account** → télécharge le JSON
4. Place le fichier dans `pipeline/google_creds.json`
5. Lance `python3 pipeline/setup_gsheet.py`

## SerpAPI (recommandé)

Pour une vérification fiable Amazon/Zalando :
1. Inscris-toi sur [serpapi.com](https://serpapi.com/) (100 recherches/mois gratuites)
2. Ajoute `SERPAPI_KEY=ta_cle` dans `pipeline/.env`

## Résultats actuels

- **5 LEADS identifiés** : Geographical Norway, Naf Naf, Celio, Chevignon, Eric Bompard
- **10 marques déjà sur les 2** : Petit Bateau, Aigle, Lacoste, Armor Lux, etc.
- **40 marques restantes** dans la queue
