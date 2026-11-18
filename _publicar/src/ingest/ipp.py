"""Descarga el IPP de Industria Manufacturera del INE (cuadros estadísticos).

El INE no publica una URL estable por archivo: los cuadros viven detrás de un
navegador de carpetas. Este módulo replica ese recorrido:

1. `GET` a la página del IPP y rescate del `data-folder` de "CUADROS ESTADÍSTICOS".
2. `POST /hijosCarpeta/` para listar subcarpetas y elegir la base 2019 y la 2014.
3. `POST /getArchivos/` para listar los archivos de cada carpeta.
4. Descarga del CSV "Industria Manufacturera" de cada base.

La base 2019=100 solo se publica desde 2023-09; la 2023 se reconstruye empalmando
con la base 2014=100 (ver `src/normalize/ipp.py`).

Uso:
    python src/ingest/ipp.py
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import requests

from common.manifest import find, read_manifest, sha256_file, upsert, utc_now
from common.paths import RAW, ensure_dirs

SOURCE = "ine"
PAGINA = ("https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/"
          "indice-de-precios-de-productor")
LICENSE = "Datos abiertos INE (citando fuente)"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) interaction-industrial/0.1"}

# carpetas de cuadros estadísticos que interesan: (etiqueta, base del índice)
BASES = {"Base anual 2019=100": "2019", "Base anual 2014=100": "2014"}


def _post(session: requests.Session, ruta: str, id_folder: str) -> dict:
    r = session.post(f"{PAGINA}/{ruta}", data={"idFolder": id_folder}, timeout=90)
    r.raise_for_status()
    return r.json()


def carpeta_cuadros(session: requests.Session, html: str) -> str:
    """`data-folder` de la tarjeta 'CUADROS ESTADÍSTICOS' de la página del IPP."""
    for m in re.finditer(r'data-folder="([0-9a-f-]{36})"', html):
        bloque = html[m.end():m.end() + 300]
        if re.search(r"CUADROS\s+ESTAD", bloque, re.I):
            return m.group(1)
    raise RuntimeError("no se encontró la carpeta 'CUADROS ESTADÍSTICOS' en la página del IPP")


def main() -> int:
    ensure_dirs()
    s = requests.Session()
    s.headers.update(UA)

    r = s.get(PAGINA, timeout=90)
    r.raise_for_status()
    raiz = carpeta_cuadros(s, r.text)

    subcarpetas = {c["Titulo"].strip(): c["Id"] for c in _post(s, "hijosCarpeta/", raiz)["folder"]}
    hoy = date.today().isoformat()

    for titulo, base in BASES.items():
        if titulo not in subcarpetas:
            print(f"  AVISO: no está la carpeta '{titulo}'")
            continue
        docs = _post(s, "getArchivos/", subcarpetas[titulo])["documento"]
        cand = [d for d in docs
                if "manufactur" in d["Titulo"].lower() and d["Tipo"].lower() == ".csv"]
        if not cand:
            print(f"  AVISO: sin CSV de manufactura en '{titulo}'")
            continue
        doc = cand[0]
        contenido = s.get(doc["Url"], timeout=240).content
        dest = RAW / SOURCE / "ipp" / f"base-{base}"
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"industria_manufacturera_{hoy}.csv"
        path.write_bytes(contenido)

        digest = sha256_file(path)
        prev = find(read_manifest(), SOURCE, f"ipp_manufactura_{base}", int(base))
        if prev and prev.get("sha256") == digest:
            print(f"  base {base}: sin cambios (sha256={digest[:12]}…)")
            continue
        upsert({
            "source": SOURCE,
            "dataset": f"ipp_manufactura_{base}",
            "year": int(base),
            "resource_id": doc["Titulo"],
            "resource_name": f"IPP Industria Manufacturera, base anual {base}=100",
            "url": doc["Url"],
            "format": "csv",
            "size_bytes": path.stat().st_size,
            "last_modified": "",
            "sha256": digest,
            "downloaded_at": utc_now(),
            "license": LICENSE,
            "local_path": str(path),
            "notes": f"Cuadro estadístico INE, carpeta '{titulo}', {doc['Peso']} bytes declarados",
        })
        print(f"  base {base}: {len(contenido):,} b -> {path.name} sha256={digest[:12]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
