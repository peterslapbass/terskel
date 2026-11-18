"""Puente CIIU Rev.4 -> categorías sectoriales del BNE.

Fuente de las reglas: hoja `BNE-CIIU 4` del Balance Nacional de Energía
(columnas `categoria_bne` y `referencia_ciiu4`, ya normalizadas en
`data/processed/cne/bne/ciiu4_map.parquet`).

Las referencias vienen en lenguaje natural ("DIVISIÓN 17", "GRUPO 241",
"CLASE 2394", "DIVISIONES 33,36-39,45-47...") y se traducen a reglas sobre el
código CIIU:

1. **clase** (4 dígitos) tiene prioridad,
2. luego **grupo** (3 dígitos),
3. luego **división** (2 dígitos),
4. si nada calza y la división es manufacturera (10–33), cae en
   `INDUSTRIAS VARIAS`, que es la categoría residual de la CNE.

Los códigos vienen en dos formatos y se homologan aquí:
- ENIA: `1071`, `10` o `C` (sección).
- RETC: `C1391` (letra de sección + clase de 4 dígitos).

Un código de sección sin dígitos no se puede asignar a una rama: queda en
`null` con `rama_regla = "sin_detalle"`.

Uso:
    python src/normalize/ciiu_bne.py            # genera la tabla de equivalencias
"""
from __future__ import annotations

import argparse
import re
import sys

import polars as pl

from common.paths import PROCESSED

RAMA_RESIDUAL = "Industrias Varias"
MANUFACTURA = range(10, 34)

# La hoja de equivalencias tiene solapes: las divisiones 36-39 aparecen tanto en
# SANITARIAS como en COMERCIO Y SERVICIO. Se resuelve con prioridad explícita
# (la categoría más específica gana). Fuera de manufactura, así que no afecta
# los indicadores industriales.
PREFERENCIA = {"SANITARIAS": 0, "COMERCIO Y SERVICIO": 99}


def _tokens(ref: str) -> tuple[set[str], set[str], set[str]]:
    """Extrae (clases, grupos, divisiones) de una referencia en texto libre."""
    ref = ref.upper()
    clases: set[str] = set()
    grupos: set[str] = set()
    divisiones: set[str] = set()

    for a, b in re.findall(r"(\d{1,2})\s*-\s*(\d{1,2})", ref):
        for d in range(int(a), int(b) + 1):
            divisiones.add(f"{d:02d}")

    for n in re.findall(r"\d+", ref):
        if len(n) == 4:
            clases.add(n)
        elif len(n) == 3:
            grupos.add(n)
        elif len(n) <= 2:
            divisiones.add(f"{int(n):02d}")

    if "CLASE" in ref:
        grupos = {g for g in grupos if g not in {c[:3] for c in clases}}
    return clases, grupos, divisiones


def build_rules(mapa: pl.DataFrame) -> list[dict]:
    reglas = []
    for row in mapa.iter_rows(named=True):
        ref = row.get("referencia_ciiu4") or ""
        cat = row.get("item_bne") or row.get("categoria_bne")
        if not ref or not cat:
            continue
        clases, grupos, divisiones = _tokens(ref)
        reglas.append(
            {
                "rama_bne": cat,
                "clases": sorted(clases),
                "grupos": sorted(grupos),
                "divisiones": sorted(divisiones),
                "referencia": ref,
            }
        )
    reglas.sort(key=lambda r: PREFERENCIA.get(r["rama_bne"].upper(), 1))
    return reglas


def normalizar_codigo(code: str | None) -> tuple[str | None, str | None]:
    """Devuelve (seccion, digitos) de un código CIIU en cualquiera de los formatos."""
    if not code:
        return None, None
    code = code.strip().upper()
    seccion = None
    if code and code[0].isalpha():
        seccion = code[0]
        code = code[1:]
    if not code.isdigit():
        return seccion, None
    return seccion, code


def assign(digitos: str | None, reglas: list[dict]) -> tuple[str | None, str]:
    if not digitos:
        return None, "sin_detalle"
    for r in reglas:
        if len(digitos) == 4 and digitos in r["clases"]:
            return r["rama_bne"], "clase"
    for r in reglas:
        if digitos[:3] in r["grupos"]:
            return r["rama_bne"], "grupo"
    for r in reglas:
        if digitos[:2] in r["divisiones"]:
            return r["rama_bne"], "division"
    if len(digitos) >= 2 and int(digitos[:2]) in MANUFACTURA:
        return RAMA_RESIDUAL, "residual"
    return None, "fuera_manufactura"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--quiet", action="store_true")
    p.parse_args(argv)

    mapa = pl.read_parquet(PROCESSED / "cne" / "bne" / "ciiu4_map.parquet")
    reglas = build_rules(mapa)

    enia = pl.read_parquet(PROCESSED / "enia" / "base" / "enia_base.parquet", columns=["ciiu4"])
    retc = pl.read_parquet(
        PROCESSED / "retc" / "emisiones_fp" / "**" / "*.parquet", columns=["ciiu4_id"]
    )

    codigos = (
        pl.concat([
            enia.select(pl.col("ciiu4").alias("codigo")),
            retc.select(pl.col("ciiu4_id").alias("codigo")),
        ])
        .drop_nulls()
        .unique()
        .sort("codigo")
    )

    norm = [normalizar_codigo(c) for c in codigos["codigo"].to_list()]
    asignado = [assign(d, reglas) for _, d in norm]

    out = codigos.with_columns(
        pl.Series("seccion", [n[0] for n in norm], dtype=pl.String),
        pl.Series("digitos", [n[1] for n in norm], dtype=pl.String),
        pl.Series("rama_bne", [a[0] for a in asignado], dtype=pl.String),
        pl.Series("rama_regla", [a[1] for a in asignado], dtype=pl.String),
    )

    dest = PROCESSED / "cne" / "bne" / "ciiu4_rama.parquet"
    out.write_parquet(dest, compression="zstd")

    resumen = out.group_by("rama_bne", "rama_regla").len().sort("len", descending=True)
    print(resumen.to_pandas().to_string(index=False))
    sin = out.filter(pl.col("rama_bne").is_null()).height
    print(f"\n{out.height} códigos CIIU -> {dest}")
    print(f"sin rama: {sin} ({sin / out.height:.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
