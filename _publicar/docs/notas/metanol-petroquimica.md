---
title: Metanol y petroquímica comparten código, no destino
date: 2026-11-11
---

# Metanol y petroquímica comparten código, no destino

### Qué observamos

El Balance Nacional de Energía separa **«Producción de Metanol»** de **«Petroquímica»**. El RETC no puede: Methanex y las plantas petroquímicas comparten la división CIIU 2011. Al fusionarlas —la única opción con el registro— el bloque declara un CO₂ que implica **22.252 TJ**, mientras el balance le asigna **8.947 TJ**:

| Ítem del balance (2024) | TJ |
|---|---|
| Producción de Metanol | 8.744 |
| Petroquímica | 203 |
| **Total fusionado** | **8.947** |

Eso da una cobertura de **249%** y una intensidad de **168 tCO₂/TJ** —por encima de cualquier valor de combustión, que no pasa de ~75—. La cifra no describe una industria ineficiente: describe un numerador y un denominador que no hablan de lo mismo.

### La trampa del archivo

El archivo tiene tres secciones y la misma etiqueta aparece en varias. En **C.TRANSFORMAC**, «Producción de Metanol» trae el gas natural con signo negativo (−37.475 TJ) porque es la entrada del proceso; el metanol que sale vale **+26.743 TJ**. El consumo real está en **DEMANDA DE ENERGÍA**: 8.744 TJ. Sumar la sección equivocada da un denominador negativo y una cobertura sin sentido.

### Qué creemos (hipótesis)

Si se usara la energía del balance como denominador, el resultado sería 168 tCO₂/TJ; si se usara la energía implícita en el CO₂, sería tautológico. Ninguna de las dos es una intensidad industrial. Y el CO₂ de Methanex (0,37 Mt) no está separado del de Enax Río Loa (0,63 Mt) en el origen: el registro declara la misma división para ambos.

### Qué falta para confirmarlo

Pedir al MMA el cruce por establecimiento con CIIU a 4 dígitos, o cruzar contra el catálogo de Methanex. Mientras no exista, la nota metodológica debe decir que **la petroquímica chilena no tiene intensidad publicable con estas dos fuentes**.

### Qué hicimos

Fusionamos las dos categorías —no hay forma de separarlas con el registro— y las marcamos como **no publicables**. La fila queda en las tablas con su cifra, su cobertura y su motivo.

### Cómo se reproduce

`python src/indicators/intensidad.py` y luego `python src/audit/retc_anomalias.py`.