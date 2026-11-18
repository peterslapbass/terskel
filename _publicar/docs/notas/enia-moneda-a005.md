---
title: Un código de moneda que valía 900 veces
date: 2026-11-12
---

# Un código de moneda que valía 900 veces

### Qué observamos

La ENIA trae el valor bruto de producción en una columna de moneda codificada (A005): **4 y 5**. El descriptor del INE no la documenta en la base actual. Al cruzar los valores con el tipo de cambio del BCCh, la aritmética la resuelve:

| Código | Interpretación | Razón implícita |
|---|---|---|
| **4** | miles de CLP | ≈ 1 |
| **5** | miles de USD | ≈ 906 |

El tipo de cambio promedio de 2024 fue **943,58 CLP/USD**, así que 906 es consistente con «miles de dólares» y no con otra cosa: un **4% de diferencia**, explicable por mezcla de meses y por el desfase entre el precio y el tipo de cambio.

Sin decodificar, **una fila en dólares se lee como pesos**: el VBP de esa planta queda **900 veces** más chico y su intensidad —CLP por TJ, o tCO₂ por CLP— queda **900 veces** más grande. Como la columna no trae diccionario, el error es silencioso y no afecta a todas las plantas por igual: solo a las que declaran en dólares.

### Qué creemos (hipótesis)

Sin decodificar, el error es silencioso y afecta solo a las plantas que declaran en dólares. La evidencia es aritmética, no documental, y está declarada como inferencia en la ficha de la ENIA. Si el código fuera otro, **todos los indicadores económicos se moverían**; los físicos no.

### Qué falta para confirmarlo

Confirmar el código con el INE. La evidencia es aritmética, no documental, y está declarada como inferencia en la ficha de la ENIA. Si el código fuera diferente, todos los indicadores económicos cambiarían, aunque los físicos (CO₂ y energía) no se ven afectados.

### Cómo se reproduce

`python src/normalize/enia.py` y la ficha ENIA.