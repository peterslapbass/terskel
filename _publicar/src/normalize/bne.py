"""Normaliza el Balance Nacional de Energía (BNE) de la CNE a Parquet largo.

Qué hace:
- Lee la hoja "Balance de energía" de cada XLSX anual (la que está expresada
  en Teracalorías, según la propia hoja: "Teracalorías ... Tcal").
- Convierte la matriz (filas = flujos/sectores, columnas = energéticos) a
  formato largo: una fila por (año, sección, ítem, energético).
- Agrega la conversión a TJ (1 Tcal = 4.1868 TJ) sin reemplazar el valor
  original.
- Extrae la tabla de equivalencias "BNE-CIIU 4", que es el puente entre las
  categorías sectoriales de la CNE y CIIU Rev.4 (clase/grupo/división).

Por qué en Tcal: el BNE no publica TJ. La hoja "Balance Energético
(u.físicas)" está en unidades físicas (Mil m3, Mil ton) y se usa como
control, no como fuente de energía.

Uso:
    python src/normalize/bne.py --years 2023 2024
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

from common.manifest import find, read_manifest
from common.paths import PROCESSED, REPORTS, ROOT, ensure_dirs
from normalize.text import norm_key

SOURCE = "cne"
DATASET = "bne"
SHEET = "Balance de energía"
SHEET_MAP = "BNE-CIIU 4"

TCAL_A_TJ = 4.1868

# fila de encabezado de grupos (ENERGÉTICOS PRIMARIOS, DERIVADOS DE PETRÓLEO...)
ROW_GROUP = 7
# fila con el nombre de cada energético
ROW_FUEL = 8
# primera fila de datos y última fila de datos (las siguientes son notas al pie)
ROW_FIRST = 9
ROW_LAST = 61
COL_SECTION = 2  # B
COL_ITEM = 3  # C
COL_FUEL_FIRST = 4  # D
COL_TOTAL = 33  # AG

# La hoja de equivalencias cambia de rótulo entre ediciones del BNE
# ("SIDERÚRGIA"/"SIDERÚRGICA", "INDUSTRIA LÁCTEA"/"INDUSTRIAS LACTEA").
# Este alias fija el nombre del ítem tal como aparece en la hoja de balance.
ALIAS_ITEM = {
    "COBRE": "Cobre",
    "SALITRE": "Salitre",
    "HIERRO": "Hierro",
    "MINAS VARIAS": "Minas Varias",
    "PAPEL Y CELULOSA": "Papel y Celulosa",
    "SIDERURGIA": "Siderurgia",
    "SIDERURGICA": "Siderurgia",
    "CEMENTO": "Cemento",
    "AZUCAR": "Azúcar",
    "PESCA": "Pesca",
    "AGROINDUSTRIA": "Agroindustria",
    "CONSTRUCCION": "Construcción",
    "PETROQUIMICA": "Petroquímica",
    "INDUSTRIA LACTEA": "Industria Láctea",
    "INDUSTRIAS LACTEA": "Industria Láctea",
    "INDUSTRIAS VARIAS": "Industrias Varias",
    "SANITARIAS": "Sanitarias",
    "PUBLICO": "Público",
    "TRANSPORTE TERRESTRE": "Terrestre",
    "TRANSPORTE FERROVIARIO": "Ferroviario",
    "TRANSPORTE MARITIMO": "Marítimo",
    "TRANSPORTE AEREO": "Aéreo",
    "TRANSPORTE POR DUCTO": "Transporte por Ducto",
}


def _txt(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _num(v) -> float | None:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def source_file(year: int, manifest: list[dict]) -> Path:
    entry = find(manifest, SOURCE, DATASET, year)
    if entry and entry.get("local_path"):
        p = Path(entry["local_path"])
        if not p.is_absolute():
            p = ROOT / p
        return p
    return PROCESSED.parent / "raw" / SOURCE / DATASET / str(year) / f"bne_{year}.xlsx"


def read_sheet(path: Path):
    import openpyxl

    wb = openpyxl.load_workbook(path, data_only=True, read_only=False)
    return wb


def parse_balance(wb, year: int) -> tuple[pl.DataFrame, dict]:
    ws = wb[SHEET]

    fuels: list[tuple[int, str, str]] = []
    group = None
    for c in range(COL_FUEL_FIRST, COL_TOTAL):
        g = _txt(ws.cell(ROW_GROUP, c).value)
        if g:
            group = g
        name = _txt(ws.cell(ROW_FUEL, c).value)
        if name:
            fuels.append((c, group or "", name))
        elif g:
            # grupos de un solo energético (Electricidad, Gas Corriente, Metanol):
            # el encabezado de grupo ES el nombre del energético
            fuels.append((c, group or "", g))

    rows = []
    section = None
    for r in range(ROW_FIRST, ROW_LAST + 1):
        s = _txt(ws.cell(r, COL_SECTION).value)
        if s:
            section = s
        item = _txt(ws.cell(r, COL_ITEM).value)
        if not item or section is None:
            continue
        for c, grupo, name in fuels:
            tcal = _num(ws.cell(r, c).value)
            if tcal is None:
                continue
            rows.append(
                {
                    "anio": year,
                    "seccion": section,
                    "item": item,
                    "grupo_energetico": grupo,
                    "energetico": name,
                    "tcal": tcal,
                    "tj": tcal * TCAL_A_TJ,
                    "es_total": False,
                }
            )
        tot = _num(ws.cell(r, COL_TOTAL).value)
        if tot is not None:
            rows.append(
                {
                    "anio": year,
                    "seccion": section,
                    "item": item,
                    "grupo_energetico": "TOTAL",
                    "energetico": "TOTAL",
                    "tcal": tot,
                    "tj": tot * TCAL_A_TJ,
                    "es_total": True,
                }
            )

    df = pl.DataFrame(rows, schema={
        "anio": pl.Int32,
        "seccion": pl.String,
        "item": pl.String,
        "grupo_energetico": pl.String,
        "energetico": pl.String,
        "tcal": pl.Float64,
        "tj": pl.Float64,
        "es_total": pl.Boolean,
    })

    # validaciones aritméticas: TOTAL de la hoja vs suma de energéticos
    checks = []
    por_item = (
        df.filter(~pl.col("es_total"))
        .group_by("seccion", "item")
        .agg(pl.col("tcal").sum().alias("suma_fuentes"))
    )
    totales = df.filter(pl.col("es_total")).select("seccion", "item", pl.col("tcal").alias("total_hoja"))
    cmp = por_item.join(totales, on=["seccion", "item"], how="inner").with_columns(
        (pl.col("total_hoja") - pl.col("suma_fuentes")).alias("dif")
    )
    for row in cmp.iter_rows(named=True):
        denom = abs(row["total_hoja"]) or 1.0
        rel = abs(row["dif"]) / denom
        if rel > 1e-6:
            checks.append(
                {
                    "anio": year,
                    "tipo": "total_vs_suma_fuentes",
                    "item": row["item"],
                    "total_hoja": row["total_hoja"],
                    "suma_fuentes": row["suma_fuentes"],
                    "dif_rel": round(rel, 9),
                }
            )

    # Sector Industrial y Minero debe ser la suma de sus ramas
    ramas = [
        "Cobre", "Salitre", "Hierro", "Papel y Celulosa", "Siderurgia",
        "Petroquímica", "Cemento", "Azúcar", "Pesca", "Agroindustria",
        "Construcción", "Industria Láctea", "Industrias Varias", "Minas Varias",
    ]
    ind = df.filter(
        (pl.col("seccion") == "DEMANDA DE ENERGÍA")
        & pl.col("item").is_in(["Sector Industrial y Minero"] + ramas)
        & pl.col("es_total")
    )
    tot_ind = ind.filter(pl.col("item") == "Sector Industrial y Minero")["tcal"].sum()
    sum_ramas = ind.filter(pl.col("item") != "Sector Industrial y Minero")["tcal"].sum()
    checks.append(
        {
            "anio": year,
            "tipo": "industria_total_vs_ramas",
            "total_hoja": float(tot_ind),
            "suma_ramas": float(sum_ramas),
            "dif_rel": round(abs(tot_ind - sum_ramas) / (abs(tot_ind) or 1.0), 9),
        }
    )

    info = {
        "anio": year,
        "filas": df.height,
        "energeticos": len(fuels),
        "items": df.select(pl.struct("seccion", "item")).n_unique(),
        "consumo_final_total_tcal": float(
            df.filter((pl.col("item") == "Consumo Final") & pl.col("es_total"))["tcal"].sum()
        ),
        "industria_total_tcal": float(tot_ind),
        "checks": checks,
    }
    return df, info


def parse_ciiu_map(wb, year: int) -> pl.DataFrame:
    ws = wb[SHEET_MAP]
    rows = []
    for r in range(8, ws.max_row + 1):
        cat = _txt(ws.cell(r, 2).value)
        ref = _txt(ws.cell(r, 3).value)
        glosa = _txt(ws.cell(r, 4).value)
        if cat and ref:
            rows.append({"categoria_bne": cat, "referencia_ciiu4": ref, "glosa": glosa or ""})
    df = pl.DataFrame(rows)
    df = df.with_columns(
        norm_key("categoria_bne").alias("categoria_norm"),
        pl.lit(year).alias("anio"),
    ).with_columns(
        pl.col("categoria_norm")
        .replace_strict(ALIAS_ITEM, default=None, return_dtype=pl.String)
        .alias("item_bne")
    )
    return df


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--years", nargs="+", required=True)
    args = p.parse_args(argv)

    ensure_dirs()
    manifest = read_manifest()
    log = []
    maps = []

    for year in (int(y) for y in args.years):
        path = source_file(year, manifest)
        if not path.exists():
            print(f"[{year}] falta el archivo: {path}")
            return 1
        wb = read_sheet(path)
        df, info = parse_balance(wb, year)
        out = PROCESSED / SOURCE / "bne" / f"year={year}"
        out.mkdir(parents=True, exist_ok=True)
        df.write_parquet(out / "part-0.parquet", compression="zstd", statistics=True)
        maps.append(parse_ciiu_map(wb, year))
        wb.close()
        print(f"[{year}] ok {df.height:,} filas | energeticos={info['energeticos']} "
              f"| industria={info['industria_total_tcal']:,.1f} Tcal")
        log.append(info)

    combined = pl.concat([pl.read_parquet(PROCESSED / SOURCE / "bne" / f"year={y}" / "part-0.parquet")
                          for y in args.years], how="vertical_relaxed")
    combined.write_parquet(PROCESSED / SOURCE / "bne" / "bne_balance.parquet", compression="zstd")

    m = (
        pl.concat(maps)
        .with_columns(pl.coalesce([pl.col("item_bne"), pl.col("categoria_norm")]).alias("_k"))
        .unique(subset=["_k"], keep="first")
        .drop("_k")
        .sort("categoria_norm")
    )
    m.write_parquet(PROCESSED / SOURCE / "bne" / "ciiu4_map.parquet", compression="zstd")

    (REPORTS / "normalizacion_bne.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
