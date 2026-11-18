"""Genera los gráficos del sitio (SVG) desde los parquet procesados.

Determinista: sin fechas ni orden aleatorio. Cada figura se escribe en
`docs/assets/fig/` con el mismo nombre que la usa la página.

    $env:PYTHONPATH="src"; python src/reports/graficos.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from common.calidad import aplicar  # noqa: E402
from common.industrias import INDUSTRIAS  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
PROC = RAIZ / "data" / "processed"
FIG = RAIZ / "docs" / "assets" / "fig"

AZUL = "#1f4e79"
VERDE = "#2e7d5b"
AMBAR = "#b7791f"
ROJO = "#9b2c2c"
GRIS = "#6b7280"
VIOLETA = "#5b4b8a"
TINTA = "#1a1a1a"

ESTADO_COLOR = {"sí": VERDE, "parcial": AMBAR, "no": ROJO, "excede": VIOLETA}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 9,
    "axes.edgecolor": "#d1d5db",
    "axes.labelcolor": TINTA,
    "text.color": TINTA,
    "xtick.color": "#4b5563",
    "ytick.color": "#4b5563",
    "svg.fonttype": "none",
    "figure.dpi": 100,
})


def limpia(ax, spines=("top", "right")):
    for s in spines:
        ax.spines[s].set_visible(False)


def guarda(fig, nombre: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / nombre, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"-> docs/assets/fig/{nombre}")


def fmt_pct(x: float) -> str:
    return f"{x * 100:.1f}%".replace(".", ",")


def n_es(x: float, dec: int = 0) -> str:
    """1.234,5 en vez de 1,234.5"""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


# ---------------------------------------------------------------- 1. captura
def fig_captura() -> None:
    d = (pl.read_parquet(PROC / "indicators" / "intensidad_rama.parquet")
         .filter((pl.col("anio") == 2024) & pl.col("rama").is_in(INDUSTRIAS))
         .select("rama", "cobertura_energetica", "captura_retc", "publicable_fisica")
         .sort("cobertura_energetica"))

    nombres = d["rama"].to_list()
    cob = [min(v, 1.0) for v in d["cobertura_energetica"].to_list()]
    estado = d["captura_retc"].to_list()
    real = d["cobertura_energetica"].to_list()

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    barras = ax.barh(nombres, cob, color=[ESTADO_COLOR[e] for e in estado], height=0.72)
    ax.set_xlim(0, 1.02)
    ax.set_xticks([0, 0.1, 0.5, 1.0])
    ax.set_xticklabels(["0", "10%", "50%", "100%"])
    ax.axvline(0.1, color=GRIS, lw=0.7, ls=":", zorder=0)
    ax.axvline(0.5, color=GRIS, lw=0.7, ls=":", zorder=0)
    ax.grid(axis="x", color="#eceef0", lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    limpia(ax, ("top", "right", "left"))
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("energía implícita en el CO₂ declarado / energía del balance")

    for b, v, e in zip(barras, real, estado):
        x = min(v, 0.99)
        etiqueta = fmt_pct(v) if v <= 1 else "249%"
        ax.text(x + 0.012, b.get_y() + b.get_height() / 2, etiqueta,
                va="center", fontsize=8, color=TINTA)

    # las cuatro con dato publicable, en negrita
    for etiqueta, publicable in zip(ax.get_yticklabels(), d["publicable_fisica"].to_list()):
        if publicable:
            etiqueta.set_fontweight("bold")

    ax.legend(handles=[Patch(color=c, label=k) for k, c in ESTADO_COLOR.items()],
              loc="lower right", frameon=False, ncol=4, fontsize=8,
              bbox_to_anchor=(1.0, -0.22))
    guarda(fig, "captura.svg")

# ----------------------------------------------------------- 2. composición
def fig_composicion() -> None:
    from indicators.intensidad import universo_retc

    u = universo_retc(2024).sort("mt", descending=True)
    grupos = u["grupo"].to_list()
    mt = u["mt"].to_list()
    total = sum(mt)
    cortos = ["Industria (14 categorías)", "Generación eléctrica", "Servicios y otros"]
    colores = [AZUL, AMBAR, GRIS]

    fig, ax = plt.subplots(figsize=(7.0, 1.9))
    izq = 0.0
    for v, c, nombre in zip(mt, colores, cortos):
        ax.barh([0], [v], left=izq, color=c, height=0.5)
        pct = v / total
        if pct > 0.1:
            ax.text(izq + v / 2, 0, f"{pct * 100:.0f}%".replace(".", ","),
                    ha="center", va="center", color="white", fontsize=13,
                    fontweight="bold")
        else:
            ax.annotate(f"{pct * 100:.0f}%", (izq + v / 2, 0.32),
                        ha="center", fontsize=9, color=TINTA)
        izq += v

    ax.set_xlim(0, total)
    ax.set_ylim(-0.55, 0.75)
    ax.set_yticks([])
    ax.set_xticks([])
    limpia(ax, ("top", "right", "left", "bottom"))
    ax.legend(handles=[Patch(color=c, label=f"{n} · {n_es(v, 1)} Mt")
                       for c, n, v in zip(colores, cortos, mt)],
              loc="upper left", frameon=False, ncol=3, fontsize=8,
              bbox_to_anchor=(0, -0.05), handlelength=0.9, columnspacing=1.2)
    guarda(fig, "retc-composicion.svg")


# ---------------------------------------------------------------- 3. GLP
def fig_glp() -> None:
    d = pl.read_parquet(PROC / "retc" / "co2_combustible.parquet")
    g = (d.filter(pl.col("combustible_primario_norm").str.to_uppercase().str.contains("LICUADO"))
         .group_by("anio")
         .agg((pl.col("emision_retc").sum() / 1e6).alias("mt"), pl.len().alias("n"))
         .sort("anio"))
    anios = [str(a) for a in g["anio"].to_list()]
    mt = g["mt"].to_list()
    n = g["n"].to_list()

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.9))
    colores = [ROJO, VERDE, VERDE]
    b = a1.bar(anios, mt, color=colores, width=0.55)
    a1.set_title("CO₂ declarado por GLP (Mt)", fontsize=9, loc="left", color=GRIS)
    a1.bar_label(b, labels=[f"{v:.2f}".replace(".", ",") for v in mt], padding=3, fontsize=8)

    b2 = a2.bar(anios, n, color=AZUL, width=0.55)
    a2.set_title("declaraciones con GLP (n)", fontsize=9, loc="left", color=GRIS)
    a2.bar_label(b2, labels=[f"{v:,}".replace(",", ".") for v in n], padding=3, fontsize=8)

    for ax in (a1, a2):
        ax.grid(axis="y", color="#eceef0", lw=0.7)
        ax.set_axisbelow(True)
        limpia(ax)
        ax.tick_params(axis="x", length=0)
        ax.set_yticks([])
    guarda(fig, "glp-2023.svg")


# ------------------------------------------------------------ 4. ediciones
def fig_ediciones() -> None:
    d = pl.read_parquet(PROC / "retc" / "co2_combustible.parquet")
    filas = []
    for y in (2023, 2024, 2025):
        x = d.filter(pl.col("anio") == y)
        filas.append({
            "anio": str(y),
            "declarado": x["emision_retc"].sum() / 1e6,
            "ajustado": x.pipe(aplicar)["emision_retc"].sum() / 1e6,
        })
    t = pl.DataFrame(filas)

    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    x = range(len(t))
    ancho = 0.34
    b1 = ax.bar([i - ancho / 2 for i in x], t["declarado"], ancho,
                color="#c9ced6", label="declarado")
    b2 = ax.bar([i + ancho / 2 for i in x], t["ajustado"], ancho,
                color=AZUL, label="ajustado por cribado")
    ax.set_xticks(list(x))
    ax.set_xticklabels(t["anio"].to_list())
    ax.bar_label(b1, labels=[f"{v:.1f}".replace(".", ",") for v in t["declarado"]],
                 padding=2, fontsize=8, color=GRIS)
    ax.bar_label(b2, labels=[f"{v:.1f}".replace(".", ",") for v in t["ajustado"]],
                 padding=2, fontsize=8, color=AZUL)
    ax.set_ylim(0, 72)
    ax.set_yticks([])
    ax.grid(axis="y", color="#eceef0", lw=0.7)
    ax.set_axisbelow(True)
    limpia(ax)
    ax.tick_params(axis="x", length=0)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_ylabel("Mt CO₂", fontsize=9, color=GRIS)
    guarda(fig, "ediciones.svg")


# ---------------------------------------------------------------- 5. cobre
def fig_cobre() -> None:
    # energía fósil que el balance le asigna al Cobre, convertida a CO₂ con los
    # factores de la guía del RETC (data/reference/factores_emision_combustible.csv)
    f = pl.read_csv(RAIZ / "data" / "reference" / "factores_emision_combustible.csv",
                    separator=";", encoding="utf-8", infer_schema_length=0)
    fac = (f.filter(pl.col("grupo_bne") != "")
            .with_columns(tco2_por_tj=pl.col("ef_carbono_kg_c_gj").cast(pl.Float64) * 44 / 12)
            .group_by("grupo_bne").agg(pl.col("tco2_por_tj").first()))
    mapa = dict(zip(fac["grupo_bne"].to_list(), fac["tco2_por_tj"].to_list()))
    mapa["Kerosene de Aviación"] = mapa["Kerosene"]

    bne = (pl.read_parquet(PROC / "cne" / "bne" / "bne_balance.parquet")
           .filter((pl.col("anio") == 2024)
                   & (pl.col("seccion") == "DEMANDA DE ENERGÍA")
                   & (pl.col("item") == "Cobre")
                   & (pl.col("energetico") != "TOTAL")
                   & (pl.col("energetico") != "Electricidad"))
           .group_by("energetico").agg(pl.col("tj").sum()))
    esperado = sum(r["tj"] * mapa.get(r["energetico"], 0.0)
                   for r in bne.iter_rows(named=True))

    real = float(pl.read_parquet(PROC / "indicators" / "intensidad_rama.parquet")
                 .filter((pl.col("anio") == 2024) & (pl.col("rama") == "Cobre"))
                 ["tco2_fosil"][0])
    fossil_tj = bne["tj"].sum()

    fig, ax = plt.subplots(figsize=(7.0, 1.9))
    etiquetas = ["declarado\npor Cobre", "si se quema lo que\nasigna el balance"]
    valores = [real / 1e6, esperado / 1e6]
    b = ax.barh(etiquetas, valores, color=[ROJO, GRIS], height=0.55)
    ax.set_xscale("log")
    ax.set_xlim(0.02, 30)
    ax.set_xticks([0.01, 0.1, 1, 10])
    ax.set_xticklabels(["0,01", "0,1", "1", "10"])
    ax.set_xlabel("Mt de CO₂ al año (escala logarítmica)")
    ax.bar_label(b, labels=[f"{n_es(v, 2)} Mt" for v in valores],
                 padding=6, fontsize=10)
    ax.grid(axis="x", color="#eceef0", lw=0.7)
    ax.set_axisbelow(True)
    limpia(ax, ("top", "right", "left"))
    ax.tick_params(axis="y", length=0)
    factor = valores[1] / valores[0]
    ax.text(0.0, 1.14, f"{n_es(factor)}× de diferencia sobre {n_es(fossil_tj)} TJ fósiles",
            transform=ax.transAxes, fontsize=9, color=ROJO)
    guarda(fig, "cobre.svg")


# ------------------------------------------------------------ 6. escenarios
def fig_escenarios() -> None:
    d = (pl.read_parquet(PROC / "scenarios" / "escenarios_2030.parquet")
         .filter(pl.col("rama") == "Total 4 ramas"))
    orden = ["observado", "congelado", "eficiencia", "descarbonizacion", "recomposicion"]
    nombres = {"observado": "2024 observado", "congelado": "2030 congelado",
               "eficiencia": "2030 eficiencia", "descarbonizacion": "2030 descarbonización",
               "recomposicion": "2030 recomposición"}
    filas = {r["escenario"]: r["tco2"] / 1e6 for r in d.iter_rows(named=True)}
    vals = [filas[k] for k in orden]
    etiquetas = [nombres[k] for k in orden]
    colores = [GRIS, ROJO, AMBAR, "#3f7d5a", AZUL]

    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    b = ax.barh(etiquetas[::-1], vals[::-1], color=colores[::-1], height=0.6)
    ax.set_xlim(0, 24)
    ax.bar_label(b, labels=[f"{v:.2f} Mt".replace(".", ",") for v in vals[::-1]],
                 padding=4, fontsize=8)
    ax.grid(axis="x", color="#eceef0", lw=0.7)
    ax.set_axisbelow(True)
    limpia(ax, ("top", "right", "left"))
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([0, 5, 10, 15, 20])
    guarda(fig, "escenarios-2030.svg")


# -------------------------------------------------------------- 7. tornado
def fig_tornado() -> None:
    t = (pl.read_parquet(PROC / "scenarios" / "tornado_2030.parquet")
         .sort("amplitud"))
    etiquetas = t["palanca"].to_list()
    vals = [v / 1e6 for v in t["amplitud"].to_list()]

    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    b = ax.barh(etiquetas, vals, color=AZUL, height=0.6)
    ax.bar_label(b, labels=[(f"{n_es(v, 2)} Mt" if v >= 0.1 else f"{n_es(v * 1000, 0)} kt")
                            for v in vals], padding=4, fontsize=8)
    ax.set_xlim(0, max(vals) * 1.28)
    ax.grid(axis="x", color="#eceef0", lw=0.7)
    ax.set_axisbelow(True)
    limpia(ax, ("top", "right", "left"))
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("amplitud del CO₂ a 2030 al mover la palanca entre sus extremos", fontsize=8)
    guarda(fig, "tornado.svg")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(RAIZ / "src"))
    fig_captura()
    fig_composicion()
    fig_glp()
    fig_ediciones()
    fig_cobre()
    fig_escenarios()
    fig_tornado()
