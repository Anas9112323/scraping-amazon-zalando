"""Configuration du logging (fichier rotatif + console)."""
from __future__ import annotations

import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

_LOG_NAME = "cours_scraping"


def setup_logging(
    log_dir: Union[str, Path],
    *,
    name: str = _LOG_NAME,
    level: int = logging.DEBUG,
    verbose_console: bool = False,
) -> logging.Logger:
    """
    Fichier : tout le détail (DEBUG+).
    Console : par défaut seulement WARNING/ERROR (problèmes visibles) ;
    avec verbose_console=True, repasse en INFO détaillé comme avant.
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"scrape_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    fmt_file = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fmt_console_verbose = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    fmt_console_quiet = logging.Formatter(
        "%(levelname)s | %(message)s",
    )

    fh = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt_file)

    ch = logging.StreamHandler()
    if verbose_console:
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt_console_verbose)
    else:
        ch.setLevel(logging.WARNING)
        ch.setFormatter(fmt_console_quiet)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.debug("Logging initialisé — fichier %s", log_file)
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Logger enfant du projet (même hiérarchie que setup_logging)."""
    if name:
        return logging.getLogger(f"{_LOG_NAME}.{name}")
    return logging.getLogger(_LOG_NAME)
