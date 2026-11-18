# Terskel

**Emisiones y energía de la industria chilena, año de referencia 2024.**
Sitio: https://peterslapbass.github.io/terskel/

Catorce categorías industriales, tres fuentes públicas y una regla: ninguna cifra se
publica sin su ficha —fórmula, unidad, cobertura, supuestos y limitaciones—. Sin
modelos, sin imputación de datos externos.

## Qué hay acá

```
docs/                 sitio Jekyll publicado desde /docs
src/                  la cadena: ingesta, normalización, auditoría, indicadores, escenarios
data/processed/       parquet que salen de la cadena (~25 MB)
data/raw/manifest.csv URL, tamaño, sha256 y licencia de cada archivo de entrada
reports/              los reportes en markdown que se publican como páginas
```

Los XLSX crudos **no** están en el repo: pesan ~180 MB y contienen datos por
establecimiento de terceros. El manifiesto entrega la URL oficial y el sha256 de cada
uno; se descargan de la fuente y se verifica el hash.

## Reproducir

```bash
pip install -r requirements.txt
export PYTHONPATH=src          # PowerShell: $env:PYTHONPATH="src"

python src/ingest/retc.py --years 2023 2024 2025
python src/normalize/retc.py --years 2023 2024 2025
python src/normalize/retc_co2_combustible.py
python src/audit/retc_anomalias.py
python src/normalize/retc_energia_implicita.py --year 2024

python src/normalize/bne.py --years 2023 2024
python src/normalize/enia.py --years 2023 2024
python src/ingest/fx.py && python src/normalize/fx.py
python src/ingest/ipp.py && python src/normalize/ipp.py
python src/normalize/ciiu_bne.py

python src/indicators/intensidad.py
python src/scenarios/escenarios.py

python src/reports/graficos.py   # 7 SVG
python src/reports/sitio.py      # páginas de resultados, datos y descargas
python src/reports/verifica.py   # revisa el sitio antes de publicar
```

Los parquet están en el repo, así que los dos últimos bloques corren sin descargar
nada.

## Las cuatro decisiones

1. **El dato primero.** Cada cifra sale de un parquet que sale de un script.
2. **Sin modelos.** Los indicadores son cocientes; los escenarios, una identidad
   contable.
3. **Sin imputar.** Cuando falta un dato se marca, no se rellena. La única excepción
   —capar un exceso contra la propia serie de la planta— está declarada en la columna
   `factor_ajuste` y en su nota.
4. **Una cifra, una ficha.** En `docs/fuentes/`.

## Licencias

- Código: MIT (ver `LICENSE`).
- Cifras, tablas y gráficos: CC BY 4.0, citando Terskel y la fuente primaria.
- Datos del RETC: ODbL, según la licencia del portal del MMA.

Ninguna de las instituciones citadas (MMA, CNE, INE, BCCh) participa en el proyecto ni
respalda sus conclusiones.
