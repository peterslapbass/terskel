"""Utilidades de normalización de texto (sin dependencias externas)."""
from __future__ import annotations

import polars as pl

_ACCENTS = {
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n",
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ü": "U", "Ñ": "N",
}


def norm_key(col: str) -> pl.Expr:
    """Clave de comparación: mayúsculas, sin tildes, espacios colapsados."""
    expr = pl.col(col).cast(pl.String, strict=False)
    for src, dst in _ACCENTS.items():
        expr = expr.str.replace_all(src, dst, literal=True)
    return (
        expr.str.to_uppercase()
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
    )
