---
title: Método
---

# Método

Cuatro decisiones ordenan todo lo demás:

## 1. El dato primero
Ninguna cifra del sitio se escribe a mano: sale de un parquet
que sale de un script. Si un número no tiene script, no está.

## 2. Sin modelos
No hay machine learning ni regresiones. Los indicadores son
cocientes; los escenarios, una identidad contable.

## 3. Sin imputar
Cuando falta un dato se marca, no se rellena. La única excepción
—capar un exceso contra la propia serie de la planta— está declarada en su nota y
en la columna `factor_ajuste`.

## 4. Una cifra, una ficha
Fórmula, unidad, cobertura, supuestos y limitaciones,
siempre juntos. Un número sin ficha no se publica.

## La cadena de datos

```
ingesta  →  normalización  →  auditoría  →  indicadores  →  escenarios  →  sitio
XLSX/CSV      parquet          parquet       parquet        parquet       SVG/MD
```

Cada etapa reescribe sus parquet completos. Los archivos crudos no se tocan nunca.

```bash
# 1. fuentes (manifiesto con URL y sha256)
python src/ingest/retc.py --years 2023 2024 2025
python src/normalize/retc.py --years 2023 2024 2025
python src/normalize/bne.py --years 2023 2024 2025
python src/normalize/enia.py --years 2023 2024 2025
python src/ingest/fx.py && python src/normalize/fx.py
python src/ingest/ipp.py && python src/normalize/ipp.py

# 2. puente CIIU → rama del balance
python src/normalize/ciiu_bne.py

# 3. CO₂ por origen y energía implícita
python src/normalize/retc_co2_combustible.py
python src/normalize/retc_energia_implicita.py --year 2024

# 4. cribado y auditoría
python src/audit/retc_anomalias.py

# 5. indicadores y escenarios
python src/indicators/intensidad.py
python src/scenarios/escenarios.py

# 6. sitio
python src/reports/graficos.py
python src/reports/sitio.py
```

En Windows, la cadena se corre con `$env:PYTHONPATH="src"`. Requiere Python 3.9 y
polars 1.36. El repositorio incluye los parquet procesados, así que los pasos 5 y 6 se
pueden correr sin descargar 180 MB de XLSX.

## Las fuentes y su papel

| Fuente | Qué aporta | Papel |
|---|---|---|
| RETC (MMA) | CO₂ por establecimiento, combustible y origen | numerador |
| BNE (CNE) | energía por ítem y energético | denominador físico |
| ENIA (INE) | VBP, valor agregado, ocupados | denominador económico |
| IPP (INE) | precios de productor, base 2019 | deflactor |
| BCCh | dólar observado | conversión y control |

Las tres primeras no comparten unidad de análisis. El RETC cuenta establecimientos, el
balance cuenta ítems de consumo y la ENIA cuenta establecimientos industriales. El
puente es la clasificación CIIU a 4 dígitos, con una tabla de correspondencia explícita
y una categoría —Petroquímica— donde el puente no alcanza y se declara.

## El año de referencia

**2024**, porque es la edición del RETC con menos exceso demostrable (7,7%) y la que
tiene el balance y la ENIA completos. 2023 y 2025 se usan como contraste: sirven para
detectar anomalías, no para construir tendencias. Ningún indicador se publica como
serie 2023–2025.

## Qué no hace este método

- No estima la combustión que el RETC no captura: la marca como hueco (ver
  [Cobre]({{ '/notas/cobre-no-capturado.html' | relative_url }}) y
  [Huachipato]({{ '/notas/huachipato-sin-carbon.html' | relative_url }}) ).
- No corrige los factores de emisión de las fuentes.
- No proyecta precios, producción ni política pública: los escenarios mueven palancas
  declaradas dentro de un rango declarado.
- No reemplaza al RETC ni al balance. Es una lectura crítica de ambos.

## Reglas de publicación

### Regla 1: Cada cifra tiene una ficha
Número, unidad, cobertura, supuestos y limitaciones deben aparecer juntos. Un dato
isolado sin ficha no es público.

### Regla 2: El año de referencia es 2024
Solo se publican indicadores y escenarios con 2024 como año base. 2023 y 2025 sirven
para contraste y detección de anomalías, no como serie temporal.

### Regla 3: No se imputan valores faltantes
Ausencias de datos se marcan como huecos. La única excepción es el ajuste contra la
misma planta en la edición anterior, declarado en `factor_ajuste`.

### Regla 4: Las fuentes no comparten unidad de análisis
RETC cuenta establecimientos, BNE cuenta ítems de consumo, ENIA cuenta establecimientos
industriales. El puente CIIU a 4 dígitos no cubre todas las categorías (Petroquímica).

## Reglas de cribado

### Condición 1: Concordancia entre ediciones
Para cada planta y año se toma la mediana de los otros dos años. Se marca el año si
los otros dos concuerdan dentro de 3×, la planta supera 1.000 t de CO₂ en alguna de
las tres ediciones y el año está sobre 10× o bajo 0,1× de esa mediana.

### Condición 2: Distinción error vs crecimiento
La condición de concordancia es la que distingue un error de una planta que crece,
cierra o entra en operación. Si las otras dos ediciones son similares y el año marcado
es un outlier, es un error de cribado.

### Condición 3: Ajuste a mediana, no imputación
Los excesos se capa a la mediana de las otras dos ediciones en `src/common/calidad.py`.
Este informe deja la evidencia planta por planta sin imputar valores externos.

## Verificar una cifra

Toda cifra del sitio tiene tres rastros: la ficha de su fuente, el parquet del que sale
(en [Datos]({{ '/datos.html' | relative_url }})) y el script que la produce (en el
[repositorio](https://github.com/peterslapbass/terskel)). Si los tres no coinciden, la
cifra está mal.