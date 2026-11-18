---
title: "Ficha — Escenarios 2030 (energía y CO₂)"
---

# Ficha — Escenarios 2030 (energía y CO₂)

<p><strong>Base:</strong> 2024 observado, ajustado por el cribado de ediciones · 4 ramas manufactureras</p>
<p><strong>Horizonte:</strong> 2030 (6 años)</p>
<p><strong>Método:</strong> identidad contable con palancas explícitas y <code>g</code> por rama, sin estimación estadística</p>
<p><strong>Parámetros:</strong> <code>data/reference/escenarios_parametros.csv</code> (editable, versionado)</p>
<p><strong>Salida:</strong> <code>data/processed/scenarios/escenarios_2030.parquet</code> · <code>reports/escenarios_2030.md</code></p>
<p><strong>Estado:</strong> calculado; sustituye a una proyección que los datos no permiten</p>

<h3>Motor de cálculo</h3>
<pre><code>energía(t) = energía(2024) × (1+g_rama)^n × (1−mi)^n
CO₂(t)     = Σ origen: fósil × (1+g_rama)^n × (1−mi)^n × (1−mf)^n
             biomasa, proceso y otro × (1+g_rama)^n × (1−mi)^n
</code></pre>

<p><strong>Parámetros clave:</strong></p>
<ul>
  <li><code>g</code>: vector de crecimiento per-calbrado por rama, calibrado para que el crecimiento VBP-pesado sea ~2,0%/año</li>
  <li><code>mi</code>: tasa de mejora de intensidad energética (por rama)</li>
  <li><code>mf</code>: factor de mitigación que actúa <strong>solo sobre CO₂ de combustión fósil</strong></li>
</ul>

<p><strong>Regla de <code>mf</code>:</strong> actúa solo sobre el CO₂ de combustión fósil. La biomasa es biogénica y el CO₂ de proceso depende del clínker, no del combustible: ninguno de los dos baja por cambiar de combustible.</p>

<h3>Ramas manufactureras consideradas</h3>
<p>Papel y Celulosa, Cemento, Siderurgia, Láctea. Las 4 ramas más intensivas en energía y con mejor cobertura de datos.</p>

<h3>Validaciones</h3>
<ul>
  <li>Cumbre de identidad contable: suma de energías y emisiones concuerda con el balance 2024.</li>
  <li>Crecimiento VBP-pesado promedio se mantiene en 2,0%/año en todas las ramas.</li>
</ul>

<h3>Limitaciones</h3>
<ol>
  <li>Proyección basada en identidad contable, no en estimación estadística de la demanda futura.</li>
  <li>Sensible al parámetro <code>g</c>: pequeñas variaciones en el crecimiento cambian los resultados finales.</li>
  <li>No considera cambios estructurales en la industria (cierre de plantas, nuevas tecnologías).</li>
  <li>La biomasa y las emisiones de proceso no se reducen con cambios de combustible.</li>
</ol>

<h3>Reproducción</h3>
<pre><code>python src/generate/escenarios.py --years 2024 2030
</code></pre>

<p>Salidas: `data/processed/scenarios/escenarios_2030.parquet`, `reports/escenarios_2030.md`.</p>
