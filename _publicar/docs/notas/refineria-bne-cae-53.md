---
title: El ítem Refinería del balance cae 53% entre ediciones
date: 2026-11-13
---

# El ítem Refinería del balance cae 53% entre ediciones

### Qué observamos

El Balance Nacional de Energía asigna al ítem **Refinería y Extracción Petróleo y Gas Natural** **49.193 TJ en 2023** y **22.981 TJ en 2024**. Menos de la mitad, en un año, sin que la capacidad de refino del país cambie en esa proporción.

Al mismo tiempo, el CO₂ declarado por el mismo bloque (divisiones CIIU 06 y 19 del RETC) se mantiene: **0,89 Mt en 2023** y **0,93 Mt en 2024**.

### Qué significa

Si se divide CO₂ por energía, la intensidad del refino se duplica de 2023 a 2024. El numerador se movió 4%; el denominador, **53%**. Es un corte de definición del balance —probablemente un cambio en cómo se imputa el consumo propio del sector energético—, no una mejora de proceso.

### Qué creemos (hipótesis)

Es un corte de definición del balance —probablemente un cambio en cómo se imputa el consumo propio del sector energético—, no una mejora de proceso. Esta explicación es una hipótesis: **confirmar con la CNE la nota metodológica del cambio**. Mientras no esté, cualquier serie de intensidad del refino hecha con dos ediciones del balance mezcla señal y definición —el mismo problema que el GLP de 2023, pero del lado de la energía.

### Qué falta para confirmarlo

Confirmar la nota metodológica del cambio con la CNE. Mientras no esté, cualquier serie de intensidad del refino hecha con dos ediciones del balance mezcla señal y definición —el mismo problema que el GLP de 2023, pero del lado de la energía.

### Cómo se reproduce

`python src/indicators/intensidad.py`; el denominador sale de `data/processed/cne/bne/bne_balance.parquet`, ítem **Refinería y Extracción Petróleo y Gas Natural**.