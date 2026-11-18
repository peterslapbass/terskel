"""Genera las páginas del sitio que salen de datos, no de la mano.

- docs/fuentes/descargas.md : fuentes, URL y sha256 desde data/raw/manifest.csv
- docs/datos.md             : inventario de los parquet publicados
- docs/resultados/*.md      : los reportes, con front matter y enlaces al sitio

    $env:PYTHONPATH="src"; python src/reports/sitio.py
"""
from __future__ import annotations

import re
from pathlib import Path

import polars as pl

RAIZ = Path(__file__).resolve().parents[2]
DOCS = RAIZ / "docs"
PROC = RAIZ / "data" / "processed"
REPO = "https://github.com/peterslapbass/terskel"

FUENTES = {
    "retc": "MMA — Registro de Emisiones y Transferencias de Contaminantes",
    "cne": "CNE — Balance Nacional de Energía",
    "enia": "INE — Encuesta Nacional Industrial Anual",
    "ine": "INE — IPP y correspondencias CIIU",
    "bcch": "BCCh — dólar observado",
}

# reportes que se publican como páginas (archivo, título corto, figuras al inicio)
REPORTES = [
    ("indicadores_intensidad", "Indicadores de intensidad",
     [("captura", "Cobertura de energía por industria y captura del RETC, 2024")]),
    ("escenarios_2030", "Escenarios 2030",
     [("escenarios-2030", "CO₂ a 2030 en los cuatro escenarios"),
      ("tornado", "Cuánto mueve cada palanca el CO₂ a 2030")]),
    ("retc_anomalias", "Cribado de anomalías del RETC", []),
    ("retc_co2_combustible", "Reparto del CO₂ por origen", []),
    ("retc_energia_implicita", "Energía implícita en el CO₂", []),
    ("retc_auditoria", "Auditoría del RETC", []),
]

ENLACES = [
    (r"\.\./\.\./reports/([\w_]+)\.md", r"../resultados/\1.html"),
    (r"\.\./docs/fuentes/([\w_]+)\.md", r"../fuentes/\1.html"),
]

TITULOS = {archivo: corto for archivo, corto, _ in REPORTES}

PIES = {
    "captura": "En negrita, las cuatro categorías con dato publicable en 2024. "
               "Los umbrales punteados son 10% y 50% de cobertura.",
    "escenarios-2030": "Misma base 2024 para las cinco barras: lo que cambia es la "
                       "palanca, no el punto de partida.",
    "tornado": "Amplitud = diferencia entre el extremo alto y el bajo de cada palanca, "
               "con las demás en su valor central.",
}


def es(x, dec: int = 0) -> str:
    """Número en formato chileno: 1.234,5"""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def front_matter(titulo: str, **extra) -> str:
    lineas = ["---", f"title: {titulo}"]
    for k, v in extra.items():
        lineas.append(f"{k}: {v}")
    lineas.append("---")
    return "\n".join(lineas) + "\n\n"


def escribe(destino: Path, texto: str) -> None:
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)
    print(f"-> {destino.relative_to(RAIZ)}")


def arregla_enlaces(texto: str) -> str:
    for patron, reemplazo in ENLACES:
        texto = re.sub(patron, reemplazo, texto)
    # menciones sueltas al archivo del reporte, en prosa
    texto = re.sub(
        r"`reports/([\w_]+)\.md`",
        lambda m: f"[{TITULOS.get(m.group(1), m.group(1))}]({m.group(1)}.html)",
        texto,
    )
    return texto


def titulo_de(texto: str) -> str:
    m = re.search(r"^#\s+(.+)$", texto, re.MULTILINE)
    return m.group(1).strip() if m else "Reporte"


# ------------------------------------------------------------------ descargas
def descargas() -> None:
    m = pl.read_csv(RAIZ / "data" / "raw" / "manifest.csv", infer_schema_length=0)
    filas = []
    for r in m.sort(["source", "dataset", "year"]).iter_rows(named=True):
        mb = int(r["size_bytes"]) / 1e6 if r["size_bytes"] else 0
        filas.append(
            f"| {FUENTES.get(r['source'], r['source'])} | {r['resource_name'] or r['dataset']} "
            f"| {r['year']} | {r['format']} | {es(mb, 1)} MB | "
            f"[descargar]({r['url']}) | `{r['sha256'][:16]}…` | {r['license']} |"
        )

    cuerpo = "\n".join([
        front_matter("Fuentes y descargas"),
        "# Fuentes y descargas\n",
        "Cada archivo que entra al proyecto queda aquí con su URL, su tamaño y su "
        "sha256. La tabla se genera desde `data/raw/manifest.csv`; si una fila no "
        "está, el dato no se usó.\n",
        "| Fuente | Archivo | Año | Formato | Tamaño | Descarga | sha256 | Licencia |",
        "|---|---|---:|---|---:|---|---|---|",
        *filas,
        "\nLos XLSX del RETC pesan ~60 MB cada uno y **no** se publican en el repo: "
        "se descargan del portal del MMA con la URL de arriba y se verifica el "
        "sha256. Los parquet derivados sí están en el repo, con las fuentes citadas "
        "en cada ficha.\n",
        "## Cómo se verifica\n",
        "```bash\npython src/ingest/retc.py --years 2023 2024 2025\n```\n",
        "La ingesta compara el sha256 del archivo descargado con el del manifest y "
        "falla si no coincide.\n",
    ])
    destino = DOCS / "fuentes" / "descargas.md"
    escribe(destino, cuerpo)


# ---------------------------------------------------------------------- datos
def datos() -> None:
    archivos = sorted(PROC.rglob("*.parquet"))
    filas = []
    for f in archivos:
        lf = pl.scan_parquet(f)
        n = lf.select(pl.len()).collect().item()
        cols = lf.collect_schema().names()
        mb = f.stat().st_size / 1e6
        muestra = ", ".join(f"`{c}`" for c in cols[:8])
        if len(cols) > 8:
            muestra += f", … (+{len(cols) - 8})"
        rel = f.relative_to(RAIZ).as_posix()
        filas.append(f"| [`{rel}`]({REPO}/blob/main/{rel}) | {es(n)} | {len(cols)} | "
                     f"{es(mb, 2)} MB | {muestra} |")

    cuerpo = "\n".join([
        front_matter("Datos publicados"),
        "# Datos publicados\n",
        "Los parquet del repo, tal como salen de la cadena. Cada uno se regenera con "
        "los comandos de la [metodología](../metodologia.html); ninguno se edita a "
        "mano.\n",
        "| Archivo | Filas | Columnas | Tamaño | Columnas principales |",
        "|---|---:|---:|---:|---|",
        *filas,
        "\nCada parquet conserva las columnas declaradas de la fuente y agrega las "
        "derivadas con nombre explícito (`emision_retc`, `co2_fosil`, "
        "`factor_ajuste`, `cobertura_energetica`). Ninguna columna derivada "
        "reemplaza a la original.\n",
    ])
    destino = DOCS / "datos.md"
    escribe(destino, cuerpo)


# ----------------------------------------------------------------- resultados
def resultados() -> None:
    (DOCS / "resultados").mkdir(parents=True, exist_ok=True)
    for archivo, corto, figuras in REPORTES:
        origen = RAIZ / "reports" / f"{archivo}.md"
        if not origen.exists():
            print(f"   falta {origen.name}, se omite")
            continue
        texto = arregla_enlaces(origen.read_text(encoding="utf-8"))
        titulo = titulo_de(texto)
        imagenes = ""
        for fig, alt in figuras:
            imagenes += (f"\n![{alt}]({{{{ '/assets/fig/{fig}.svg' | relative_url }}}})"
                         f"{{: .figura }}\n")
            if fig in PIES:
                imagenes += f"\n*{PIES[fig]}*\n"
        if imagenes:
            # después del primer encabezado
            texto = re.sub(r"^(#\s+.+)$", lambda m: m.group(1) + "\n" + imagenes,
                           texto, count=1, flags=re.MULTILINE)
        cuerpo = front_matter(corto) + texto
        destino = DOCS / "resultados" / f"{archivo}.md"
        escribe(destino, cuerpo)


if __name__ == "__main__":
    descargas()
    datos()
    resultados()
