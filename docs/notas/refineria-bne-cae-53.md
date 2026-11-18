---
title: El ítem Refinería del balance cae 53% entre ediciones
date: 2026-11-13
---

# El ítem Refinería del balance cae 53% entre ediciones

<div class="tech-only">
<p><strong>Qué encontramos.</strong> El Balance Nacional de Energía asigna al ítem <code>Refinería y Extracción Petróleo y Gas Natural</code> <strong>49.193 TJ en 2023</strong> y <strong>22.981 TJ en 2024</strong>. Menos de la mitad, en un año, sin que la capacidad de refino del país cambie en esa proporción.</p>

<p>Al mismo tiempo, el CO₂ declarado por el mismo bloque (divisiones CIIU 06 y 19 del RETC) se mantiene: 0,89 Mt en 2023 y 0,93 Mt en 2024.</p>

<p><strong>Qué significa.</strong> Si se divide CO₂ por energía, la intensidad del refino se duplica de 2023 a 2024. El numerador se movió 4%; el denominador, 53%. Es un corte de definición del balance —probablemente un cambio en cómo se imputa el consumo propio del sector energético—, no una mejora de proceso.</p>

<p><strong>Qué hicimos.</strong> Refinería entra como categoría propia (no estaba en la primera versión del análisis) porque su cobertura de energía en 2024 es buena: 66% de la energía que el balance le asigna aparece implícita en el CO₂ declarado. Eso la hace publicable como intensidad física en 2024.</p>

<p>Pero la serie no se publica: solo 2024. El sitio no muestra una variación que es del denominador.</p>

<p><strong>Qué queda.</strong> Confirmar la nota metodológica del cambio con la CNE. Mientras no esté, cualquier serie de intensidad del refino hecha con dos ediciones del balance mezcla señal y definición —el mismo problema que el GLP de 2023, pero del lado de la energía.</p>

<p><strong>Cómo se reproduce.</strong> <code>python src/indicators/intensidad.py</code>; el denominador sale de <code>data/processed/cne/bne/bne_balance.parquet</code>, ítem <code>Refinería y Extracción Petróleo y Gas Natural</code>.</p>
</div>

<div class="plain-only">
<h3>¿Por qué el refino parece duplicar su intensidad en un año?</h3>

<p>En palabras simples: <strong>no es que la refinería haya cambiado, es que el denominador cambió</strong>.</p>

<p><strong>¿Qué pasó?</strong> El Balance Nacional de Energía le asigna a la refinería 49.193 TJ de energía en 2023 y solo 22.981 TJ en 2024. Eso es menos de la mitad en un año, sin que la capacidad de refino del país haya cambiado. Mientras tanto, el CO₂ que la refinería declara se mantuvo prácticamente igual (0,89 Mt vs 0,93 Mt).</p>

<p><strong>¿Qué significa esto?</strong> Si divides CO₂ entre energía, la intensidad del refino parece duplicarse de 2023 a 2024. Pero eso no es porque la refinería haya empeorado: es porque el denominador (energía) se redujo un 53% por un cambio en cómo el balance contabiliza el consumo propio del sector energético. Es un cambio de reglas, no un cambio real.</p>

<p><strong>¿Qué hicimos?</strong> Incluimos la refinería como categoría porque en 2024 tiene buena cobertura de datos (66% de la energía que el balance le asigna aparece en el CO₂ declarado). Pero no publicamos una serie histórica: solo 2024. Mostrar una variación de un año a otro sería mezclar señal real con un cambio en cómo se contabiliza.</p>

<p><strong>¿Qué queda por hacer?</strong> Confirmar con la CNE por qué cambió la contabilidad de la refinería entre 2023 y 2024. Mientras no se aclare, cualquier comparación de intensidad del refino entre ediciones mezcla lo que realmente pasó con un cambio en las reglas de conteo.</p>
</div>