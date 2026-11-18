---
title: Notas de datos
---

# Notas de datos

Errores, cortes y huecos de las fuentes —y de nuestras propias cuentas— con la cifra
que los delata y lo que hicimos con cada uno.

{% assign notas = site.pages | where_exp: "p", "p.path contains 'notas/'" %}
{% assign notas = notas | where_exp: "p", "p.name != 'index.md'" | sort: "date" | reverse %}
<ul class="lista">
{% for n in notas %}
  <li><time>{{ n.date | date: "%d-%m-%Y" }}</time><a href="{{ n.url | relative_url }}">{{ n.title }}</a></li>
{% endfor %}
</ul>
