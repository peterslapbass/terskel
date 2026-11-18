"""Convierte el dólar observado crudo en serie diaria y resumen anual.

Acepta dos formatos:

- **XLSX de exportación del BCCh** (`DownloadExcel`, layout horizontal): dos filas
  paralelas — fechas y valores — desde 1982-08-09. Se parsea con `zipfile` +
  `ElementTree` porque el XLSX trae ~11.000 columnas y los lectores de hoja de
  cálculo se cuelgan con ese ancho.
- **JSON** de la API BDE (`Series.Obs`) o del espejo mindicador (`serie`).

El promedio anual es **promedio simple de los días publicados**, que es la
convención del propio BCCh: la nota metodológica de la exportación dice que las
series de frecuencia anual "corresponden exclusivamente a promedios simples de
dichos valores diarios".

Salidas:
- `data/processed/bcch/dolar_diario.parquet` — fecha, valor, anio, fuente
- `data/processed/bcch/fx_anual.parquet` — anio, fx_promedio, fx_mediana, fx_min, fx_max, n_dias

Uso:
    python src/normalize/fx.py
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import polars as pl

from common.paths import PROCESSED, RAW

SOURCE = "bcch"
DATASET = "dolar_observado"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _celda(c: ET.Element) -> str:
    if c.get("t") == "inlineStr":
        is_el = c.find(f"{NS}is")
        return "".join(n.text or "" for n in is_el.iter(f"{NS}t")) if is_el is not None else ""
    v = c.find(f"{NS}v")
    return (v.text or "") if v is not None else ""


def parse_xlsx_bcch(path: Path) -> list[tuple[str, float]]:
    """Extrae (fecha, valor) del XLSX horizontal del BCCh."""
    with zipfile.ZipFile(path) as z:
        nombres = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
        hojas = []
        for n in sorted(nombres):
            root = ET.fromstring(z.read(n))
            sd = root.find(f"{NS}sheetData")
            if sd is not None:
                hojas.append(sd.findall(f"{NS}row"))

    for filas in hojas:
        for i, fila in enumerate(filas):
            celdas = [_celda(c) for c in fila.findall(f"{NS}c")]
            if celdas and celdas[0].strip().lower() == "descripción series":
                fechas = celdas[1:]
                if i + 1 >= len(filas):
                    continue
                valores = [_celda(c) for c in filas[i + 1].findall(f"{NS}c")][1:]
                obs = []
                for f, v in zip(fechas, valores):
                    f, v = f[:10], v.replace(",", "").strip()
                    if len(f) == 10 and v:
                        obs.append((f, float(v)))
                if obs:
                    return obs
    raise ValueError(f"no se reconoce el layout del XLSX del BCCh: {path.name}")


def parse_json(path: Path) -> list[tuple[str, float]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    obs: list[tuple[str, float]] = []
    for row in (payload.get("Series") or {}).get("Obs", []) or []:
        f = str(row.get("indexdate", ""))[:10]
        v = str(row.get("value", "")).replace(",", "").strip()
        if f and v:
            obs.append((f, float(v)))
    for row in payload.get("serie", []) or []:
        f = str(row.get("fecha", ""))[:10]
        if f and row.get("valor") is not None:
            obs.append((f, float(row["valor"])))
    return obs


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.parse_args(argv)

    base = RAW / SOURCE / DATASET
    if not base.exists():
        print(f"ERROR: no hay datos en {base}. Ejecutar src/ingest/fx.py primero.", file=sys.stderr)
        return 2

    xlsx = sorted(base.glob("serie_completa/*.xlsx"))
    if xlsx:
        origen, fuente = xlsx[-1], "bde-export"
        obs = parse_xlsx_bcch(origen)
    else:
        jsons = sorted(base.glob("*/*.json"))
        if not jsons:
            print("ERROR: no hay snapshots del dólar observado", file=sys.stderr)
            return 3
        origen = jsons[-1]
        fuente = "bde" if "bde" in origen.name else "mindicador"
        obs = parse_json(origen)

    diario = (
        pl.DataFrame(obs, schema=["fecha", "valor"], orient="row")
        .with_columns(pl.col("fecha").str.to_date(), pl.lit(fuente).alias("fuente"))
        .unique(subset=["fecha"], keep="last")
        .sort("fecha")
        .with_columns(pl.col("fecha").dt.year().alias("anio"))
    )

    anual = (
        diario.group_by("anio")
        .agg(
            pl.col("valor").mean().round(2).alias("fx_promedio"),
            pl.col("valor").median().round(2).alias("fx_mediana"),
            pl.col("valor").min().alias("fx_min"),
            pl.col("valor").max().alias("fx_max"),
            pl.len().alias("n_dias"),
            pl.col("fecha").min().alias("desde"),
            pl.col("fecha").max().alias("hasta"),
            pl.col("fuente").first().alias("fuente"),
            pl.lit("USD").alias("moneda_origen"),
            pl.lit("CLP").alias("moneda_destino"),
            pl.lit("USD/CLP").alias("par"),
        )
        .sort("anio")
    )

    dest = PROCESSED / SOURCE
    dest.mkdir(parents=True, exist_ok=True)
    diario.write_parquet(dest / "dolar_diario.parquet", compression="zstd")
    anual.write_parquet(dest / "fx_anual.parquet", compression="zstd")

    print(f"origen: {origen.name} ({fuente}) · {diario.height:,} días")
    print(anual.tail(5).to_pandas().to_string(index=False))
    print(f"\n-> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
