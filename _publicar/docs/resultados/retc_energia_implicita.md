---
title: Energía implícita en el CO₂
---

# Energía implícita en el CO₂ del RETC (2024)

Se invierte la ecuación de la guía: `TJ = CO₂ / (EF_carbono × 44/12 / 1000)`, con
los factores de la Tabla 4-3 (MMA 2021). Es una reconstrucción, no una medición:
hereda el error del CO₂ y del factor. El CO₂ de entrada pasa por el cribado de
ediciones (`src/common/calidad.py`): el exceso planta-año se capa antes de invertir.

## Contraste con el BNE (7 ramas manufactureras)

| Grupo BNE | TJ implícito RETC | TJ sin planta dominante | TJ BNE 7 ramas | Cobertura | Cobertura sin dominante |
|---|---:|---:|---:|---:|---:|
| Petróleo Diesel | 15,464 | 15,454 | 141,941 | 11% | 11% |
| Gas Natural | 30,571 | 30,571 | 63,038 | 48% | 48% |
| Biomasa | 44,522 | 42,446 | 51,023 | 87% | 83% |
| Licor Negro | 127,882 | 115,889 | 22,818 | 560% | 508% |
| Gas Licuado | 20,221 | 6,204 | 17,911 | 113% | 35% |
| Petróleo Combustible | 4,374 | 4,069 | 15,980 | 27% | 25% |
| Coque de Petróleo | 3,587 | 3,587 | 8,134 | 44% | 44% |
| Carbón | 1,880 | 795 | 3,648 | 52% | 22% |
| Gas Coque | 213 | 0 | 1,540 | 14% | 0% |
| Gas de Altos Hornos | 128 | 0 | 216 | 59% | 0% |
| Biogás | 10 | 10 | 76 | 13% | 13% |
| Kerosene | 0 | 0 | 60 | 1% | 1% |
| Gas de Refinería | 8,685 | 8,685 | 6 | 141576% | 141576% |
| Gasolina de Motor | 0 | 0 | 0 | — | — |

**Total**: 257,536 TJ implícitos contra 525,326 TJ del BNE
(49% de cobertura).

Cierran dentro de ±30%: **Biomasa, Gas Licuado**.

Sin cobertura en el RETC (el BNE los registra, el RETC no los declara como
combustible): Electricidad, D.I. de Petróleo, Nafta, Kerosene de Aviación, Pellet de Biomasa, Coque Mineral, Gasolina de Aviación.

## Por combustible

| Combustible RETC | tCO₂/TJ | TJ implícito |
|---|---:|---:|
| LICOR NEGRO | 102.3 | 127,882 |
| BIOMASA COMBUSTIBLE | 102.3 | 42,498 |
| GAS NATURAL | 56.1 | 30,419 |
| PETROLEO N 2 (DIESEL) | 74.1 | 15,362 |
| PROPANO | 63.1 | 14,189 |
| GAS DE REFINERIA | 57.6 | 8,685 |
| GAS LICUADO DE PETROLEO | 63.1 | 6,033 |
| PETROLEO N 6 | 77.4 | 4,209 |
| COKE DE PETROLEO (PETCOKE) | 97.5 | 2,047 |
| CARBON BITUMINOSO | 97.5 | 1,880 |

## Combustibles sin factor

| Combustible | CO₂ (t) |
|---|---:|
| ACEITE USADO | 123 |

## Cómo leer esto

- La cobertura **no debería ser 100%**: el RETC solo registra fuentes sobre umbral
  y admite dos combustibles por fuente.
- Si un combustible cierra cerca del 100%, las dos fuentes son consistentes y el
  factor es plausible.
- Si está muy por debajo, el registro no ve esa quema (diésel disperso, grupos
  electrógenos).
- Si está muy por encima, la CNE ubica esa energía en otra parte del balance:
  el licor negro se consume en autoproducción y aparece como `Consumo Final` en
  transformación, no en la demanda del sector.

## Límites

- El factor de biomasa de la guía es genérico; el licor negro tiene uno propio
  (~26 kg C/GJ), así que su TJ implícito puede estar sobrestimado.
- El reparto fósil/biomasa del RETC es proporcional a lo declarado.
- Un error de unidad en una planta se propaga entero a su combustible.
