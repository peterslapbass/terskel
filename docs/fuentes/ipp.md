---
title: "Ficha de fuente — IPP Industria Manufacturera (INE)"
---

# Ficha de fuente — IPP Industria Manufacturera (INE)

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
