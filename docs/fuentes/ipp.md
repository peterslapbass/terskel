---
title: "Ficha de fuente — IPP Industria Manufacturera (INE)"
---

# Ficha de fuente — IPP Industria Manufacturera (INE)

<div class="tech-only">
<p><strong>Institución:</strong> INE</p>
<p><strong>Producto:</strong> Índice de Precios de Productor (IPP), Industria Manufacturera</p>
<p><strong>Portal:</strong> ine.gob.cl › precios-e-inflacion › indice-de-precios-de-productor</p>
<p><strong>Base:</strong> 2019 = 100</p>
<p><strong>Frecuencia:</strong> mensual, por división CIIU Rev.4</p>
<p><strong>Cobertura:</strong> 2023-09 → 2026-09 (base 2019) · 2017-01 → 2023-08 (base 2014)</p>
<p><strong>Estado:</strong> normalizada a Parquet, promedio anual</p>

<h3>Qué mide</h3>
<p>Precios de venta del productor industrial, no costos ni precios al consumidor. Sirve para <strong>deflactar</strong> valores nominales de la ENIA (VBP, VA) y expresarlos en pesos de 2019.</p>

<h3>Divisiones publicadas (15)</h3>
<p>10, 11, 12, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 28, 31. No se publican 13, 14, 15, 26, 29, 30, 32, 33 (secreto estadístico o cobertura insuficiente): para esas se usa el total de manufactura.</p>

<h3>Cómo se usa en el proyecto</h3>
<ul>
  <li>Se toma el promedio mensual de cada división para obtener el valor anual.</li>
  <li>Se aplica como factor de deflactor al VBP nominal de ENIA para obtener VBP en pesos constantes 2019.</li>
  <li>Fórmula: <code>VBP_real = VBP_nominal / (IPP/100)</code></li>
</ul>

<h3>Validaciones</h3>
<ul>
  <li>IPP 2024 promedio = 115,3 (base 2019=100), lo que indica un aumento del 15,3% en precios desde 2019.</li>
  <li>Coherencia interanual: variación año-año consistente con la inflación industrial.</li>
</ul>

<h3>Limitaciones</h3>
<ol>
  <li><strong>Secretismo estadístico:</strong> muchas divisiones no tienen información pública detallada.</li>
  <li><strong>Base 2019:</strong> no es adecuado para comparar con años lejanos sin ajuste.</li>
  <li><strong>Solo divisiones CIIU:</strong> no hay información a nivel de rama (4 dígitos) para todas las categorías.</li>
  <li><strong>No incluye servicios no manufactureros:</strong> divisiones 36-39 no están cubiertas.</li>
</ol>

<h3>Reproducción</h3>
<pre><code>python src/ingest/ipp.py --years 2023 2024
python src/normalize/ipp.py
</code></pre>

<p>Salidas: `data/processed/ine/ipp/year=YYYY/part-0.parquet`, `ipp_anual.parquet`, `reports/ipp_resumen.json`.</p>
</div>

<div class="plain-only">
<h3>¿Qué es el Índice de Precios de Productor?</h3>
<p>En palabras simples: es un índice que mide cómo cambian los precios de lo que fabrican las fábricas chilenas. Publicado por el INE, te dice si los precios de la industria están subiendo o bajando mes a mes.</p>

<p><strong>¿Por qué nos importa?</strong> En este proyecto, el IPP nos sirve como "deflactor": toma los valores de producción que reportan las fábricas en pesos corrientes (con inflación) y los ajusta a precios de 2019. Esto permite comparar la producción real a lo largo de los años, sin que la inflación confunda las cifras.</p>

<p><strong>¿Cómo funciona?</strong> El INE publica este índice cada mes para 15 divisiones de la industria (como comida, textiles, metalmecánica, etc.). El valor base es 100 para el año 2019. Si el índice está en 115, significa que los precios de la industria en promedio son un 15% más altos que en 2019.</p>

<p><strong>Los números:</strong> En 2024, el índice promedio para la industria manufacturera estaba en 115,3 (base 2019 = 100). Esto significa que, en promedio, los precios de lo que fabrican las fábricas chilenas son un 15,3% más altos que hace 5 años.</p>

<p><strong>¿Cómo se usa en este proyecto?</strong> Cuando miramos los datos de la ENIA (la encuesta a las fábricas), los valores de ventas están en pesos de cada año (con inflación). Para comparar entre años o calcular verdaderas variaciones de producción, aplicamos el IPP para "quitar" el efecto de la inflación y dejar los valores en precios de 2019.</p>

<p><strong>Cosita importante:</strong> Solo cubre las 15 divisiones manufactureras que el INE publica. Algunas divisiones más específicas no tienen datos públicos detallados, así que para esas usamos el total de manufactura.</p>
</div>