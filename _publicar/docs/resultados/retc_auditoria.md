---
title: Auditoría del RETC
---

# Auditoría RETC — emisiones al aire de fuentes puntuales

Años auditados: **2023, 2024, 2025**  
Filas totales: **1,028,616**  
Fuente: `datosretc.mma.gob.cl`, conjunto `emisiones-al-aire-de-fuente-puntuales` (licencia ODbL).

> **Unidad de emisión:** no viene declarada ni en los datos ni en la hoja `Resumen`.
> Se adopta **t/año** como inferencia documentada desde la guía metodológica RETC
> (umbrales en t/año, FE en kg/unidad de actividad, y magnitud: 65,4 M de CO₂ en 2023
> frente a ~80 Mt CO₂ del sector energía del país). Ver `docs/fuentes/retc.md#unidades-de-emisión`.
> Falta solo la confirmación formal (formulario RUEA/F138).
> Todo lo que sigue se expresa en **toneladas/año**.

## 1. Volumen y cobertura

| anio | filas | establecimientos | declaraciones | contaminantes | rubros | ciiu4 | combustibles | regiones |
|---|---|---|---|---|---|---|---|---|
| 2023 | 339,543 | 12,560 | 12,560 | 18 | 19 | 276 | 28 | 16 |
| 2024 | 348,274 | 12,794 | 12,794 | 18 | 19 | 271 | 27 | 16 |
| 2025 | 340,799 | 12,159 | 12,159 | 18 | 19 | 265 | 24 | 16 |

## 2. Esquema

- Columnas por año: 2023: 47, 2024: 47, 2025: 47
- Esquema idéntico entre años: **sí**

## 3. Persistencia de establecimientos (`id_vu`)

| comparación | intersección | solo en el primero | solo en el segundo | Jaccard |
|---|---|---|---|---|
| 2023 vs 2024 | 11,259 | 1,301 | 1,535 | 79.9% |
| 2024 vs 2025 | 10,963 | 1,831 | 1,196 | 78.4% |

- Presentes en los 3 años: **9,785** establecimientos.

## 4. Estabilidad de atributos para el mismo establecimiento

| atributo | establecimientos_comparados | cambian | pct |
|---|---|---|---|
| rubro | 10,113 | 0 | 0.0 |
| ciiu4 | 10,113 | 0 | 0.0 |
| region | 10,113 | 0 | 0.0 |
| comuna | 10,113 | 0 | 0.0 |

Comparación 2023 → 2025 sobre establecimientos presentes en ambos años.

## 5. Calidad de las columnas de emisión

| control | casos |
|---|---|
| emision_retc_nulos | 0 |
| emision_total_nulos | 1,051 |
| retc_distinto_de_total | 127,503 |
| retc_en_cero | 107,341 |
| retc_cero_con_estimacion_positiva | 101,291 |
| componentes_nulas | 0 |
| total_distinto_de_suma | 1,360 |

- `emision_retc` en cero con estimación RUEA positiva: **9.8%** de las filas.
  Tratar ese 0 como «no emitió» sesga el análisis: son valores validados como no confiables, no mediciones de cero.
- `emision_retc` difiere de `emision_total` en **12.4%** de las filas.

### Nulos por columna (todas las filas)

| columna | nulos | pct |
|---|---|---|
| ccf8_procesos | 1,015,847 | 98.8 |
| ccf8_secundario | 986,124 | 95.9 |
| combustible_secundario | 983,103 | 95.6 |
| combustible_secundario_norm | 983,103 | 95.6 |
| razon_social | 4,367 | 0.4 |
| emision_combustible_primario | 1,051 | 0.1 |
| emision_combustible_secundario | 1,051 | 0.1 |
| emision_procesos | 1,051 | 0.1 |
| emision_total | 1,051 | 0.1 |

## 6. Cobertura por contaminante

| contaminante | 2023 | 2024 | 2025 |
|---|---|---|---|
| Carbon monoxide | 12,560 | 12,794 | 12,159 |
| Carbon dioxide | 12,560 | 12,794 | 12,159 |
| Sulfur oxides (SOx) | 12,560 | 12,794 | 12,159 |
| PM10, primary | 12,552 | 12,787 | 12,154 |
| PM, primary | 12,552 | 12,787 | 12,154 |
| PM2.5, primary | 12,552 | 12,787 | 12,154 |
| Sulfur dioxide | 12,508 | 12,747 | 12,118 |
| Nitrogen oxides (NOx) | 12,201 | 12,511 | 11,916 |
| Benzene | 12,120 | 12,359 | 11,774 |
| Toluene | 11,821 | 12,069 | 11,525 |
| Methane | 4,232 | 4,206 | 3,950 |
| Nitrous oxide | 2,949 | 2,905 | 2,673 |
| Lead | 2,934 | 2,896 | 2,669 |
| Arsenic | 2,928 | 2,893 | 2,663 |
| Ammonia | 2,608 | 2,552 | 2,348 |
| Volatile organic compounds (VOC) | 2,302 | 2,319 | 2,193 |
| Mercury | 2,156 | 2,160 | 2,033 |
| PCDD-F | 1,073 | 1,117 | 1,069 |

## 7. Rubros: tamaño y emisión de CO₂

| rubro | establecimientos | filas | emision_retc | pct_emision |
|---|---|---|---|---|
| Termoeléctricas | 202 | 3,737 | 5.673e+07 | 35.2 |
| Industria del papel y celulosa | 61 | 695 | 5.362e+07 | 33.3 |
| Otras industrias manufactureras | 1,280 | 10,309 | 1.614e+07 | 10.0 |
| Otras actividades | 6,573 | 35,683 | 6.22e+06 | 3.9 |
| Industria química, de plástico y caucho | 221 | 1,581 | 5.912e+06 | 3.7 |
| Gestores de residuos | 50 | 263 | 5.835e+06 | 3.6 |
| Industria de la madera y silvicultura | 163 | 1,173 | 4.461e+06 | 2.8 |
| Refinería de petróleo | 16 | 367 | 3.824e+06 | 2.4 |
| Minería | 188 | 6,958 | 3.003e+06 | 1.9 |
| Producción de cemento, cal y yeso | 22 | 138 | 2.266e+06 | 1.4 |
| Comercio minorista | 2,111 | 10,526 | 1.256e+06 | 0.8 |
| Pesca y acuicultura | 908 | 5,566 | 8.49e+05 | 0.5 |
| Otras centrales de generación eléctrica | 248 | 1,949 | 5.868e+05 | 0.4 |
| Producción agropecuaria | 465 | 2,575 | 2.879e+05 | 0.2 |
| Construcción | 293 | 1,792 | 8.451e+04 | 0.1 |
| Captación, tratamiento y distribución de agua | 1,420 | 5,037 | 4.347e+04 | 0.0 |
| Plantas de tratamiento de aguas servidas | 297 | 926 | 3.281e+04 | 0.0 |
| Comercio mayorista | 282 | 2,932 | 1.687e+04 | 0.0 |
| Ventas y mantención de vehículos automotores | 163 | 465 | 2,548 | 0.0 |

### CO₂ por año

| anio | filas | establecimientos | emision_retc | emision_total | filas_en_cero | pct_en_cero |
|---|---|---|---|---|---|---|
| 2023 | 30,519 | 12,560 | 6.544e+07 | 1.463e+08 | 2,904 | 9.5 |
| 2024 | 31,340 | 12,794 | 4.871e+07 | 1.643e+08 | 2,624 | 8.4 |
| 2025 | 30,813 | 12,159 | 4.702e+07 | 8.94e+07 | 2,389 | 7.8 |

> **Alerta de continuidad:** la suma de CO₂ cae 26% entre 2023 y 2024 y luego 3% en 2025,
> mientras `emision_total` sube 12% y luego cae 46%. Las dos columnas cuentan historias
> distintas porque las revisiones del MMA cambian qué valores se validan y cuáles se anulan.
> No hay serie temporal publicable con ninguna de las dos sin un tratamiento explícito.

### Continuidad por establecimiento (CO₂, misma planta en dos años)

| transición | plantas_en_ambos | positivo→cero | cero→positivo | positivo→positivo |
|---|---|---|---|---|
| 2023→2024 | 11,259 | 124 | 154 | 10,745 |
| 2024→2025 | 10,963 | 97 | 150 | 10,511 |

### Mayores revisiones de valor (CO₂, primer par de años)

| establecimiento | rubro | e0 | e1 | delta |
|---|---|---|---|---|
| RELLENO SANITARIO SANTA MARTA | Gestores de residuos | 5.749e+06 | 23.79 | -5.749e+06 |
| SAN CLEMENTE FOODS SA | Otras industrias manufactureras | 5.554e+06 | 251.6 | -5.554e+06 |
| ENAEX PLANTA RIO LOA | Industria química, de plástico y caucho | 2.634e+06 | 6.295e+05 | -2.004e+06 |
| PLANTA OSORNO | Otras industrias manufactureras | 1.979e+06 | 1.108e+04 | -1.968e+06 |
| CMPC CELULOSA PLANTA LAJA | Industria del papel y celulosa | 2.489e+06 | 1.056e+06 | -1.434e+06 |
| PLANTA VALDIVIA | Industria del papel y celulosa | 1.757e+06 | 2.455e+06 | 6.985e+05 |
| PLANTA ARAUCO | Industria del papel y celulosa | 3.854e+06 | 4.579e+06 | 7.245e+05 |
| CARTOCOR CHILE SA | Industria del papel y celulosa | 5,791 | 3.049e+06 | 3.043e+06 |

- Las **5 mayores caídas explican 90%** del cambio total (-18,473,914 unidades).
- Un relleno sanitario que pasa de 5,7 millones a 24 unidades en un año no es una mejora ambiental:
  es una revisión de dato o un cambio de unidad/metodología en origen.
- Conclusión: la serie no se puede publicar sin detección y tratamiento de outliers por planta.

## 8. Tipo de fuente declarado

| tipo_fuente | filas | establecimientos | pct_filas |
|---|---|---|---|
| Grupo Electrógeno | 615,136 | 13,459 | 59.8 |
| Caldera Agua Caliente | 243,995 | 3,182 | 23.7 |
| Caldera Industrial (Generadora de Vapor o Agua Caliente) | 49,256 | 688 | 4.8 |
| Horno de Panaderia | 44,818 | 698 | 4.4 |
| Horno de Panadería | 27,932 | 454 | 2.7 |
| Motor Generacion Electrica | 10,772 | 72 | 1.0 |
| Motor Generación Eléctrica | 8,870 | 75 | 0.9 |
| Caldera de Fluido Térmico | 4,465 | 83 | 0.4 |
| Horno | 3,771 | 32 | 0.4 |
| Grupo Electrogeno | 3,750 | 118 | 0.4 |
| Turbina de Gas | 2,576 | 38 | 0.3 |
| Horno Proceso | 2,214 | 3 | 0.2 |
| Caldera de Generación Eléctrica | 1,515 | 27 | 0.1 |
| Horno Rotatorio | 1,130 | 26 | 0.1 |
| Convertidor Pierce Smith (CPS) | 949 | 7 | 0.1 |

- Filas de grupos electrógenos: **618,886** (60.2%). No son proceso industrial: se excluyen por defecto en los indicadores, no del dataset.

## 9. Combustibles primarios por emisión de CO₂

| combustible_primario | filas | establecimientos | emision_retc | pct_emision |
|---|---|---|---|---|
| Licor Negro | 27 | 8 | 3.752e+07 | 23.28 |
| Carbón Bituminoso Pulverizado | 41 | 8 | 3.166e+07 | 19.64 |
| Gas Natural | 13,716 | 2,085 | 3.089e+07 | 19.17 |
| Gas Licuado de Petróleo | 9,530 | 1,739 | 1.858e+07 | 11.53 |
| Biomasa Combustible | 826 | 270 | 1.815e+07 | 11.26 |
| Petróleo N 2 (Diesel) | 66,343 | 13,951 | 6.64e+06 | 4.12 |
| Carbón Sub Bituminoso | 11 | 2 | 5.027e+06 | 3.12 |
| Coke de Petróleo (Petcoke) | 28 | 7 | 3.73e+06 | 2.31 |
| Petróleo N 6 | 368 | 76 | 2.319e+06 | 1.44 |
| Gas de Refinería | 194 | 2 | 2.081e+06 | 1.29 |
| Propano | 68 | 9 | 1.738e+06 | 1.08 |
| Carbón Bituminoso | 58 | 17 | 9.1e+05 | 0.56 |

## 10. Hallazgos y decisiones

1. **Esquema estable** en el piloto: 35 columnas idénticas en los tres años. La deriva de esquema habrá que verificarla al extender la serie hacia 2005–2015.
2. **Los `id_vu` no son un panel perfecto**: 9.785 plantas están en los tres años (Jaccard ~78–80% entre pares). Cualquier serie por establecimiento debe declarar su base de comparación.
3. **Los atributos del establecimiento sí son estables**: rubro, CIIU4, región y comuna no cambian para el mismo `id_vu`. El registro de establecimientos funciona como maestro fijo.
4. **No usar `emision_retc` como verdad absoluta**: 9,8% de las filas tienen `0` que significa «dato no confiable», no «emisión nula».
5. **La serie está rota por revisiones puntuales**: 5 plantas explican 90% de la caída de CO₂ 2023→2024. Sin detección de outliers por planta no hay tendencia publicable.
6. **Separar grupos electrógenos** (60% de las filas) del análisis industrial desde el primer indicador.
7. **Unidad resuelta por inferencia documentada** (t/año, ver encabezado): habilita el cálculo, la publicación espera la confirmación formal.

### Decisiones abiertas

- [x] Unidad de emisión: documentada como t/año (inferencia desde la guía metodológica).
- [ ] Confirmación formal de la unidad (formulario RUEA/F138 o contacto MMA).
- [ ] Elegir columna oficial de emisión: `emision_retc` (validada) vs `emision_total` (estimada RUEA).
- [ ] Definir si los ceros de `emision_retc` se imputan, se excluyen o se marcan.
- [ ] Confirmar factores de emisión por combustible para reconstruir TJ.

