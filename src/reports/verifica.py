"""Revisa que el sitio se pueda publicar: front matter, enlaces y rutas.

Se corre antes de subir; no genera nada.

    $env:PYTHONPATH="src"; python src/reports/verifica.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DOCS = RAIZ / "docs"

errores: list[str] = []
avisos: list[str] = []


def yaml_simple(texto: str) -> dict:
    """Lee el front matter sin PyYAML: clave en la primera columna, valor el resto."""
    datos = {}
    for linea in texto.splitlines():
        if not linea.strip() or linea.startswith("#"):
            continue
        if ":" not in linea:
            continue
        k, v = linea.split(":", 1)
        datos[k.strip()] = v.strip().strip('"').strip("'")
    return datos


def revisa_front_matter() -> None:
    for f in sorted(DOCS.rglob("*.md")):
        texto = io.open(f, encoding="utf-8").read()
        rel = f.relative_to(DOCS).as_posix()
        if not texto.startswith("---\n"):
            errores.append(f"{rel}: sin front matter (Jekyll lo copiaria tal cual)")
            continue
        fin = texto.find("\n---", 4)
        if fin < 0:
            errores.append(f"{rel}: front matter sin cerrar")
            continue
        fm = yaml_simple(texto[4:fin])
        if "title" not in fm:
            errores.append(f"{rel}: front matter sin title")
        for k, v in fm.items():
            if k == "title" and (":" in v and '"' not in texto[4:fin]):
                avisos.append(f"{rel}: titulo con ':' sin comillas")


def revisa_enlaces() -> None:
    conocidas = {p.with_suffix(".html").relative_to(DOCS).as_posix()
                 for p in DOCS.rglob("*.md")}
    for f in sorted(DOCS.rglob("*.md")):
        texto = io.open(f, encoding="utf-8").read()
        rel = f.relative_to(DOCS)
        for destino in re.findall(r"\]\(([^)\s]+)\)", texto):
            if destino.startswith(("http", "#", "mailto:")):
                continue
            if destino.endswith(".md"):
                errores.append(f"{rel}: enlace a .md ({destino})")
                continue
            limpio = destino.split("#")[0]
            if not limpio:
                continue
            if limpio.startswith("/"):
                objetivo = limpio.lstrip("/")
            else:
                objetivo = (rel.parent / limpio).as_posix()
            objetivo = re.sub(r"^\./", "", objetivo)
            # normaliza ../
            partes: list[str] = []
            for trozo in objetivo.split("/"):
                if trozo == "..":
                    if partes:
                        partes.pop()
                elif trozo not in ("", "."):
                    partes.append(trozo)
            objetivo = "/".join(partes)
            if objetivo not in conocidas and not (DOCS / objetivo).exists():
                errores.append(f"{rel}: enlace roto ({destino})")

        # enlaces armados con liquid: {{ '/algo.html' | relative_url }}
        for ruta in re.findall(r"['\"]/([\w./-]+\.(?:html|svg))['\"]", texto):
            if not (DOCS / ruta).exists() and ruta not in conocidas:
                errores.append(f"{rel}: ruta liquid inexistente (/{ruta})")


def revisa_figuras() -> None:
    for f in sorted(DOCS.rglob("*.md")):
        texto = io.open(f, encoding="utf-8").read()
        for fig in re.findall(r"/assets/fig/([\w.-]+\.svg)", texto):
            if not (DOCS / "assets" / "fig" / fig).exists():
                errores.append(f"{f.relative_to(DOCS)}: falta assets/fig/{fig}")


def revisa_liquid() -> None:
    for f in sorted(DOCS.rglob("*.md")) + sorted(DOCS.rglob("*.html")):
        texto = io.open(f, encoding="utf-8").read()
        if texto.count("{%") != texto.count("%}"):
            errores.append(f"{f.relative_to(DOCS)}: tag liquid sin cerrar")
        if texto.count("{{") != texto.count("}}"):
            errores.append(f"{f.relative_to(DOCS)}: variable liquid sin cerrar")


def revisa_rutas() -> None:
    # armado por partes para que este archivo no contenga el literal que busca
    patrones = ("URZ" + "KEN", "C:" + chr(92) + "Users", "C:/Users")
    objetivos = [f for f in DOCS.rglob("*") if f.is_file() and f.suffix in
                 {".md", ".html", ".css", ".yml", ".svg"}]
    objetivos.append(RAIZ / "data" / "raw" / "manifest.csv")
    for f in objetivos:
        texto = io.open(f, encoding="utf-8", errors="replace").read()
        for patron in patrones:
            if patron in texto:
                errores.append(f"{f.relative_to(RAIZ)}: contiene {patron}")


if __name__ == "__main__":
    revisa_front_matter()
    revisa_enlaces()
    revisa_figuras()
    revisa_liquid()
    revisa_rutas()

    for a in avisos:
        print("aviso:", a)
    for e in errores:
        print("ERROR:", e)
    if errores:
        print(f"\n{len(errores)} errores")
        sys.exit(1)
    print(f"ok: sitio consistente ({len(list(DOCS.rglob('*.md')))} páginas)")
