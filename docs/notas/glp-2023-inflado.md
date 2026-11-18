---
title: El GLP de 2023 está inflado 12×
date: 2026-11-17
---

# El GLP de 2023 está inflado 12×

<div class="tech-only">
<p><strong>Qué encontramos.</strong> El CO₂ que el RETC atribuye al gas licuado de petróleo (GLP) se multiplica por doce entre una edición y otra, sin que cambie el número de declaraciones:</p>

<table>
<tr><th>Edición</th><th>CO₂ por GLP</th><th>Declaraciones</th><th>Plantas</th></tr>
<tr><td>2023</td><td>16,15 Mt</td><td>3.130</td><td>1.503</td></tr>
<tr><td>2024</td><td>1,32 Mt</td><td>3.198</td><td>1.536</td></tr>
<tr><td>2025</td><td>1,10 Mt</td><td>3.202</td><td>1.501</td></tr>
</table>

<p>Mismo número de fuentes, mismo número de plantas, doce veces el CO₂. Si fuera un cambio real en el consumo, las declaraciones no serían idénticas en cantidad.</p>

<img src="{{ '/assets/fig/glp-2023.svg' | relative_url }}" alt="CO₂ declarado por GLP y número de declaraciones, 2023–2025" style="max-width: 100%; height: auto;">

<p><strong>Qué lo delata.</strong> 31 de las 85 plantas marcadas como anómalas en 2023 tienen el GLP como combustible dominante, y no comparten sector, tamaño ni región: lo único que comparten es el combustible. Es un factor de emisión de esa edición, no una conducta de las empresas.</p>

<p><strong>Qué hicimos.</strong> No corregimos el factor —no tenemos el de esa edición— ni imputamos un valor externo. Capamos el exceso de cada planta-año a la mediana de las otras dos ediciones, que es un valor que esa misma planta declaró. El parquet conserva el dato original en <code>emision_retc_declarada</code> y el factor aplicado en <code>factor_ajuste</code>.</p>

<p><strong>Qué queda.</strong> 2023 pasa de 65,4 a 48,4 Mt declaradas-ajustadas: 17,0 Mt, el 26% del total de esa edición, es un artefacto. Por eso el año de referencia es 2024 y 2023 se usa solo como contraste. El bloque GLP de 2023 no sirve para comparar nada, y cualquier serie 2022–2025 que lo use sin cribar muestra una caída que no ocurrió.</p>

<p><strong>Cómo se reproduce.</strong> <code>python src/audit/retc_anomalias.py</code>, que escribe <code>data/processed/retc/anomalias.parquet</code> y <code>reports/retc_anomalias.md</code>.</p>
</div>

<div class="plain-only">
<h3>¿Qué pasó con el gas licuado (GLP) en 2023?</h3>

<p>En palabras simples: <strong>el registro de emisiones se equivocó en 2023</strong>. Dijo que las plantas quemaban 12 veces más GLP que en 2024, pero eso no es cierto.</p>

<p><strong>La prueba es clara:</strong> el número de declaraciones y de plantas es casi el mismo en 2023 y 2024 (unos 3.100 declaraciones y 1.500 plantas). Si las empresas realmente hubieran quemado 12 veces más gas, habrían declarado mucho más. Como no lo hicieron, el error está en el registro, no en las empresas.</p>

<p><strong>¿Por qué pasó?</strong> El RETC usa un "factor de emisión" para calcular cuánto CO₂ produce quemar GLP. En 2023, ese factor estaba mal calculado y era 12 veces más alto de lo que debería ser. Como resultado, el CO₂ del GLP se vio inflado artificialmente.</p>

<p><strong>¿Qué hicimos?</strong> No inventamos datos ni corregimos el factor (no tenemos el original). Lo que hicimos fue limitar los valores extremos: para cada planta que declaró un valor desmesurado en 2023, usamos el valor medio que ella misma declaró en 2024 y 2025. Así evitamos que un error del registro se vea como una realidad industrial.</p>

<p><strong>¿Qué significa esto?</strong> Las 17 Mt de CO₂ que parecían haber emitido las plantas por GLP en 2023 no existen realmente. Es un error del archivo. Por eso usamos 2024 como año de referencia y tratamos a 2023 solo como comparación, no como dato confiable.</p>

<p>En resumen: <strong>el GLP de 2023 está "inflado 12×" porque el registro se equivocó, no porque las empresas quemaran más gas.</strong></p>
</div>