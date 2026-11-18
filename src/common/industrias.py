"""Industrias identificables en las tres fuentes (RETC, BNE, ENIA).

La granularidad máxima no la fija el RETC —que trae CIIU a 4 dígitos para todo el
país— sino el BNE: su tabla de equivalencia `BNE-CIIU 4` define 13 categorías
industriales. Fuera de ellas quedan comercio, servicios, transporte, construcción
y sector público, que el balance no separa como demanda industrial.

Siete son manufactureras (divisiones 10–32) y seis primarias o extractivas.

El orden de las reglas importa: las clases y grupos específicos se evalúan antes
que su división, porque Cemento (2394) vive dentro de la 23 y Cobre (0729) dentro
de la 07-08.
"""
from __future__ import annotations

import polars as pl

MANUFACTURA = [
    "Papel y Celulosa", "Petroquímica", "Cemento", "Azúcar",
    "Industria Láctea", "Siderurgia", "Industrias Varias",
]

EXTRACTIVAS = [
    "Cobre", "Hierro", "Minas Varias", "Pesca", "Salitre", "Agroindustria",
]

ENERGIA = ["Refinería y Extracción Petróleo y Gas Natural"]

INDUSTRIAS = MANUFACTURA + ENERGIA + EXTRACTIVAS

# El BNE separa «Producción de Metanol» de «Petroquímica»; el RETC no puede: ambas
# plantas son CIIU 2011. Se suman para comparar contra un denominador único.
BNE_ALIAS = {"Producción de Metanol": "Petroquímica"}


def _codigo(col: str) -> pl.Expr:
    return (pl.col(col).cast(pl.String)
            .str.replace(r"^[A-Za-z]", "")
            .str.strip_chars()
            .str.replace_all(r"\.0$", ""))


def industria_expr(col: str) -> pl.Expr:
    """Categoría industrial BNE a partir del código CIIU4 (clase, grupo o división)."""
    x = _codigo(col)
    return (
        pl.when(x.str.starts_with("2394")).then(pl.lit("Cemento"))
        .when(x.str.starts_with("1072")).then(pl.lit("Azúcar"))
        .when(x.str.starts_with("1050")).then(pl.lit("Industria Láctea"))
        .when(x.str.starts_with("0891")).then(pl.lit("Salitre"))
        .when(x.str.starts_with("0729")).then(pl.lit("Cobre"))
        .when(x.str.starts_with("071")).then(pl.lit("Hierro"))
        .when(x.str.starts_with("241")).then(pl.lit("Siderurgia"))
        .when(x.str.starts_with("17")).then(pl.lit("Papel y Celulosa"))
        .when(x.str.starts_with("20")).then(pl.lit("Petroquímica"))
        .when(x.str.slice(0, 2).is_in(["06", "19"]))
        .then(pl.lit("Refinería y Extracción Petróleo y Gas Natural"))
        .when(x.str.starts_with("03")).then(pl.lit("Pesca"))
        .when(x.str.slice(0, 2).is_in(["07", "08"])).then(pl.lit("Minas Varias"))
        .when(x.str.slice(0, 2).is_in(["01", "02"])).then(pl.lit("Agroindustria"))
        .when(x.str.slice(0, 2).cast(pl.Int32, strict=False).is_between(10, 32))
        .then(pl.lit("Industrias Varias"))
        .otherwise(pl.lit(None, dtype=pl.String))
    )


# Motivo de no publicar, por industria. Solo las que quedan fuera.
MOTIVOS: dict[str, str] = {
    "Cemento": "VBP de la ENIA cubre 4 plantas: solo intensidad física",
    "Azúcar": "una sola planta explica 99,96% del CO₂ fósil: es un caso, no una industria",
    "Pesca": "cobertura de energía implícita 24%: el RETC no captura todo el combustible de la flota",
    "Agroindustria": "cobertura 1%: la ENIA no cubre las divisiones 01-02, no hay contraparte",
    "Cobre": "el RETC captura ~0,2 tCO₂/TJ de los 206.000 TJ del BNE: falta casi toda la combustión",
    "Salitre": "cobertura de energía implícita 4% del BNE",
    "Siderurgia": "Huachipato no declara el carbón ni el coque; el RETC captura ~8% de la energía",
    "Petroquímica": "con metanol incluido el BNE asigna 8.947 TJ: el RETC declara 3× esa energía",
    "Refinería y Extracción Petróleo y Gas Natural": "solo 2024: el ítem del BNE cae 53% entre ediciones (49.193 → 22.981 TJ)",
    "Industrias Varias": "cajón residual de 7 divisiones: no es una industria",
    "Hierro": "cobertura 14% y una planta explica 99% del CO₂ fósil",
    "Minas Varias": "cobertura 11% y una planta explica 78% del CO₂ fósil",
}

# Publicables: física y económica se deciden por separado.
PUBLICABLE_FISICA = {"Papel y Celulosa", "Cemento", "Industria Láctea",
                     "Refinería y Extracción Petróleo y Gas Natural"}
PUBLICABLE_ECONOMICA = {"Papel y Celulosa", "Industria Láctea"}
