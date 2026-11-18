"""Energía implícita en el CO₂ del RETC y contraste contra el BNE.

Invierte la ecuación de la guía del RETC para estimar cuánta energía se quemó:

    CO₂ (t) = TJ × EF_carbono(kg C/GJ) × (44/12) / 1000
    TJ      = CO₂ / (EF_carbono × 3,6667)

Los factores vienen de la Tabla 4-3 de la *Guía metodológica para la estimación
de emisiones de fuentes puntuales* (MMA, 2021), registrados en
`data/reference/factores_emision_combustible.csv`.

El resultado se compara con el consumo del BNE para las 7 ramas manufactureras.
No es una validación de ±30%: el RETC solo cubre fuentes sobre umbral y la CNE
asigna la cogeneración a transformación, así que la razón mide **cobertura**, y
las diferencias por combustible son la información.

Salidas:
- `data/processed/retc/energia_implicita.parquet`
- `reports/retc_energia_implicita.md`

Uso:
    python src/normalize/retc_energia_implicita.py [--year 2024]
"""
from __future__ import annotations

import argparse

import polars as pl

from common.paths import PROCESSED, REPORTS, ROOT, ensure_dirs
from common.calidad import aplicar as aplicar_anomalias
from indicators.intensidad import RAMAS, rama_expr

CO2 = PROCESSED / "retc" / "co2_combustible.parquet"
BNE = PROCESSED / "cne" / "bne" / "bne_balance.parquet"
FACTORES = ROOT / "data" / "reference" / "factores_emision_combustible.csv"
OUT = PROCESSED / "retc" / "energia_implicita.parquet"

C_POR_CO2 = 44 / 12  # kg C -> kg CO2


def leer_factores() -> pl.DataFrame:
    f = pl.read_csv(FACTORES, separator=";", encoding="utf-8", infer_schema_length=0)
    return f.with_columns(
        ef_carbono_kg_c_gj=pl.col("ef_carbono_kg_c_gj").cast(pl.Float64, strict=False),
        grupo_bne=pl.col("grupo_bne").replace("", None),
    ).with_columns(
        # EF en kg C/GJ -> t CO2/TJ: 1 TJ = 1000 GJ, y 1 t C = 44/12 t CO2
        tco2_por_tj=pl.col("ef_carbono_kg_c_gj") * 44 / 12,
    )


def bne_ramas(y: int) -> pl.DataFrame:
    return (pl.read_parquet(BNE)
            .filter((pl.col("anio") == y)
                    & (pl.col("seccion") == "DEMANDA DE ENERGÍA")
                    & pl.col("item").is_in(RAMAS)
                    & (pl.col("energetico") != "TOTAL"))
            .group_by(pl.col("energetico").alias("grupo_bne"))
            .agg(pl.col("tj").sum().alias("tj_bne")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2024)
    y = ap.parse_args().year

    ensure_dirs()
    factores = leer_factores()

    retc = (pl.read_parquet(CO2)
            .filter(pl.col("anio") == y)
            .pipe(aplicar_anomalias)
            .with_columns(rama=rama_expr("ciiu4_id"))
            .filter(pl.col("rama").is_not_null())
            # numerador según el origen: fósil usa co2_fosil, biomasa co2_biomasa
            .with_columns(co2=pl.when(pl.col("clase_primario") == "biomasa")
                              .then(pl.col("co2_biomasa"))
                              .otherwise(pl.col("co2_fosil"))))

    # variante sin la planta que domina el CO₂ fósil de su rama (>50%): aísla el
    # efecto de un dato individual sobre la comparación con el BNE
    dominantes = (retc.group_by(["rama", "id_vu"])
                  .agg(pl.col("co2_fosil").sum().alias("t"))
                  .with_columns(share=pl.col("t") / pl.col("t").sum().over("rama"))
                  .filter(pl.col("share") > 0.5)
                  .select("rama", "id_vu"))
    limpio = retc.join(dominantes, on=["rama", "id_vu"], how="anti")

    def por_combustible(df: pl.DataFrame) -> pl.DataFrame:
        return (df.group_by("combustible_primario_norm")
                .agg(pl.col("co2").sum().alias("co2"))
                .join(factores, left_on="combustible_primario_norm",
                      right_on="combustible", how="left")
                .with_columns(tj_implicito=pl.when(pl.col("tco2_por_tj").is_not_null()
                                                   & (pl.col("tco2_por_tj") > 0))
                              .then(pl.col("co2") / pl.col("tco2_por_tj"))
                              .otherwise(None)))

    detalle = por_combustible(retc)
    detalle_limpio = por_combustible(limpio)

    por_grupo = (detalle.filter(pl.col("grupo_bne").is_not_null())
                 .group_by("grupo_bne")
                 .agg(pl.col("co2").sum(), pl.col("tj_implicito").sum())
                 .join(bne_ramas(y), on="grupo_bne", how="full", coalesce=True)
                 .join(detalle_limpio.filter(pl.col("grupo_bne").is_not_null())
                       .group_by("grupo_bne")
                       .agg(pl.col("tj_implicito").sum().alias("tj_sin_dominante")),
                       on="grupo_bne", how="left")
                 .with_columns(
                     cobertura=pl.col("tj_implicito") / pl.col("tj_bne"),
                     cobertura_sin=pl.col("tj_sin_dominante") / pl.col("tj_bne"),
                     brecha=pl.col("tj_implicito") - pl.col("tj_bne"))
                 .sort("tj_bne", descending=True))

    sin_factor = (detalle.filter(pl.col("grupo_bne").is_null())
                  .select("combustible_primario_norm", "co2")
                  .sort("co2", descending=True))

    detalle.sort("co2", descending=True).write_parquet(OUT, compression="zstd")
    escribir_informe(y, por_grupo, sin_factor, detalle)
    print(por_grupo.select("grupo_bne", pl.col("tj_implicito").round(0),
                           pl.col("tj_bne").round(0),
                           pl.col("cobertura").round(2)).to_pandas().to_string(index=False))
    print(f"\n-> {OUT}")
    print(f"-> {REPORTS / 'retc_energia_implicita.md'}")
    return 0


def escribir_informe(y: int, g: pl.DataFrame, sin_factor: pl.DataFrame,
                     detalle: pl.DataFrame) -> None:
    tot_i = float(g["tj_implicito"].sum())
    tot_b = float(g["tj_bne"].sum())
    filas = ["| Grupo BNE | TJ implícito RETC | TJ sin planta dominante | TJ BNE 7 ramas | Cobertura | Cobertura sin dominante |",
             "|---|---:|---:|---:|---:|---:|"]
    cierran = []
    no_cubiertos = []
    for r in g.iter_rows(named=True):
        tb = 0.0 if r["tj_bne"] is None else r["tj_bne"]
        if r["tj_implicito"] is None:
            if tb > 0:
                no_cubiertos.append(r["grupo_bne"])
            continue
        ti = r["tj_implicito"]
        ts = 0.0 if r["tj_sin_dominante"] is None else r["tj_sin_dominante"]
        if ti == 0 and tb == 0:
            continue
        c1 = "—" if tb == 0 else f"{ti/tb*100:.0f}%"
        c2 = "—" if tb == 0 else f"{ts/tb*100:.0f}%"
        if tb > 0 and abs(ti / tb - 1) <= 0.30:
            cierran.append(r["grupo_bne"])
        filas.append(f"| {r['grupo_bne']} | {ti:,.0f} | {ts:,.0f} | {tb:,.0f} | {c1} | {c2} |")
    veredicto = (", ".join(cierran) if cierran else "ninguno")
    sin_cobertura = (", ".join(no_cubiertos) if no_cubiertos else "ninguno")

    sf = ["| Combustible | CO₂ (t) |", "|---|---:|"]
    for r in sin_factor.iter_rows(named=True):
        sf.append(f"| {r['combustible_primario_norm']} | {r['co2']:,.0f} |")

    top = (detalle.filter(pl.col("tj_implicito").is_not_null())
           .sort("tj_implicito", descending=True).head(10))
    td = ["| Combustible RETC | tCO₂/TJ | TJ implícito |", "|---|---:|---:|"]
    for r in top.iter_rows(named=True):
        td.append(f"| {r['combustible_primario_norm']} | {r['tco2_por_tj']:.1f} | "
                  f"{r['tj_implicito']:,.0f} |")

    texto = f"""# Energía implícita en el CO₂ del RETC ({y})

Se invierte la ecuación de la guía: `TJ = CO₂ / (EF_carbono × 44/12 / 1000)`, con
los factores de la Tabla 4-3 (MMA 2021). Es una reconstrucción, no una medición:
hereda el error del CO₂ y del factor. El CO₂ de entrada pasa por el cribado de
ediciones (`src/common/calidad.py`): el exceso planta-año se capa antes de invertir.

## Contraste con el BNE (7 ramas manufactureras)

{chr(10).join(filas)}

**Total**: {tot_i:,.0f} TJ implícitos contra {tot_b:,.0f} TJ del BNE
({tot_i/tot_b*100:.0f}% de cobertura).

Cierran dentro de ±30%: **{veredicto}**.

Sin cobertura en el RETC (el BNE los registra, el RETC no los declara como
combustible): {sin_cobertura}.

## Por combustible

{chr(10).join(td)}

## Combustibles sin factor

{chr(10).join(sf) if sin_factor.height else "- ninguno"}

## Cómo leer esto

- La cobertura **no debería ser 100%**: el RETC solo registra fuentes sobre umbral
  y admite dos combustibles por fuente.
- Si un combustible cierra cerca del 100%, las dos fuentes son consistentes y el
  factor es plausible.
- Si está muy por debajo, el registro no ve esa quema (diésel disperso, grupos
  electrógenos).
- Si está muy por encima, la CNE ubica esa energía en otra parte del balance:
  el licor negro se consume en autoproducción y aparece como `Consumo Final` en
  transformación, no en la demanda del sector.

## Límites

- El factor de biomasa de la guía es genérico; el licor negro tiene uno propio
  (~26 kg C/GJ), así que su TJ implícito puede estar sobrestimado.
- El reparto fósil/biomasa del RETC es proporcional a lo declarado.
- Un error de unidad en una planta se propaga entero a su combustible.
"""
    (REPORTS / "retc_energia_implicita.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
