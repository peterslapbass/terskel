"""Control de integración: energía (BNE) vs actividad (ENIA) por rama.

No es un indicador publicable: verifica que las tres fuentes (RETC, BNE, ENIA)
se pueden unir por CIIU y que los órdenes de magnitud son coherentes. Sirve para
detectar errores de mapeo antes de construir indicadores.

Salvedades:
- El BNE es nacional y usa categorías fijas; la ENIA es por establecimiento y
  cubre solo 10+ trabajadores.
- El VBP de la ENIA está en miles de la moneda declarada: los que informan en
  dólares se convierten con `--fx` (provisional; el definitivo es el tipo de
  cambio nominal promedio anual del BCCh).
- La energía del BNE incluye biomasa y licor negro.
- No hay deflactor: los montos son nominales.

Uso:
    python src/audit/integracion_rama.py --year 2024 --fx 950
"""
from __future__ import annotations

import argparse
import sys

import polars as pl

from common.paths import PROCESSED, REPORTS

# Qué tan confiable es la equivalencia BNE <-> CIIU de cada rama.
CALIDAD = {
    "Papel y Celulosa": "directa (división 17)",
    "Cemento": "directa (clase 2394)",
    "Siderurgia": "directa (grupo 241)",
    "Azúcar": "directa (clase 1072)",
    "Industria Láctea": "directa (clase 1050)",
    "Petroquímica": "revisar: el BNE declara solo ~200 TJ para la división 20",
    "Industrias Varias": "residual (divisiones 1, 2, 10-16, 18, 21-32)",
}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--fx", type=float, default=None,
                   help="CLP por USD; por defecto usa el promedio anual del BCCh")
    args = p.parse_args(argv)
    y = args.year

    fx_path = PROCESSED / "bcch" / "fx_anual.parquet"
    fx_fuente = "BCCh (promedio anual del dólar observado)"
    if args.fx is None:
        if not fx_path.exists():
            print("ERROR: falta el tipo de cambio. Ejecutar:\n"
                  "  python src/ingest/fx.py\n  python src/normalize/fx.py", file=sys.stderr)
            return 2
        tabla = pl.read_parquet(fx_path).filter(pl.col("anio") == y)
        if tabla.height == 0:
            print(f"ERROR: no hay tipo de cambio para {y}", file=sys.stderr)
            return 2
        args.fx = float(tabla["fx_promedio"][0])
    else:
        fx_fuente = "valor impuesto por --fx (no usar para publicar)"

    enia = pl.read_parquet(PROCESSED / "enia" / "base" / "enia_base.parquet").filter(pl.col("anio") == y)
    mapa = pl.read_parquet(PROCESSED / "cne" / "bne" / "ciiu4_rama.parquet").select("codigo", "rama_bne")

    enia = enia.join(mapa, left_on="ciiu4", right_on="codigo", how="left").with_columns(
        pl.when(pl.col("moneda") == "USD").then(pl.col("vbp") * args.fx).otherwise(pl.col("vbp"))
        .alias("vbp_clp"),
        pl.when(pl.col("moneda") == "USD").then(pl.col("valor_agregado") * args.fx).otherwise(pl.col("valor_agregado"))
        .alias("va_clp"),
    )

    total = float(enia["vbp_clp"].sum())
    sin_rama = enia.filter(pl.col("rama_bne").is_null())
    print(f"ENIA {y}: {enia.height:,} establecimientos | VBP equivalente {total/1e9:,.1f} billones CLP")
    print(f"  tipo de cambio: {args.fx:,.2f} CLP/USD — {fx_fuente}")
    print(f"  sin rama BNE: {sin_rama.height} establecimientos, "
          f"{float(sin_rama['vbp_clp'].sum())/total:.1%} del VBP")
    print(f"  informan en USD: {enia.filter(pl.col('moneda') == 'USD').height} establecimientos, "
          f"{float(enia.filter(pl.col('moneda') == 'USD')['vbp_clp'].sum())/total:.1%} del VBP equivalente\n")

    act = (
        enia.filter(pl.col("rama_bne").is_not_null())
        .group_by("rama_bne")
        .agg(
            pl.len().alias("establecimientos"),
            (pl.col("moneda") == "USD").mean().alias("share_usd"),
            pl.col("vbp_clp").sum().alias("vbp_clp_miles"),
            pl.col("va_clp").sum().alias("va_clp_miles"),
        )
    )

    bne = (
        pl.read_parquet(PROCESSED / "cne" / "bne" / "bne_balance.parquet")
        .filter((pl.col("anio") == y) & (pl.col("seccion") == "DEMANDA DE ENERGÍA") & pl.col("es_total"))
        .select(pl.col("item").alias("rama_bne"), pl.col("tj").alias("energia_tj"))
    )

    out = (
        act.join(bne, on="rama_bne", how="left")
        .with_columns(
            (pl.col("energia_tj") / (pl.col("vbp_clp_miles") / 1e9)).alias("tj_por_billon_vbp"),
            (pl.col("energia_tj") / (pl.col("va_clp_miles") / 1e9)).alias("tj_por_billon_va"),
            pl.col("rama_bne").replace_strict(CALIDAD, default="", return_dtype=pl.String).alias("calidad_mapeo"),
            pl.lit(args.fx).alias("fx_clp_usd"),
            pl.lit(fx_fuente).alias("fx_fuente"),
        )
        .sort("energia_tj", descending=True)
    )

    REPORTS.mkdir(parents=True, exist_ok=True)
    out.write_csv(REPORTS / f"integracion_rama_{y}.csv")

    view = out.select(
        "rama_bne", "establecimientos",
        (pl.col("share_usd") * 100).round(0).alias("usd_%"),
        (pl.col("vbp_clp_miles") / 1e9).round(1).alias("vbp_billones_clp"),
        (pl.col("va_clp_miles") / 1e9).round(1).alias("va_billones_clp"),
        pl.col("energia_tj").round(0),
        pl.col("tj_por_billon_vbp").round(0),
        pl.col("tj_por_billon_va").round(0),
    )
    print(view.to_pandas().to_string(index=False))
    print(f"\n-> {REPORTS / f'integracion_rama_{y}.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())