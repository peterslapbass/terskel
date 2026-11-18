"""Split del CO2 del RETC en fósil, biomasa, proceso y otros.

Problema que resuelve: `emision_retc` es un total validado por fuente, sin
desglose por combustible. La intensidad física `tCO2/TJ fósil` no era
interpretable en ramas que queman biomasa (Papel y Celulosa usaba 502 tCO2/TJ
porque el CO2 del licor negro entraba en el numerador).

Método (asignación proporcional, no estimación):
1. `emision_total` = primario + secundario + procesos (identidad verificada por
   fila, error < 1e-8).
2. Cada componente se clasifica como fósil, biomasa u otro con
   `data/reference/combustibles_clase.csv`.
3. Esa estructura declarada reparte el total validado:

       co2_clase = emision_retc × (componente_clase / emision_total)

   Así la suma de clases es exactamente `emision_retc`: no se crea ni se
   destruye emisión, solo se le asigna origen.

Salida:
- `data/processed/retc/co2_combustible.parquet` (grano: fuente × año)
- `reports/retc_co2_combustible.md`

Uso:
    python src/normalize/retc_co2_combustible.py
"""
from __future__ import annotations

import polars as pl

from common.paths import PROCESSED, REPORTS, ROOT, ensure_dirs

RETC = PROCESSED / "retc" / "emisiones_fp"
CLASES = ROOT / "data" / "reference" / "combustibles_clase.csv"
OUT = PROCESSED / "retc" / "co2_combustible.parquet"

CLASES_VALIDAS = {"fosil", "biomasa", "otro"}


def leer_clases() -> dict[str, str]:
    tabla = pl.read_csv(CLASES, separator=";", encoding="utf-8", infer_schema_length=0)
    mapa = {r["combustible"]: r["clase"] for r in tabla.iter_rows(named=True)}
    malas = {k: v for k, v in mapa.items() if v not in CLASES_VALIDAS}
    if malas:
        raise SystemExit(f"clases inválidas en {CLASES.name}: {malas}")
    return mapa


def clasificar(col: str, mapa: dict[str, str]) -> pl.Expr:
    return (pl.when(pl.col(col).is_null())
            .then(pl.lit("ninguno"))
            .otherwise(pl.col(col).replace_strict(mapa, default="sin_clase")))


def main() -> int:
    ensure_dirs()
    mapa = leer_clases()

    co2 = (pl.read_parquet(RETC, hive_partitioning=True)
           .filter(pl.col("contaminante_norm") == "CARBON DIOXIDE")
           .with_columns(clase_primario=clasificar("combustible_primario_norm", mapa),
                         clase_secundario=clasificar("combustible_secundario_norm", mapa)))

    prim = pl.col("emision_combustible_primario")
    sec = pl.col("emision_combustible_secundario")
    proc = pl.col("emision_procesos")
    total = prim + sec + proc

    # control: emision_total debe ser la suma de sus componentes
    desvio = float(co2.select((pl.col("emision_total") - total).abs().max()).item())
    if desvio > 1e-6:
        raise SystemExit(f"emision_total no cuadra con sus componentes: {desvio}")

    def componente(clase: str) -> pl.Expr:
        return ((pl.when(pl.col("clase_primario") == clase).then(prim).otherwise(0.0))
                + (pl.when(pl.col("clase_secundario") == clase).then(sec).otherwise(0.0)))

    partes = {
        "co2_fosil": componente("fosil"),
        "co2_biomasa": componente("biomasa"),
        "co2_otro": componente("otro"),
        "co2_proceso": proc,
    }
    # residuo: lo que no cae en ninguna clase (combustible sin clasificar o con
    # nombre nulo pero emisión positiva). Se conserva para que la suma cuadre.
    partes["co2_sin_clase"] = (total - partes["co2_fosil"] - partes["co2_biomasa"]
                              - partes["co2_otro"] - partes["co2_proceso"]).clip(0.0, None)

    con_partes = co2.with_columns(**partes).with_columns(
        base=total,
    ).with_columns(
        # reparto proporcional del total validado según la estructura declarada
        **{k: pl.when(pl.col("base") > 0)
              .then(pl.col("emision_retc") * pl.col(k) / pl.col("base"))
              .otherwise(0.0)
           for k in partes}
    )

    salida = con_partes.select(
        "anio", "id_vu", "rut_razon_social", "razon_social", "nombre_establecimiento",
        "ciiu4_id", "region_norm", "source_id", "tipo_fuente_norm",
        "combustible_primario_norm", "clase_primario",
        "combustible_secundario_norm", "clase_secundario",
        "emision_total", "emision_retc",
        "co2_fosil", "co2_biomasa", "co2_proceso", "co2_otro", "co2_sin_clase",
    ).sort(["anio", "id_vu", "source_id"])

    # control: la suma de clases reproduce el total validado
    suma = pl.col("co2_fosil") + pl.col("co2_biomasa") + pl.col("co2_proceso") \
        + pl.col("co2_otro") + pl.col("co2_sin_clase")
    err = float(salida.select((suma - pl.col("emision_retc")).abs().max()).item())
    if err > 1e-6:
        raise SystemExit(f"el split no reproduce emision_retc: {err}")

    salida.write_parquet(OUT, compression="zstd")
    escribir_informe(salida)
    print(f"-> {OUT}")
    print(f"-> {REPORTS / 'retc_co2_combustible.md'}")
    return 0


def escribir_informe(df: pl.DataFrame) -> None:
    nacional = (df.group_by("anio")
                .agg(pl.col("emision_retc").sum().alias("total"),
                     pl.col("co2_fosil").sum(), pl.col("co2_biomasa").sum(),
                     pl.col("co2_proceso").sum(), pl.col("co2_otro").sum(),
                     pl.col("co2_sin_clase").sum())
                .sort("anio"))

    lineas = ["| Año | Total validado | Fósil | Biomasa | Proceso | Otro | Sin clase |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for r in nacional.iter_rows(named=True):
        t = r["total"]
        lineas.append(
            f"| {r['anio']} | {t:,.0f} | {r['co2_fosil']:,.0f} "
            f"({r['co2_fosil']/t*100:.1f}%) | {r['co2_biomasa']:,.0f} "
            f"({r['co2_biomasa']/t*100:.1f}%) | {r['co2_proceso']:,.0f} "
            f"({r['co2_proceso']/t*100:.1f}%) | {r['co2_otro']:,.0f} | "
            f"{r['co2_sin_clase']:,.0f} |")

    y = int(df["anio"].max())
    combustibles = (df.filter(pl.col("anio") == y)
                    .group_by("combustible_primario_norm")
                    .agg(pl.col("co2_fosil").sum().alias("fosil"),
                         pl.col("co2_biomasa").sum().alias("biomasa"),
                         pl.col("co2_proceso").sum().alias("proceso"))
                    .with_columns(masa=pl.col("fosil") + pl.col("biomasa") + pl.col("proceso"))
                    .sort("masa", descending=True)
                    .head(12))
    tabla = ["| Combustible primario | CO₂ fósil | CO₂ biomasa | CO₂ proceso |",
             "|---|---:|---:|---:|"]
    for r in combustibles.iter_rows(named=True):
        tabla.append(f"| {r['combustible_primario_norm']} | {r['fosil']:,.0f} | "
                     f"{r['biomasa']:,.0f} | {r['proceso']:,.0f} |")

    texto = f"""# Split del CO₂ del RETC por origen ({y})

Método: el desglose declarado (`emision_combustible_primario`, `_secundario`,
`emision_procesos`) se clasifica por combustible y reparte proporcionalmente el
total validado (`emision_retc`). No se estima nada: la suma de las clases es
exactamente el total.

## Nacional

{chr(10).join(lineas)}

`Proceso` es CO₂ de calcinación y procesos químicos, no de combustión. Por eso
la intensidad `tCO₂ fósil/TJ fósil` lo excluye y el `tCO₂ total` lo incluye.

## Combustibles principales ({y})

{chr(10).join(tabla)}

## Límites

- El reparto es **proporcional a lo declarado**, no medido: si una planta declara
  mal su mezcla, el split hereda el error. Lo que se conserva exacto es el total.
- `emision_total` (declarado) es 3,4 veces `emision_retc` (validado). Se usa el
  validado como total y el declarado solo como estructura.
- `otro` (aceite usado, combustible sólido alternativo) y `sin_clase` quedan
  fuera de fósil y biomasa por convención, no por evidencia.
"""
    (REPORTS / "retc_co2_combustible.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
