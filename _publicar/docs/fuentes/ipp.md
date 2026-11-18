---
title: "Ficha de fuente — IPP Industria Manufacturera (INE)"
---

# Ficha de fuente — IPP Industria Manufacturera (INE)

| Campo | Valor |
|---|---|
| Institución | INE |
| Producto | Índice de Precios de Productor (IPP), Industria Manufacturera |
| Portal | ine.gob.cl › precios-e-inflacion › indice-de-precios-de-productor |
| Acceso | navegador de carpetas (POST `hijosCarpeta` / `getArchivos`), sin URL fija |
| Base | **2019 = 100** |
| Frecuencia | mensual, por división CIIU Rev.4 |
| Cobertura | 2023-09 → 2026-09 (base 2019) · 2017-01 → 2023-08 (base 2014) |
| Estado | normalizada a Parquet, promedio anual |

## Qué mide

Precios de venta del productor industrial, no costos ni precios al consumidor.
Sirve para **deflactar** valores nominales de la ENIA (VBP, VA) y expresarlos en
pesos de 2019.

Divisiones publicadas (15): 10, 11, 12, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
28, 31. No se publican 13, 14, 15, 26, 29, 30, 32, 33 (secreto estadístico o
cobertura insuficiente): para esas se usa el total de manufactura.

## El empalme de 2023

La base 2019 solo se publica desde 2023-09, así que 2023 no tiene año completo. Se
empalma con la base 2014 usando un factor por división:

```
k = I_2019(2023-09) / [ I_2014(2023-08) × (1 + v_2019(2023-09)/100) ]
I_2019(m ≤ 2023-08) = I_2014(m) × k
```

Es el mismo criterio del INE, que **no** mantiene el nivel continuo: la serie
empalmada oficial de agosto 2023 vale 148,82 mientras la base 2014 marca 160,17.
El factor agregado calculado es **0,929403** contra 0,92914 de la serie empalmada
oficial → error **0,03%**. Encadenar solo por variaciones mensuales habría
sobrestimado 2023 en ~7%.

Los factores por división se dispersan (0,53 en la 18 a 1,68 en la 28): el cambio
de base no solo reescala, también recambia canastas y ponderaciones (la división 27
deja de publicarse, la 28 cambia de glosa). **Solo el agregado es verificable**
contra la serie empalmada del INE; el nivel 2023 por división es el eslabón más
débil y las comparaciones 2023→2024 por división deben leerse con cautela.

## Cifras de control (promedio anual, base 2019 = 100)

| Código | División | 2023 | 2024 | Var. 24/23 |
|---|---|---:|---:|---:|
| 00 | Industria Manufacturera | 149,85 | 156,55 | +4,5% |
| 10 | Alimentos | 154,63 | 161,12 | +4,2% |
| 17 | Papel | 133,20 | 150,61 | +13,1% |
| 23 | Minerales no metálicos (cemento) | 154,97 | 166,37 | +7,4% |
| 24 | Metales comunes (siderurgia) | 179,09 | 177,47 | −0,9% |

Uso: `VBP_real_2019 = VBP_nominal / (IPP / 100)`.

## Limitaciones

1. **Deflación simple.** Deflactar el VA con el IPP de producción es una
   aproximación; lo correcto sería doble deflación (precio de producto y de
   insumos). Se documenta como supuesto.
2. **Solo 15 divisiones.** Las divisiones sin IPP heredan el total de manufactura.
3. **2023 es empalmado** (`empalmado = true` en el Parquet) y arrastra el error de
   redondeo de las variaciones publicadas (≤0,05 pp por mes).
4. **2026 está incompleto** (`completo = false`): no usar como año cerrado.
5. El IPP mide precios **del productor**: no incorpora márgenes de comercio.

## Reproducción

```bash
python src/ingest/ipp.py
python src/normalize/ipp.py
```

Salidas:

- `data/raw/ine/ipp/base-{2019,2014}/industria_manufacturera_YYYY-MM-DD.csv`
- `data/processed/ine/ipp/ipp_mensual.parquet` (nivel × código × mes)
- `data/processed/ine/ipp/ipp_anual.parquet` (`anio, nivel, codigo, glosa, ipp, n_meses, empalmado, completo, base`)
- `reports/normalizacion_ipp.json` (factor k, validaciones, años incompletos)
