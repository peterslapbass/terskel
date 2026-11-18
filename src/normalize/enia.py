"""Normaliza los microdatos ENIA (CSV del INE) a un Parquet angosto y documentado.

El archivo publicado trae 277 columnas con códigos (`A001`, `K009`...) que no se
explican solos. El mapeo de abajo se reconstruyó con el descriptor del INE
(`descriptor_datos_seguimiento_enia.xlsx`, columna "Variables 2019") y se validó
contra los datos:

- `K009 = K010 + K011` en 100,0% de las filas con tolerancia de ±1 (VBP = CI + VA).
- La mediana de `K007 / K009` es 1,000 (ingresos por venta ≈ VBP).
- La mediana de `K010 / K009` es 0,636 y la de `K011 / K009` es 0,364
  (estructura de costos manufacturera plausible).
- `corr(B001, K009) = 0,976` (ingreso por fabricación propia vs VBP).
- `I068`/`I078`/`I080`/`I104` tienen mediana 1/29/39/42 personas.

Unidades: los montos vienen en **miles** de la moneda declarada en `moneda`
(ISO 4217: `CLP` para el código interno 4, `USD` para el 5, con `moneda_multiplo`
= 1000). No se convierten aquí: mezclar monedas en una suma es un error, y la
conversión exige un tipo de cambio (BCCh) que es una decisión del indicador. El
empleo está en **personas**.

Uso:
    python src/normalize/enia.py --years 2023 2024
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

from common.manifest import find, read_manifest
from common.paths import PROCESSED, REPORTS, ROOT, ensure_dirs

SOURCE = "enia"
DATASET = "base"

# código en la base publicada -> nombre de la columna normalizada
ECON = {
    "K006": "costo_total",
    "K007": "ingresos_venta",
    "K009": "vbp",
    "K010": "consumo_intermedio",
    "K011": "valor_agregado",
    "B001": "ingreso_fabricacion_propia",
}

# gasto en energía y agua (miles de la moneda declarada en `moneda`)
ENERGIA_GASTO = {
    "G005": "gasto_electricidad_comprada",
    "G013": "gasto_agua",
    "G014": "gasto_vapor",
    "G023": "gasto_petroleo_combustible",
    "G026": "gasto_petroleo_diesel",
    "G029": "gasto_bencina",
    "G032": "gasto_parafina",
    "G035": "gasto_gas_licuado",
    "G038": "gasto_gas_natural",
    "G041": "gasto_gnl",
    "G044": "gasto_metanol",
    "G047": "gasto_lena",
    "G050": "gasto_lubricantes",
    "G051": "gasto_otros_combustibles",
}

# A005 es la moneda de la contabilidad (el descriptor la mapea desde "Moneda en
# que lleva su contabilidad"). Los códigos 4 y 5 no están en el anexo del
# descriptor (1=M CLP, 2=M USD, 3=M EUR), **no son ISO 4217** (ahí CLP=152 y
# USD=840) y **no son la tabla CMF** (013=USD, 999=CLP). Son un código interno
# del INE. Se identificaron así:
#   - los establecimientos con A005=5 se concentran en ramas exportadoras
#     (1020 pesca, 1610 aserrío, 2011 química básica, 1701 celulosa);
#   - su remuneración por ocupado (I081/I080) es ~906 veces menor que la del
#     grupo 4, del orden del tipo de cambio (943,58 CLP/USD en 2024): es unidad,
#     no productividad.
# En la salida se publica el código ISO 4217 (alfa-3 y numérico), no el interno.
MONEDA_ISO = {4: "CLP", 5: "USD"}
MONEDA_ISO_NUM = {4: 152, 5: 840}

EMPLEO = {
    "I068": "propietarios_hombres",
    "I069": "propietarios_mujeres",
    "I080": "ocupados_con_contrato",
    "I104": "ocupados_total",
}

REGIONES = {
    1: "Tarapacá", 2: "Antofagasta", 3: "Atacama", 4: "Coquimbo", 5: "Valparaíso",
    6: "O'Higgins", 7: "Maule", 8: "Biobío", 9: "La Araucanía", 10: "Los Lagos",
    11: "Aysén", 12: "Magallanes", 13: "Metropolitana", 14: "Los Ríos",
    15: "Arica y Parinacota", 16: "Ñuble",
}


def source_file(year: int, manifest: list[dict]) -> Path:
    entry = find(manifest, SOURCE, DATASET, year)
    if entry and entry.get("local_path"):
        p = Path(entry["local_path"])
        return p if p.is_absolute() else ROOT / p
    return ROOT / "data" / "raw" / SOURCE / DATASET / str(year) / f"base-enia-{year}.csv"


def load_year(year: int, manifest: list[dict]) -> tuple[pl.DataFrame, dict]:
    path = source_file(year, manifest)
    if not path.exists():
        raise FileNotFoundError(path)

    raw = pl.read_csv(path, separator=";", infer_schema_length=0, null_values=["", " "])

    missing = [c for c in list(ECON) + list(ENERGIA_GASTO) + list(EMPLEO) if c not in raw.columns]
    if missing:
        raise ValueError(f"faltan columnas en {path.name}: {missing}")

    def num(code: str, name: str) -> pl.Expr:
        return pl.col(code).cast(pl.Float64, strict=False).alias(name)

    df = raw.select(
        pl.col("ID").cast(pl.Int64).alias("id"),
        pl.col("ANIO").cast(pl.Int32).alias("anio"),
        pl.col("REGION").cast(pl.Int32).alias("region"),
        pl.col("CIIU4").cast(pl.String).alias("ciiu4"),
        pl.col("CLASIFICACION").cast(pl.String).alias("clasificacion"),
        pl.col("IMPUTACION").cast(pl.Int8).alias("imputado"),
        pl.col("A005").cast(pl.Int8).alias("moneda_codigo"),
        pl.col("TAMANO").cast(pl.Int16).alias("tamano"),
        pl.col("TEED").cast(pl.Int16).alias("teed"),
        *[num(c, n) for c, n in ECON.items()],
        *[num(c, n) for c, n in ENERGIA_GASTO.items()],
        *[num(c, n) for c, n in EMPLEO.items()],
    )

    df = df.with_columns(
        pl.col("region").replace_strict(REGIONES, default=None, return_dtype=pl.String).alias("region_nombre"),
        pl.col("ciiu4").str.len_chars().cast(pl.Int8).alias("ciiu_largo"),
        pl.when(pl.col("ciiu4").str.len_chars() == 4).then(pl.lit("clase"))
        .when(pl.col("ciiu4").str.len_chars() == 3).then(pl.lit("grupo"))
        .when(pl.col("ciiu4").str.len_chars() == 2).then(pl.lit("division"))
        .otherwise(pl.lit("seccion")).alias("ciiu_nivel"),
        pl.when(pl.col("ciiu4").str.len_chars() >= 2)
        .then(pl.col("ciiu4").str.slice(0, 2)).otherwise(None).alias("ciiu_division"),
        pl.col("moneda_codigo").replace_strict(MONEDA_ISO, default=None, return_dtype=pl.String).alias("moneda"),
        pl.col("moneda_codigo").replace_strict(MONEDA_ISO_NUM, default=None, return_dtype=pl.Int16).alias("moneda_iso_num"),
        # los montos vienen en miles: monto_en_moneda = valor * moneda_multiplo
        pl.lit(1000, dtype=pl.Int32).alias("moneda_multiplo"),
    )

    entry = find(manifest, SOURCE, DATASET, year) or {}
    df = df.with_columns(
        pl.lit(SOURCE).alias("source"),
        pl.lit(DATASET).alias("dataset"),
        pl.lit(path.name).alias("source_file"),
        pl.lit(str(entry.get("sha256", ""))).alias("source_sha256"),
    )

    # validaciones
    ident = (pl.col("vbp") - (pl.col("consumo_intermedio") + pl.col("valor_agregado"))).abs() <= 1
    info = {
        "anio": year,
        "filas": df.height,
        "archivo": str(path),
        "ids_unicos": df.select(pl.col("id").n_unique()).item(),
        "regiones": df.select(pl.col("region").n_unique()).item(),
        "ciiu_codigos": df.select(pl.col("ciiu4").n_unique()).item(),
        "ciiu_nivel": df.group_by("ciiu_nivel").len().sort("ciiu_nivel").to_dicts(),
        "imputados": int(df["imputado"].sum()),
        "moneda": df.group_by("moneda").len().sort("moneda").to_dicts(),
        "moneda_codigos": sorted(int(c) for c in df["moneda_codigo"].drop_nulls().unique()),
        "vbp_nulos": int(df["vbp"].null_count()),
        "vbp_cero": int((df["vbp"] == 0).sum()),
        "va_negativo": int((df["valor_agregado"] < 0).sum()),
        "identidad_vbp_ci_va": round(float(df.select(ident.mean()).item()), 5),
        # no se suman: están en monedas distintas
        "vbp_clp_miles": float(df.filter(pl.col("moneda") == "CLP")["vbp"].sum()),
        "vbp_usd_miles": float(df.filter(pl.col("moneda") == "USD")["vbp"].sum()),
    }
    return df, info


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
        desconocidos = [c for c in info["moneda_codigos"] if c not in MONEDA_ISO]
        if desconocidos:
            print(f"[{year}] ADVERTENCIA: códigos de moneda no mapeados {desconocidos} "
                  f"(esperado {sorted(MONEDA_ISO)}); revisar el catálogo del INE")
        out = PROCESSED / SOURCE / DATASET / f"year={year}"
        out.mkdir(parents=True, exist_ok=True)
        df.write_parquet(out / "part-0.parquet", compression="zstd", statistics=True)
        print(f"[{year}] ok {df.height:,} filas x {df.width} cols | "
              f"VBP CLP {info['vbp_clp_miles']/1e9:,.1f} billones | "
              f"VBP USD {info['vbp_usd_miles']/1e6:,.1f} mil millones | "
              f"identidad VBP=CI+VA {info['identidad_vbp_ci_va']:.2%}")
        log.append(info)

    combined = pl.concat(
        [pl.read_parquet(PROCESSED / SOURCE / DATASET / f"year={y}" / "part-0.parquet") for y in args.years],
        how="vertical_relaxed",
    )
    combined.write_parquet(PROCESSED / SOURCE / DATASET / "enia_base.parquet", compression="zstd")

    (REPORTS / "normalizacion_enia.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
