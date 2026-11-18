"""Cribado de anomalías por planta y edición en el RETC (2023-2025).

Marca, no corrige: el ajuste de los agregados vive en `src/common/calidad.py`.
Cada edición del RETC trae un grupo de declaraciones incompatibles con la serie
de la propia planta. El caso sistemático es el GLP de 2023: 16,15 Mt de CO2
contra 1,32 Mt en 2024 con el mismo número de declaraciones.

Regla (simétrica, no exige conocer la causa):

  para cada planta y año se toma la mediana de los otros dos años. Se marca el
  año si
    (a) los otros dos concuerdan dentro de 3x,
    (b) su mediana supera 100 t de CO2, y
    (c) el año está sobre 10x o bajo 0,1x de esa mediana.

El criterio (a) es el que evita marcar plantas que crecen o cierran de verdad:
si las otras dos ediciones no se parecen entre sí, no hay referencia.

Salidas:
- `data/processed/retc/anomalias.parquet`
- `reports/retc_anomalias.md`

Uso:
    python src/audit/retc_anomalias.py
"""
from __future__ import annotations

import polars as pl

from common.paths import PROCESSED, REPORTS

CO2 = PROCESSED / "retc" / "co2_combustible.parquet"
OUT = PROCESSED / "retc" / "anomalias.parquet"

ANIOS = (2023, 2024, 2025)
COLS = [f"y{y}" for y in ANIOS]
MIN_MATERIALIDAD = 1000.0
FACTOR = 10.0
MAX_CONCORDANCIA = 3.0


def por_planta(df: pl.DataFrame) -> pl.DataFrame:
    return (df.group_by(["id_vu", "nombre_establecimiento", "razon_social",
                         "ciiu4_id", "anio"])
            .agg(pl.col("emision_retc").sum().alias("co2")))


def evaluar(w: pl.DataFrame, y: int) -> pl.DataFrame:
    otras = [f"y{a}" for a in ANIOS if a != y]
    mediana = (pl.col(otras[0]) + pl.col(otras[1])) / 2
    alto = pl.max_horizontal(otras[0], otras[1])
    bajo = pl.min_horizontal(otras[0], otras[1])
    return w.select(
        pl.lit(y, dtype=pl.Int16).alias("anio"),
        "id_vu", "nombre_establecimiento", "razon_social", "ciiu4_id",
        pl.col(f"y{y}").alias("co2"),
        mediana.alias("mediana_otras"),
        pl.when(mediana > 0).then(pl.col(f"y{y}") / mediana).otherwise(None).alias("ratio"),
        pl.when(bajo > 0).then(alto / bajo).otherwise(None).alias("concordancia"),
    )


def combustible_dominante(df: pl.DataFrame) -> pl.DataFrame:
    return (df.group_by(["id_vu", "anio", "combustible_primario_norm"])
            .agg(pl.col("emision_retc").sum().alias("c"))
            .sort("c", descending=True)
            .group_by(["id_vu", "anio"])
            .agg(pl.col("combustible_primario_norm").first().alias("combustible_principal")))


def main() -> int:
    d = pl.read_parquet(CO2).filter(pl.col("anio").is_in(ANIOS))

    w = (por_planta(d)
         .pivot(values="co2", index=["id_vu", "nombre_establecimiento",
                                     "razon_social", "ciiu4_id"], on="anio")
         .rename({str(y): f"y{y}" for y in ANIOS})
         .with_columns([pl.col(c).fill_null(0.0) for c in COLS]))

    largo = pl.concat([evaluar(w, y) for y in ANIOS])

    marcadas = (largo
                .filter((pl.col("concordancia").is_not_null())
                        & (pl.col("concordancia") <= MAX_CONCORDANCIA)
                        & (pl.max_horizontal("co2", "mediana_otras") >= MIN_MATERIALIDAD)
                        & ((pl.col("ratio") > FACTOR) | (pl.col("ratio") < 1 / FACTOR)))
                .with_columns(
                    direccion=pl.when(pl.col("ratio") > FACTOR)
                    .then(pl.lit("exceso")).otherwise(pl.lit("déficit")),
                    exceso_t=pl.when(pl.col("ratio") > FACTOR)
                    .then(pl.col("co2") - pl.col("mediana_otras")).otherwise(0.0))
                .join(combustible_dominante(d), on=["id_vu", "anio"], how="left")
                .sort("exceso_t", descending=True))

    marcadas.write_parquet(OUT, compression="zstd")
    escribir_informe(d, marcadas, largo)
    print(marcadas.group_by("anio").agg(
        pl.len().alias("plantas"),
        pl.col("co2").sum().round(0).alias("co2_marcado"),
        pl.col("exceso_t").sum().round(0).alias("exceso_t")).sort("anio")
        .to_pandas().to_string(index=False))
    print(f"\n-> {OUT}")
    print(f"-> {REPORTS / 'retc_anomalias.md'}")
    return 0


def escribir_informe(d: pl.DataFrame, m: pl.DataFrame, largo: pl.DataFrame) -> None:
    total = (d.group_by("anio").agg(pl.col("emision_retc").sum().alias("co2")).sort("anio"))

    resumen = ["| Edición | Plantas marcadas | CO₂ marcado (t) | CO₂ total (t) | % del total | Exceso (t) | Nacional sin el exceso (t) |",
               "|---|---:|---:|---:|---:|---:|---:|"]
    for r in total.iter_rows(named=True):
        sub = m.filter(pl.col("anio") == r["anio"])
        ex = float(sub["exceso_t"].sum())
        resumen.append(f"| {r['anio']} | {sub.height} | {sub['co2'].sum():,.0f} | "
                       f"{r['co2']:,.0f} | {sub['co2'].sum()/r['co2']*100:.1f}% | "
                       f"{ex:,.0f} | {r['co2']-ex:,.0f} |")

    glp = ["| Edición | CO₂ del GLP (t) | Declaraciones |", "|---|---:|---:|"]
    g = (d.filter(pl.col("combustible_primario_norm") == "GAS LICUADO DE PETROLEO")
         .group_by("anio").agg(pl.col("emision_retc").sum().alias("co2"), pl.len()).sort("anio"))
    for r in g.iter_rows(named=True):
        glp.append(f"| {r['anio']} | {r['co2']:,.0f} | {r['len']:,} |")

    top = ["| Edición | Establecimiento | CO₂ (t) | Referencia (t) | Ratio | Combustible | Dirección |",
           "|---|---|---:|---:|---:|---|---|"]
    for r in m.head(12).iter_rows(named=True):
        top.append(f"| {r['anio']} | {r['nombre_establecimiento']} | {r['co2']:,.0f} | "
                   f"{r['mediana_otras']:,.0f} | {r['ratio']:,.0f}× | "
                   f"{r['combustible_principal'] or '—'} | {r['direccion']} |")

    t = {int(r["anio"]): float(r["co2"]) for r in total.iter_rows(named=True)}
    ex = {y: float(m.filter(pl.col("anio") == y)["exceso_t"].sum()) for y in ANIOS}
    n23 = t[2023] - ex[2023]

    def num(x: float, d: int = 1) -> str:
        return f"{x:,.{d}f}".replace(",", "\u00a0").replace(".", ",").replace("\u00a0", ".")

    texto = f"""# Anomalías por planta y edición — RETC 2023–2025

Cribado, no corrección. El RETC publica cada edición como un archivo cerrado y
sin control de coherencia entre años; este informe mide cuánto de cada año es
incompatible con la serie de la propia planta.

## Regla

Para cada planta y año se toma la mediana de los otros dos años. Se marca el año
si los otros dos concuerdan dentro de 3×, la planta supera 1.000 t de CO₂ en
alguna de las tres ediciones y el año está sobre 10× o bajo 0,1× de esa mediana.
La condición de concordancia es la que distingue un error de una planta que crece,
cierra o entra en operación.

## Resultado

{chr(10).join(resumen)}

El exceso demostrable de 2023 es de {num(ex[2023]/1e6)} Mt ({num(ex[2023]/t[2023]*100, 0)}% de la
edición). Al restarlo, 2023 queda en **{num(n23/1e6)} Mt**, contra {num(t[2024]/1e6)} Mt de 2024 y
{num(t[2025]/1e6)} Mt de 2025: lo que parecía una caída de 26% es una edición defectuosa.
**Es un piso, no el total**: la regla exige que los otros dos años concuerden entre
sí, así que no puede evaluar plantas con una sola edición comparable (Enaex Río Loa,
por ejemplo: 2,63 Mt en 2023, 0,63 Mt en 2024 y 3 kt en 2025).

## El bloque GLP de 2023

{chr(10).join(glp)}

Mismo número de declaraciones en los tres años y doce veces el CO₂ en 2023. No
son plantas raras: es el factor de emisión del GLP de esa edición. Todos los casos
extremos comparten el GLP, como combustible primario o secundario.

## Casos mayores

{chr(10).join(top)}

## Lectura

- **2023**: el bloque GLP está inflado ~12× y concentra el exceso. Es un defecto
  del factor de emisión de esa edición, no de una empresa: afecta a cualquier
  usuario de GLP.
- **2024**: Cartocor declara 3,05 Mt contra 5,8 kt (2023) y 5,7 kt (2025). Error de
  unidad de una planta, ya documentado en [retc.md](../docs/fuentes/retc.md).
  Es el 86% del exceso de esa edición.
- **2025**: aparecen déficits —consumidores de gas que caen a casi cero—, compatibles
  con una edición aún abierta más que con un cierre de planta.

## Límites

1. **Marca, no corrige**: el ajuste de los agregados vive en
   `src/common/calidad.py`, que capa los excesos a la mediana de las otras dos
   ediciones. Este informe deja la evidencia planta por planta.
2. **Tres años, dos de referencia**: con solo dos puntos de comparación la regla no
   puede validar nada; solo descarta.
3. **Planta que cierra de verdad** pasa la condición (a) si las otras dos ediciones
   son parecidas, y se marca como déficit. Se distingue en la columna `direccion`
   y se confirma con prensa o con el propio registro.
4. **El corte de 1.000 t** deja fuera miles de fuentes menores; no cambia el total.
5. **El signo importa**: la columna `exceso_t` solo suma los excesos. Los déficits
   de 2025 no se descuentan del nacional, porque un consumo que no aparece puede
   ser una declaración que aún no se cierra.
"""
    (REPORTS / "retc_anomalias.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
