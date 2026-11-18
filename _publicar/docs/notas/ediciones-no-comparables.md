---
title: Las ediciones del RETC no son comparables
date: 2026-11-16
---

# Las ediciones del RETC no son comparables

### Qué observamos

El CO₂ nacional validado del RETC cae de 65,4 Mt (2023) a 48,7 Mt (2024) y 47,0 Mt (2025). Una caída de 18,4 Mt en un año no tiene una explicación industrial evidente; es más coherente con un problema del archivo.

Cada edición trae un defecto distinto y medible:

| Edición | CO₂ declarado | Exceso (respecto a la mediana) | CO₂ ajustado |
|---|---|---|---|
| 2023 | 65,4 Mt | 17,0 Mt (26%) | 48,4 Mt |
| 2024 | 48,7 Mt | 3,7 Mt (7,7%) | 45,0 Mt |
| 2025 | 47,0 Mt | 0,1 Mt (0,4%) | 46,9 Mt |

2023: el bloque GLP muestra un exceso 12×. 2024: una planta, Cartocor, con un valor 527× su declaración previa. 2025: 141 déficits contra 7 excesos, la mitad de ellos consumidores de gas natural —compatible con una edición aún abierta.

<img src="/terskel/assets/fig/ediciones.svg" alt="CO₂ declarado y ajustado por edición" style="max-width: 100%; height: auto;">

### Qué creemos (hipótesis)

Una regla única, en `src/common/calidad.py`: para cada planta-año, si el valor supera 10 veces la mediana de las otras dos ediciones (y la materialidad es al menos 1.000 t), se capa a esa mediana. Nunca se sube un valor, solo se baja un exceso. Un déficit no se toca: puede ser una edición sin cerrar, y rellenarlo sería inventar.

El factor multiplica todas las columnas de emisión de la fila, así que se conserva el reparto por origen (fósil, biomasa, proceso) y el reparto por combustible.

### Qué falta para confirmarlo

Factor de emisión por edición del RETC y consumo de GLP del BNE para 2023 y 2024. Con esos datos se podría decidir si la hipótesis del factor incorrecto se confirma o descarta.

### Qué queda

278 planta-año marcadas. El ajuste no convierte las ediciones en comparables: evita que el defecto se lea como señal. La serie 2023–2024 sirve como contraste, no como tendencia; el nivel de referencia es 2024.

### Lo que la regla no ve

Una planta que declara de menos en las tres ediciones —Huachipato, por ejemplo— no se detecta por comparación entre años. Ese hueco se cierra por otra vía: contrastar la energía implícita en el CO₂ contra el balance energético.

### Cómo se reproduce

`python src/audit/retc_anomalias.py`.