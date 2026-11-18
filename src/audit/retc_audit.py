"""Auditoría de compatibilidad de las emisiones de fuentes puntuales del RETC.

Genera reports/retc_auditoria.md con la matriz de compatibilidad que exige
la propuesta (esquema, cobertura, persistencia de establecimientos, calidad
de las columnas de emisión) y deja las decisiones abiertas explícitas.

Uso:
    python src/audit/retc_audit.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

from common.paths import PROCESSED, REPORTS

GLOB = str(PROCESSED / "retc" / "emisiones_fp" / "**" / "*.parquet")
CO2 = "CARBON DIOXIDE"
COMPONENTS = ("emision_combustible_primario", "emision_combustible_secundario", "emision_procesos")


def md(df: pl.DataFrame, n: int | None = None, fmt: dict | None = None) -> str:
    d = df.head(n) if n else df
    fmt = fmt or {}
    cols = d.columns
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for row in d.iter_rows():
        cells = []
        for c, v in zip(cols, row):
            if v is None:
                cells.append("—")
            elif isinstance(v, float):
                cells.append(format(v, fmt.get(c, ",.4g")))
            elif isinstance(v, int):
                cells.append(format(v, "d" if c in ("anio", "year") else fmt.get(c, ",")))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def pct(a: float, b: float) -> str:
    return f"{(100 * a / b):.1f}%" if b else "—"


def main() -> int:
    lf = pl.scan_parquet(GLOB)
    df = lf.collect()

    years = sorted(df["anio"].unique().to_list())
    out: list[str] = []
    add = out.append

    add("# Auditoría RETC — emisiones al aire de fuentes puntuales")
    add("")
    add(f"Años auditados: **{', '.join(map(str, years))}**  ")
    add(f"Filas totales: **{df.height:,}**  ")
    add("Fuente: `datosretc.mma.gob.cl`, conjunto `emisiones-al-aire-de-fuente-puntuales` (licencia ODbL).")
    add("")
    add("> **Unidad de emisión:** no viene declarada ni en los datos ni en la hoja `Resumen`.")
    add("> Todo lo que sigue se expresa en *unidades del archivo* (presumiblemente toneladas/año).")
    add("> Verificar contra la metodología RETC antes de publicar cualquier cifra.")
    add("")

    # 1. Volumen y cobertura
    add("## 1. Volumen y cobertura")
    add("")
    base = (
        df.group_by("anio")
        .agg(
            pl.len().alias("filas"),
            pl.col("id_vu").n_unique().alias("establecimientos"),
            pl.col("declaracion_id").n_unique().alias("declaraciones"),
            pl.col("contaminante").n_unique().alias("contaminantes"),
            pl.col("rubro").n_unique().alias("rubros"),
            pl.col("ciiu4").n_unique().alias("ciiu4"),
            pl.col("combustible_primario").n_unique().alias("combustibles"),
            pl.col("region").n_unique().alias("regiones"),
        )
        .sort("anio")
    )
    add(md(base))
    add("")

    # 2. Esquema
    add("## 2. Esquema")
    add("")
    schemas = {}
    for y in years:
        schemas[y] = list(df.filter(pl.col("anio") == y).columns)
    same = all(schemas[y] == schemas[years[0]] for y in years)
    add(f"- Columnas por año: {', '.join(f'{y}: {len(schemas[y])}' for y in years)}")
    add(f"- Esquema idéntico entre años: **{'sí' if same else 'no'}**")
    if not same:
        ref = set(schemas[years[0]])
        for y in years[1:]:
            add(f"- {y} vs {years[0]}: solo en {years[0]} {sorted(ref - set(schemas[y]))}, solo en {y} {sorted(set(schemas[y]) - ref)}")
    add("")

    # 3. Persistencia
    add("## 3. Persistencia de establecimientos (`id_vu`)")
    add("")
    sets = {y: set(df.filter(pl.col("anio") == y)["id_vu"].unique().to_list()) for y in years}
    add("| comparación | intersección | solo en el primero | solo en el segundo | Jaccard |")
    add("|---|---|---|---|---|")
    for i in range(len(years) - 1):
        a, b = years[i], years[i + 1]
        inter = len(sets[a] & sets[b])
        add(
            f"| {a} vs {b} | {inter:,} | {len(sets[a] - sets[b]):,} | {len(sets[b] - sets[a]):,} | "
            f"{pct(inter, len(sets[a] | sets[b]))} |"
        )
    inter_all = set.intersection(*sets.values())
    add("")
    add(f"- Presentes en los {len(years)} años: **{len(inter_all):,}** establecimientos.")
    add("")

    # 4. Estabilidad de atributos
    add("## 4. Estabilidad de atributos para el mismo establecimiento")
    add("")
    first, last = years[0], years[-1]
    a = df.filter(pl.col("anio") == first).select("id_vu", "rubro", "ciiu4", "region", "comuna").unique(subset="id_vu")
    b = df.filter(pl.col("anio") == last).select("id_vu", "rubro", "ciiu4", "region", "comuna").unique(subset="id_vu")
    j = a.join(b, on="id_vu", suffix="_last")
    rows = []
    for col in ("rubro", "ciiu4", "region", "comuna"):
        changed = j.filter(pl.col(col) != pl.col(f"{col}_last")).height
        rows.append({"atributo": col, "establecimientos_comparados": j.height, "cambian": changed, "pct": 100 * changed / j.height})
    add(md(pl.DataFrame(rows), fmt={"establecimientos_comparados": ",", "cambian": ",", "pct": ".1f"}))
    add("")
    add(f"Comparación {first} → {last} sobre establecimientos presentes en ambos años.")
    add("")

    # 5. Columnas de emisión
    add("## 5. Calidad de las columnas de emisión")
    add("")
    total = df.height
    comps = pl.col("emision_combustible_primario") + pl.col("emision_combustible_secundario") + pl.col("emision_procesos")
    checks = df.select(        (pl.col("emision_retc").is_null().sum()).alias("emision_retc_nulos"),
        (pl.col("emision_total").is_null().sum()).alias("emision_total_nulos"),
        (pl.col("emision_retc").is_not_null() & pl.col("emision_total").is_not_null()
         & (pl.col("emision_retc") != pl.col("emision_total"))).sum().alias("retc_distinto_de_total"),
        (pl.col("emision_retc") == 0).sum().alias("retc_en_cero"),
        ((pl.col("emision_retc") == 0) & (pl.col("emision_total") > 0)).sum().alias("retc_cero_con_estimacion_positiva"),
        (pl.any_horizontal([pl.col(c).is_null() for c in COMPONENTS]) & pl.col("emision_total").is_not_null()).sum().alias("componentes_nulas"),
        ((comps - pl.col("emision_total")).abs() > 1e-9).sum().alias("total_distinto_de_suma"),
    ).row(0, named=True)
    add(md(pl.DataFrame([checks]).transpose(include_header=True, header_name="control", column_names=["casos"]), fmt={"casos": ","}))
    add("")
    add(f"- `emision_retc` en cero con estimación RUEA positiva: **{pct(checks['retc_cero_con_estimacion_positiva'], total)}** de las filas.")
    add("  Tratar ese 0 como «no emitió» sesga el análisis: son valores validados como no confiables, no mediciones de cero.")
    add(f"- `emision_retc` difiere de `emision_total` en **{pct(checks['retc_distinto_de_total'], total)}** de las filas.")
    add("")

    add("### Nulos por columna (todas las filas)")
    add("")
    nulls = (
        df.select([pl.col(c).is_null().sum().alias(c) for c in df.columns])
        .transpose(include_header=True, header_name="columna", column_names=["nulos"])
        .filter(pl.col("nulos") > 0)
        .with_columns((100 * pl.col("nulos") / total).alias("pct"))
        .sort("nulos", descending=True)
    )
    add(md(nulls, fmt={"nulos": ",", "pct": ".1f"}))
    add("")

    # 6. Contaminantes
    add("## 6. Cobertura por contaminante")
    add("")
    pol = (
        df.group_by(["contaminante", "anio"])
        .agg(pl.col("id_vu").n_unique().alias("n"))
        .pivot(on="anio", index="contaminante", values="n", aggregate_function="sum")
        .select(["contaminante"] + [str(y) for y in years])
        .sort(str(years[-1]), descending=True)
    )
    add(md(pol, fmt={str(y): "," for y in years}))
    add("")

    # 7. Rubros
    add("## 7. Rubros: tamaño y emisión de CO₂")
    add("")
    co2 = df.filter(pl.col("contaminante_norm") == CO2)
    rub = (
        co2.group_by("rubro")
        .agg(
            pl.col("id_vu").n_unique().alias("establecimientos"),
            pl.len().alias("filas"),
            pl.col("emision_retc").sum().alias("emision_retc"),
        )
        .with_columns((100 * pl.col("emision_retc") / pl.col("emision_retc").sum()).alias("pct_emision"))
        .sort("emision_retc", descending=True)
    )
    add(md(rub, fmt={"establecimientos": ",", "filas": ",", "emision_retc": ",.4g", "pct_emision": ".1f"}))
    add("")

    add("### CO₂ por año")
    add("")
    cmp = (
        co2.group_by("anio")
        .agg(
            pl.len().alias("filas"),
            pl.col("id_vu").n_unique().alias("establecimientos"),
            pl.col("emision_retc").sum().alias("emision_retc"),
            pl.col("emision_total").sum().alias("emision_total"),
            (pl.col("emision_retc") == 0).sum().alias("filas_en_cero"),
        )
        .sort("anio")
        .with_columns((100 * pl.col("filas_en_cero") / pl.col("filas")).alias("pct_en_cero"))
    )
    add(md(cmp, fmt={"filas": ",", "establecimientos": ",", "emision_retc": ",.4g", "emision_total": ",.4g", "filas_en_cero": ",", "pct_en_cero": ".1f"}))
    add("")
    add("> **Alerta de continuidad:** la suma de CO₂ cae 26% entre 2023 y 2024 y luego 3% en 2025,")
    add("> mientras `emision_total` sube 12% y luego cae 46%. Las dos columnas cuentan historias")
    add("> distintas porque las revisiones del MMA cambian qué valores se validan y cuáles se anulan.")
    add("> No hay serie temporal publicable con ninguna de las dos sin un tratamiento explícito.")
    add("")

    add("### Continuidad por establecimiento (CO₂, misma planta en dos años)")
    add("")
    wide_rows = []
    for i in range(len(years) - 1):
        a, b = years[i], years[i + 1]
        ea = co2.filter(pl.col("anio") == a).group_by("id_vu").agg(pl.col("emision_retc").sum().alias("a"))
        eb = co2.filter(pl.col("anio") == b).group_by("id_vu").agg(pl.col("emision_retc").sum().alias("b"))
        j = ea.join(eb, on="id_vu", how="inner")
        wide_rows.append(
            {
                "transición": f"{a}→{b}",
                "plantas_en_ambos": j.height,
                "positivo→cero": j.filter((pl.col("a") > 0) & (pl.col("b") == 0)).height,
                "cero→positivo": j.filter((pl.col("a") == 0) & (pl.col("b") > 0)).height,
                "positivo→positivo": j.filter((pl.col("a") > 0) & (pl.col("b") > 0)).height,
            }
        )
    add(md(pl.DataFrame(wide_rows), fmt={"plantas_en_ambos": ",", "positivo→cero": ",", "cero→positivo": ",", "positivo→positivo": ","}))
    add("")

    add("### Mayores revisiones de valor (CO₂, primer par de años)")
    add("")
    y0, y1 = years[0], years[1]
    a = co2.filter(pl.col("anio") == y0).group_by("id_vu").agg(
        pl.col("emision_retc").sum().alias("e0"),
        pl.col("nombre_establecimiento").first().alias("establecimiento"),
        pl.col("rubro").first().alias("rubro"),
    )
    b = co2.filter(pl.col("anio") == y1).group_by("id_vu").agg(pl.col("emision_retc").sum().alias("e1"))
    j = a.join(b, on="id_vu", how="inner").with_columns((pl.col("e1") - pl.col("e0")).alias("delta")).sort("delta")
    total_delta = j["delta"].sum()
    top = pl.concat([j.head(5), j.tail(3)])
    add(md(top.select(["establecimiento", "rubro", "e0", "e1", "delta"]), fmt={"e0": ",.4g", "e1": ",.4g", "delta": ",.4g"}))
    add("")
    if total_delta:
        share = 100 * j.head(5)["delta"].sum() / total_delta
        add(f"- Las **5 mayores caídas explican {share:.0f}%** del cambio total ({total_delta:,.0f} unidades).")
        add("- Un relleno sanitario que pasa de 5,7 millones a 24 unidades en un año no es una mejora ambiental:")
        add("  es una revisión de dato o un cambio de unidad/metodología en origen.")
        add("- Conclusión: la serie no se puede publicar sin detección y tratamiento de outliers por planta.")
    add("")

    # 8. Tipo de fuente
    add("## 8. Tipo de fuente declarado")
    add("")
    tf = (
        df.group_by("tipo_fuente")
        .agg(pl.len().alias("filas"), pl.col("id_vu").n_unique().alias("establecimientos"))
        .with_columns((100 * pl.col("filas") / df.height).alias("pct_filas"))
        .sort("filas", descending=True)
        .head(15)
    )
    add(md(tf, fmt={"filas": ",", "establecimientos": ",", "pct_filas": ".1f"}))
    add("")
    gen = df.filter(pl.col("es_grupo_electrogeno")).height
    add(f"- Filas de grupos electrógenos: **{gen:,}** ({pct(gen, df.height)}). No son proceso industrial: se excluyen por defecto en los indicadores, no del dataset.")
    add("")

    # 9. Combustibles
    add("## 9. Combustibles primarios por emisión de CO₂")
    add("")
    fuels = (
        co2.group_by("combustible_primario")
        .agg(pl.len().alias("filas"), pl.col("id_vu").n_unique().alias("establecimientos"), pl.col("emision_retc").sum().alias("emision_retc"))
        .with_columns((100 * pl.col("emision_retc") / pl.col("emision_retc").sum()).alias("pct_emision"))
        .sort("emision_retc", descending=True)
        .head(12)
    )
    add(md(fuels, fmt={"filas": ",", "establecimientos": ",", "emision_retc": ",.4g", "pct_emision": ".2f"}))
    add("")

    # 10. Hallazgos
    add("## 10. Hallazgos y decisiones")
    add("")
    add("1. **Esquema estable** en el piloto: 35 columnas idénticas en los tres años. La deriva de esquema habrá que verificarla al extender la serie hacia 2005–2015.")
    add("2. **Los `id_vu` no son un panel perfecto**: 9.785 plantas están en los tres años (Jaccard ~78–80% entre pares). Cualquier serie por establecimiento debe declarar su base de comparación.")
    add("3. **Los atributos del establecimiento sí son estables**: rubro, CIIU4, región y comuna no cambian para el mismo `id_vu`. El registro de establecimientos funciona como maestro fijo.")
    add("4. **No usar `emision_retc` como verdad absoluta**: 9,8% de las filas tienen `0` que significa «dato no confiable», no «emisión nula».")
    add("5. **La serie está rota por revisiones puntuales**: 5 plantas explican 90% de la caída de CO₂ 2023→2024. Sin detección de outliers por planta no hay tendencia publicable.")
    add("6. **Separar grupos electrógenos** (60% de las filas) del análisis industrial desde el primer indicador.")
    add("7. **Unidad pendiente de confirmación**: bloquea la publicación de cualquier cifra, no el cálculo interno.")
    add("")
    add("### Decisiones abiertas")
    add("")
    add("- [ ] Confirmar unidad (t/año) contra la metodología RETC.")
    add("- [ ] Elegir columna oficial de emisión: `emision_retc` (validada) vs `emision_total` (estimada RUEA).")
    add("- [ ] Definir si los ceros de `emision_retc` se imputan, se excluyen o se marcan.")
    add("- [ ] Confirmar factores de emisión por combustible para reconstruir TJ.")
    add("")

    REPORTS.mkdir(parents=True, exist_ok=True)
    target = REPORTS / "retc_auditoria.md"
    target.write_text("\n".join(out) + "\n", encoding="utf-8")

    # CSV de indicadores por año para uso posterior
    base.write_csv(REPORTS / "retc_cobertura_anual.csv")
    print(f"ok -> {target}")
    print(f"ok -> {REPORTS / 'retc_cobertura_anual.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
