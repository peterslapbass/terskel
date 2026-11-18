---
title: "Ficha de fuente — BNE (Balance Nacional de Energía, CNE)"
---

# Ficha de fuente — BNE (Balance Nacional de Energía, CNE)

| Campo | Valor |
|---|---|
| Institución | CNE / Ministerio de Energía |
| Portal | https://energiaabierta.cl/categorias-estadistica/balance-energetico |
| Cobertura descargada | 2023, 2024 |
| Formato | XLSX, 37 hojas |
| Unidad | **Tcal** en la hoja `Balance de energía`; **1 Tcal = 4,1868 TJ** |
| Estado | normalizada a Parquet |

## Qué contiene

Hoja `Balance de energía` = matriz: 53 ítems en 3 secciones (`OFERTA`,
`C.TRANSFORMAC`, `DEMANDA DE ENERGÍA`) × 29 energéticos + `TOTAL`.

Bajo `DEMANDA DE ENERGÍA` está `Sector Industrial y Minero`, con 14 ramas: Cobre,
Salitre, Hierro, Papel y Celulosa, Siderurgia, Petroquímica, Cemento, Azúcar, Pesca,
Agroindustria, Construcción, Industria Láctea, Industrias Varias y Minas Varias.

La hoja **`BNE-CIIU 4`** publica el puente explícito:

| Categoría BNE | CIIU Rev.4 |
|---|---|
| Papel y Celulosa | división 17 |
| Cemento | clase 2394 |
| Azúcar | clase 1072 |
| Siderurgia | grupo 241 |
| Petroquímica | división 20 |
| Industria Láctea | clase 1050 |
| Industrias Varias | divisiones 1, 2, 10–16, 18, 21–32 (resto) |

Ese puente conecta energía (BNE), emisiones (RETC) y actividad (ENIA), todos CIIU4.
Los rótulos cambian entre ediciones (`SIDERÚRGIA`/`SIDERÚRGICA`); el Parquet agrega
`categoria_norm` (sin tildes) e `item_bne`: 22 categorías, 21 con ítem asignado.

## Validaciones (1.590 filas/año)

- `TOTAL` = suma de los 29 energéticos en los 53 ítems (diferencia 0).
- `Sector Industrial y Minero` = suma de sus 14 ramas (diferencia relativa 0).

## Cifras de control

| Concepto | 2023 | 2024 |
|---|---:|---:|
| Consumo final total (Tcal) | 327.090 | 329.250 |
| Sector industrial y minero (Tcal) | 121.316 | 122.199 |
| **Manufactura** (TJ) | 230.092 | 236.894 |
| **Minería** (TJ) | 238.576 | 237.254 |

Manufactura = Papel y Celulosa, Siderurgia, Petroquímica, Cemento, Azúcar, Láctea e
Industrias Varias (CIIU 10–33). Se excluyen minería (Cobre, Salitre, Hierro, Minas
Varias) y Pesca, Agroindustria y Construcción, que el BNE agrupa en "industrial".

## Limitaciones

1. **Nacional**, sin desagregación regional.
2. **Categorías fijas**: 7 manufactureras, no 24 divisiones CIIU. La intensidad solo
   se publica a ese nivel.
3. **`Industrias Varias` es cajón residual** (~46% de la energía manufacturera): el
   bloque más heterogéneo.
4. **Incluye biomasa y licor negro** (biogénico): para comparar con emisiones fósiles
   hay que separar por energético, no usar el total.
5. **El licor negro está subrepresentado.** El BNE registra 22.818 TJ en 2024; el
   CO₂ biogénico del RETC implica ~128.000 TJ al factor de la guía (ver
   [ficha de energía implícita](energia_implicita.html)). La CNE parece contabilizar solo
   la fracción que entra a autoproducción.
5. **La serie se revisa**: 2024 puede traer cifras corregidas de años previos.
6. **La equivalencia BNE ↔ CIIU no es una partición**: hay solapes (divisiones 36–39
   en `SANITARIAS` y `COMERCIO Y SERVICIO`) y categorías que no representan al CIIU
   real — `Petroquímica` declara ~200 TJ para toda la división 20, mientras la ENIA
   reporta 198 establecimientos químicos con VBP de 13 billones de CLP; su energía
   está en `Industrias Varias`. **Intensidad publicable solo para Papel y Celulosa,
   Cemento, Siderurgia y Láctea**, y aun así depende de que la ENIA codifique a 4 dígitos.

## Reproducción

```bash
python src/ingest/manual.py --source cne --dataset bne --year 2024 --file "..." ^
  --url "https://energiaabierta.cl/categorias-estadistica/balance-energetico" ^
  --license "Datos abiertos CNE (citando fuente)"
python src/normalize/bne.py --years 2023 2024
python src/audit/bne_resumen.py
```

Salidas: `data/processed/cne/bne/year=YYYY/part-0.parquet`, `bne_balance.parquet`,
`ciiu4_map.parquet`, `reports/normalizacion_bne.json`, `reports/bne_industria_ramas.csv`.
