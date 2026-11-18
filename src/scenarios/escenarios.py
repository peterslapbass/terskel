"""Escenarios 2030 para energia y CO2 de la manufactura (deterministico, sin ML).

El motor no proyecta una tendencia (solo hay dos años observados): aplica una
identidad contable sobre el nivel de 2024, con palancas explicitas y acotadas.

    energia_2030 = energia_2024 × (1+g_rama)^n × (1-mi)^n
    CO2_2030     = CO2_fosil_2024 × (1+g_rama)^n × (1-mi)^n × (1-mf)^n
                 + (CO2_biomasa + CO2_proceso) × (1+g_rama)^n × (1-mi)^n

`g_rama` es un vector por rama, no un escalar: la actividad de cada sector crece
a su propio ritmo, asi que la estructura productiva cambia. El vector central esta
calibrado para que el agregado ponderado por VBP quede en 2,0%/año, igual que la
version escalar, de modo que la diferencia sea composicion y no nivel.

`mf` actua solo sobre el CO2 de combustion fosil: la biomasa es biogenica y el CO2
de proceso depende del clinker, no del combustible.

Escenarios:
- congelado:        la actividad crece por rama, la intensidad y el mix no cambian.
- eficiencia:       ademas baja la intensidad energetica.
- descarbonizacion: ademas mejora el factor de emision (sustitucion de combustibles).
- recomposicion:    misma eficiencia y mix que descarbonizacion, con un vector de
                    crecimiento sectorial alternativo (cemento y siderurgia se contraen).

Salidas:
- `data/processed/scenarios/escenarios_2030.parquet`
- `reports/escenarios_2030.md`

Uso:
    python src/scenarios/escenarios.py
"""
from __future__ import annotations

import polars as pl

from common.paths import PROCESSED, REPORTS, ROOT, ensure_dirs

INTENSIDAD = PROCESSED / "indicators" / "intensidad_rama.parquet"
PARAMS = ROOT / "data" / "reference" / "escenarios_parametros.csv"
OUT = PROCESSED / "scenarios"

RAMAS = ["Papel y Celulosa", "Siderurgia", "Cemento", "Industria Láctea"]

RAMA_PARAM = {
    "Papel y Celulosa": "g_papel",
    "Siderurgia": "g_siderurgia",
    "Cemento": "g_cemento",
    "Industria Láctea": "g_lactea",
}

ESCENARIOS = {
    "congelado": {"mi": 0.0, "mf": 0.0, "g": "central"},
    "eficiencia": {"mi": None, "mf": 0.0, "g": "central"},
    "descarbonizacion": {"mi": None, "mf": None, "g": "central"},
    "recomposicion": {"mi": None, "mf": None, "g": "recomposicion"},
}

ETIQUETAS = {
    "observado": "Observado",
    "congelado": "Congelado",
    "eficiencia": "Eficiencia",
    "descarbonizacion": "Descarbonización",
    "recomposicion": "Recomposición sectorial",
}

ETIQUETAS_PALANCA = {
    "g_papel": "Crecimiento Papel y Celulosa",
    "g_siderurgia": "Crecimiento Siderurgia",
    "g_cemento": "Crecimiento Cemento",
    "g_lactea": "Crecimiento Industria Láctea",
    "mi": "Mejora de intensidad",
    "mf": "Mejora del factor de emisión",
}


def leer_parametros() -> tuple[dict[str, dict[str, float | None]], int, int]:
    p = pl.read_csv(PARAMS, separator=";", encoding="utf-8", infer_schema_length=0)

    def num(x: str | None) -> float | None:
        return None if x is None or x.strip() == "" else float(x)

    tabla: dict[str, dict[str, float | None]] = {}
    for r in p.iter_rows(named=True):
        tabla[r["parametro"]] = {
            "central": num(r["central"]),
            "minimo": num(r["minimo"]),
            "maximo": num(r["maximo"]),
            "recomposicion": num(r.get("recomposicion")),
        }
    return tabla, int(tabla["anio_base"]["central"]), int(tabla["anio_meta"]["central"])


def mapa_g(par: dict[str, dict[str, float | None]], columna: str = "central") -> dict[str, float]:
    """Vector de crecimiento por rama; si la columna no trae valor, usa el central."""
    salida = {}
    for rama, clave in RAMA_PARAM.items():
        v = par[clave].get(columna)
        salida[rama] = float(par[clave]["central"] if v is None else v)
    return salida


def base(anio: int) -> pl.DataFrame:
    return (pl.read_parquet(INTENSIDAD)
            .filter((pl.col("anio") == anio) & pl.col("rama").is_in(RAMAS))
            .select("rama", "energia_tj", "tco2", "tco2_fosil", "tco2_biomasa",
                    "tco2_proceso", "vbp_real_billones",
                    "econ_tj_por_billon_clp2019", "fis_tco2_por_tj_total",
                    "publicable_economica")
            # residual: clases "otro" y "sin_clase" del split, que no son fósil ni
            # biomasa ni proceso (combustibles alternativos, origen no identificado)
            .with_columns(tco2_otro=pl.col("tco2") - pl.col("tco2_fosil")
                          - pl.col("tco2_biomasa") - pl.col("tco2_proceso"))
            .sort("rama"))


def proyectar(b: pl.DataFrame, n: int, g: dict[str, float],
              mi: float, mf: float) -> pl.DataFrame:
    gm = pl.DataFrame({"rama": list(g), "g": [float(v) for v in g.values()]})
    fac_int = (1 - mi) ** n
    # `mf` (cambio de mix) solo puede reducir CO2 de combustión fósil: la biomasa
    # es biogénica y el CO2 de proceso depende del clínker, no del combustible
    fac_emi = (1 - mf) ** n
    return (b.join(gm, on="rama", how="left")
            .with_columns(g=pl.col("g").fill_null(0.0),
                          fac_act=(1 + pl.col("g")) ** n)
            .with_columns(
                energia_tj=pl.col("energia_tj") * pl.col("fac_act") * fac_int,
                tco2_fosil=pl.col("tco2_fosil") * pl.col("fac_act") * fac_int * fac_emi,
                tco2_biomasa=pl.col("tco2_biomasa") * pl.col("fac_act") * fac_int,
                tco2_proceso=pl.col("tco2_proceso") * pl.col("fac_act") * fac_int,
                tco2_otro=pl.col("tco2_otro") * pl.col("fac_act") * fac_int,
                vbp_real_billones=pl.col("vbp_real_billones") * pl.col("fac_act"),
            )
            .with_columns(
                tco2=(pl.col("tco2_fosil") + pl.col("tco2_biomasa")
                      + pl.col("tco2_proceso") + pl.col("tco2_otro")),
                econ_tj_por_billon_clp2019=pl.col("energia_tj") / pl.col("vbp_real_billones"),
                fis_tco2_por_tj_total=pl.col("tco2") / pl.col("energia_tj"),
            )
            .drop(["g", "fac_act"]))


def main() -> int:
    ensure_dirs()
    OUT.mkdir(parents=True, exist_ok=True)
    par, a0, a1 = leer_parametros()
    n = a1 - a0

    b = base(a0)
    g_central = mapa_g(par, "central")

    # puerta de coherencia: sin palancas y sin años, el motor devuelve el dato base
    cero = proyectar(b, 0, g_central, 0.0, 0.0)
    dif_e = float((cero["energia_tj"] - b["energia_tj"]).abs().max())
    dif_c = float((cero["tco2"] - b["tco2"]).abs().max())
    if dif_e > 1e-6 or dif_c > 1e-6:
        raise SystemExit(f"puerta de coherencia fallida: dE={dif_e} dC={dif_c}")

    filas = [b.with_columns(escenario=pl.lit("observado"), anio=pl.lit(a0, dtype=pl.Int16))]
    for nombre, lev in ESCENARIOS.items():
        g = mapa_g(par, lev["g"])
        mi = par["mi"]["central"] if lev["mi"] is None else lev["mi"]
        mf = par["mf"]["central"] if lev["mf"] is None else lev["mf"]
        filas.append(proyectar(b, n, g, float(mi), float(mf))
                     .with_columns(escenario=pl.lit(nombre), anio=pl.lit(a1, dtype=pl.Int16)))

    res = pl.concat(filas).select(
        "anio", "escenario", "rama", "energia_tj", "tco2",
        "tco2_fosil", "tco2_biomasa", "tco2_proceso", "tco2_otro",
        "vbp_real_billones", "econ_tj_por_billon_clp2019",
        "fis_tco2_por_tj_total", "publicable_economica")

    total = (res.group_by(["anio", "escenario"])
             .agg(pl.col("energia_tj").sum().alias("energia_tj"),
                  pl.col("tco2").sum().alias("tco2"),
                  pl.col("tco2_fosil").sum().alias("tco2_fosil"),
                  pl.col("tco2_biomasa").sum().alias("tco2_biomasa"),
                  pl.col("tco2_proceso").sum().alias("tco2_proceso"),
                  pl.col("tco2_otro").sum().alias("tco2_otro"),
                  pl.col("vbp_real_billones").sum().alias("vbp_real_billones"))
             .with_columns(
                 rama=pl.lit("Total 4 ramas"),
                 econ_tj_por_billon_clp2019=pl.col("energia_tj") / pl.col("vbp_real_billones"),
                 fis_tco2_por_tj_total=pl.col("tco2") / pl.col("energia_tj"),
                 publicable_economica=pl.lit(False),
             )
             .select(res.columns))

    final = pl.concat([res, total], how="vertical")
    final.write_parquet(OUT / "escenarios_2030.parquet", compression="zstd")

    # tornado: cada palanca entre su minimo y maximo, las otras en el central
    tor = []
    for clave, etiqueta in ETIQUETAS_PALANCA.items():
        vals = {}
        for extremo in ("minimo", "maximo"):
            g = dict(g_central)
            mi = float(par["mi"]["central"])
            mf = float(par["mf"]["central"])
            if clave in RAMA_PARAM.values():
                rama = next(r for r, p in RAMA_PARAM.items() if p == clave)
                g[rama] = float(par[clave][extremo])
            elif clave == "mi":
                mi = float(par["mi"][extremo])
            else:
                mf = float(par["mf"][extremo])
            vals[extremo] = float(proyectar(b, n, g, mi, mf)["tco2"].sum())
        tor.append({"palanca": etiqueta, "min": vals["minimo"], "max": vals["maximo"],
                    "amplitud": abs(vals["maximo"] - vals["minimo"])})

    pl.DataFrame(tor).write_parquet(OUT / "tornado_2030.parquet", compression="zstd")

    escribir_informe(final, tor, par, a0, a1, n, g_central)
    print(final.filter(pl.col("rama") == "Total 4 ramas")
          .select("anio", "escenario", pl.col("energia_tj").round(0),
                  pl.col("tco2").round(0))
          .to_pandas().to_string(index=False))
    print(f"\n-> {REPORTS / 'escenarios_2030.md'}")
    return 0


def escribir_informe(res: pl.DataFrame, tor: list[dict], par: dict,
                     a0: int, a1: int, n: int, g_central: dict[str, float]) -> None:
    tot = res.filter(pl.col("rama") == "Total 4 ramas").sort("anio", "escenario")
    obs = tot.filter(pl.col("anio") == a0).row(0, named=True)
    cong = tot.filter(pl.col("escenario") == "congelado").row(0, named=True)

    def var(x: float, y: float) -> str:
        return f"{(x / y - 1) * 100:+.1f}%".replace(".", ",")

    def pct(x: float | None) -> str:
        return "—" if x is None else f"{x * 100:+.1f}%".replace(".", ",")

    filas = ["| Escenario | Energía 2030 (TJ) | CO₂ 2030 (t) | vs 2024 | vs congelado |",
             "|---|---:|---:|---:|---:|"]
    for r in tot.filter(pl.col("anio") == a1).iter_rows(named=True):
        filas.append(f"| {ETIQUETAS.get(r['escenario'], r['escenario'])} | {r['energia_tj']:,.0f} | "
                     f"{r['tco2']:,.0f} | "
                     f"{var(r['tco2'], obs['tco2'])} | {var(r['tco2'], cong['tco2'])} |")

    param = ["| Palanca | Central | Mín | Máx | Recomposición |",
             "|---|---:|---:|---:|---:|"]
    for clave in ("g_papel", "g_siderurgia", "g_cemento", "g_lactea", "mi", "mf"):
        r = par[clave]
        param.append(f"| {ETIQUETAS_PALANCA[clave]} | {pct(r['central'])}/año | "
                     f"{pct(r['minimo'])} | {pct(r['maximo'])} | {pct(r.get('recomposicion'))} |")

    # recomposición: cómo cambia la estructura de VBP y qué pasa con el CO2
    obs_rama = (res.filter((pl.col("anio") == a0) & (pl.col("rama") != "Total 4 ramas"))
                .select("rama", vbp0=pl.col("vbp_real_billones"), co20=pl.col("tco2")))
    rec_rama = (res.filter((pl.col("anio") == a1) & (pl.col("escenario") == "recomposicion")
                           & (pl.col("rama") != "Total 4 ramas"))
                .select("rama", vbp1=pl.col("vbp_real_billones"), co21=pl.col("tco2")))
    est = (obs_rama.join(rec_rama, on="rama")
           .with_columns(share0=pl.col("vbp0") / pl.col("vbp0").sum(),
                         share1=pl.col("vbp1") / pl.col("vbp1").sum())
           .sort("vbp1", descending=True))
    estructura = ["| Rama | VBP 2024 | VBP 2030 | Peso 2024 | Peso 2030 | CO₂ 2024 | CO₂ 2030 | Var. CO₂ |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in est.iter_rows(named=True):
        v0 = f"{r['vbp0']:.2f}".replace(".", ",")
        v1 = f"{r['vbp1']:.2f}".replace(".", ",")
        estructura.append(
            f"| {r['rama']} | {v0} | {v1} | "
            f"{r['share0']*100:.1f}% | {r['share1']*100:.1f}% | "
            f"{r['co20']:,.0f} | {r['co21']:,.0f} | {var(r['co21'], r['co20'])} |")

    desc = res.filter((pl.col("anio") == a1) & (pl.col("escenario") == "descarbonizacion")
                      & (pl.col("rama") != "Total 4 ramas")).sort("tco2", descending=True)
    por_rama = ["| Rama | Energía 2030 (TJ) | CO₂ 2030 (t) | tCO₂/TJ | Publicable económica |",
                "|---|---:|---:|---:|---|"]
    for r in desc.iter_rows(named=True):
        por_rama.append(f"| {r['rama']} | {r['energia_tj']:,.0f} | {r['tco2']:,.0f} | "
                        f"{r['fis_tco2_por_tj_total']:,.1f} | "
                        f"{'sí' if r['publicable_economica'] else 'no'} |")

    origen = ["| Escenario | CO₂ fósil (t) | CO₂ biomasa (t) | CO₂ proceso (t) | CO₂ otro (t) | CO₂ total (t) |",
              "|---|---:|---:|---:|---:|---:|"]
    for r in tot.sort("anio", "escenario").iter_rows(named=True):
        etiqueta = ETIQUETAS.get(r["escenario"], r["escenario"])
        origen.append(f"| {etiqueta} {r['anio']} | {r['tco2_fosil']:,.0f} | "
                      f"{r['tco2_biomasa']:,.0f} | {r['tco2_proceso']:,.0f} | "
                      f"{r['tco2_otro']:,.0f} | {r['tco2']:,.0f} |")

    tornado = ["| Palanca | CO₂ con palanca al mínimo (t) | CO₂ con palanca al máximo (t) | Amplitud (t) |",
               "|---|---:|---:|---:|"]
    for t in sorted(tor, key=lambda x: -x["amplitud"]):
        tornado.append(f"| {t['palanca']} | {t['min']:,.0f} | {t['max']:,.0f} | {t['amplitud']:,.0f} |")

    texto = f"""# Escenarios 2030 — energía y CO₂ (4 ramas manufactureras)

## Introducción

Base observada {a0}, ajustada por el cribado de ediciones del RETC (los excesos se
capan a la mediana de las otras dos ediciones; ver
`reports/retc_anomalias.md`), horizonte {a1} ({n} años). Motor determinístico sobre el nivel
de 2024: la actividad y la eficiencia escalan energía y CO₂; el cambio de mix
(`mf`) actúa **solo sobre el CO₂ de combustión fósil**, porque la biomasa es
biogénica y el CO₂ de proceso depende del clínker. No es una proyección
estadística: con dos años observados no hay tendencia que estimar.

`g` es un **vector por rama**, no un escalar. El vector central está calibrado para
que el crecimiento agregado ponderado por VBP quede en 2,0%/año, el mismo valor de la
versión escalar. El nivel de 2030 no queda igual: Papel concentra el 94% del CO₂ de
las cuatro ramas y crece al 3,0%, así que el congelado sube a 21,9 Mt (20,9 Mt con un
`g` escalar del 2,0%).

## Parámetros

{chr(10).join(param)}

## Resultado agregado

{chr(10).join(filas)}

## Recomposición sectorial

Estructura de VBP y CO₂ con el vector alternativo (cemento y siderurgia se contraen,
papel y láctea crecen por encima del central). Papel pasa de 57,9% a 61,1% del VBP y
concentra el 94% del CO₂ de las cuatro ramas, así que el total lo mueve sobre todo lo
que le pasa a Papel; la contracción de Cemento y Siderurgia se ve en la estructura,
no en el agregado.

{chr(10).join(estructura)}

## Descomposición por origen del CO₂

{chr(10).join(origen)}

## Descarbonización por rama

{chr(10).join(por_rama)}

## Sensibilidad (tornado sobre CO₂ de 2030)

{chr(10).join(tornado)}

## Límites

### El crecimiento sectorial es un supuesto
Es un supuesto declarado, no una estimación: la ENIA tiene dos años y sus
variaciones por rama son artefactos de muestra (Cemento pasa de 6 a 4
establecimientos; Papel crece 51% en el denominador). El vector se elige, no se ajusta.

### La recomposición mueve la estructura
Mueve poco el CO₂ agregado porque las ramas que se contraen son pequeñas en VBP
(Cemento y Siderurgia suman ~14% del VBP de las 4). Su efecto es de **estructura**,
no de total.

### Cemento y la intensidad económica
Cemento entra en energía y CO₂ (datos sólidos) pero no en la intensidad económica:
su VBP en la ENIA cubre solo 4 plantas.

### El factor de emisión es agregado
Se modela como un parámetro agregado por rama; no distingue sustitución de
combustible de electrificación o de cambio de proceso.

### La columna `otro`
Recoge los combustibles que el split no clasifica como fósil, biomasa ni proceso
(BECSA, aceite usado, origen no identificado): 0,3% del CO₂. No la mueve `mf`.

### El año base
Es 2024 y está ajustado: 2023 trae el bloque GLP inflado ~12× y 2024 el error de
Cartocor (3,05 Mt, capado). La serie histórica no es una tendencia.
"""
    (REPORTS / "escenarios_2030.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
