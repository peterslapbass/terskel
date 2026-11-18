"""Descarga el dólar observado diario del Banco Central de Chile.

Tres rutas, en orden de preferencia:

1. **`bde-export` (por defecto, sin credenciales)** — replica la exportación a Excel
   del visor de series del BCCh (`DownloadExcel`). Devuelve la **serie completa**
   desde 1982-08-09 hasta el último día publicado, en un XLSX con fechas y valores
   en dos filas paralelas (layout horizontal).

2. **`bde` (API oficial)** — `SieteRestWS` con credenciales gratuitas del registro
   en https://siid.cl, en `BCCH_USER` / `BCCH_PASS`. Serie `F073.TCO.PRE.Z.D`.

3. **`mindicador`** — espejo del mismo dólar observado, sin credenciales. Solo
   respaldo del piloto: el servidor suele limitar la tasa de peticiones.

Cada descarga queda como archivo inmutable con la fecha del snapshot en el nombre
(`dolar_observado_bde_2026-11-11.xlsx`) y su sha256 en el manifest.

Uso:
    python src/ingest/fx.py
    python src/ingest/fx.py --source bde --years 2023 2024
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests

from common.manifest import find, read_manifest, sha256_file, upsert, utc_now
from common.paths import RAW, ensure_dirs

SOURCE = "bcch"
DATASET = "dolar_observado"
LICENSE = "Uso libre citando fuente (Banco Central de Chile)"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) interaction-industrial/0.1"}

SERIE_BDE = "F073.TCO.PRE.Z.D"  # Dólar Observado, diario
API_BDE = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
API_MINDICADOR = "https://mindicador.cl/api/dolar"
PAGINA_BDE = (
    "https://si3.bcentral.cl/Siete/ES/Siete/Cuadro/CAP_TIPO_CAMBIO/"
    "MN_TIPO_CAMBIO4/DOLAR_OBS_ADO?idSerie=F073.TCO.PRE.Z.D"
)
EXPORT_BDE = "https://si3.bcentral.cl/Siete/ES/Siete/DownloadExcel"
TOKEN_RE = re.compile(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"')


def get_json(url: str, params: dict | None = None) -> dict:
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("inalcanzable")


def descargar_bde_export() -> bytes:
    """Replica la exportación Excel del visor de series (serie completa)."""
    s = requests.Session()
    s.headers.update(UA)

    r = s.get(PAGINA_BDE, timeout=60)
    r.raise_for_status()
    m = TOKEN_RE.search(r.text)
    if not m:
        raise RuntimeError("no se encontró __RequestVerificationToken en la página del BCCh")
    token = m.group(1)

    form = {
        "__RequestVerificationToken": token,
        "codCuadro": "DOLAR_OBS_ADO",
        "frecuencia": "DAILY",
        "calculo": "NONE",
        "IsVertical": "false",
        "IsFullSeries": "true",
        "SoloSeries": "N",
        "fechaInicio": "",
        "fechaTermino": "",
        "fechaDiaria": "",
        "VistaOrigen": "CuadroSearch",
        "Series": "",
    }
    p = s.post(EXPORT_BDE, data=form, timeout=120)
    p.raise_for_status()
    if not p.content.startswith(b"PK"):
        raise RuntimeError(f"el BCCh no devolvió un XLSX (content-type={p.headers.get('content-type')})")
    return p.content


def fetch_bde(year: int, user: str, password: str) -> dict:
    return get_json(
        API_BDE,
        {
            "user": user,
            "pass": password,
            "function": "GetSeries",
            "timeseries": SERIE_BDE,
            "firstdate": f"{year}-01-01",
            "lastdate": f"{year}-12-31",
        },
    )


def fetch_mindicador(year: int) -> dict:
    return get_json(f"{API_MINDICADOR}/{year}")


def _registrar(path: Path, year: int, url: str, notas: str, resource_name: str) -> None:
    digest = sha256_file(path)
    manifest = read_manifest()
    prev = find(manifest, SOURCE, DATASET, year)
    if prev and prev.get("sha256") == digest:
        print(f"  sin cambios (sha256={digest[:12]}…)")
        return
    upsert({
        "source": SOURCE,
        "dataset": DATASET,
        "year": year,
        "resource_id": SERIE_BDE,
        "resource_name": resource_name,
        "url": url,
        "format": path.suffix.lstrip("."),
        "size_bytes": path.stat().st_size,
        "last_modified": "",
        "sha256": digest,
        "downloaded_at": utc_now(),
        "license": LICENSE,
        "local_path": str(path),
        "notes": notas,
    })
    print(f"  registrado sha256={digest[:12]}…")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", choices=["bde-export", "bde", "mindicador"], default="bde-export")
    p.add_argument("--years", nargs="+", default=["2023", "2024"],
                   help="solo para --source bde|mindicador (bde-export trae la serie completa)")
    args = p.parse_args(argv)

    ensure_dirs()
    user, password = os.environ.get("BCCH_USER"), os.environ.get("BCCH_PASS")

    if args.source == "bde-export":
        contenido = descargar_bde_export()
        hoy = date.today().isoformat()
        dest = RAW / SOURCE / DATASET / "serie_completa"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"dolar_observado_bde_{hoy}.xlsx"
        path.write_bytes(contenido)
        print(f"[bde-export] {len(contenido):,} bytes -> {path.name}")
        _registrar(
            path, date.today().year,
            PAGINA_BDE,
            "Exportación Excel del visor de series del BCCh (serie completa desde 1982-08-09)",
            "Dólar observado diario (serie completa)",
        )
        return 0

    if args.source == "bde" and not (user and password):
        print("ERROR: --source bde requiere BCCH_USER y BCCH_PASS", file=sys.stderr)
        return 2

    for year in (int(y) for y in args.years):
        if args.source == "bde":
            payload = fetch_bde(year, user, password)
            if payload.get("Codigo") not in (0, "0"):
                print(f"[{year}] BDE error: {payload.get('Descripcion')}", file=sys.stderr)
                return 3
            url, notas = f"{API_BDE}?timeseries={SERIE_BDE}", f"Serie oficial BDE {SERIE_BDE}"
        else:
            payload = fetch_mindicador(year)
            url = f"{API_MINDICADOR}/{year}"
            notas = "Espejo mindicador.cl del dólar observado BCCh"

        dest = RAW / SOURCE / DATASET / str(year)
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"dolar_observado_{args.source}_{year}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{year}] {args.source} -> {path.name}")
        _registrar(path, year, url, notas, f"Dólar observado diario {year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
