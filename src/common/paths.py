"""Rutas compartidas del proyecto."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

MANIFEST_PATH = RAW / "manifest.csv"


def ensure_dirs() -> None:
    for p in (RAW, PROCESSED, REPORTS, DOCS):
        p.mkdir(parents=True, exist_ok=True)
