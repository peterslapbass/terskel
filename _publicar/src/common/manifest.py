"""Manifest de adquisición: una fila por archivo descargado.

Reglas:
- Nunca se sobrescribe silenciosamente un archivo raw: si cambia el sha256,
  se registra una fila nueva y se conserva el anterior con otro nombre.
- El manifest es la fuente de verdad de la trazabilidad (URL, fecha, hash).
"""
from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .paths import MANIFEST_PATH, ensure_dirs

FIELDS = [
    "source",
    "dataset",
    "year",
    "resource_id",
    "resource_name",
    "url",
    "format",
    "size_bytes",
    "last_modified",
    "sha256",
    "downloaded_at",
    "license",
    "local_path",
    "notes",
]

KEY = ("source", "dataset", "year", "sha256")


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(path: Path = MANIFEST_PATH) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def find(records: Iterable[dict], source: str, dataset: str, year: int | str) -> dict | None:
    year = str(year)
    for r in records:
        if r.get("source") == source and r.get("dataset") == dataset and str(r.get("year")) == year:
            return r
    return None


def upsert(record: dict, path: Path = MANIFEST_PATH) -> None:
    ensure_dirs()
    record = {k: record.get(k, "") for k in FIELDS}
    rows = read_manifest(path)
    rows = [r for r in rows if not all(str(r.get(k, "")) == str(record[k]) for k in KEY)]
    rows.append(record)
    rows.sort(key=lambda r: (r.get("source", ""), r.get("dataset", ""), str(r.get("year", ""))))
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
