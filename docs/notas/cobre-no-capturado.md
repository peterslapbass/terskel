---
title: El registro no captura la gran minería del cobre
date: 2026-11-15
---

# El registro no captura la gran minería del cobre

<div class="tech-only">
<p><strong>Qué encontramos.</strong> El Cobre es el ítem industrial más grande del Balance Nacional de Energía: <strong>205.998 TJ</strong> en 2024, el 39% de toda la energía de las 14 categorías industriales. El RETC le imputa <strong>42 kt de CO₂</strong>.</p>

<p>La mitad de esa energía es electricidad (102.348 TJ), que no genera emisiones directas en la mina: se contabilizan en la central que la produce. La otra mitad —103.650 TJ— sí es combustible quemado en el sitio, sobre todo diésel (94.969 TJ).</p>

<p><strong>La cuenta.</strong> Con los factores de la guía del RETC (74,1 tCO₂/TJ para el diésel, 56,1 para el gas natural, 77,4 para el petróleo combustible), esos 103.650 TJ fósiles implican <strong>7,58 Mt de CO₂</strong>. El registro declara 0,042 Mt: <strong>182 veces menos</strong>.</p>

<img src="{{ '/assets/fig/cobre.svg' | relative_url }}" alt="CO₂ del Cobre: lo que implica la energía del balance y lo que declara el registro" style="max-width: 100%; height: auto;">

<p><strong>Qué significa.</strong> La gran minería no declara su combustión al registro: declara electricidad y poco más. No es que el RETC esté mal calculado; es que <strong>no es un inventario industrial</strong>, es un registro de establecimientos sobre ciertos umbrales, y lo que sus fuentes no declaran no aparece.</p>

<p><strong>Qué hicimos.</strong> Publicamos las 14 industrias con su cobertura de energía —energía implícita en el CO₂ declarado sobre energía del balance— y una columna <code>captura_retc</code> que la resume en cuatro estados: sí, parcial, no, excede. Cobre queda en «no», con 0,3% de cobertura (0,6% si se compara solo contra la energía fósil).</p>

<p>Los 7,58 Mt <strong>no entran en ninguna tabla</strong>: son una estimación con dos supuestos —que la energía del balance se quema completa y con el factor de su combustible— y se publican solo acá, para dimensionar el hueco. Un dato declarado y una estimación no se mezclan.</p>

<p><strong>Por qué importa.</strong> Cualquier inventario que use el RETC para hablar de emisiones industriales subestima el sector minero en dos órdenes de magnitud. Es la limitación más grande de la fuente, no un problema de agregación.</p>

<p><strong>Qué queda.</strong> Cerrar el hueco requiere la declaración de las faenas, no un factor. El balance dice cuánta energía hay; no dice cuánto de ella se reportó. Mientras no haya declaración, la cifra del RETC para Cobre mide cobertura, no emisiones.</p>

<p><strong>Cómo se reproduce.</strong> <code>python src/indicators/intensidad.py</code> (columna <code>cobertura_energetica</code>) y <code>python src/reports/graficos.py</code> para la figura.</p>
</div>

<div class="plain-only">
<h3>¿Por qué el cobre no aparece en el registro de emisiones?</h3>

<p>En palabras simples: <strong>la gran minería del cobre no declara todo lo que quema</strong>. El registro de emisiones (RETC) le atribuye apenas 42 kilotoneladas de CO₂, cuando la energía que usa implica mucho más.</p>

<p><strong>La cuenta no cuadra:</strong> El cobre usa 205.998 TJ de energía al año, casi el 40% de toda la energía industrial del país. La mitad es electricidad (que no genera emisiones en la mina, sino en la central eléctrica). La otra mitad —103.650 TJ— es combustible quemado en el sitio, principalmente diésel.</p>

<p>Si calculamos cuánto CO₂ debería producir quemar ese diésel y otros combustibles, el resultado es 7,58 Mt de CO₂ al año. Pero el registro declara solo 0,042 Mt: <strong>182 veces menos</strong>.</p>

<p><strong>¿Por qué pasa esto?</strong> El RETC no es un inventario completo de todas las emisiones industriales. Es un registro de establecimientos que cumplen ciertos umbrales de declaración. La gran minería declara electricidad y poco más, pero no declara toda la combustión de diésel que quema en sus faenas.</p>

<p><strong>¿Qué hicimos?</strong> Publicamos las 14 industrias con su cobertura de energía —cuánto del CO₂ declarado corresponde a la energía que usan—. El cobre queda marcado como «no capturado»: solo cubre el 0,3% de su energía con el CO₂ declarado. Los 7,58 Mt restantes no los pusimos en ninguna tabla porque son una estimación, no un dato declarado oficialmente.</p>

<p><strong>¿Por qué importa?</strong> Si alguien usa el RETC para hablar de emisiones industriales en Chile, estará subestimando al sector minero de forma masiva. Es la limitación más grande de esta fuente de datos.</p>

<p>En resumen: <strong>el cobre quema mucho diésel en sus faenas, pero el registro apenas captura una fracción mínima.</strong> Los datos oficiales subestiman enormemente las emisiones de la minería.</p>
</div>