"""Normaliza los XLSX crudos del RETC a Parquet, sin alterar la capa raw.

Decisiones:
- Se lee todo como texto y luego se castea explícitamente, para que la
  inferencia de tipos no dependa del año ni del orden de las filas.
- Columnas de código se mantienen como texto (RUT, CIIU, ccf8, código
  territorial): son identificadores, no números.
- Se agregan columnas *_norm (mayúsculas, sin tildes) para agrupar sin
  destruir el valor original.

Uso:
    python src/normalize/retc.py --years 2023 2024 2025
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

from common.manifest import find, read_manifest
from common.paths import PROCESSED, RAW, REPORTS, ensure_dirs
from normalize.text import norm_key

SOURCE = "retc"
DATASET = "fuente_puntual"
SHEET = "Data"

RENAME = {"año": "anio"}

SCHEMA: dict[str, pl.DataType] = {
    "anio": pl.Int32(),
    "id_vu": pl.Int64(),
    "razon_social": pl.String(),
    "rut_razon_social": pl.String(),
    "nombre_establecimiento": pl.String(),
    "rubro": pl.String(),
    "rubro_id": pl.Int32(),
    "ciiu4": pl.String(),
    "ciiu4_id": pl.String(),
    "ciiu6": pl.String(),
    "ciiu6_id": pl.String(),
    "region": pl.String(),
    "provincia": pl.String(),
    "comuna": pl.String(),
    "codigo_unico_territorial": pl.String(),
    "latitud": pl.Float64(),
    "longitud": pl.Float64(),
    "declaracion_id": pl.Int64(),
    "codigo_fuente": pl.String(),
    "source_id": pl.Int64(),
    "id_fuente_emisora_general": pl.Int64(),
    "tipo_fuente": pl.String(),
    "combustible_primario": pl.String(),
    "ccf8_primario": pl.String(),
    "combustible_secundario": pl.String(),
    "ccf8_secundario": pl.String(),
    "ccf8_procesos": pl.String(),
    "contaminante_id": pl.Int32(),
    "contaminante": pl.String(),
    "emision_combustible_primario": pl.Float64(),
    "emision_combustible_secundario": pl.Float64(),
    "emision_procesos": pl.Float64(),
    "emision_total": pl.Float64(),
    "emision_retc": pl.Float64(),
    "origen_data": pl.String(),
}

NORM_COLS = ["rubro", "region", "tipo_fuente", "contaminante", "combustible_primario", "combustible_secundario"]


def source_file(year: int) -> Path:
    return RAW / SOURCE / DATASET / str(year) / "original.xlsx"


def load_year(year: int, manifest: list[dict]) -> tuple[pl.DataFrame, dict]:
    path = source_file(year)
    if not path.exists():
        raise FileNotFoundError(path)

    raw = pl.read_excel(path, sheet_name=SHEET, infer_schema_length=0)
    raw = raw.rename({k: v for k, v in RENAME.items() if k in raw.columns})

    casts, notes = [], []
    for col, dtype in SCHEMA.items():
        if col not in raw.columns:
            notes.append(f"columna ausente: {col}")
            continue
        if dtype == pl.String():
            casts.append(pl.col(col).cast(pl.String, strict=False))
            continue
        # intento estricto primero, para detectar valores no numéricos
        try:
            raw.select(pl.col(col).cast(dtype, strict=True))
            casts.append(pl.col(col).cast(dtype))
        except Exception:
            before = raw.select(pl.col(col).is_not_null().sum()).item()
            casted = pl.col(col).cast(dtype, strict=False)
            after = raw.select(casted.is_not_null().sum()).item()
            notes.append(f"cast no estricto en {col}: {before - after} valores a null")
            casts.append(casted)

    df = raw.with_columns(casts)

    extra = [c for c in df.columns if c not in SCHEMA]
    if extra:
        notes.append(f"columnas extra conservadas como texto: {extra}")

    entry = find(manifest, SOURCE, DATASET, year) or {}
    df = df.with_columns(
        pl.lit(SOURCE).alias("source"),
        pl.lit(DATASET).alias("dataset"),
        pl.lit(str(path.name)).alias("source_file"),
        pl.lit(str(entry.get("resource_id", ""))).alias("resource_id"),
        pl.lit(str(entry.get("sha256", ""))).alias("source_sha256"),
    )

    df = df.with_columns([norm_key(c).alias(f"{c}_norm") for c in NORM_COLS if c in df.columns])
    df = df.with_columns(
        pl.col("tipo_fuente_norm").str.contains("GRUPO ELECTROGENO").fill_null(False).alias("es_grupo_electrogeno")
    )

    # orden estable: columnas del esquema primero, luego extra
    ordered = [c for c in SCHEMA if c in df.columns] + [c for c in df.columns if c not in SCHEMA]
    info = {"year": year, "rows": df.height, "cols": df.width, "notes": notes, "file": str(path)}
    return df.select(ordered), info


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--years", nargs="+", required=True)
    args = p.parse_args(argv)

    ensure_dirs()
    manifest = read_manifest()
    log = []

    for year in (int(y) for y in args.years):
        print(f"[{year}] normalizando ...")
        df, info = load_year(year, manifest)
        out = PROCESSED / SOURCE / "emisiones_fp" / f"year={year}"
        out.mkdir(parents=True, exist_ok=True)
        df.write_parquet(out / "part-0.parquet", compression="zstd", statistics=True)
        size_mb = (out / "part-0.parquet").stat().st_size / 1e6
        print(f"[{year}] ok {df.height:,} filas x {df.width} cols -> {size_mb:.1f} MB")
        for n in info["notes"]:
            print(f"       nota: {n}")
        log.append(info)

    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "normalizacion_retc.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
