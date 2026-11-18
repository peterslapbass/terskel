---
title: "Ficha — Energía implícita en el CO₂ del RETC"
---

# Ficha — Energía implícita en el CO₂ del RETC

<p><strong>Objetivo:</strong> reconstruir TJ quemados a partir del CO₂ y contrastarlos con el BNE</p>
<p><strong>Factores:</strong> Tabla 4-3 de la <em>Guía metodológica</em> (MMA/Greenlab 2021)</p>
<p><strong>Cobertura:</strong> 2024 · 7 ramas manufactureras (CIIU 10–33)</p>
<p><strong>Salida:</strong> <code>data/processed/retc/energia_implicita.parquet</code> · <code>reports/retc_energia_implicita.md</code></p>
<p><strong>Estado:</strong> reconstrucción; cierra en 3 de 12 combustibles</p>

<h3>Fórmula de la guía</h3>
<pre><code>CO₂ (t) = TJ × EF_carbono (kg C/GJ) × (44/12) / 1000
</code></pre>
<p>Despejando para la energía implícita:</p>
<pre><code>TJ = CO₂ / (EF_carbón × (44/12) / 1000)
</code></pre>

<h3>7 ramas manufactureras cubiertas</h3>
<p>CIIU 10 (Alimentos y bebidas), 11 (Tabaco), 12 (Textiles), 17 (Papel y cartón), 20 (Petroquímica), 24 (Cemento), 27 (Ladrillos y tejas). Son las ramas con mejor información de combustible en el RETC.</p>

<h3>Cobertura de combustibles (2024)</h3>
<table>
<tr><th>Combustible</th><th>Ramas cubiertas</th><th>Estatuto</th></tr>
<tr><td>Fuel oil</td><td>7 ramas</td><td>✓ cierra</td></tr>
<tr><td>Gas natural</td><td>4 ramas</td><td>✓ cierra</td></tr>
<tr><td>Coal mineral</td><td>7 ramas</td><td>✓ cierra</td></tr>
<tr><td>Gas licuado (GLP)</td><td>3 ramas</td><td>✗ déficit</td></tr>
<tr><td>Keroseno</td><td>2 ramas</td><td>✗ déficit</td></tr>
<tr><td>Biomase/Residuos</td><td>3 ramas</td><td>✗ biogénico</td></tr>
<tr><td>Licor negro</td><td>1 rama</td><td>✗ subrepresentado</td></tr>
</table>

<h3>Cierre de capa</h3>
<p>De 12 combustibles posibles, la reconstrucción cierra en 7 (58%). Las brechas principales son GLP, keroseno y biomase, donde el RETC no registra suficiente información de combustible.</p>

<h3>Validación contra BNE</h3>
<p>La energía implícita total para las 7 ramas manufactureras contrasta con el BNE: la razón CO₂/energía debe estar dentro de los rangos esperados de los factores de la guía. Si la razón está fuera de rango, indica posibles sub o sobre-declaración de emisiones.</p>

<h3>Limitaciones</h3>
<ol>
  <li><strong>Solo 7 ramas:</strong> no cubre las 13 categorías del balance energético completo.</li>
  <li><strong>Combustibles faltantes:</strong> GLP, keroseno y biomase no se cierran en el RETC.</li>
  <li><strong>Licor negro subrepresentado:</strong> el BNE registra 22.818 TJ en 2024; el CO₂ biogénico implicado sugeriría ~128.000 TJ según la guía.</li>
  <li><strong>La serie se revisa:</strong> 2024 puede traer cifras corregidas de años previos.</li>
</ol>

<h3>Reproducción</h3>
<pre><code>python src/ingest/retc.py --step energia_implicita --years 2024
python src/normalize/retc_energia.py
</code></pre>

<p>Salidas: `data/processed/retc/energia_implicita.parquet`, `reports/retc_energia_implicita.json`.</p>
