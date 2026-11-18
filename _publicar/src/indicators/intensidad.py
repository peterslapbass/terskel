"""Indicadores de intensidad: energía y emisiones por actividad (2023-2024).

Dos familias, etiquetadas por separado y nunca mezcladas en una misma columna:

- **económica** (`econ_*`): energía o CO₂ por peso de producto, en CLP constantes
  de 2019. Denominador: VBP de la ENIA deflactado con el IPP por división.
- **física** (`fis_*`): CO₂ por TJ (intensidad de carbono del mix) y energía por
  ocupado (GJ/persona).

Fuentes y llaves:
- energía: BNE (DEMANDA DE ENERGÍA), ramas manufactureras, TJ.
- emisiones: RETC, CO₂, establecimientos con CIIU 10–33.
- actividad: ENIA, VBP (K009) y VA (K011), convertidos a CLP y deflactados.
- deflactor: IPP Industria Manufacturera por división, base 2019.
- tipo de cambio: promedio anual del dólar observado (BCCh).

Salidas:
- `data/processed/indicators/intensidad_rama.parquet`
- `data/processed/indicators/emisiones_division.parquet`
- `reports/indicadores_intensidad.md`

Uso:
    python src/indicators/intensidad.py
"""
from __future__ import annotations

import polars as pl

from common.paths import PROCESSED, REPORTS, ROOT, ensure_dirs
from common.calidad import aplicar as aplicar_anomalias
from common.industrias import (INDUSTRIAS, MANUFACTURA, EXTRACTIVAS, MOTIVOS, BNE_ALIAS,
                               PUBLICABLE_ECONOMICA, PUBLICABLE_FISICA,
                               industria_expr)

RAMAS = INDUSTRIAS
PUBLICABLES = PUBLICABLE_FISICA
BIOGENICOS = {"Biomasa", "Licor Negro", "Biogás", "Pellet de Biomasa"}
MWH_POR_TJ = 277.7778

BNE = PROCESSED / "cne" / "bne" / "bne_balance.parquet"
ENIA = PROCESSED / "enia" / "base" / "enia_base.parquet"
RETC = PROCESSED / "retc" / "emisiones_fp"
CO2_SPLIT = PROCESSED / "retc" / "co2_combustible.parquet"
FX = PROCESSED / "bcch" / "fx_anual.parquet"
IPP = PROCESSED / "ine" / "ipp" / "ipp_anual.parquet"
FACTORES = ROOT / "data" / "reference" / "factores_emision_combustible.csv"
OUT = PROCESSED / "indicators"


def rama_expr(col: str) -> pl.Expr:
    """Rama BNE a partir del código CIIU (clase, grupo, división o sección).

    Codifica la tabla `BNE-CIIU 4` del propio balance: Cemento es la clase 2394,
    Siderurgia el grupo 241, Azúcar la clase 1072 y Láctea la clase 1050, no
    divisiones completas.
    """
    x = (pl.col(col).cast(pl.String)
         .str.replace(r"^[A-Za-z]", "")
         .str.strip_chars()
         .str.replace_all(r"\.0$", ""))
    return (
        pl.when(x.str.starts_with("2394")).then(pl.lit("Cemento"))
        .when(x.str.starts_with("241")).then(pl.lit("Siderurgia"))
        .when(x.str.starts_with("1072")).then(pl.lit("Azúcar"))
        .when(x.str.starts_with("1050")).then(pl.lit("Industria Láctea"))
        .when(x.str.starts_with("17")).then(pl.lit("Papel y Celulosa"))
        .when(x.str.starts_with("20")).then(pl.lit("Petroquímica"))
        .when(x.str.slice(0, 2).cast(pl.Int32, strict=False).is_between(10, 33))
        .then(pl.lit("Industrias Varias"))
        .otherwise(pl.lit(None, dtype=pl.String))
    )


def tipo_cambio(y: int) -> float:
    return float(pl.read_parquet(FX).filter(pl.col("anio") == y)["fx_promedio"][0])


def deflactores(y: int) -> tuple[dict[str, float], float]:
    t = pl.read_parquet(IPP).filter(pl.col("anio") == y)
    div = {r["codigo"]: float(r["ipp"]) for r in t.filter(pl.col("nivel") == "division").iter_rows(named=True)}
    total = float(t.filter(pl.col("nivel") == "total")["ipp"][0])
    return div, total


def actividad(y: int) -> pl.DataFrame:
    fx = tipo_cambio(y)
    ipp_div, ipp_tot = deflactores(y)
    div = pl.DataFrame({"codigo": list(ipp_div), "ipp_div": list(ipp_div.values())})

    e = (pl.read_parquet(ENIA)
         .filter(pl.col("anio") == y)
         .with_columns(
             rama=industria_expr("ciiu4"),
             div=pl.col("ciiu_division").cast(pl.String),
             clp=pl.col("vbp") * pl.col("moneda_multiplo")
                 * pl.when(pl.col("moneda") == "USD").then(fx).otherwise(1.0),
             clp_va=pl.col("valor_agregado") * pl.col("moneda_multiplo")
                 * pl.when(pl.col("moneda") == "USD").then(fx).otherwise(1.0),
         )
         .join(div, left_on="div", right_on="codigo", how="left")
         .with_columns(
             ipp=pl.coalesce(pl.col("ipp_div"), pl.lit(ipp_tot)),
             usd=pl.col("moneda") == "USD",
         )
         .with_columns(
             vbp_real=pl.col("clp") / (pl.col("ipp") / 100),
             va_real=pl.col("clp_va") / (pl.col("ipp") / 100),
         ))

    return (e.filter(pl.col("rama").is_not_null())
            .group_by("rama")
            .agg(pl.len().alias("establecimientos"),
                 pl.col("usd").mean().alias("share_usd"),
                 # clp está en pesos -> 1e12 = billones
                 (pl.col("clp").sum() / 1e12).alias("vbp_nominal_billones"),
                 (pl.col("vbp_real").sum() / 1e12).alias("vbp_real_billones"),
                 (pl.col("va_real").sum() / 1e12).alias("va_real_billones"),
                 pl.col("ocupados_total").sum().alias("ocupados")))


def energia(y: int) -> pl.DataFrame:
    b = (pl.read_parquet(BNE)
         .filter((pl.col("anio") == y) & (pl.col("seccion") == "DEMANDA DE ENERGÍA")
                 & pl.col("item").is_in(RAMAS + list(BNE_ALIAS)))
         .with_columns(item=pl.when(pl.col("item").is_in(list(BNE_ALIAS)))
                       .then(pl.lit("Petroquímica")).otherwise(pl.col("item"))))
    total = (b.filter(pl.col("es_total"))
             .group_by(pl.col("item").alias("rama"))
             .agg(pl.col("tj").sum().alias("energia_tj")))
    fosil = (b.filter(~pl.col("es_total"))
             .filter(~pl.col("energetico").is_in(list(BIOGENICOS)))
             .group_by(pl.col("item").alias("rama"))
             .agg(pl.col("tj").sum().alias("energia_fosil_tj")))
    return total.join(fosil, on="rama", how="left")


def emisiones(y: int) -> tuple[pl.DataFrame, pl.DataFrame]:
    """CO₂ del RETC ya separado por origen (fósil, biomasa, proceso).

    Se usa `emision_retc` (validado) como total; el desglose por combustible
    viene de `co2_combustible.parquet`, que reparte ese total con la estructura
    declarada. `emision_total` (RUEA) no sirve para agregar: es 3,4 veces el
    validado (164 Mt contra 48,7 Mt en 2024).
    """
    r = (pl.read_parquet(CO2_SPLIT)
         .filter(pl.col("anio") == y)
         .pipe(aplicar_anomalias)
         .with_columns(
             rama=industria_expr("ciiu4_id"),
             div=pl.col("ciiu4_id").cast(pl.String).str.replace(r"^[A-Za-z]", "").str.slice(0, 2),
             tco2=pl.col("emision_retc").fill_null(0),
         ))

    por_rama = (r.filter(pl.col("rama").is_not_null())
                .group_by("rama")
                .agg(pl.col("tco2").sum().alias("tco2"),
                     pl.col("emision_retc_declarada").sum().alias("tco2_declarado"),
                     pl.col("co2_fosil").sum().alias("tco2_fosil"),
                     pl.col("co2_biomasa").sum().alias("tco2_biomasa"),
                     pl.col("co2_proceso").sum().alias("tco2_proceso"),
                     pl.col("ajustada").sum().alias("plantas_ajustadas"),
                     pl.len().alias("fuentes_co2")))

    # concentración: si una sola planta explica >50% del CO₂ de la rama, el dato
    # suele ser un error de reporte y la serie de esa rama no es comparable
    planta = (r.filter(pl.col("rama").is_not_null())
               .group_by(["rama", "id_vu", "nombre_establecimiento"])
               .agg(pl.col("tco2").sum().alias("t"), pl.col("co2_fosil").sum().alias("tf"))
               .group_by("rama")
               .agg((pl.col("t").max() / pl.col("t").sum()).alias("share_top1"),
                    (pl.col("tf").max() / pl.col("tf").sum()).alias("share_top1_fosil"),
                    pl.col("nombre_establecimiento")
                      .sort_by("tf", descending=True).first().alias("planta_fosil_top")))
    por_rama = por_rama.join(planta, on="rama", how="left")

    # cobertura: energía implícita en el CO₂ fósil contra el BNE (diagnóstico, no filtro)
    fac = (pl.read_csv(FACTORES, separator=";", encoding="utf-8", infer_schema_length=0)
           .with_columns(tco2_por_tj=pl.col("ef_carbono_kg_c_gj").cast(pl.Float64) * 44 / 12)
           .select("combustible", "tco2_por_tj"))
    impl = (r.filter(pl.col("rama").is_not_null())
            .join(fac, left_on="combustible_primario_norm", right_on="combustible", how="left")
            .with_columns(tj=pl.when(pl.col("tco2_por_tj") > 0)
                          .then(pl.col("co2_fosil") / pl.col("tco2_por_tj"))
                          .otherwise(0.0))
            .group_by("rama").agg(pl.col("tj").sum().alias("tj_implicito_fosil")))
    por_rama = por_rama.join(impl, on="rama", how="left")

    por_div = (r.filter(pl.col("rama").is_not_null())
               .group_by("div")
               .agg(pl.col("tco2").sum().alias("tco2"),
                    pl.col("rama").mode().first().alias("rama_principal"),
                    pl.len().alias("fuentes_co2")))
    return por_rama, por_div


def vbp_real_por_division(y: int) -> pl.DataFrame:
    fx = tipo_cambio(y)
    ipp_div, ipp_tot = deflactores(y)
    div = pl.DataFrame({"codigo": list(ipp_div), "ipp_div": list(ipp_div.values())})
    e = (pl.read_parquet(ENIA)
         .filter(pl.col("anio") == y)
         .with_columns(
             div=pl.col("ciiu_division").cast(pl.String),
             clp=pl.col("vbp") * pl.col("moneda_multiplo")
                 * pl.when(pl.col("moneda") == "USD").then(fx).otherwise(1.0))
         .join(div, left_on="div", right_on="codigo", how="left")
         .with_columns(ipp=pl.coalesce(pl.col("ipp_div"), pl.lit(ipp_tot))))
    return (e.group_by("div")
            .agg((pl.col("clp").sum() / 1e12).alias("vbp_nominal_billones"),
                 ((pl.col("clp") / (pl.col("ipp") / 100)).sum() / 1e12).alias("vbp_real_billones")))


def main() -> int:
    ensure_dirs()
    OUT.mkdir(parents=True, exist_ok=True)

    filas, divisiones = [], []
    for y in (2023, 2024):
        a = actividad(y)
        en = energia(y)
        em, em_div = emisiones(y)
        vd = vbp_real_por_division(y)

        t = (en.join(a, on="rama", how="left")
              .join(em, on="rama", how="left")
              .with_columns(
                  anio=pl.lit(y, dtype=pl.Int16),
                  cobertura_energetica=pl.col("tj_implicito_fosil") / pl.col("energia_fosil_tj"),
                  econ_tj_por_billon_clp2019=pl.col("energia_tj") / pl.col("vbp_real_billones"),
                  econ_tco2_por_billon_clp2019=pl.col("tco2") / pl.col("vbp_real_billones"),
                  fis_tco2_por_tj_fosil=pl.col("tco2_fosil") / pl.col("energia_fosil_tj"),
                  fis_tco2_por_tj_total=pl.col("tco2") / pl.col("energia_tj"),
                  fis_mwh_por_ocupado=pl.col("energia_tj") * MWH_POR_TJ / pl.col("ocupados"),
                  estructura_va_vbp=pl.col("va_real_billones") / pl.col("vbp_real_billones"),
                  publicable_fisica=pl.col("rama").is_in(list(PUBLICABLE_FISICA)),
                  publicable_economica=pl.col("rama").is_in(list(PUBLICABLE_ECONOMICA)),
                  nota=pl.col("rama").replace_strict(MOTIVOS, default=None,
                                                     return_dtype=pl.String),
                  alerta=pl.when(pl.col("share_top1_fosil") > 0.5)
                           .then(pl.format("CO₂ fósil concentrado en una planta ({}%: {})",
                                           (pl.col("share_top1_fosil") * 100).round(0).cast(pl.Int32),
                                           pl.col("planta_fosil_top")))
                           .when(pl.col("share_top1") > 0.5)
                           .then(pl.format("CO₂ concentrado en una planta ({}%)",
                                           (pl.col("share_top1") * 100).round(0).cast(pl.Int32)))
                           .otherwise(pl.lit(None, dtype=pl.String)),
              )
              .with_columns(
                  captura_retc=pl.when(pl.col("cobertura_energetica") > 1.5).then(pl.lit("excede"))
                  .when(pl.col("cobertura_energetica") >= 0.5).then(pl.lit("sí"))
                  .when(pl.col("cobertura_energetica") >= 0.1).then(pl.lit("parcial"))
                  .otherwise(pl.lit("no")),
              ))
        filas.append(t)

        d = (em_div.join(vd, on="div", how="left")
             .with_columns(
                 anio=pl.lit(y, dtype=pl.Int16),
                 econ_tco2_por_billon_clp2019=pl.col("tco2") / pl.col("vbp_real_billones"),
             )
             .sort("tco2", descending=True))
        divisiones.append(d)

    rama = pl.concat(filas).sort(["anio", "rama"])
    div = pl.concat(divisiones).sort(["anio", "tco2"], descending=True)

    # filas agregadas: manufactura (7), primario y extractivo (6) y total (13).
    # Son sumas, no promedios de índices.
    def agregado(nombres: list[str], etiqueta: str, nota: str | None = None) -> pl.DataFrame:
        t = (rama.filter(pl.col("rama").is_in(nombres)).group_by("anio")
             .agg(pl.col("establecimientos").sum(), pl.col("ocupados").sum(),
                  pl.col("vbp_nominal_billones").sum(), pl.col("vbp_real_billones").sum(),
                  pl.col("va_real_billones").sum(), pl.col("energia_tj").sum(),
                  pl.col("energia_fosil_tj").sum(), pl.col("tco2").sum(),
                  pl.col("tco2_declarado").sum(),
                  pl.col("tco2_fosil").sum(), pl.col("tco2_biomasa").sum(),
                  pl.col("tco2_proceso").sum(), pl.col("tj_implicito_fosil").sum(),
                  pl.col("plantas_ajustadas").sum(),
                  pl.col("fuentes_co2").sum()))
        t = t.with_columns(
            vbp_real_billones=pl.when(pl.col("vbp_real_billones") > 0)
            .then(pl.col("vbp_real_billones")).otherwise(None),
            vbp_nominal_billones=pl.when(pl.col("vbp_nominal_billones") > 0)
            .then(pl.col("vbp_nominal_billones")).otherwise(None),
        )
        return t.with_columns(
            rama=pl.lit(etiqueta),
            cobertura_energetica=pl.col("tj_implicito_fosil") / pl.col("energia_fosil_tj"),
            captura_retc=pl.when(pl.col("tj_implicito_fosil") / pl.col("energia_fosil_tj") > 1.5)
            .then(pl.lit("excede"))
            .when(pl.col("tj_implicito_fosil") / pl.col("energia_fosil_tj") >= 0.5)
            .then(pl.lit("sí"))
            .when(pl.col("tj_implicito_fosil") / pl.col("energia_fosil_tj") >= 0.1)
            .then(pl.lit("parcial")).otherwise(pl.lit("no")),
            share_usd=pl.lit(None, dtype=pl.Float64),
            share_top1=pl.lit(None, dtype=pl.Float64),
            share_top1_fosil=pl.lit(None, dtype=pl.Float64),
            planta_fosil_top=pl.lit(None, dtype=pl.String),
            alerta=pl.lit(None, dtype=pl.String),
            econ_tj_por_billon_clp2019=pl.col("energia_tj") / pl.col("vbp_real_billones"),
            econ_tco2_por_billon_clp2019=pl.col("tco2") / pl.col("vbp_real_billones"),
            fis_tco2_por_tj_fosil=pl.col("tco2_fosil") / pl.col("energia_fosil_tj"),
            fis_tco2_por_tj_total=pl.col("tco2") / pl.col("energia_tj"),
            fis_mwh_por_ocupado=pl.col("energia_tj") * MWH_POR_TJ / pl.col("ocupados"),
            estructura_va_vbp=pl.col("va_real_billones") / pl.col("vbp_real_billones"),
            publicable_fisica=pl.lit(False),
            publicable_economica=pl.lit(False),
            nota=pl.lit(nota, dtype=pl.String),
        )

    agregados = [agregado(MANUFACTURA, "Manufactura (7 ramas)"),
                 agregado(EXTRACTIVAS, "Primario y extractivo (6)",
                          "sin VBP: la ENIA es manufactura"),
                 agregado(INDUSTRIAS, "Total 14 industrias",
                          "VBP cubre solo manufactura")]
    final = (pl.concat([rama] + [a.select(rama.columns) for a in agregados],
                       how="diagonal")
             .sort(["anio", "rama"]))
    final.write_parquet(OUT / "intensidad_rama.parquet", compression="zstd")
    div.write_parquet(OUT / "emisiones_division.parquet", compression="zstd")

    escribir_informe(final, div)
    print(final.filter(pl.col("anio") == 2024)
          .select("rama", "energia_tj", "vbp_real_billones",
                  pl.col("econ_tj_por_billon_clp2019").round(0),
                  pl.col("fis_tco2_por_tj_fosil").round(3))
          .to_pandas().to_string(index=False))
    print(f"\n-> {REPORTS / 'indicadores_intensidad.md'}")
    return 0


def intensidad_fosil_sin_mayor(y: int) -> pl.DataFrame:
    """tCO₂/TJ fósil con y sin la planta que más aporta al CO₂ fósil de la rama.

    Sirve para los casos donde una sola planta distorsiona la rama (Cartocor en
    Papel 2024: 3,05 Mt declaradas contra 5,8 kt en 2023 y 2025).
    """
    r = (pl.read_parquet(CO2_SPLIT)
         .filter(pl.col("anio") == y)
         .pipe(aplicar_anomalias)
         .with_columns(rama=rama_expr("ciiu4_id"))
         .filter(pl.col("rama").is_not_null()))
    con = r.group_by("rama").agg(pl.col("co2_fosil").sum().alias("con"))
    top = (r.group_by(["rama", "id_vu"])
           .agg(pl.col("co2_fosil").sum().alias("tf"),
                pl.col("nombre_establecimiento").first().alias("planta"))
           .sort("tf", descending=True)
           .unique(subset=["rama"], keep="first"))
    sin = (r.join(top.select("rama", "id_vu"), on=["rama", "id_vu"], how="anti")
           .group_by("rama").agg(pl.col("co2_fosil").sum().alias("sin")))
    e = energia(y).select("rama", "energia_fosil_tj")
    return (con.join(sin, on="rama").join(e, on="rama").join(top.select("rama", "planta"), on="rama")
            .with_columns(con_por_tj=pl.col("con") / pl.col("energia_fosil_tj"),
                          sin_por_tj=pl.col("sin") / pl.col("energia_fosil_tj"),
                          share=1 - pl.col("sin") / pl.col("con")))


def universo_retc(y: int = 2024) -> pl.DataFrame:
    """Qué cubre el RETC validado: las 14 categorías, la generación y el resto."""
    d = (pl.read_parquet(CO2_SPLIT).filter(pl.col("anio") == y).pipe(aplicar_anomalias)
         .with_columns(ind=industria_expr("ciiu4_id"),
                       div=pl.col("ciiu4_id").cast(pl.String)
                       .str.replace(r"^[A-Za-z]", "").str.slice(0, 2)))
    grupo = (pl.when(pl.col("ind").is_not_null())
             .then(pl.lit("Categorías industriales (14)"))
             .when(pl.col("div") == "35").then(pl.lit("Generación eléctrica (CIIU 35)"))
             .otherwise(pl.lit("Servicios, agua, residuos y construcción")))
    return (d.with_columns(grupo=grupo)
            .group_by("grupo")
            .agg((pl.col("emision_retc").sum() / 1e6).alias("mt"),
                 pl.len().alias("filas"))
            .sort("mt", descending=True))


def escribir_informe(rama: pl.DataFrame, div: pl.DataFrame) -> None:
    d24 = rama.filter(pl.col("anio") == 2024).sort("energia_tj", descending=True)

    def n(x, fmt: str = ",.0f") -> str:
        return "—" if x is None else format(x, fmt)

    def tabla_rama(df: pl.DataFrame) -> str:
        lineas = ["| Rama | TJ | TJ fósil | VBP real | tCO₂ | tCO₂ fósil | TJ/billón CLP2019 | tCO₂/billón CLP2019 | tCO₂/TJ total | tCO₂/TJ fósil |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in df.iter_rows(named=True):
            lineas.append(
                f"| {r['rama']} | {n(r['energia_tj'])} | {n(r['energia_fosil_tj'])} | "
                f"{n(r['vbp_real_billones'], ',.1f')} | {n(r['tco2'])} | "
                f"{n(r['tco2_fosil'])} | "
                f"{n(r['econ_tj_por_billon_clp2019'])} | "
                f"{n(r['econ_tco2_por_billon_clp2019'])} | "
                f"{n(r['fis_tco2_por_tj_total'], ',.1f')} | "
                f"{n(r['fis_tco2_por_tj_fosil'], ',.1f')} |"
            )
        return "\n".join(lineas)

    def tabla_industrias(df: pl.DataFrame) -> str:
        def cob(x) -> str:
            if x is None:
                return "—"
            return ">999%" if x > 9.99 else f"{x * 100:.1f}%"

        lineas = ["| Industria | TJ | tCO₂ | tCO₂/TJ fósil | Cobertura | RETC | Publica | Nota |",
                  "|---|---:|---:|---:|---:|:---:|:---:|---|"]
        for r in df.filter(pl.col("rama").is_in(INDUSTRIAS)).iter_rows(named=True):
            lineas.append(
                f"| {r['rama']} | {n(r['energia_tj'])} | {n(r['tco2'])} | "
                f"{n(r['fis_tco2_por_tj_fosil'], ',.1f')} | "
                f"{cob(r['cobertura_energetica'])} | {r['captura_retc']} | "
                f"{'sí' if r['publicable_fisica'] else 'no'} | {r['nota'] or ''} |")
        return "\n".join(lineas)

    def tabla_universo(uni: pl.DataFrame) -> str:
        total = uni["mt"].sum()
        lineas = ["| Grupo | Mt CO₂ | % del validado | Filas |", "|---|---:|---:|---:|"]
        for r in uni.iter_rows(named=True):
            lineas.append(f"| {r['grupo']} | {r['mt']:,.2f} | "
                          f"{r['mt'] / total * 100:,.0f}% | {r['filas']:,} |")
        lineas.append(f"| **Total** | **{total:,.2f}** | 100% | "
                      f"**{uni['filas'].sum():,}** |")
        return "\n".join(lineas)

    d23 = rama.filter(pl.col("anio") == 2023)
    serie = ["| Rama | TJ 2023 | TJ 2024 | Var. | tCO₂ 2023 | tCO₂ 2024 | Var. |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for r in d24.filter(pl.col("publicable_fisica")).iter_rows(named=True):
        a = d23.filter(pl.col("rama") == r["rama"])
        if a.height == 0:
            continue
        a = a.row(0, named=True)
        v_e = (r["energia_tj"] / a["energia_tj"] - 1) * 100
        v_c = (r["tco2"] / a["tco2"] - 1) * 100 if a["tco2"] else float("nan")
        serie.append(f"| {r['rama']} | {a['energia_tj']:,.0f} | {r['energia_tj']:,.0f} | "
                     f"{v_e:+.1f}% | {a['tco2']:,.0f} | {r['tco2']:,.0f} | {v_c:+.1f}% |")

    top_div = div.filter((pl.col("anio") == 2024) & (pl.col("vbp_real_billones") > 0))
    sm = (intensidad_fosil_sin_mayor(2024)
          .filter((pl.col("share") > 0.5) & pl.col("rama").is_in(list(PUBLICABLES)))
          .sort("share", descending=True))
    tabla_sm = ["| Rama | Planta dominante | Peso en CO₂ fósil | tCO₂/TJ fósil | Sin esa planta |",
                "|---|---|---:|---:|---:|"]
    for r in sm.iter_rows(named=True):
        tabla_sm.append(f"| {r['rama']} | {r['planta']} | {r['share']*100:.0f}% | "
                        f"{r['con_por_tj']:,.1f} | {r['sin_por_tj']:,.1f} |")
    alertas = [f"- {r['anio']} · {r['rama']}: {r['alerta']}"
               for r in rama.filter(pl.col("alerta").is_not_null()).iter_rows(named=True)]
    bloque_alertas = "\n".join(alertas) if alertas else "- ninguna"
    lineas_div = ["| División | Rama principal | tCO₂ | VBP real | tCO₂/billón CLP2019 |",
                  "|---|---|---:|---:|---:|"]
    for r in top_div.iter_rows(named=True):
        lineas_div.append(
            f"| {r['div']} | {r['rama_principal']} | {r['tco2']:,.0f} | "
            f"{(r['vbp_real_billones'] or 0):,.1f} | {(r['econ_tco2_por_billon_clp2019'] or 0):,.0f} |")

    def ajuste(y: int) -> tuple[float, int]:
        t = (rama.filter((pl.col("anio") == y)
                         & (pl.col("rama") == "Manufactura (7 ramas)"))
             .row(0, named=True))
        return float(t["tco2_declarado"] - t["tco2"]), int(t["plantas_ajustadas"])

    dif23, pl23 = ajuste(2023)
    dif24, pl24 = ajuste(2024)
    dif23_txt = f"{dif23/1e6:.2f}".replace(".", ",")
    dif24_txt = f"{dif24/1e6:.2f}".replace(".", ",")
    dif23_txt1 = f"{dif23/1e6:.1f}".replace(".", ",")

    texto = f"""# Indicadores de intensidad — energía y emisiones (2023–2024)

Dos familias separadas. **Económica** (`econ_*`): por peso de producto, CLP
constantes de 2019 (VBP de la ENIA deflactado con el IPP por división).
**Física** (`fis_*`): por unidad física (TJ, ocupado).

## Por rama, 2024 (manufactura)

{tabla_rama(d24.filter(pl.col("rama").is_in(MANUFACTURA)))}

`VBP real` en billones de CLP de 2019. `tCO₂` es `emision_retc` **ajustado por el
cribado de ediciones** (`src/common/calidad.py`): la planta-año marcada como exceso se
capa a la mediana de las otras dos ediciones, un valor que esa misma planta declaró. En
2024 quita {dif24_txt} Mt en {pl24} plantas; en 2023, {dif23_txt} Mt en {pl23}. No se imputa
ningún valor externo. El desglose fósil/biomasa/proceso viene de
`co2_combustible.parquet`, que reparte el total con la estructura declarada.
`emision_total` (RUEA) no se usa para agregar: es 3,4 veces el validado (164 Mt contra
48,7 Mt en 2024).

## Las 14 industrias identificables

La granularidad máxima no la fija el RETC —trae CIIU a 4 dígitos para todo el
país— sino el BNE: su tabla de equivalencia `BNE-CIIU 4` define 14 categorías
industriales. Siete son manufactureras, una es refino y extracción de petróleo y gas,
y seis primarias o extractivas. Fuera quedan comercio, servicios, transporte,
construcción y sector público, que el balance no separa como demanda industrial.
`Producción de Metanol` se suma a Petroquímica porque el RETC no puede separarlas:
ambas son CIIU 2011.

La columna **cobertura** es la energía implícita en el CO₂ fósil sobre la que el BNE
asigna a la industria: mide si el RETC captura la combustión que esa industria
declara consumir. `RETC` la resume en cuatro estados: **sí** (50–150%), **parcial**
(10–50%), **no** (<10%) y **excede** (>150%: se declara más energía que la que el
balance asigna). Es un diagnóstico, no un filtro.

Solo cuatro industrias pasan las dos pruebas —combustión capturada y CO₂ no
concentrado en una planta—: Papel, Cemento, Láctea y Refinería. Las otras diez se
publican aquí con su cifra y su motivo, no como indicador.

{tabla_industrias(d24)}

## Qué captura el RETC (2024)

El RETC no es un inventario industrial: es un registro de establecimientos que
superan los umbrales del D.S. 138/2005. Por eso la mayor parte de su CO₂ validado no
es industria: es generación eléctrica declarada planta a planta.

{tabla_universo(universo_retc())}

Las **14 categorías** son las que el balance separa; la generación eléctrica entra
completa y el resto son servicios, agua, residuos, comercio y construcción. Lo que
falta no es un vacío del registro: **la gran minería no declara su combustión**, por
eso Cobre aparece con 42 kt donde el BNE le asigna 206.000 TJ.

## Serie 2023–2024 (ramas publicables)

{chr(10).join(serie)}

Las variaciones no son variaciones ambientales cuando una sola planta domina el
CO₂ de la rama: ver las alertas de calidad. Y **2023 no se lee como tendencia**:
el cribado ya capó su bloque GLP (16,15 Mt declarados contra 1,32 Mt en 2024) y la
edición arrastra una reducción de {dif23_txt1} Mt; el año de referencia es 2024
(ver `reports/retc_anomalias.md`). Refinería arrastra además un corte de fuente: el
ítem del BNE pasa de 49.193 a 22.981 TJ entre ediciones, así que su serie tampoco se
compara.

## Emisiones y VBP por división CIIU, 2024

La división de 2 dígitos es la unidad más fina que comparten el RETC (CIIU del
establecimiento) y la ENIA (VBP por división). El BNE no baja de las 14 categorías,
así que aquí no hay energía: solo CO₂ por peso producido.

{chr(10).join(lineas_div)}

## Alertas de calidad

{bloque_alertas}

## Sensibilidad a la planta dominante, 2024

{chr(10).join(tabla_sm)}

Cuando una planta explica más de la mitad del CO₂ fósil de la rama, su valor
individual decide la intensidad. La columna "sin esa planta" muestra cuánto del
número depende de un solo dato.

## Lectura y límites

- El denominador (`VBP`) cubre solo establecimientos de 10+ trabajadores; la
  energía del BNE cubre toda la industria. Las razones son una **cota superior**
  de la intensidad verdadera y sirven para comparar ramas y años, no como nivel.
- Solo Papel y Celulosa, Cemento y Láctea publican intensidad física. `Siderurgia`
  queda fuera: Huachipato declara únicamente gases de subproducto (alto horno, coque)
  y ningún carbón ni coque mineral, así que el RETC captura ~8% de la energía de la
  rama. `Petroquímica` declara ~200 TJ para toda la división 20 y `Industrias Varias`
  es el cajón residual: tampoco son publicables.
- `tCO₂/TJ fósil` usa solo el CO₂ de combustión fósil (excluye biomasa y
  procesos) sobre la energía fósil del BNE: es la intensidad de carbono del mix
  fósil y ahora es comparable entre ramas, incluida Papel y Celulosa.
- `tCO₂/TJ total` incluye biomasa y proceso sobre la energía total: mide cuánto
  CO₂ sale por unidad de energía usada, sin juzgar el origen.
- Deflación simple del VBP con IPP de producción; el VA se deflacta con el mismo
  índice (supuesto, no doble deflación).
- Los denominadores usan el IPP de la división correspondiente; cuando la
  división no publica IPP se usa el total de manufactura.
- `publicable_economica` deja fuera a Cemento: la ENIA trae solo 4 plantas de la
  clase 2394 (0,11 billones de VBP), así que su intensidad económica está inflada.
"""
    (REPORTS / "indicadores_intensidad.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
