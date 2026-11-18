"""Resumen del BNE: consumo de energía por rama industrial, en TJ.

Genera `reports/bne_industria_ramas.csv` con el consumo final de cada categoría
sectorial de la CNE bajo "Sector Industrial y Minero", separando minería de
manufactura, y una tabla de control en Tcal.

Uso:
    python src/audit/bne_resumen.py
"""
from __future__ import annotations

import sys

import polars as pl

from common.paths import PROCESSED, REPORTS

RAMAS_MINERIA = ["Cobre", "Salitre", "Hierro", "Minas Varias"]

# Divisiones 10–33 de CIIU Rev.4. Ojo: "Industrias Varias" es la categoría
# residual de la CNE e incluye también divisiones 1 y 2 (agro/silvicultura).
RAMAS_MANUFACTURA = [
    "Papel y Celulosa",
    "Siderurgia",
    "Petroquímica",
    "Cemento",
    "Azúcar",
    "Industria Láctea",
    "Industrias Varias",
]

# Están bajo "Sector Industrial y Minero" del BNE pero no son manufactura:
# pesca (div. 03), agro/silvicultura (div. 1-2) y construcción (div. 41-43).
RAMAS_OTROS = ["Pesca", "Agroindustria", "Construcción"]


def main() -> int:
    df = pl.read_parquet(PROCESSED / "cne" / "bne" / "bne_balance.parquet")

    ind = (
        df.filter((pl.col("seccion") == "DEMANDA DE ENERGÍA") & pl.col("es_total"))
        .filter(pl.col("item").is_in(RAMAS_MINERIA + RAMAS_MANUFACTURA + RAMAS_OTROS))
        .group_by(["anio", "item"])
        .agg(pl.col("tj").sum().alias("tj"))
    )

    out = (
        ind.with_columns(
            pl.when(pl.col("item").is_in(RAMAS_MINERIA))
            .then(pl.lit("mineria"))
            .when(pl.col("item").is_in(RAMAS_MANUFACTURA))
            .then(pl.lit("manufactura"))
            .otherwise(pl.lit("otros_no_manufactura"))
            .alias("grupo")
        )
        .sort(["anio", "grupo", "tj"], descending=[False, False, True])
    )

    totals = out.group_by(["anio", "grupo"]).agg(pl.col("tj").sum().alias("tj_total"))
    out = out.join(totals, on=["anio", "grupo"]).with_columns(
        (pl.col("tj") / pl.col("tj_total")).alias("participacion")
    )

    REPORTS.mkdir(parents=True, exist_ok=True)
    out.write_csv(REPORTS / "bne_industria_ramas.csv")
    print(out.select("anio", "grupo", "item", "tj", "participacion").to_pandas().to_string(index=False))
    print()
    print(totals.sort(["anio", "grupo"]).to_pandas().to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
