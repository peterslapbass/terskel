"""Descarga las emisiones al aire de fuentes puntuales del RETC vía API CKAN.

Uso:
    python src/ingest/retc.py --years 2023 2024 2025
    python src/ingest/retc.py --years 2005-2025

El listado de recursos se resuelve siempre desde la API (nunca hardcodeado),
de modo que si el MMA publica una revisión cambia el hash y queda registrado.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import requests

from common.manifest import find, read_manifest, sha256_file, upsert, utc_now
from common.paths import RAW, ensure_dirs

CKAN = "https://datosretc.mma.gob.cl/api/3/action"
PACKAGE = "emisiones-al-aire-de-fuente-puntuales"
SOURCE = "retc"
DATASET = "fuente_puntual"
LICENSE = "ODbL (Open Data Commons Open Database License)"
UA = {"User-Agent": "interaction-industrial/0.1 (data acquisition)"}
YEAR_RE = re.compile(r"(\d{4})\s*$")


def api_get(path: str, **params):
    url = f"{CKAN}/{path}"
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=60)
            r.raise_for_status()
            payload = r.json()
            if not payload.get("success"):
                raise RuntimeError(f"CKAN error: {payload.get('error')}")
            return payload["result"]
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2**attempt)


def resolve_resources(years: list[int]) -> dict[int, dict]:
    pkg = api_get("package_show", id=PACKAGE)
    found: dict[int, dict] = {}
    for res in pkg["resources"]:
        m = YEAR_RE.search(res["name"].strip())
        if not m:
            continue
        year = int(m.group(1))
        if year in years:
            # el id está en /dataset/<pkg>/resource/<id>/download/<archivo>
            parts = res["url"].split("/resource/")
            rid = parts[1].split("/")[0] if len(parts) > 1 else ""
            found[year] = {**res, "resource_id": rid}
    missing = sorted(set(years) - set(found))
    if missing:
        print(f"[warn] sin recurso para: {missing}", file=sys.stderr)
    return found


def target_path(year: int, res: dict) -> Path:
    name = res["url"].rsplit("/", 1)[-1]
    suffix = Path(name).suffix.lower() or ".bin"
    return RAW / SOURCE / DATASET / str(year) / f"original{suffix}"


def download(url: str, dest: Path) -> tuple[str, int]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    total = 0
    with requests.get(url, headers=UA, stream=True, timeout=120) as r:
        r.raise_for_status()
        declared = int(r.headers.get("content-length") or 0)
        with tmp.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if not chunk:
                    continue
                fh.write(chunk)
                total += len(chunk)
                if declared:
                    pct = 100 * total / declared
                    print(f"\r  {dest.parent.name}: {total/1e6:6.1f}/{declared/1e6:.1f} MB ({pct:5.1f}%)", end="")
    print()
    tmp.replace(dest)
    return sha256_file(dest), total


def expand_years(tokens: list[str]) -> list[int]:
    years: set[int] = set()
    for tok in tokens:
        if "-" in tok:
            a, b = tok.split("-", 1)
            years.update(range(int(a), int(b) + 1))
        else:
            years.add(int(tok))
    return sorted(years)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", nargs="+", required=True, help="ej: 2023 2024 2025 o 2005-2025")
    parser.add_argument("--force", action="store_true", help="re-descargar aunque el hash coincida")
    args = parser.parse_args(argv)

    ensure_dirs()
    years = expand_years(args.years)
    print(f"Resolviendo recursos RETC/{DATASET} para {years} ...")
    resources = resolve_resources(years)
    manifest = read_manifest()

    for year in years:
        res = resources.get(year)
        if not res:
            continue
        dest = target_path(year, res)
        prev = find(manifest, SOURCE, DATASET, year)

        if dest.exists() and prev and not args.force:
            current = sha256_file(dest)
            if current == prev["sha256"]:
                print(f"[{year}] sin cambios (sha256 {current[:12]}…) -> skip")
                continue
            # el archivo local cambió: se conserva como versión anterior
            backup = dest.with_name(f"original.{current[:12]}{dest.suffix}")
            dest.replace(backup)
            print(f"[{year}] versión local distinta, respaldada en {backup.name}")

        print(f"[{year}] descargando {res['name']}")
        digest, size = download(res["url"], dest)

        upsert(
            {
                "source": SOURCE,
                "dataset": DATASET,
                "year": year,
                "resource_id": res["resource_id"],
                "resource_name": res["name"],
                "url": res["url"],
                "format": res.get("format", ""),
                "size_bytes": size,
                "last_modified": res.get("last_modified", ""),
                "sha256": digest,
                "downloaded_at": utc_now(),
                "license": LICENSE,
                "local_path": str(dest.relative_to(RAW.parent.parent)),
                "notes": "emisiones al aire de fuentes puntuales; unidad sin declarar en metadatos",
            }
        )
        print(f"[{year}] ok {size/1e6:.1f} MB sha256={digest[:12]}…")

    print("Listo. Manifest:", RAW / "manifest.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
