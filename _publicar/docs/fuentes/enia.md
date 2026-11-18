---
title: "Ficha de fuente — ENIA (microdatos por establecimiento)"
---

# Ficha de fuente — ENIA (microdatos por establecimiento)

| Campo | Valor |
|---|---|
| Institución | INE — Encuesta Nacional Industrial Anual |
| Portal | ine.gob.cl › industria-energia-y-construccion › estructura-de-la-industria-manufacturera |
| Cobertura descargada | 2023, 2024 |
| Formato | CSV `;` UTF-8, 277 columnas |
| Registros | 3.151 (2023) · 3.132 (2024) |
| Unidad de observación | establecimiento manufacturero, 10+ trabajadores |
| Geografía | 16 regiones (sin comuna) |
| Moneda | miles de CLP (2.917) y miles de USD (215), en 2024 |
| Estado | normalizada a Parquet, 44 columnas |

## Bloques

| Bloque | Contenido |
|---|---|
| `ID`,`ANIO`,`REGION`,`CIIU4`,`CLASIFICACION`,`IMPUTACION` | metadatos |
| A001–A012 | org. jurídica, capital, moneda |
| B001–B030 | ingresos (B001 = fabricación propia) |
| C001–C007 · E001–E004 | compras y traspasos |
| D001–D048 | gastos |
| F001–F012 | gastos financieros |
| G (20) | energía, en dinero |
| H001–H020 | activos |
| I001–I110 | empleo y remuneraciones |
| K001–K011 | variables económicas calculadas |
| `TAMANO`,`TEED` | estratos de tamaño |

**`TAMANO` verificado**: son 9 bandas de ocupación, con los límites exactos en los
mínimos y máximos de cada grupo.

| `tamano` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| ocupados | 0–5 | 5–10 | 10–20 | 20–50 | 50–100 | 100–200 | 200–500 | 500–1.000 | 1.000+ |

`CLASIFICACION` (A–F) **no es atributo de la empresa ni sección CIIU**: la tasa de
imputación sube de 1,3% en A a 33% en E, así que parece un estrato de calidad del
dato. No se usa en ningún indicador.

## Decodificación

Fuentes: descriptor 1995–2019 (columna "Variables 2019" = puente al layout actual)
y documento de trabajo N.1/2018 (catálogos y definición del producto de seguimiento).

| Código | Variable | Validación |
|---|---|---|
| K009 | VBP | `K009 = K010 + K011` en 100,0% (±1) |
| K010 | consumo intermedio | `CI/VBP` mediana 0,636 |
| K011 | valor agregado | `VA/VBP` mediana 0,364 |
| K007 | ingresos por venta | `K007/VBP` mediana 1,000 |
| B001 | ingreso por fabricación propia | `corr(B001,K009) = 0,976` |
| I080 / I104 | ocupados con contrato / totales | mediana 39 / 42 |
| I081 | remuneraciones | — |

## Dos monedas (la trampa)

`A005` toma 4 (2.917 casos) y 5 (215); no calza con ningún catálogo: INE 2018 usa
1/2/3, CMF 999/013, ISO 4217 152/840. Es recodificación del INE — ninguna de las
277 columnas trae la distribución 1/2/3.

Prueba: remuneración por ocupado = 2.355 en el grupo 4 vs 2,6 en el grupo 5 →
razón **906**, del orden del tipo de cambio (943,58 en 2024). **4 = miles CLP,
5 = miles USD**; los establecimientos en USD son el **45,8% del VBP 2024**.

Salida en ISO 4217: `moneda_codigo` (interno), `moneda` (CLP/USD), `moneda_iso_num`
(152/840), `moneda_multiplo` (1000). No se convierte en la capa de datos: el
indicador aplica el dólar observado anual ([ficha del tipo de cambio](fx.html)).

## Limitaciones

1. `ID` no enlaza entre años (110 colisiones). El panel es otro producto (*base de
   seguimiento*, `ID_PLANTA` persistente) pero **sin región**: no hay panel y región
   a la vez en datos públicos.
2. CIIU de granularidad mixta: clase (2.632), grupo (205), división (129), sección
   (166). El puente CIIU→rama resuelve clase→grupo→división; queda sin rama solo la
   sección sin dígitos (5,8% del VBP).
3. La energía del bloque G está en dinero, no en TJ → para TJ se usa el BNE.
4. Sin descriptor: `K001–K004`, `K008`, `G009`, `G010`, `G017`, `G020` y parte de D/E/F/H.
5. Universo 10+ trabajadores: no cubre microindustria.
6. Montos nominales: requieren deflactor.

## Reproducción

```bash
python src/ingest/manual.py --source ine --dataset descriptor --year 2019 ...
python src/normalize/enia.py --years 2023 2024
python src/normalize/ciiu_bne.py
python src/ingest/fx.py && python src/normalize/fx.py
python src/audit/integracion_rama.py --year 2024
```

Salidas: `data/processed/enia/base/year=YYYY/part-0.parquet` (44 cols),
`enia_base.parquet`, `reports/normalizacion_enia.json`, `reports/integracion_rama_YYYY.csv`.

## Pendientes

- [x] Tipo de cambio anual (2023 = 839,07 · 2024 = 943,58).
- [x] Deflactor: IPP industria **base 2019 = 100** por división ([ficha del IPP](ipp.html)).
- [ ] Confirmar con el INE la recodificación de `A005` (la evidencia interna ya la fija:
      razón 906 entre grupos 4 y 5 contra un tipo de cambio de 943,58).
- [ ] Evaluar la base de seguimiento si se necesita panel.
- [x] `TAMANO`: 9 bandas de ocupación verificadas por sus límites.
- [ ] `CLASIFICACION` (A–F): no incide en los indicadores; la tasa de imputación sugiere
      estrato de calidad, no atributo de la empresa.
