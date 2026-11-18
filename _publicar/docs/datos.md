---
title: Datos publicados
---


# Datos publicados

Los parquet del repo, tal como salen de la cadena. Cada uno se regenera con los comandos de la [metodología](../metodologia.html); ninguno se edita a mano.

| Archivo | Filas | Columnas | Tamaño | Columnas principales |
|---|---:|---:|---:|---|
| [`data/processed/bcch/dolar_diario.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/bcch/dolar_diario.parquet) | 11.038 | 4 | 0,06 MB | `fecha`, `valor`, `fuente`, `anio` |
| [`data/processed/bcch/fx_anual.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/bcch/fx_anual.parquet) | 45 | 12 | 0,01 MB | `anio`, `fx_promedio`, `fx_mediana`, `fx_min`, `fx_max`, `n_dias`, `desde`, `hasta`, … (+4) |
| [`data/processed/cne/bne/bne_balance.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/cne/bne/bne_balance.parquet) | 3.180 | 8 | 0,02 MB | `anio`, `seccion`, `item`, `grupo_energetico`, `energetico`, `tcal`, `tj`, `es_total` |
| [`data/processed/cne/bne/ciiu4_map.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/cne/bne/ciiu4_map.parquet) | 22 | 6 | 0,00 MB | `categoria_bne`, `referencia_ciiu4`, `glosa`, `categoria_norm`, `anio`, `item_bne` |
| [`data/processed/cne/bne/ciiu4_rama.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/cne/bne/ciiu4_rama.parquet) | 399 | 5 | 0,00 MB | `codigo`, `seccion`, `digitos`, `rama_bne`, `rama_regla` |
| [`data/processed/cne/bne/year=2023/part-0.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/cne/bne/year=2023/part-0.parquet) | 1.590 | 8 | 0,01 MB | `anio`, `seccion`, `item`, `grupo_energetico`, `energetico`, `tcal`, `tj`, `es_total` |
| [`data/processed/cne/bne/year=2024/part-0.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/cne/bne/year=2024/part-0.parquet) | 1.590 | 8 | 0,01 MB | `anio`, `seccion`, `item`, `grupo_energetico`, `energetico`, `tcal`, `tj`, `es_total` |
| [`data/processed/enia/base/enia_base.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/enia/base/enia_base.parquet) | 6.283 | 44 | 0,34 MB | `id`, `anio`, `region`, `ciiu4`, `clasificacion`, `imputado`, `moneda_codigo`, `tamano`, … (+36) |
| [`data/processed/enia/base/year=2023/part-0.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/enia/base/year=2023/part-0.parquet) | 3.151 | 44 | 0,18 MB | `id`, `anio`, `region`, `ciiu4`, `clasificacion`, `imputado`, `moneda_codigo`, `tamano`, … (+36) |
| [`data/processed/enia/base/year=2024/part-0.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/enia/base/year=2024/part-0.parquet) | 3.132 | 44 | 0,18 MB | `id`, `anio`, `region`, `ciiu4`, `clasificacion`, `imputado`, `moneda_codigo`, `tamano`, … (+36) |
| [`data/processed/indicators/emisiones_division.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/indicators/emisiones_division.parquet) | 56 | 8 | 0,00 MB | `div`, `tco2`, `rama_principal`, `fuentes_co2`, `vbp_nominal_billones`, `vbp_real_billones`, `anio`, `econ_tco2_por_billon_clp2019` |
| [`data/processed/indicators/intensidad_rama.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/indicators/intensidad_rama.parquet) | 34 | 33 | 0,02 MB | `rama`, `energia_tj`, `energia_fosil_tj`, `establecimientos`, `share_usd`, `vbp_nominal_billones`, `vbp_real_billones`, `va_real_billones`, … (+25) |
| [`data/processed/ine/ipp/ipp_anual.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/ine/ipp/ipp_anual.parquet) | 128 | 9 | 0,01 MB | `nivel`, `codigo`, `glosa`, `anio`, `ipp`, `n_meses`, `empalmado`, `completo`, … (+1) |
| [`data/processed/ine/ipp/ipp_mensual.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/ine/ipp/ipp_mensual.parquet) | 1.872 | 7 | 0,02 MB | `nivel`, `codigo`, `glosa`, `anio`, `mes`, `ipp`, `empalmado` |
| [`data/processed/retc/anomalias.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/retc/anomalias.parquet) | 278 | 12 | 0,02 MB | `anio`, `id_vu`, `nombre_establecimiento`, `razon_social`, `ciiu4_id`, `co2`, `mediana_otras`, `ratio`, … (+4) |
| [`data/processed/retc/co2_combustible.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/retc/co2_combustible.parquet) | 92.672 | 20 | 2,09 MB | `anio`, `id_vu`, `rut_razon_social`, `razon_social`, `nombre_establecimiento`, `ciiu4_id`, `region_norm`, `source_id`, … (+12) |
| [`data/processed/retc/emisiones_fp/year=2023/part-0.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/retc/emisiones_fp/year=2023/part-0.parquet) | 339.543 | 47 | 7,11 MB | `anio`, `id_vu`, `razon_social`, `rut_razon_social`, `nombre_establecimiento`, `rubro`, `rubro_id`, `ciiu4`, … (+39) |
| [`data/processed/retc/emisiones_fp/year=2024/part-0.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/retc/emisiones_fp/year=2024/part-0.parquet) | 348.274 | 47 | 7,68 MB | `anio`, `id_vu`, `razon_social`, `rut_razon_social`, `nombre_establecimiento`, `rubro`, `rubro_id`, `ciiu4`, … (+39) |
| [`data/processed/retc/emisiones_fp/year=2025/part-0.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/retc/emisiones_fp/year=2025/part-0.parquet) | 340.799 | 47 | 7,62 MB | `anio`, `id_vu`, `razon_social`, `rut_razon_social`, `nombre_establecimiento`, `rubro`, `rubro_id`, `ciiu4`, … (+39) |
| [`data/processed/retc/energia_implicita.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/retc/energia_implicita.parquet) | 25 | 9 | 0,00 MB | `combustible_primario_norm`, `co2`, `grupo_bne`, `clase`, `ef_carbono_kg_c_gj`, `fuente`, `nota`, `tco2_por_tj`, … (+1) |
| [`data/processed/scenarios/escenarios_2030.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/scenarios/escenarios_2030.parquet) | 25 | 13 | 0,01 MB | `anio`, `escenario`, `rama`, `energia_tj`, `tco2`, `tco2_fosil`, `tco2_biomasa`, `tco2_proceso`, … (+5) |
| [`data/processed/scenarios/tornado_2030.parquet`](https://github.com/peterslapbass/terskel/blob/main/data/processed/scenarios/tornado_2030.parquet) | 6 | 4 | 0,00 MB | `palanca`, `min`, `max`, `amplitud` |

Cada parquet conserva las columnas declaradas de la fuente y agrega las derivadas con nombre explícito (`emision_retc`, `co2_fosil`, `factor_ajuste`, `cobertura_energetica`). Ninguna columna derivada reemplaza a la original.
