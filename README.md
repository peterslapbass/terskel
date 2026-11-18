# INTERACTION — Inteligencia industrial con datos públicos (Chile)

Base analítica reproducible que integra actividad industrial, energía y emisiones
a partir de fuentes públicas chilenas. Proyecto por etapas: **primero datos,
después indicadores, y solo entonces modelos**.

Estado actual: **piloto completo hasta escenarios**. RETC normalizado
(2023–2025), BNE normalizado (2023–2024), ENIA normalizada (2023–2024) con sus
variables clave decodificadas (VBP, consumo intermedio, valor agregado, empleo,
gasto energético), tipo de cambio del BCCh, deflactor IPP base 2019, indicadores
de intensidad y escenarios 2030.

## Estructura

```
data/
  raw/                     # archivos originales, inmutables
    manifest.csv           # URL, fecha, sha256, licencia de cada archivo
    retc/fuente_puntual/2023/original.xlsx
    enia/base/2024/base-enia-2024.csv
    cne/bne/2024/bne_2024.xlsx
  processed/               # Parquet normalizado
    retc/emisiones_fp/year=2023/part-0.parquet
    cne/bne/year=2024/part-0.parquet
    enia/base/year=2024/part-0.parquet
src/
  common/                  # rutas y manifest
  ingest/                  # descarga RETC (CKAN) y registro manual
  normalize/               # XLSX/CSV -> Parquet con tipos explícitos
  audit/                   # matriz de compatibilidad y calidad
  indicators/              # intensidad física y económica
  scenarios/               # escenarios 2030 con palancas explícitas
  reports/                 # gráficos SVG, páginas del sitio y control previo
docs/                      # sitio Jekyll (GitHub Pages desde /docs)
  fuentes/                 # una ficha por fuente
  notas/                   # notas de datos
  resultados/              # reportes publicados (se generan)
reports/                   # salidas generadas (no editar a mano)
```

## Requisitos

```
pip install -r requirements.txt
```

## Uso

```powershell
$env:PYTHONPATH="src"
python src/ingest/retc.py --years 2023 2024 2025
python src/normalize/retc.py --years 2023 2024 2025
python src/normalize/retc_co2_combustible.py
python src/audit/retc_anomalias.py
python src/normalize/retc_energia_implicita.py --year 2024
python src/audit/retc_audit.py

python src/normalize/bne.py --years 2023 2024
python src/audit/bne_resumen.py

python src/normalize/enia.py --years 2023 2024
python src/normalize/ciiu_bne.py
python src/ingest/fx.py
python src/normalize/fx.py
python src/ingest/ipp.py
python src/normalize/ipp.py
python src/audit/integracion_rama.py --year 2024
python src/indicators/intensidad.py
python src/scenarios/escenarios.py

# sitio
python src/reports/graficos.py    # 7 SVG en docs/assets/fig/
python src/reports/sitio.py       # resultados, datos y descargas
python src/reports/verifica.py    # control previo a publicar
python src/reports/publicar.py    # arma _publicar/ para el repo público
```

## Indicadores

Dos familias etiquetadas por separado ([ficha](docs/fuentes/indicadores.md)):

- **económica**: TJ y tCO₂ por billón de CLP de 2019 (VBP deflactado con IPP).
- **física**: tCO₂/TJ y MWh por ocupado.

Se identifican las **14 categorías industriales** que define la tabla `BNE-CIIU 4`
del balance (7 manufactureras, refino y extracción de petróleo y gas, y 6 primarias o
extractivas) y se publican solo las que pasan dos pruebas: combustión capturada por el
RETC y CO₂ no concentrado en una sola planta. Quedan cuatro: Papel y Celulosa,
Cemento, Industria Láctea y Refinería. Siderurgia queda fuera (Huachipato no declara
carbón ni coque) y Cobre también: el RETC le imputa 0,2 tCO₂/TJ a los 206.000 TJ del
balance. El registro tampoco es un inventario industrial: 40% de su CO₂ validado es
generación eléctrica.
Salida: `data/processed/indicators/` y `reports/indicadores_intensidad.md`.

El CO₂ se separa por origen (fósil, biomasa, proceso) y se reconvierte a TJ con
los factores de la guía del RETC para contrastarlo con el BNE
([ficha](docs/fuentes/energia_implicita.md)). Antes de agregar, las ediciones pasan
por un cribado que capa los excesos planta-año a la mediana de las otras dos
ediciones ([ficha](docs/fuentes/retc.md#las-ediciones-no-son-comparables-entre-sí)):
el año base es 2024.

## Escenarios

Cuatro escenarios a 2030 sobre las cuatro ramas publicables
([ficha](docs/fuentes/escenarios.md)): **congelado**, **eficiencia**,
**descarbonización** y **recomposición sectorial**. Motor determinístico con
palancas declaradas en `data/reference/escenarios_parametros.csv` y tornado de
sensibilidad: `g` es un **vector por rama** (la estructura cambia), `mi` y `mf` son
globales. No es una proyección estadística: con dos años observados no hay tendencia
que estimar. Salida: `data/processed/scenarios/` y `reports/escenarios_2030.md`.

Consultas con DuckDB sobre los Parquet:

```sql
SELECT rubro, sum(emision_retc) AS co2
FROM read_parquet('data/processed/retc/emisiones_fp/**/*.parquet', hive_partitioning = true)
WHERE contaminante_norm = 'CARBON DIOXIDE'
GROUP BY 1 ORDER BY 2 DESC;
```

## Fuentes

| Fuente | Estado | Ficha |
|---|---|---|
| RETC — emisiones al aire de fuentes puntuales | descargada y normalizada 2023–2025 | [docs/fuentes/retc.md](docs/fuentes/retc.md) |
| CNE — Balance Nacional de Energía (BNE) | descargada y normalizada 2023–2024 | [docs/fuentes/bne.md](docs/fuentes/bne.md) |
| ENIA / INE — microdatos | descargada y normalizada 2023–2024 | [docs/fuentes/enia.md](docs/fuentes/enia.md) |
| INE — IPP Industria Manufacturera (base 2019) | descargada y normalizada; deflactor por división | [docs/fuentes/ipp.md](docs/fuentes/ipp.md) |
| INE — descriptor de variables y correspondencias CIIU | registrado (documentación) | [docs/fuentes/enia.md](docs/fuentes/enia.md) |
| INE — base de seguimiento (panel de establecimientos) | identificada, no descargada (sin región) | [docs/fuentes/enia.md](docs/fuentes/enia.md) |
| BCCh — dólar observado diario | descargada y normalizada (serie completa) | [docs/fuentes/fx.md](docs/fuentes/fx.md) |
| SNI Chile | pendiente (referencia macro) | — |

## Publicación

El sitio es un Jekyll nativo de GitHub Pages servido desde `docs/` (tema propio,
`_layouts/default.html` + `assets/estilo.css`, sin build local). Repo público:
`peterslapbass/terskel` → Pages desde `main` / `/docs`.

Flujo:

1. `python src/reports/graficos.py` — 7 SVG deterministas desde los parquet.
2. `python src/reports/sitio.py` — genera `docs/fuentes/descargas.md`,
   `docs/datos.md` y `docs/resultados/*.md` desde el manifiesto y los reportes.
3. `python src/reports/verifica.py` — front matter, enlaces, figuras y rastros de
   rutas absolutas. Falla si algo no se puede publicar.
4. `python src/reports/publicar.py` — arma `_publicar/` con la estructura exacta del
   repo (README, LICENSE, `docs/`, `src/`, `data/processed/`, `data/raw/manifest.csv`,
   `reports/`, `requirements.txt`). Esa carpeta es la que se sube.

`data/raw` queda fuera del repo público: son ~180 MB de XLSX con datos por
establecimiento. El manifiesto entrega URL, tamaño y sha256 de cada archivo.

## Reglas del proyecto

1. La capa `raw` no se modifica nunca. Toda transformación se reconstruye desde ahí.
2. Cada archivo se registra en `data/raw/manifest.csv` con su hash.
3. Los nulos, los ceros y los valores imputados son cosas distintas y se marcan como tales.
4. Ningún indicador se publica sin su ficha: fórmula, unidad, cobertura, supuestos y limitaciones.
