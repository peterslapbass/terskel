---
title: "Ficha de fuente — BNE (Balance Nacional de Energía, CNE)"
---

# Ficha de fuente — BNE (Balance Nacional de Energía, CNE)

<p><strong>Institución:</strong> CNE / Ministerio de Energía</p>
<p><strong>Portal:</strong> https://energiaabierta.cl/categorias-estadistica/balance-energetico</p>
<p><strong>Cobertura descargada:</strong> 2023, 2024</p>
<p><strong>Formato:</strong> XLSX, 37 hojas</p>
<p><strong>Unidad:</strong> Tcal en la hoja `Balance de energía`; 1 Tcal = 4,1868 TJ</p>
<p><strong>Estado:</strong> normalizada a Parquet</p>

<h3>Qué contiene</h3>
<p>Hoja `Balance de energía` = matriz: 53 ítems en 3 secciones (`OFERTA`, `C.TRANSFORMAC`, `DEMANDA DE ENERGÍA`) × 29 energéticos + `TOTAL`.</p>
<p>Bajo `DEMANDA DE ENERGÍA` está `Sector Industrial y Minero`, con 14 ramas: Cobre, Salitre, Hierro, Papel y Celulosa, Siderurgia, Petroquímica, Cemento, Azúcar, Pesca, Agroindustria, Construcción, Industria Láctea, Industrias Varias y Minas Varias.</p>

<h3>Puente BNE-CIIU 4</h3>
<table>
<tr><th>Categoría BNE</th><th>CIIU Rev.4</th></tr>
<tr><td>Papel y Celulosa</td><td>división 17</td></tr>
<tr><td>Cemento</td><td>clase 2394</td></tr>
<tr><td>Azúcar</td><td>clase 1072</td></tr>
<tr><td>Siderurgia</td><td>grupo 241</td></tr>
<tr><td>Petroquímica</td><td>división 20</td></tr>
<tr><td>Industria Láctea</td><td>clase 1050</td></tr>
<tr><td>Industrias Varias</td><td>divisiones 1, 2, 10–16, 18, 21–32 (resto)</td></tr>
</table>

<p>Ese puente conecta energía (BNE), emisiones (RETC) y actividad (ENIA), todos CIIU4. Los rótulos cambian entre ediciones (`SIDERÚRGIA`/`SIDERÚRGICA`); el Parquet agrega `categoria_norm` (sin tildes) e `item_bne`: 22 categorías, 21 con ítem asignado.</p>

<h3>Validaciones (1.590 filas/año)</h3>
<ul>
  <li>`TOTAL` = suma de los 29 energéticos en los 53 ítems (diferencia 0).</li>
  <li>`Sector Industrial y Minero` = suma de sus 14 ramas (diferencia relativa 0).</li>
</ul>

<h3>Cifras de control</h3>
<table>
<tr><th>Concepto</th><th>2023</th><th>2024</th></tr>
<tr><td>Consumo final total (Tcal)</td><td>327.090</td><td>329.250</td></tr>
<tr><td>Sector industrial y minero (Tcal)</td><td>121.316</td><td>122.199</td></tr>
<tr><td>Manufactura (TJ)</td><td>230.092</td><td>236.894</td></tr>
<tr><td>Minería (TJ)</td><td>238.576</td><td>237.254</td></tr>
</table>

<p>Manufactura = Papel y Celulosa, Siderurgia, Petroquímica, Cemento, Azúcar, Láctea e Industrias Varias (CIIU 10–33). Se excluyen minería (Cobre, Salitre, Hierro, Minas Varias) y Pesca, Agroindustria y Construcción, que el BNE agrupa en "industrial".</p>

<h3>Limitaciones</h3>
<ol>
  <li><strong>Nacional</strong>, sin desagregación regional.</li>
  <li><strong>Categorías fijas</strong>: 7 manufactureras, no 24 divisiones CIIU. La intensidad solo se publica a ese nivel.</li>
  <li><strong>`Industrias Varias` es cajón residual</strong> (~46% de la energía manufacturera): el bloque más heterogéneo.</li>
  <li><strong>Incluye biomasa y licor negro</strong> (biogénico): para comparar con emisiones fósiles hay que separar por energético, no usar el total.</li>
  <li><strong>El licor negro está subrepresentado</strong>. El BNE registra 22.818 TJ en 2024; el CO₂ biogénico del RETC implica ~128.000 TJ al factor de la guía (ver ficha de energía implícita). La CNE parece contabilizar solo la fracción que entra a autoproducción.</li>
  <li><strong>La serie se revisa:</strong> 2024 puede traer cifras corregidas de años previos.</li>
  <li><strong>La equivalencia BNE ↔ CIIU no es una partición:</strong> hay solapes (divisiones 36–39 en `SANITARIAS` y `COMERCIO Y SERVICIO`) y categorías que no representan al CIIU real — `Petroquímica` declara ~200 TJ para toda la división 20, mientras la ENIA reporta 198 establecimientos químicos con VBP de 13 billones de CLP; su energía está en `Industrias Varias`. <strong>Intensidad publicable solo para Papel y Celulosa, Cemento, Siderurgia y Láctea</strong>, y aun así depende de que la ENIA codifique a 4 dígitos.</li>
</ol>

<h3>Reproducción</h3>
<pre><code>python src/ingest/manual.py --source cne --dataset bne --year 2024 --url "https://energiaabierta.cl/categorias-estadistica/balance-energetico" --license "Datos abiertos CNE (citando fuente)"
python src/normalize/bne.py --years 2023 2024
python src/audit/bne_resumen.py
</code></pre>

<p>Salidas: `data/processed/cne/bne/year=YYYY/part-0.parquet`, `bne_balance.parquet`, `ciiu4_map.parquet`, `reports/normalizacion_bne.json`, `reports/bne_industria_ramas.csv`.</p>
