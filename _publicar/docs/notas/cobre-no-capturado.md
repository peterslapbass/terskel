---
title: El registro no captura la gran minería del cobre
date: 2026-11-15
---

# El registro no captura la gran minería del cobre

### Qué observamos

El Cobre es el ítem industrial más grande del Balance Nacional de Energía: 205.998 TJ en 2024, el 39% de toda la energía de las 14 categorías industriales. El RETC le imputa 42 kt de CO₂.

La mitad de esa energía es electricidad (102.348 TJ), que no genera emisiones directas en la mina: se contabilizan en la central que la produce. La otra mitad —103.650 TJ— sí es combustible quemado en el sitio, sobre todo diésel (94.969 TJ).

### La cuenta

Con los factores de la guía del RETC (74,1 tCO₂/TJ para el diésel, 56,1 para el gas natural, 77,4 para el petróleo combustible), esos 103.650 TJ fósiles implican **7,58 Mt de CO₂**. El registro declara 0,042 Mt: **182 veces menos**.

<img src="/terskel/assets/fig/cobre.svg" alt="CO₂ del Cobre: lo que implica la energía del balance y lo que declara el registro" style="max-width: 100%; height: auto;">

### Qué creemos (hipótesis)

La gran minería no declara su combustión al registro: declara electricidad y poco más. No es que el RETC esté mal calculado; es que **no es un inventario industrial**, es un registro de establecimientos sobre ciertos umbrales, y lo que sus fuentes no declara no aparece.

### Qué falta para confirmarlo

Un inventario minero completo que cruce la energía declarada con las emisiones reportadas por la minería. Sin eso, la cifra del RETC para Cobre mide cobertura, no emisiones.

### Cómo se reproduce

`python src/indicators/intensidad.py` (columna `cobertura_energetica`) y `python src/reports/graficos.py` para la figura.