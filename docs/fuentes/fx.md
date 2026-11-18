---
title: "Ficha de fuente — Tipo de cambio (dólar observado, BCCh)"
---

# Ficha de fuente — Tipo de cambio (dólar observado, BCCh)

<p><strong>Institución:</strong> Banco Central de Chile</p>
<p><strong>Serie:</strong> F073.TCO.PRE.Z.D — dólar observado, diario</p>
<p><strong>Portal:</strong> si3.bcentral.cl › CAP_TIPO_CAMBIO › DOLAR_OBS_ADO</p>
<p><strong>Cobertura:</strong> 1982-08-09 a la fecha de extracción</p>
<p><strong>Unidad:</strong> CLP/USD</p>
<p><strong>Licencia:</strong> uso libre citando fuente</p>
<p><strong>Extracción:</strong> 2026-11-11</p>

<h3>Por qué está en el proyecto</h3>
<p>La ENIA trae establecimientos que contabilizan en <strong>miles de USD</strong> (<code>moneda_codigo = 5</code>): 215 de 3.132 en 2024, con el <strong>45,8% del VBP</strong> equivalente. Sin tipo de cambio la industria se subestima casi a la mitad.</p>

<h3>Rutas de obtención</h3>
<table>
<tr><th>Ruta</th><th>Credenciales</th><th>Qué trae</th></tr>
<tr><td>bde-export (defecto)</td><td>no</td><td>XLSX con la serie completa desde 1982</td></tr>
<tr><td>bde</td><td>BCCH_USER / BCCH_PASS</td><td>JSON por año (SieteRestWS)</td></tr>
<tr><td>mindicador</td><td>no</td><td>espejo del mismo dólar (respaldo; limita la tasa)</td></tr>
</table>

<h3>Método</h3>
<p><strong>Promedio simple de los días publicados</strong>, la convención del propio BCCh (nota metodológica del archivo exportado).</p>

<table>
<tr><th>Año</th><th>FX promedio</th><th>Mediana</th><th>Mín</th><th>Máx</th><th>Días</th></tr>
<tr><td>2023</td><td>839,07</td><td>821,59</td><td>781,49</td><td>945,61</td><td>247</td></tr>
<tr><td>2024</td><td>943,58</td><td>943,92</td><td>877,12</td><td>996,35</td><td>248</td></tr>
<tr><td>2025</td><td>951,64</td><td>948,67</td><td>904,54</td><td>1012,76</td><td>248</td></tr>
</table>

<p><strong>Control cruzado con la ENIA</strong></p>
<p>Remuneración mediana por ocupado (<code>I081</code>/<code>I080</code>): 2.355 en <code>moneda_codigo = 4</code> y 2,6 en <code>5</code> → razón <strong>906</strong> vs FX 943,58 (2024). Diferencia de unidad, no de productividad.</p>

<h3>Salidas</h3>
<ul>
  <li><code>data/raw/bcch/dolar_observado/serie_completa/dolar_observado_bde_YYYY-MM-DD.xlsx</code></li>
  <li><code>data/processed/bcch/dolar_diario.parquet</code></li>
  <li><code>data/processed/bcch/fx_anual.parquet</code> (<code>par = USD/CLP</code>, <code>moneda_origen</code>, <code>moneda_destino</code>, ISO 4217)</li>
</ul>

<h3>Limitaciones</h3>
<ol>
  <li>La exportación es <strong>rodante</strong>: el sha256 cambia a diario; el nombre lleva la fecha del snapshot y el manifest acumula versiones.</li>
  <li>El BCCh <strong>revisa</strong> la serie: citar siempre la fecha de extracción.</li>
  <li>2026 está incompleto; su promedio anual no es definitivo.</li>
</ol>

<h3>Reproducción</h3>
<pre><code>python src/ingest/fx.py && python src/normalize/fx.py
</code></pre>
