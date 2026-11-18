"""Normaliza el IPP de Industria Manufacturera del INE a Parquet.

Fuente: `src/ingest/ipp.py` (dos CSVs, bases 2019=100 y 2014=100).

El índice base 2019=100 solo se publica desde 2023-09. Para 2023 se empalma con la
base 2014=100 usando el mismo criterio del INE: un factor de enlace por división

    k = I_2019(2023-09) / [ I_2014(2023-08) × (1 + v_2019(2023-09)/100) ]

y luego `I_2019(m) = I_2014(m) × k` para m <= 2023-08. Los meses siguientes se usan
tal como se publican. El factor agregado reproduce el de la serie empalmada del INE
(0,9291 vs 0,9294).

Salidas:
- `data/processed/ine/ipp/ipp_mensual.parquet` (nivel × código × mes, base 2019)
- `data/processed/ine/ipp/ipp_anual.parquet` (promedio anual por división)
- `reports/normalizacion_ipp.json`

Uso:
    python src/normalize/ipp.py
"""
from __future__ import annotations

import io
import json
import re

import polars as pl

from common.paths import PROCESSED, RAW, REPORTS, ensure_dirs

SOURCE = "ine"
DATASET = "ipp"
BASE = 2019
ENLACE = (2023, 8)           # último mes de la base 2014 usado en el empalme
PRIMER_MES_2019 = (2023, 9)  # primer mes publicado en la base 2019

COLS_2014 = ["Año", "Mes", "División", "Grupo", "Clase", "Subclase", "Producto",
             "Glosa", "Ponderación", "Índice", "v1", "v2", "v3", "v4", "v5", "v6"]

COL_INDICE = "Índice"
COL_PONDERACION = "Ponderación"
COL_VAR19 = "Variación Mensual (%)"
COL_VAR14 = "v1"


def num(col: str) -> pl.Expr:
    return (pl.col(col).str.strip_chars().str.replace(",", ".")
            .cast(pl.Float64, strict=False))


def _csv_2019(path) -> pl.DataFrame:
    df = pl.read_csv(path, separator=";", encoding="latin1", infer_schema_length=0,
                     null_values=["", " "], truncate_ragged_lines=True)
    df = df.select([c for c in df.columns if c and not c.startswith("_")])
    return df.rename({c: c.replace("\ufeff", "").strip() for c in df.columns})


def _csv_2014(path) -> pl.DataFrame:
    """La cabecera de esta base trae saltos de línea dentro de campos citados:
    se descarta y se parte desde la primera fila que empieza con un año."""
    lineas = open(path, encoding="latin1").read().splitlines()
    i = next(k for k, l in enumerate(lineas) if re.match(r"^\d{4};", l))
    return pl.read_csv(io.StringIO("\n".join(lineas[i:])), separator=";",
                       has_header=False, new_columns=COLS_2014,
                       infer_schema_length=0, null_values=["", " "],
                       truncate_ragged_lines=True)


def niveles(df: pl.DataFrame, col_var: str) -> pl.DataFrame:
    """Deja solo el total de manufactura y el nivel de división."""
    base = df.select(
        anio=pl.col("Año").str.strip_chars().cast(pl.Int16, strict=False),
        mes=pl.col("Mes").str.strip_chars().cast(pl.Int8, strict=False),
        division=pl.col("División").str.strip_chars(),
        grupo=pl.col("Grupo").str.strip_chars(),
        glosa=pl.col("Glosa").str.strip_chars(),
        indice=num(COL_INDICE),
        var_mensual=num(col_var),
    )
    total = (base.filter(pl.col("division").is_null())
                 .with_columns(pl.lit("total").alias("nivel"),
                               pl.lit("00").alias("codigo")))
    div = (base.filter(pl.col("division").is_not_null())
               .filter(pl.col("grupo").is_null())
               .with_columns(pl.lit("division").alias("nivel"),
                             pl.col("division").alias("codigo")))
    return pl.concat([total, div]).filter(pl.col("anio").is_not_null())


def indices_anuales(mensual: pl.DataFrame) -> pl.DataFrame:
    return (mensual.group_by(["nivel", "codigo", "glosa", "anio"])
            .agg(pl.col("ipp").mean().alias("ipp"),
                 pl.len().alias("n_meses"),
                 pl.col("empalmado").max().alias("empalmado"))
            .with_columns((pl.col("n_meses") == 12).alias("completo"))
            .filter(pl.col("anio") >= BASE)
            .sort(["nivel", "codigo", "anio"]))


def main() -> int:
    ensure_dirs()
    raw = RAW / SOURCE / "ipp"
    f19 = sorted((raw / "base-2019").glob("*.csv"))[-1]
    f14 = sorted((raw / "base-2014").glob("*.csv"))[-1]
    print(f"base 2019: {f19.name}\nbase 2014: {f14.name}")

    n19 = niveles(_csv_2019(f19), COL_VAR19)
    n14 = niveles(_csv_2014(f14), COL_VAR14)

    # factor de enlace por división (el total sirve de referencia y de respaldo)
    ref19 = n19.filter((pl.col("anio") == PRIMER_MES_2019[0])
                       & (pl.col("mes") == PRIMER_MES_2019[1]))
    ref14 = n14.filter((pl.col("anio") == ENLACE[0]) & (pl.col("mes") == ENLACE[1]))
    k = (ref19.select("nivel", "codigo", nivel_2019=pl.col("indice"),
                      var19=pl.col("var_mensual"))
              .join(ref14.select("nivel", "codigo", nivel_2014=pl.col("indice")),
                    on=["nivel", "codigo"], how="inner")
              .with_columns(k=pl.col("nivel_2019")
                            / (pl.col("nivel_2014") * (1 + pl.col("var19") / 100))))
    k_total = k.filter(pl.col("nivel") == "total")["k"][0]
    k_div = k.filter(pl.col("nivel") == "division")

    # meses previos al enlace: base 2014 escalada por k
    previos = (n14.filter((pl.col("anio") < PRIMER_MES_2019[0])
                          | ((pl.col("anio") == PRIMER_MES_2019[0])
                             & (pl.col("mes") <= ENLACE[1])))
                 .join(k_div.select("codigo", "k"), on="codigo", how="left")
                 .with_columns(k=pl.coalesce(pl.col("k"), pl.lit(k_total)))
                 .with_columns(ipp=pl.col("indice") * pl.col("k"),
                               empalmado=pl.lit(True)))

    nuevos = n19.with_columns(ipp=pl.col("indice"), empalmado=pl.lit(False))

    # la glosa y el set de divisiones vigentes los manda la base 2019: la base 2014
    # trae una división que ya no se publica (27) y glosas con otra ortografía (28)
    glosas = (n19.filter(pl.col("nivel") == "division")
                 .select("codigo", pl.col("glosa").alias("glosa_19"))
                 .unique("codigo"))
    vigentes = glosas["codigo"].to_list()

    mensual = (pl.concat([
        previos.select("nivel", "codigo", "glosa", "anio", "mes", "ipp", "empalmado"),
        nuevos.select("nivel", "codigo", "glosa", "anio", "mes", "ipp", "empalmado"),
    ])
        .filter((pl.col("nivel") == "total") | pl.col("codigo").is_in(vigentes))
        .join(glosas, on="codigo", how="left")
        .with_columns(glosa=pl.coalesce(pl.col("glosa_19"), pl.col("glosa")))
        .drop("glosa_19")
        .sort(["nivel", "codigo", "anio", "mes"]))

    anual = indices_anuales(mensual).with_columns(pl.lit(BASE).alias("base"))

    # validación: reproducir la variación mensual publicada desde los niveles
    v = (nuevos.sort(["nivel", "codigo", "anio", "mes"])
               .with_columns(var_calc=(pl.col("indice")
                                       / pl.col("indice").shift(1).over(["nivel", "codigo"])
                                       - 1) * 100)
               .drop_nulls(["var_calc", "var_mensual"])
               .with_columns(dif=(pl.col("var_calc") - pl.col("var_mensual")).abs()))
    v_max, v_med = float(v["dif"].max()), float(v["dif"].median())

    incompletos = (anual.filter(pl.col("n_meses") < 12)
                        .select("anio", "n_meses").unique().sort("anio"))

    out = PROCESSED / SOURCE / DATASET
    out.mkdir(parents=True, exist_ok=True)
    mensual.write_parquet(out / "ipp_mensual.parquet", compression="zstd")
    anual.write_parquet(out / "ipp_anual.parquet", compression="zstd")

    info = {
        "fuente": {"base_2019": f19.name, "base_2014": f14.name},
        "filas_mensual": mensual.height,
        "filas_anual": anual.height,
        "anios": sorted(int(a) for a in anual["anio"].unique()),
        "divisiones": sorted(anual.filter(pl.col("nivel") == "division")["codigo"].unique()),
        "k_total": round(k_total, 6),
        "k_division": {r["codigo"]: round(r["k"], 6) for r in k_div.iter_rows(named=True)},
        "validacion_var_mensual": {"dif_max_pp": round(v_max, 4),
                                   "dif_mediana_pp": round(v_med, 4)},
        "anios_incompletos": incompletos.to_dicts(),
        "nota": "2023 empalmado desde la base 2014 (k por división); 2026 parcial",
    }
    (REPORTS / "normalizacion_ipp.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"mensual: {mensual.height} filas · anual: {anual.height} filas")
    print(f"k total = {k_total:.6f} · divisiones = {k_div.height}")
    print(f"variación mensual reproducida: dif máx {v_max:.4f} pp (mediana {v_med:.4f})")
    print(anual.filter(pl.col("nivel") == "total")
          .filter(pl.col("anio").is_in([2023, 2024, 2025]))
          .to_pandas().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
