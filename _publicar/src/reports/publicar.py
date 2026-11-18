"""Arma la carpeta que se sube al repositorio público.

    $env:PYTHONPATH="src"; python src/reports/publicar.py

Deja todo en `_publicar/`, con la estructura exacta del repo: la raíz con README,
LICENSE y requirements, y `docs/` como fuente de GitHub Pages. Nunca copia
`data/raw` salvo el manifiesto.
"""
from __future__ import annotations

import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "_publicar"

IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", ".ipynb_checkpoints")


def copia(origen: Path, destino: Path) -> None:
    if not origen.exists():
        print(f"   falta {origen.relative_to(RAIZ)}")
        return
    if origen.is_dir():
        shutil.copytree(origen, destino, ignore=IGNORAR, dirs_exist_ok=True)
    else:
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino)


def borra(carpeta: Path) -> None:
    """rmtree tolerante a read-only y a locks de OneDrive."""
    import os
    import stat

    def onerror(func, ruta, _exc):
        os.chmod(ruta, stat.S_IWRITE)
        func(ruta)

    shutil.rmtree(carpeta, onerror=onerror)


def main() -> None:
    if DESTINO.exists():
        borra(DESTINO)
    DESTINO.mkdir()

    copia(RAIZ / "docs", DESTINO / "docs")
    copia(RAIZ / "src", DESTINO / "src")
    copia(RAIZ / "data" / "processed", DESTINO / "data" / "processed")
    copia(RAIZ / "data" / "raw" / "manifest.csv", DESTINO / "data" / "raw" / "manifest.csv")
    copia(RAIZ / "data" / "reference", DESTINO / "data" / "reference")
    # la carpeta de publicacion no se publica
    sobra = DESTINO / "data" / "reference" / "publicacion"
    if sobra.exists():
        borra(sobra)
    copia(RAIZ / "requirements.txt", DESTINO / "requirements.txt")

    for f in sorted((RAIZ / "reports").glob("*.md")):
        copia(f, DESTINO / "reports" / f.name)

    base = RAIZ / "data" / "reference" / "publicacion"
    copia(base / "README.md", DESTINO / "README.md")
    copia(base / "LICENSE", DESTINO / "LICENSE")

    archivos = [f for f in DESTINO.rglob("*") if f.is_file()]
    mb = sum(f.stat().st_size for f in archivos) / 1e6
    print(f"\n{len(archivos)} archivos, {mb:.1f} MB en _publicar/")
    grandes = sorted(archivos, key=lambda f: -f.stat().st_size)[:3]
    for f in grandes:
        print(f"   {f.stat().st_size / 1e6:5.1f} MB  {f.relative_to(DESTINO).as_posix()}")


if __name__ == "__main__":
    main()
