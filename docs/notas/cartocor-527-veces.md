---
title: El registro validó un valor 527 veces mayor
date: 2026-11-16
---

# El registro validó un valor 527 veces mayor

<div class="tech-only">
<p><strong>Qué encontramos.</strong> La planta de Cartocor en Pilar declaró, en la edición 2024 del RETC, <strong>3.049.178 t de CO₂</strong>. En 2023 había declarado 5.791 t y en 2025 declaró 5.719 t. El factor entre el valor de 2024 y su propia serie es <strong>527</strong>.</p>

<p>No es un cambio de proceso: una planta que produce cartón corrugado no multiplica por 527 su combustión y vuelve al nivel anterior al año siguiente.</p>

<p><strong>Lo que hace distinto este caso.</strong> El registro publica la emisión por combustible primario, por secundario, por procesos, el total, y —aparte— <code>emision_retc</code>, la columna validada. Es esa última la que trae los 3,05 Mt como buenos: el valor pasó el control del propio registro y llegó a la capa que todo el mundo usa. Por eso el cribado por serie no es un lujo: es la única forma de ver el error sin salir de la fuente.</p>

<p>Y pesa: el exceso de Cartocor son 3,04 Mt sobre los 3,74 Mt de exceso de toda la edición 2024, el <strong>81%</strong>.</p>

<p><strong>Qué hicimos.</strong> El cribado por planta-año lo compara con las otras dos ediciones y capa el exceso a la mediana, que en este caso es su propio valor de 2023–2025. Cartocor 2024 queda en 5,8 kt; el declarado sigue visible en <code>emision_retc_declarada</code>.</p>

<p>Además de la corrección, el caso obliga a reportar la concentración: en Papel, una sola planta explica el 59% del CO₂ fósil de la industria en 2024. Por eso cada indicador se publica con su sensibilidad «sin la planta dominante».</p>

<p><strong>Qué queda.</strong> El efecto sobre la industria del papel es grande, y conviene verlo como lo que es: dos indicadores distintos. Contando todo el CO₂ —incluida la biomasa, que en esta rama es el 90%— la intensidad es <strong>166 tCO₂/TJ de energía total</strong>; contando solo el CO₂ fósil, <strong>38,3 tCO₂/TJ fósil</strong>. El primero mide carga biogénica; el segundo, combustión. Se publican por separado, con su etiqueta.</p>

<p><strong>Cómo se reproduce.</strong> <code>python src/audit/retc_anomalias.py</code> y luego <code>python src/indicators/intensidad.py</code>.</p>
</div>

<div class="plain-only">
<h3>¿Por qué una planta declaró 527 veces más CO₂?</h3>

<p>En palabras simples: <strong>una planta declaró un valor absurdo y el registro lo aceptó</strong>.</p>

<p><strong>¿Qué pasó?</strong> La planta Cartocor en Pilar declaró 3.049.178 toneladas de CO₂ en 2024. Pero en 2023 había declarado 5.791 t y en 2025 declaró 5.719 t. Es decir, el valor de 2024 es 527 veces mayor que lo que esa planta declara normalmente. Eso es imposible: una planta de cartón corrugado no multiplica por 527 su combustión en un año y vuelve al nivel anterior al siguiente.</p>

<p><strong>¿Por qué pasó?</strong> El registro tiene una columna llamada <code>emision_retc</code> que es la versión "validada" de los datos. Ese valor de Cartocor pasó el control de calidad del registro y llegó a la capa de datos que todo el mundo usa. Por eso el cribado por serie no es opcional: es la única forma de detectar el error sin salir de la fuente misma.</p>

<p><strong>¿Qué hicimos?</strong> Comparamos cada planta con sus valores de las otras dos ediciones y limitamos el exceso al valor medio. Para Cartocor en 2024, eso significa que el valor queda en 5,8 kt (su valor normal), aunque el declarado siga visible en <code>emision_retc_declarada</code>.</p>

<p><strong>¿Qué significa esto?</strong> Una sola planta explica el 81% del exceso total de la edición 2024. Y en la industria del papel, una sola planta explica el 59% del CO₂ fósil de toda la industria. Por eso cada indicador se publica con una nota que dice "sin la planta dominante", para que se pueda ver cuánto cambia el resultado si se excluye ese valor atípico.</p>

<p><strong>En resumen:</strong> Cartocor declaró 3 millones de toneladas de CO₂ en 2024, pero normalmente declara unas 5.800. Ese valor imposible pasó los controles del registro y afecta todas las estadísticas si no se corrige.</p>
</div>