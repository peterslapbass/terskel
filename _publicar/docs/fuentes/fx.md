---
title: "Ficha de fuente — Tipo de cambio (dólar observado, BCCh)"
---

# Ficha de fuente — Tipo de cambio (dólar observado, BCCh)

| Campo | Valor |
|---|---|
| Institución | Banco Central de Chile |
| Serie | `F073.TCO.PRE.Z.D` — dólar observado, diario |
| Portal | si3.bcentral.cl › CAP_TIPO_CAMBIO › DOLAR_OBS_ADO |
| Cobertura | 1982-08-09 a la fecha de extracción |
| Unidad | CLP/USD |
| Licencia | uso libre citando fuente |
| Extracción | 2026-11-11 |

## Por qué está en el proyecto

La ENIA trae establecimientos que contabilizan en **miles de USD**
(`moneda_codigo = 5`): 215 de 3.132 en 2024, con el **45,8% del VBP** equivalente.
Sin tipo de cambio la industria se subestima casi a la mitad.

## Rutas de obtención (`src/ingest/fx.py`)

| Ruta | Credenciales | Qué trae |
|---|---|---|
| `bde-export` (defecto) | no | XLSX con la serie completa desde 1982 |
| `bde` | `BCCH_USER`/`BCCH_PASS` | JSON por año (`SieteRestWS`) |
| `mindicador` | no | espejo del mismo dólar (respaldo; limita la tasa) |

`bde-export`: `GET` a la página del cuadro para token y cookies, `POST` a
`/Siete/ES/Siete/DownloadExcel` con `IsFullSeries=true`. El XLSX trae fechas y
valores en dos filas paralelas (~11.000 columnas) → se parsea con `zipfile` +
`ElementTree`, no con un lector de hojas.

## Método

**Promedio simple de los días publicados**, la convención del propio BCCh (nota
metodológica del archivo exportado).

| Año | FX promedio | Mediana | Mín | Máx | Días |
|---|---:|---:|---:|---:|---:|
| 2023 | 839,07 | 821,59 | 781,49 | 945,61 | 247 |
| 2024 | 943,58 | 943,92 | 877,12 | 996,35 | 248 |
| 2025 | 951,64 | 948,67 | 904,54 | 1012,76 | 248 |

## Control cruzado con la ENIA

Remuneración mediana por ocupado (`I081`/`I080`): 2.355 en `moneda_codigo = 4` y
2,6 en `5` → razón **906** vs FX 943,58 (2024). Diferencia de unidad, no de
productividad.

## Salidas

- `data/raw/bcch/dolar_observado/serie_completa/dolar_observado_bde_YYYY-MM-DD.xlsx`
- `data/processed/bcch/dolar_diario.parquet`
- `data/processed/bcch/fx_anual.parquet` (`par = USD/CLP`, `moneda_origen`,
  `moneda_destino`, ISO 4217)

## Limitaciones

1. La exportación es **rodante**: el sha256 cambia a diario; el nombre lleva la fecha
   del snapshot y el manifest acumula versiones.
2. El BCCh **revisa** la serie: citar siempre la fecha de extracción.
3. 2026 está incompleto; su promedio anual no es definitivo.

## Reproducción

```bash
python src/ingest/fx.py && python src/normalize/fx.py
```
