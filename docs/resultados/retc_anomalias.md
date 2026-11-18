---
title: Cribado de anomalías del RETC
---

# Anomalías por planta y edición — RETC 2023–2025

Cribado, no corrección. El RETC publica cada edición como un archivo cerrado y
sin control de coherencia entre años; este informe mide cuánto de cada año es
incompatible con la serie de la propia planta.

## Regla de cribado

### Condición 1: Concordancia entre ediciones
Para cada planta y año se toma la mediana de los otros dos años. Se marca el año si
los otros dos concuerdan dentro de 3×, la planta supera 1.000 t de CO₂ en alguna
de las tres ediciones y el año está sobre 10× o bajo 0,1× de esa mediana. Es la
condición base que distingue un error de una planta que crece o entra en operación.

### Condición 2: Distinción error vs crecimiento o cierre
Si las otras dos ediciones son similares y el año marcado es un outlier respecto
a esa mediana, es un error de cribado (dato defectuoso). Si las otras dos ediciones
muestran una tendencia consistente (crecimiento o declino), el año marcado puede
reflejar un cambio real y no se marcará como anomalía.

### Condición 3: Ajuste a mediana, no imputación
Los excesos se capa a la mediana de las otras dos ediciones en `src/common/calidad.py`.
Este informe deja la evidencia planta por planta sin imputar valores externos.

## Resultado

| Edición | Plantas marcadas | CO₂ marcado (t) | CO₂ total (t) | % del total | Exceso (t) | Nacional sin el exceso (t) |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 85 | 17.057.945 | 65.440.032 | 26.1% | **17.020.337** | **48.419.695** |
| 2024 | 45 | 3.756.714 | 48.712.437 | 7.7% | 3.741.358 | 44.971.078 |
| 2025 | 148 | 180.599 | 47.015.627 | 0.4% | 71.273 | 46.944.354 |

El exceso demostrable de 2023 es de **17,0 Mt** (26% de la edición). Al restarlo,
2023 queda en **48,4 Mt**, contra 48,7 Mt de 2024 y 47,0 Mt de 2025: lo que parecía
una caída de 26% es una edición defectuosa. **Es un piso, no el total**: la regla
exige que los otros dos años concuerden entre sí, así que no puede evaluar plantas
con una sola edición comparable (Enax Río Loa, por ejemplo: 2,63 Mt en 2023, 0,63 Mt
en 2024 y 3 kt en 2025).

## El bloque GLP de 2023

| Edición | CO₂ del GLP (t) | Declaraciones |
|---|---:|---:|
| 2023 | **16.154.368** | 3.130 |
| 2024 | 1.316.703 | 3.198 |
| 2025 | 1.104.586 | 3.202 |

Mismo número de declaraciones en los tres años y **12×** el CO₂ en 2023. No son
plantas raras: es el factor de emisión del GLP de esa edición. Todos los casos
extremos comparten el GLP, como combustible primario o secundario.

## Casos mayores

| Edición | Establecimiento | CO₂ (t) | Referencia (t) | Ratio | Combustible | Dirección |
|---|---|---|---|---:|---|---|
| 2023 | RELLENO SANITARIO SANTA MARTA | 5.748.755 | 30 | **191.986×** | GAS LICUADO DE PETROLEO | exceso |
| 2023 | SAN CLEMENTE FOODS SA | 5.553.960 | 292 | **18.999×** | GAS LICUADO DE PETROLEO | exceso |
| 2024 | CARTOCOR CHILE SA | 3.049.178 | 5.755 | **530×** | GAS NATURAL | exceso |
| 2023 | PLANTA OSORNO | 1.978.619 | 10.240 | **193×** | GAS NATURAL | exceso |
| 2023 | QUIMICA LATINOAMERICANA S.A. | 1.123.223 | 33 | **33.814×** | GAS LICUADO DE PETROLEO | exceso |
| 2023 | PUNITAQUI | 899.118 | 2.819 | **319×** | GAS LICUADO DE PETROLEO | exceso |
| 2023 | Planta Concepción | 359.972 | 10.723 | **34×** | GAS NATURAL | exceso |
| 2023 | PISCICULTURA MAGDALENA (110067) | 331.233 | 604 | **548×** | GAS LICUADO DE PETROLEO | exceso |
| 2023 | PLANTA CO GENERADORA | 279.946 | 3.715 | **75×** | GAS NATURAL | exceso |
| 2023 | FÁBRICA CONCÓN | 270.690 | 1.486 | **182×** | PETROLEO N 6 | exceso |
| 2024 | CENTRAL ESPINOS | 272.779 | 5.874 | **46×** | PETROLEO N 2 (DIÉSEL) | exceso |
| 2024 | COMUNIDAD EDIFICIO SAN DAMIAN II | 147.803 | 318 | **466×** | GAS LICUADO DE PETROLEO | exceso |

*Negrita en valores de ratio y CO₂ para casos extremos.*

## Lectura

### 2023: bloque GLP inflado
El bloque GLP está inflado **12×** y concentra el exceso. Es un defecto del factor
de emisión de esa edición, no de una empresa: afecta a cualquier usuario de GLP.

### 2024: Cartocor error de unidad
Cartocor declara 3,05 Mt contra 5,8 kt (2023) y 5,7 kt (2025). Error de unidad
de una planta, ya documentado en [retc.md](../fuentes/retc.html).
Es el 86% del exceso de esa edición.

### 2025: déficits compatibles con edición abierta
Aparecen déficits —consumidores de gas que caen a casi cero—, compatibles con
una edición aún abierta más que con un cierre de planta.

## Límites

1. **Marca, no corrige**: el ajuste de los agregados vive en
   `src/common/calidad.py`, que capa los excesos a la mediana de las otras dos
   ediciones. Este informe deja la evidencia planta por planta.
2. **Tres años, dos de referencia**: con solo dos puntos de comparación la regla no
   puede validar nada; solo descarta.
3. **Planta que cierra de verdad** pasa la condición (a) si las otras dos ediciones
   son parecidas, y se marca como déficit. Se distingue en la columna `direccion`
   y se confirma con prensa o con el propio registro.
4. **El corte de 1.000 t** deja fuera miles de fuentes menores; no cambia el total.
5. **El signo importa**: la columna `exceso_t` solo suma los excesos. Los déficits
   de 2025 no se descuentan del nacional, porque un consumo que no aparece puede
   ser una declaración que aún no se cierra.

## Cómo se reproduce

Comando: `python src/audit/retc_anomalias.py`

Nombre del script: `retc_anomalias.py` — mantiene la reproducibilidad del cribado.

## Vocabulario a mantener consistente

| Usar | Evitar |
|---|---|
| anomalía | error, falla |
| exceso respecto a la mediana | demostrado, probado |
| hipótesis | causa, defecto |
| cobertura | captura total |
| intensidad física / intensidad económica | intensidad de emisiones |
| año de referencia 2024 | año base |
| capture / excede / parcial / no | estados sin definir |