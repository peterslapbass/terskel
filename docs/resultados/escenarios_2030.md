---
title: Escenarios 2030
---

# Escenarios 2030 — energía y CO₂ (4 ramas manufactureras)

![CO₂ a 2030 en los cuatro escenarios]({{ '/assets/fig/escenarios-2030.svg' | relative_url }}){: .figura }

*Misma base 2024 para las cinco barras: lo que cambia es la palanca, no el punto de partida.*

![Cuánto mueve cada palanca el CO₂ a 2030]({{ '/assets/fig/tornado.svg' | relative_url }}){: .figura }

*Amplitud = diferencia entre el extremo alto y el bajo de cada palanca, con las demás en su valor central.*


## Introducción

Base observada 2024, ajustada por el cribado de ediciones del RETC (los excesos se
capan a la mediana de las otras dos ediciones; ver
[Cribado de anomalías del RETC](retc_anomalias.html)), horizonte 2030 (6 años). Motor determinístico sobre el nivel
de 2024: la actividad y la eficiencia escalan energía y CO₂; el cambio de mix
(`mf`) actúa **solo sobre el CO₂ de combustión fósil**, porque la biomasa es
biogénica y el CO₂ de proceso depende del clínker. No es una proyección
estadística: con dos años observados no hay tendencia que estimar.

`g` es un **vector por rama**, no un escalar. El vector central está calibrado para
que el crecimiento agregado ponderado por VBP quede en 2,0%/año, el mismo valor de la
versión escalar. El nivel de 2030 no queda igual: Papel concentra el 94% del CO₂ de
las cuatro ramas y crece al 3,0%, así que el congelado sube a 21,9 Mt (20,9 Mt con un
`g` escalar del 2,0%).

## Parámetros

| Palanca | Central | Mín | Máx | Recomposición |
|---|---:|---:|---:|---:|
| Crecimiento Papel y Celulosa | +3,0%/año | +0,0% | +4,0% | +2,5% |
| Crecimiento Siderurgia | +0,0%/año | -2,0% | +2,0% | -2,0% |
| Crecimiento Cemento | -3,0%/año | -6,0% | +0,0% | -5,0% |
| Crecimiento Industria Láctea | +1,0%/año | +0,0% | +3,0% | +1,5% |
| Mejora de intensidad | +1,5%/año | +0,5% | +2,5% | — |
| Mejora del factor de emisión | +1,0%/año | +0,0% | +2,0% | — |

## Resultado agregado

| Escenario | Energía 2030 (TJ) | CO₂ 2030 (t) | vs 2024 | vs congelado |
|---|---:|---:|---:|---:|
| Congelado | 141.642 | 21.861.029 | +17,9% | +0,0% |
| Descarbonización | 129.363 | 19.848.959 | +7,1% | -9,2% |
| Eficiencia | 129.363 | 19.965.858 | +7,7% | -8,7% |
| Recomposición sectorial | 124.425 | 19.204.706 | +3,6% | -12,2% |

## Recomposición sectorial

Estructura de VBP y CO₂ con el vector alternativo (cemento y siderurgia se contraen,
papel y láctea crecen por encima del central). Papel pasa de 57,9% a 61,1% del VBP y
concentra el 94% del CO₂ de las cuatro ramas, así que el total lo mueve sobre todo lo
que le pasa a Papel; la contracción de Cemento y Siderurgia se ve en la estructura,
no en el agregado.


| Rama | VBP 2024 | VBP 2030 | Peso 2024 | Peso 2030 | CO₂ 2024 | CO₂ 2030 | Var. CO₂ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Papel y Celulosa | 3,54 | 4,11 | 57,9% | 61,1% | 17.485.123 | 18.422.515 | +5,4% |
| Industria Láctea | 1,69 | 1,85 | 27,6% | 27,4% | 242.946 | 238.185 | -2,0% |
| Siderurgia | 0,82 | 0,72 | 13,4% | 10,8% | 65.740 | 50.490 | -23,2% |
| Cemento | 0,07 | 0,05 | 1,1% | 0,7% | 747.603 | 493.516 | -34,0% |

## Descomposición por origen del CO₂

| Escenario | CO₂ fósil (t) | CO₂ biomasa (t) | CO₂ proceso (t) | CO₂ otro (t) | CO₂ total (t) |
|---|---:|---:|---:|---:|---:|
| Observado 2024 | 1.911.356 | 15.852.886 | 712.604 | 64.567 | 18.541.413 |
| Congelado 2030 | 2.187.223 | 18.939.811 | 680.165 | 53.830 | 21.861.029 |
| Descarbonización 2030 | 1.880.709 | 17.297.886 | 621.200 | 49.163 | 19.848.959 |
| Eficiencia 2030 | 1.997.609 | 17.297.886 | 621.200 | 49.163 | 19.965.858 |
| Recomposición sectorial 2030 | 1.810.168 | 16.780.606 | 570.518 | 43.413 | 19.204.706 |

## Descarbonización por rama

| Rama | Energía 2030 (TJ) | CO₂ 2030 (t) | tCO₂/TJ | Publicable económica |
|---|---:|---:|---:|---|
| Papel y Celulosa | 114.982 | 19.001.501 | 152,1 | sí |
| Cemento | 7.978 | 559.229 | 93,7 | no |
| Industria Láctea | 1.623 | 231.231 | 149,6 | sí |
| Siderurgia | 4.780 | 56.997 | 13,8 | no |

## Sensibilidad (tornado sobre CO₂ de 2030)

| Palanca | CO₂ con palanca al mínimo (t) | CO₂ con palanca al máximo (t) | Amplitud (t) |
|---|---:|---:|---:|
| Crecimiento Papel y Celulosa | 16.733.134 | 20.947.906 | 4.214.772 |
| Mejora de intensidad | 21.089.138 | 18.670.160 | 2.418.978 |
| Mejora del factor de emisión | 19.965.858 | 19.737.816 | 228.042 |
| Crecimiento Cemento | 19.752.885 | 19.961.096 | 208.211 |
| Crecimiento Industria Láctea | 19.835.558 | 19.877.828 | 42.270 |
| Crecimiento Siderurgia | 19.842.452 | 19.856.150 | 13.698 |

## Prueba de robustez: Siderurgia {#prueba-robustez-siderurgia}

El escenario principal incluye sólo las ramas con intensidad física publicable. Esta prueba agrega Siderurgia para ver si la conclusión depende de ella.
Su energía declarada cubre cerca de 8% de lo que el balance le asigna, así que su resultado no es confiable. Motivo de la exclusión en el escenario principal: [ver límites](#siderurgia-fuera).
**Qué mide esta prueba:** la diferencia en el CO₂ total de 2030 entre el escenario principal y el mismo escenario con Siderurgia incluida, con su base observada de 2024 (0,07 Mt) y su crecimiento central.
**Resultado:** pendiente de cálculo. Cuando esté, se reporta aquí la diferencia en toneladas y en porcentaje del total.
Si el resultado cambia poco, la conclusión no depende de los datos de Siderurgia.

## Límites

### El crecimiento sectorial es un supuesto
Es un supuesto declarado, no una estimación: la ENIA tiene dos años y sus
variaciones por rama son artefactos de muestra (Cemento pasa de 6 a 4
establecimientos; Papel crece 51% en el denominador). El vector se elige, no se ajusta.

### La recomposición mueve la estructura
Mueve poco el CO₂ agregado porque las ramas que se contraen son pequeñas en VBP
(Cemento y Siderurgia suman ~14% del VBP de las 4). Su efecto es de **estructura**,
no de total.

### Cemento y la intensidad económica
Cemento entra en energía y CO₂ (datos sólidos) pero no en la intensidad económica:
su VBP en la ENIA cubre solo 4 plantas.

### Siderurgia fuera del escenario principal {#siderurgia-fuera}

Siderurgia no entra en el escenario principal porque su energía declarada cubre
cerca de 8% de lo que el balance le asigna. Su efecto se prueba aparte en
[la prueba de robustez](#prueba-robustez-siderurgia).

### El factor de emisión es agregado
Se modela como un parámetro agregado por rama; no distingue sustitución de
combustible de electrificación o de cambio de proceso.

### La columna `otro`
Recoge los combustibles que el split no clasifica como fósil, biomasa ni proceso
(BECSA, aceite usado, origen no identificado): 0,3% del CO₂. No la mueve `mf`.

### El año base
Es 2024 y está ajustado: 2023 trae el bloque GLP inflado ~12× y 2024 el error de
Cartocor (3,05 Mt, capado). La serie histórica no es una tendencia.
