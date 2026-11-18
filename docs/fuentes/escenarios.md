---
title: "Ficha — Escenarios 2030 (energía y CO₂)"
---

# Ficha — Escenarios 2030 (energía y CO₂)

<div class="tech-only">
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
</div>

<div class="plain-only">
<h3>¿Qué son los escenarios 2030?</h3>
<p>En palabras simples: son proyecciones de cómo será el consumo de energía y las emisiones de CO₂ de las fábricas chilenas en el año 2030, basadas en los datos actuales y en algunas suposiciones claras.</p>

<p><strong>¿Por qué hacemos esto?</strong> Para entender el futuro de la industria energética de Chile. Si continuamos con los mismos patrones actuales, ¿dónde estaríamos en 2030? Estos escenarios nos ayudan a planificar y a ver el efecto de diferentes decisiones.</p>

<p><strong>¿Cómo se construyen?</strong> Usando una "identidad contable": partimos de los datos de 2024 y los proyectamos 6 años al futuro. Consideramos:</p>
<ul>
  <li><strong>Crecimiento:</strong> La industria crece alrededor del 2% anual</li>
  <li><b>Mejora energética:</strong> Las fábricas se hacen más eficientes con el tiempo (usando menos energía por unidad producida)</li>
  <li><b>Mitigación de CO₂:</strong> Algunas fábricas reducen sus emisiones de combustibles fósiles</li>
</ul>

<p><strong>Las 4 ramas consideradas:</strong> Papel y celulosa, cemento, siderurgia (acero) y láctea. Son las industrias más grandes en consumo de energía y más relevantes para las emisiones de CO₂.</p>

<p><strong>Los números clave:</strong> En 2024, estas 4 ramas tienen un consumo energético y niveles de emisión base. Proyectados al 2030 con un crecimiento del 2% anual y mejoras de eficiencia, las emisiones y el consumo seguirán una tendencia calculada matemáticamente.</p>

<p><strong>¿Qué no incluye?</strong> No es una predicción estadística realista de qué ocurrirá en el mercado, sino un ejercicio de "si todo continúa como hoy". No considera cierres de plantas, nuevas tecnologías disruptivas ni cambios en la estructura industrial.</p>

<p><strong>¿Para qué sirven?</strong> Sirven como referencia para decidir políticas públicas. Si los escenarios muestran que las emisiones crecerán mucho, pueden justificarse políticas más estrictas. Si las mejoras de eficiencia son suficientes, quizás solo se necesitan incentivos voluntarios.</p>
</div>