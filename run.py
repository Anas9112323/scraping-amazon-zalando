#!/usr/bin/env python3
"""Point d'entrée : lancer depuis la racine du projet."""
from src.pipeline import run

if __name__ == "__main__":
    p = run()
    print(f"CSV écrit : {p}")
