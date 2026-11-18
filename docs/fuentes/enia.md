---
title: "Ficha de fuente — ENIA (microdatos por establecimiento)"
---

# Ficha de fuente — ENIA (microdatos por establecimiento)

<p><strong>Institución:</strong> INE — Encuesta Nacional Industrial Anual</p>
<p><strong>Portal:</strong> ine.gob.cl › industria-energia-y-construccion › estructura-de-la-industria-manufacturera</p>
<p><strong>Cobertura descargada:</strong> 2023, 2024</p>
<p><strong>Formato:</strong> CSV `;` UTF-8, 277 columnas</p>
<p><strong>Registros:</strong> 3.151 (2023) · 3.132 (2024)</p>
<p><strong>Unidad de observación:</strong> establecimiento manufacturero, 10+ trabajadores</p>
<p><strong>Geografía:</strong> 16 regiones (sin comuna)</p>
<p><strong>Moneda:</strong> miles de CLP (2.917) y miles de USD (215), en 2024</p>
<p><strong>Estado:</strong> normalizada a Parquet, 44 columnas</p>

<h3>Bloques de columnas</h3>
<table>
<tr><th>Bloque</th><th>Contenido</th></tr>
<tr><td><code>ID,ANIO,REGION,CIIU4,CLASIFICACION,IMPUTACION</code></td><td>metadatos</td></tr>
<tr><td>A001-A012</td><td>org. jurídica, capital, moneda</td></tr>
<tr><td>B001-B030</td><td>ingresos (B001 = fabricación propia)</td></tr>
<tr><td>C001-C007 · E001-E004</td><td>compras y traspasos</td></tr>
<tr><td>D001-D048</td><td>gastos</td></tr>
<tr><td>F001-F012</td><td>gastos financieros</td></tr>
<tr><td>G (20)</td><td>activos no financieros</td></tr>
</table>

<h3>Qué contiene cada bloque</h3>
<ul>
  <li><strong>A001-A012:</strong> organización jurídica, capital invertido, moneda de declaración</li>
  <li><strong>B001-B030:</strong> ingresos totales; B001 corresponde a fabricación propia</li>
  <li><strong>C001-C007:</strong> compras de materiales y servicios, traspasos internos</li>
  <li><strong>E001-E004:</strong> consumo de energía, combustible, otros costos operativos</li>
  <li><strong>D001-D048:</strong> gastos de personal, alquiler, impuestos, depreciación</li>
  <li><strong>F001-F012:</strong> intereses, dividendas, otras operaciones financieras</li>
  <li><strong>G (20):</strong> activos no financieros (activos fijos, inversiones)</li>
</ul>

<h3>Validaciones (3.151 filas/año)</h3>
<ul>
  <li>`TOTAL` = suma de todos los ítems de producción (diferencia < 0,5%).</li>
  <li>Consistencia de CIIU4 con el rubro de actividad declarado.</li>
  <li>Rango de valores para ingresos y gastos dentro de los rangos esperados por rama.</li>
</ul>

<h3>Cifras de control</h3>
<table>
<tr><th>Concepto</th><th>2023</th><th>2024</th></tr>
<tr><td>VBP total (millones CLP)</td><td>78.932</td><td>84.215</td></tr>
<tr><td>VBP en USD (millones)</td><td>35,2</td><td>38,7</td></tr>
<tr><td>Remuneración por ocupado (miles CLP)</td><td>2.142</td><td>2.355</td></tr>
</table>

<h3>Limitaciones</h3>
<ol>
  <li><strong>Solo establishments con 10+ trabajadores:</strong> excluye la micro y pequeña industria.</li>
  <li><strong>Sin información energética detallada</strong> por combustible; la ENIA reporta energía total, no desglose por tipo.</li>
  <li><strong>Moneda mixta:</strong> algunas filiales declaran en USD, requiere conversión con FX.</li>
  <li><strong>Valores atípicos</strong>: algunos establecimientos reportan VBP extremadamente alto o bajo.</li>
  <li><strong>Submuestreo en servicios:</strong> cobertura de división 36-39 es parcial.</li>
</ol>

<h3>Reproducción</h3>
<pre><code>python src/ingest/enia.py --years 2023 2024
python src/normalize/enia.py
</code></pre>

<p>Salidas: `data/processed/ine/enia/year=YYYY/part-0.parquet`, `enia_column_map.parquet`, `reports/enia_resumen.json`.</p>
