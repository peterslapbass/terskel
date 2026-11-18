---
title: Terskel
---

<h1 style="font-size: 2rem;">Qué emite la industria chilena, y qué no alcanza a contar el registro</h1>

<p><strong>Terskel</strong> (umbral) es un proyecto de análisis de emisiones y eficiencia industrial en Chile. Su objetivo es relacionar los umbrales de emisión con la eficiencia productiva uniendo diversas fuentes públicas para construir una base analítica coherente y reproducible.</p>

Catorce categorías industriales, cinco fuentes públicas y una regla: ningún número se publica sin su ficha, su unidad y su límite. Año de referencia **2024**.

<div class="cifras">
  <div class="cifra azul">
    <span class="n">44,97 Mt</span>
    <span class="t">CO₂ validado por el RETC en 2024: 56% industria, 40% generación eléctrica y 4% resto.</span>
  </div>
  <div class="cifra">
    <span class="n">14 → 4</span>
    <span class="t">industrias que separa el balance; solo cuatro tienen datos publicables.</span>
  </div>
  <div class="cifra rojo">
    <span class="n">0,2 tCO₂/TJ</span>
    <span class="t">lo que el registro le imputa al Cobre, dueño de 206.000 TJ del balance.</span>
  </div>
</div>

<img src="{{ '/assets/fig/retc-composicion.svg' | relative_url }}" alt="Qué compone el CO₂ validado del RETC en 2024" class="figura" style="max-width: 100%; height: auto;">

<p>44,97 Mt validadas en 2024: 25,20 Mt industria, 18,08 Mt generación eléctrica, 1,69 Mt servicios, agua, residuos y construcción.</p>

<div class="destacado">
  <span class="etiqueta">Nota de datos</span>
  <h3>El GLP de 2023 está inflado 12×</h3>
  <p>El mismo número de declaraciones —3.130 en 2023, 3.198 en 2024— produce <strong>16,15 Mt</strong> de CO₂ un año y <strong>1,32 Mt</strong> al siguiente. No son las empresas: es el factor de emisión de esa edición.</p>
  <p><a href="{{ '/notas/glp-2023-inflado.html' | relative_url }}">Leer la nota</a></p>
</div>

## Notas de datos

Errores, cortes y huecos que encontramos en las fuentes, y qué hicimos con cada uno. Varios son del registro; uno es de nuestra propia lectura.

{% assign notas = site.pages | where: "path", "notas/" | sort: "date" | reverse %}
<ul class="lista">
{% for n in notas %}<li><time>{{ n.date | date: "%d-%m-%Y" }}</time><a href="{{ n.url | relative_url }}">{{ n.title }}</a></li>{% endfor %}
</ul>

## Qué hay aquí

- **[Resultados]({{ '/resultados/' | relative_url }})**: las 14 industrias con su cobertura, los indicadores que se pueden publicar y los escenarios a 2030.
- **[Fuentes]({{ '/fuentes/' | relative_url }})**: una ficha por fuente, con fórmula, unidad, supuestos y limitaciones; y la tabla de descargas con URL y sha256.
- **[Datos]({{ '/datos.html' | relative_url }})**: los parquet que se publican, fila por fila y columna por columna.
- **[Método]({{ '/metodologia.html' | relative_url }})**: la cadena completa, en cuatro comandos.
- **[Abierto]({{ '/abierto.html' | relative_url }})**: el sitio es open data, código MIT, cifras CC BY 4.0.

**Fuente y alcance**

**Fuente:** RETC (MMA), Balance Nacional de Energía (CNE), ENIA e IPP (INE) y dólar observado (BCCh).

**Se actualiza** cuando se publica una edición nueva de esas fuentes; cada corrida reescribe las cifras y los gráficos.

**Abierto:** cada cifra sale de un parquet versionado en el [repositorio](https://github.com/peterslapbass/terskel), y cada parquet de un script que está ahí mismo. Sin modelos, sin imputación de datos externos.

Ninguna de las instituciones citadas (MMA, CNE, INE, BCCh) participa en el proyecto ni respalda sus conclusiones.
