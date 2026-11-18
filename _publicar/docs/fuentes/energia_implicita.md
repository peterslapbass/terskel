---
title: "Ficha — Energía implícita en el CO₂ del RETC"
---

# Ficha — Energía implícita en el CO₂ del RETC

| Campo | Valor |
|---|---|
| Objetivo | reconstruir TJ quemados a partir del CO₂ y contrastarlos con el BNE |
| Factores | Tabla 4-3 de la *Guía metodológica* (MMA/Greenlab 2021) |
| Cobertura | 2024 · 7 ramas manufactureras (CIIU 10–33) |
| Salida | `data/processed/retc/energia_implicita.parquet` · `reports/retc_energia_implicita.md` |
| Estado | reconstrucción; cierra en 3 de 12 combustibles |

Esta ficha contrasta **solo las 7 ramas manufactureras**: es la prueba de que el CO₂
declarado corresponde a un consumo de combustible razonable. La capa de indicadores
usa el mismo cálculo por industria para medir cobertura en las 13 categorías del
balance ([ficha de indicadores](indicadores.html)).

## Fórmula

La guía calcula el CO₂ de combustión así:

```
CO₂ (t) = TJ × EF_carbono (kg C/GJ) × (44/12) / 1000
```

Despejando, la energía implícita:

```
TJ = CO₂ / (EF_carbono × 3,6667)      [t CO₂/TJ = EF × 44/12]
```

Se aplica al CO₂ ya separado por origen ([ficha del RETC](retc.html)): `co2_fosil` para los
combustibles fósiles y `co2_biomasa` para los biogénicos.

## Factores usados (kg C/GJ)

| Combustible | EF | tCO₂/TJ |
|---|---:|---:|
| Gas natural | 15,3 | 56,1 |
| GLP / propano | 17,2 | 63,1 |
| Diésel | 20,2 | 74,1 |
| Petróleo combustible 6 | 21,1 | 77,4 |
| Coque de petróleo | 26,6 | 97,5 |
| Carbón | 26,6 | 97,5 |
| Biomasa / licor negro | 27,9 | 102,3 |
| Gas de coque | 29,2 | 107,1 |
| Gas de alto horno | 70,8 | 259,6 |

Fuente: `data/reference/factores_emision_combustible.csv` (32 combustibles).

## Resultado 2024 (7 ramas)

| Combustible | TJ implícito | TJ BNE | Cobertura |
|---|---:|---:|---:|
| Biomasa | 44.632 | 50.717 | **88%** |
| Petróleo diésel | 15.465 | 20.077 | **77%** |
| Carbón | 1.880 | 2.611 | **72%** |
| Gas natural | 30.571 | 42.094 | **73%** |
| Gas licuado | 20.221 | 13.909 | 145% |
| Licor negro | 127.882 | 22.818 | 560% |
| Petróleo combustible | 4.374 | 11.991 | 36% |
| Coque de petróleo | 3.587 | 8.123 | 44% |

El detalle por planta dominante (columna "sin dominante") está en
`reports/retc_energia_implicita.md`.

## Lectura

- **Cierran**: biomasa, diésel y carbón. Que tres combustibles independientes
  cierren a ±30% valida a la vez el reparto por origen, los factores y la
  comparación BNE↔CIIU.
- **Gas natural**: con Cartocor capada cierra en 73%. El 204% que daba el dato
  crudo era íntegramente ese error de unidad: la misma anomalía que destaparon los
  indicadores, confirmada por una vía independiente. Por eso este contraste es
  también la verificación de que la unidad del RETC es t/año (un factor 10³ daría
  razones de 10³, no de 0,7).
- **Gas licuado**: 145% en 2024 —el BNE registra menos GLP del que implica el CO₂—
  y 12× en 2023, donde el problema está en el factor de emisión de la edición.
- **Licor negro**: el BNE registra 22.818 TJ y el CO₂ implica 127.882. Chile
  produce ~5 Mt de celulosa al año, lo que exige del orden de 120.000–150.000 TJ
  de licor negro: el número del RETC es el plausible y el del BNE está incompleto.
- **Petróleo combustible y coque de petróleo quedan bajos** porque el RETC admite
  solo dos combustibles por fuente y muchos equipos declaran uno.
- **Electricidad (62.220 TJ)** no es un combustible: no tiene CO₂ directo en el
  RETC y queda fuera de la comparación.

## Limitaciones

1. **Es una reconstrucción, no una medición**: hereda el error del CO₂ y del
   factor. Un factor por defecto correcto no corrige un CO₂ mal declarado.
2. **Factor genérico de biomasa**: el licor negro tiene factor propio (~26 kg C/GJ);
   se usa 27,9 y se declara.
3. **Dos combustibles por fuente**: la mezcla real está subrepresentada.
4. **Cobertura estructural**: el RETC solo registra fuentes sobre umbral, así que
   la cobertura bajo 100% no es un error por sí misma.
5. **No reemplaza al BNE**: el BNE sigue siendo la fuente de energía de los
   indicadores; esta reconstrucción es un control independiente.

## Reproducción

```bash
python src/normalize/retc_co2_combustible.py
python src/normalize/retc_energia_implicita.py --year 2024
```
