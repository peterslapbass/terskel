---
title: "Ficha de fuente — ENIA (microdatos por establecimiento)"
---

# Ficha de fuente — ENIA (microdatos por establecimiento)

<div class="tech-only">
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
</div>

<div class="plain-only">
<h3>¿Qué es la Encuesta Nacional Industrial Anual?</h3>
<p>En palabras simples: es una encuesta que el Instituto Nacional de Estadísticas (INE) realiza cada año a las fábricas y plantas manufactureras de Chile con 10 o más trabajadores. El objetivo es conocer cómo está la industria chilena: cuánto producen, cuánto ganan, cuánto gastan y cuántas personas trabajan ahí.</p>

<p><strong>¿Por qué nos importa?</strong> Porque es la fuente principal de datos sobre la producción industrial en Chile. Con ella podemos medir el consumo de energía, los ingresos y los gastos de las fábricas, lo cual es esencial para calcular la intensidad energética y de emisiones.</p>

<p><strong>¿A quiénes cubre?</strong> A unas 3.000 fábricas manufactureras en las 16 regiones del país. No incluye las microempresas (menos de 10 trabajadores) ni la minería a gran escala (que tiene otras encuestas).</p>

<p><strong>¿Qué información tenemos?</strong> Para cada fábrica sabemos: su razón social, qué tipo de industria es (según el sistema CIIU), cuántos trabajadores tiene, cuánto factura (ingresos), cuánto gastan en materiales y energía, cuánto pagan de sueldos y cuánto tienen de activos. Todo esto en pesos chilenos y también en dólares para las empresas extranjeras.</p>

<p><strong>Los números clave:</strong> En 2024, las 3.132 fábricas encuestadas reportaron un valor total de producción de aproximadamente 84.215 millones de pesos chilenos. La remuneración promedio por trabajador fue de 2.355 mil pesos al mes.</p>

<p><strong>¿Cómo se usan los datos?</strong> En este proyecto, los datos de ENIA nos dicen cuánta energía usa cada fábrica. Luego comparamos con el registro de emisiones (RETC) para ver si hay coherencia. Si una fábrica usa mucha energía pero declara pocas emisiones, puede que esté faltando información o usando combustibles que no se reportan.</p>

<p><strong>¿Qué cosas hay que tener en cuenta?</strong> La encuesta no cubre las empresas más pequeñas, algunos rubros (como servicios manufactureros) tienen menos cobertura y algunas empresas declaran en dólares, lo que requiere conversión al tipo de cambio actual.</p>
</div>