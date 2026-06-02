#!/usr/bin/env python3
"""Point d'entrée session 2 (local ou conteneur Docker)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    print(f"Session 2 — racine : {ROOT}")
    print("Branche ton code dans src/, puis étends ce script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
