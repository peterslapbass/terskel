---
title: El registro validó un valor 527 veces mayor
date: 2026-11-16
---

# El registro validó un valor 527 veces mayor

### Qué observamos

La planta de Cartocor en Pilar declaró, en la edición 2024 del RETC, **3.049.178 t de CO₂**. En 2023 había declarado 5.791 t y en 2025 declaró 5.719 t. El factor entre el valor de 2024 y su propia serie es **527**.

Es muy poco probable que sea un cambio de proceso: **una planta que produce cartón corrugado no multiplica por 527 su combustión y vuelve al nivel anterior al año siguiente**.

### Lo que hace distinto este caso

El registro publica la emisión por combustible primario, por secundario, por procesos, el total, y —aparte— **emision_retc**, la columna validada. Es esa última la que trae los 3,05 Mt como buenos: **el valor pasó el control de calidad del registro y llegó a la capa de datos publicada**. Por eso el cribado por serie no es un lujo: **es una forma de ver la anomalía sin salir de la fuente**.

**Pesa: el exceso de Cartocor son 3,04 Mt sobre los 3,74 Mt de exceso de toda la edición 2024, el 81%**.

### Qué creemos (hipótesis)

El cribado por planta-año lo compara con las otras dos ediciones y capa el exceso a la mediana, que en este caso es su propio valor de 2023–2025. **Cartocor 2024 queda en 5,8 kt**; el declarado sigue visible en emision_retc_declarada.

Además de la corrección, el caso obliga a reportar la concentración: en Papel, **una sola planta explica el 59% del CO₂ fósil de la industria en 2024**. Por eso cada indicador se publica con su sensibilidad **"sin la planta dominante"**.

### Qué falta para confirmarlo

**Sensibilidad del umbral: probar el de 5× y el de 20×. Si la conclusión cambia mucho, eso debe decirse en la nota.**

### Cómo se reproduce

`python src/audit/retc_anomalias.py` y luego `python src/indicators/intensidad.py`.