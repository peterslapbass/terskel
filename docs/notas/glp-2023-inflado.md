---
title: El GLP de 2023 está inflado 12×
date: 2026-11-17
---

# El GLP de 2023 está inflado 12×

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
