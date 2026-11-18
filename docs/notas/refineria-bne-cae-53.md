---
title: El ítem Refinería del balance cae 53% entre ediciones
date: 2026-11-13
---

# El ítem Refinería del balance cae 53% entre ediciones

<p><strong>Qué encontramos.</strong> El Balance Nacional de Energía asigna al ítem <code>Refinería y Extracción Petróleo y Gas Natural</code> <strong>49.193 TJ en 2023</strong> y <strong>22.981 TJ en 2024</strong>. Menos de la mitad, en un año, sin que la capacidad de refino del país cambie en esa proporción.</p>

<p>Al mismo tiempo, el CO₂ declarado por el mismo bloque (divisiones CIIU 06 y 19 del RETC) se mantiene: 0,89 Mt en 2023 y 0,93 Mt en 2024.</p>

<p><strong>Qué significa.</strong> Si se divide CO₂ por energía, la intensidad del refino se duplica de 2023 a 2024. El numerador se movió 4%; el denominador, 53%. Es un corte de definición del balance —probablemente un cambio en cómo se imputa el consumo propio del sector energético—, no una mejora de proceso.</p>

<p><strong>Qué hicimos.</strong> Refinería entra como categoría propia (no estaba en la primera versión del análisis) porque su cobertura de energía en 2024 es buena: 66% de la energía que el balance le asigna aparece implícita en el CO₂ declarado. Eso la hace publicable como intensidad física en 2024.</p>

<p>Pero la serie no se publica: solo 2024. El sitio no muestra una variación que es del denominador.</p>

<p><strong>Qué queda.</strong> Confirmar la nota metodológica del cambio con la CNE. Mientras no esté, cualquier serie de intensidad del refino hecha con dos ediciones del balance mezcla señal y definición —el mismo problema que el GLP de 2023, pero del lado de la energía.</p>

<p><strong>Cómo se reproduce.</strong> <code>python src/indicators/intensidad.py</code>; el denominador sale de <code>data/processed/cne/bne/bne_balance.parquet</code>, ítem <code>Refinería y Extracción Petróleo y Gas Natural</code>.</p>
