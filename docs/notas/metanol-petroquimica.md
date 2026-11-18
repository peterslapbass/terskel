---
title: Metanol y petroquímica comparten código, no destino
date: 2026-11-11
---

# Metanol y petroquímica comparten código, no destino

<p><strong>Qué encontramos.</strong> El Balance Nacional de Energía separa «Producción de Metanol» de «Petroquímica». El RETC no puede: Methanex y las plantas petroquímicas comparten la división CIIU 2011. Al fusionarlas —la única opción con el registro— el bloque declara un CO₂ que implica <strong>22.252 TJ</strong>, mientras el balance le asigna <strong>8.947 TJ</strong>:</p>

<table>
<tr><th>Ítem del balance (2024)</th><th>TJ</th></tr>
<tr><td>Producción de Metanol</td><td>8.744</td></tr>
<tr><td>Petroquímica</td><td>203</td></tr>
<tr><td><strong>Total fusionado</strong></td><td><strong>8.947</strong></td></tr>
</table>

<p>Eso da una cobertura de <strong>249%</strong> y una intensidad de <strong>168 tCO₂/TJ</strong> —por encima de cualquier valor de combustión, que no pasa de ~75—. La cifra no describe una industria ineficiente: describe un numerador y un denominador que no hablan de lo mismo.</p>

<p><strong>La trampa del balance.</strong> El archivo tiene tres secciones y la misma etiqueta aparece en varias. En <code>C.TRANSFORMAC</code>, «Producción de Metanol» trae el gas natural con signo negativo (−37.475 TJ) porque es la entrada del proceso; el metanol que sale vale +26.743 TJ. El consumo real está en <code>DEMANDA DE ENERGÍA</code>: 8.744 TJ. Sumar la sección equivocada da un denominador negativo y una cobertura sin sentido.</p>

<p><strong>Qué hicimos.</strong> Fusionamos las dos categorías —no hay forma de separarlas con este registro— y las marcamos como <strong>no publicables</strong>. La fila queda en las tablas con su cifra, su cobertura y su motivo.</p>

<p><strong>Por qué no se arregla con un factor.</strong> Si se usara la energía del balance como denominador, el resultado sería 168 tCO₂/TJ; si se usara la energía implícita en el CO₂, sería tautológico. Ninguna de las dos es una intensidad industrial. Y el CO₂ de Methanex (0,37 Mt) no está separado del de Enax Río Loa (0,63 Mt) en el origen: el registro declara la misma división para ambos.</p>

<p><strong>Qué queda.</strong> Pedir al MMA el cruce por establecimiento con CIIU a 4 dígitos, o cruzar contra el catálogo de Methanex. Mientras no exista, la nota metodológica debe decir que la petroquímica chilena no tiene intensidad publicable con estas dos fuentes.</p>
