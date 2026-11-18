"""Ajuste por anomalías de edición del RETC.

El cribado (`src/audit/retc_anomalias.py`) marca planta-año incompatibles con la
propia serie de la planta. Aquí se traduce en un factor que aplican los agregados.

Regla: **los excesos se capan al valor de referencia** —la mediana de las otras
dos ediciones—, que es un valor que la misma planta declaró. Los déficits no se
tocan: un consumo que no aparece puede ser una edición aún abierta, y subirlo
sería inventar. El valor ajustado nunca viene de fuera de la planta.

El factor se aplica a todas las columnas de emisión de la fila, así que el reparto
por origen (fósil/biomasa/proceso) se conserva.
"""
from __future__ import annotations

import polars as pl

from common.paths import PROCESSED

ANOMALIAS = PROCESSED / "retc" / "anomalias.parquet"

COLUMNAS_EMISION = ("emision_retc", "emision_total", "co2_fosil", "co2_biomasa",
                    "co2_proceso", "co2_otro", "co2_sin_clase")


def factores() -> pl.DataFrame:
    """Factor de ajuste por (id_vu, anio). Vacío si no hay cribado."""
    if not ANOMALIAS.exists():
        return pl.DataFrame(schema={"id_vu": pl.Int64, "anio": pl.Int16,
                                    "factor_ajuste": pl.Float64})
    return (pl.read_parquet(ANOMALIAS)
            .filter(pl.col("direccion") == "exceso")
            .select("id_vu", "anio",
                    factor_ajuste=(pl.col("mediana_otras") / pl.col("co2")).clip(0.0, 1.0))
            .unique(subset=["id_vu", "anio"]))


def aplicar(df: pl.DataFrame) -> pl.DataFrame:
    """Agrega `factor_ajuste`, `ajustada` y las emisiones ajustadas.

    Requiere las columnas `id_vu` y `anio`. Devuelve el mismo grano: el factor es
    por planta-año y se reparte proporcionalmente entre sus fuentes.
    """
    salida = (df.join(factores(), on=["id_vu", "anio"], how="left")
              .with_columns(factor_ajuste=pl.col("factor_ajuste").fill_null(1.0))
              .with_columns(ajustada=pl.col("factor_ajuste") < 1.0))
    if "emision_retc" in salida.columns:
        salida = salida.with_columns(
            emision_retc_declarada=pl.col("emision_retc"))
    presentes = [c for c in COLUMNAS_EMISION if c in salida.columns]
    return salida.with_columns([(pl.col(c) * pl.col("factor_ajuste")).alias(c)
                                for c in presentes])
