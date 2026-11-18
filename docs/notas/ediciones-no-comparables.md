---
title: Las ediciones del RETC no son comparables
date: 2026-11-16
---

# Las ediciones del RETC no son comparables

<div class="tech-only">
<p><strong>Qué encontramos.</strong> El CO₂ nacional validado del RETC cae de 65,4 Mt (2023) a 48,7 Mt (2024) y 47,0 Mt (2025). Una caída de 18,4 Mt en un año no la produce ninguna industria: la produce el archivo.</p>

<p>Cada edición trae un defecto distinto y medible:</p>

<table>
<tr><th>Edición</th><th>CO₂ declarado</th><th>Exceso demostrable</th><th>CO₂ ajustado</th></tr>
<tr><td>2023</td><td>65,4 Mt</td><td>17,0 Mt (26%)</td><td>48,4 Mt</td></tr>
<tr><td>2024</td><td>48,7 Mt</td><td>3,7 Mt (7,7%)</td><td>45,0 Mt</td></tr>
<tr><td>2025</td><td>47,0 Mt</td><td>0,1 Mt (0,4%)</td><td>46,9 Mt</td></tr>
</table>

<p>2023: el bloque GLP inflado 12×. 2024: una planta, Cartocor, con un valor 527 veces su declaración de 2023. 2025: 141 déficits contra 7 excesos, la mitad de ellos consumidores de gas natural —compatible con una edición aún abierta.</p>

<img src="{{ '/assets/fig/ediciones.svg' | relative_url }}" alt="CO₂ declarado y ajustado por edición" style="max-width: 100%; height: auto;">

<p><strong>Qué hicimos.</strong> Una regla única, en <code>src/common/calidad.py</code>: para cada planta-año, si el valor supera <strong>10 veces</strong> la mediana de las otras dos ediciones (y la materialidad es al menos 1.000 t), se capa a esa mediana. Nunca se sube un valor, solo se baja un exceso. Un déficit no se toca: puede ser una edición sin cerrar, y rellenarlo sería inventar.</p>

<p>El factor multiplica todas las columnas de emisión de la fila, así que se conserva el reparto por origen (fósil, biomasa, proceso) y el reparto por combustible.</p>

<p><strong>Qué queda.</strong> 278 planta-año marcadas. El ajuste no convierte las ediciones en comparables: evita que el defecto se lea como señal. La serie 2023–2024 sirve como contraste, no como tendencia; el nivel de referencia es 2024.</p>

<p><strong>Lo que la regla no ve.</strong> Una planta que declara de menos en las tres ediciones —Huachipato, por ejemplo— no se detecta por comparación entre años. Ese hueco se cierra por otra vía: contrastar la energía implícita en el CO₂ contra el balance energético.</p>

<p><strong>Cómo se reproduce.</strong> <code>python src/audit/retc_anomalias.py</code>.</p>
</div>

<div class="plain-only">
<h3>¿Por qué las ediciones del RETC no se pueden comparar?</h3>

<p>En palabras simples: <strong>las tres ediciones del registro (2023, 2024 y 2025) no son comparables entre sí</strong>. Cada una tiene errores distintos, y la caída de emisiones que aparenta no es real.</p>

<p><strong>¿Qué pasó en cada edición?</strong></p>

<ul>
  <li><strong>2023:</strong> El gas licuado (GLP) estaba inflado 12 veces. Eso agregó 17 Mt de CO₂ que no existían realmente.</li>
  <li><strong>2024:</strong> Una sola planta (Cartocor) declaró un valor 527 veces mayor que lo que normalmente declara.</li>
  <li><strong>2025:</strong> La edición parecía tener muchos huecos (141 déficits) porque aún no estaba cerrada completamente.</li>
</ul>

<p><strong>¿Qué hicimos?</strong> Crear una regla única: si una planta declara un valor 10 veces mayor que lo que suele declarar, lo limitamos al valor medio de las otras dos ediciones. Nunca subimos un valor, solo bajamos los excesos. Si una planta declara menos de lo normal, lo dejamos tal cual, porque puede ser que la edición aún no esté completa.</p>

<p><strong>¿Qué significa esto?</strong> No puedes comparar directamente las emisiones de 2023 con las de 2024 o 2025. Los cambios que ves no son reales: son errores del registro. Usamos 2024 como año de referencia porque es el más confiable.</p>

<p><strong>En resumen:</strong> Las emisiones no cayeron de 65,4 a 47 Mt en tres años. Eso es un error del archivo, no una realidad industrial.</p>
</div>