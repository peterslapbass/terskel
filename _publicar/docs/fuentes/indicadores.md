---
title: "Ficha — Indicadores de intensidad (energía y emisiones)"
---

# Ficha — Indicadores de intensidad (energía y emisiones)

| Campo | Valor |
|---|---|
| Cobertura | 2023, 2024 · 14 industrias identificables; 4 publicables |
| Numeradores | energía BNE (TJ) · CO₂ RETC (t/año, ajustado por cribado) |
| Denominadores | VBP y VA de la ENIA en CLP constantes de 2019 |
| Salida | `data/processed/indicators/*.parquet` · `reports/indicadores_intensidad.md` |
| Estado | calculado; intensidad publicable en 3 industrias; año base 2024 |

## Dos familias, nunca mezcladas

| Columna | Fórmula | Unidad | Familia |
|---|---|---|---|
| `econ_tj_por_billon_clp2019` | `TJ / (VBP_real/10¹²)` | TJ por billón CLP2019 | económica |
| `econ_tco2_por_billon_clp2019` | `tCO₂ / (VBP_real/10¹²)` | tCO₂ por billón CLP2019 | económica |
| `fis_tco2_por_tj_total` | `tCO₂ total / TJ total` | tCO₂/TJ | física |
| `fis_tco2_por_tj_fosil` | `tCO₂ fósil / TJ fósil` | tCO₂/TJ | física |
| `fis_mwh_por_ocupado` | `TJ × 277,78 / ocupados` | MWh/persona | física |

El CO₂ se usa desglosado por origen: `tco2_fosil`, `tco2_biomasa`, `tco2_proceso`
([retc.md](retc.md#reparto-por-origen-del-co2)). `tco2` es el total validado y
ajustado por el cribado de ediciones ([retc.md](retc.md#las-ediciones-no-son-comparables-entre-sí)).

`VBP_real = VBP_nominal × FX_anual / (IPP_división / 100)`, con FX del BCCh y el
IPP base 2019 ([ficha del IPP](ipp.html)). Si la división no publica IPP se usa el total de
manufactura.

## Supuestos

1. **CO₂ = `emision_retc` ajustado** y nada más. `emision_total` (RUEA) mide otra
   cosa: es 3,4 veces el validado en 2024 (164 Mt contra 48,7 Mt). El desglose por
   origen reparte el total con la estructura declarada. El ajuste capa los excesos
   planta-año a la mediana de las otras dos ediciones; no imputa valores externos.
2. **Energía BNE**: sección `DEMANDA DE ENERGÍA`, fila del ítem con `es_total`;
   la parte fósil excluye biomasa, licor negro, biogás y pellet.
3. **Mapeo CIIU→industria**: las 14 categorías de la tabla `BNE-CIIU 4` del
   balance (clase 2394 Cemento, clase 1072 Azúcar, clase 1050 Láctea, clase 0891
   Salitre, clase 0729 Cobre, grupo 071 Hierro, grupo 241 Siderurgia, división 17
   Papel, división 20 + metanol Petroquímica, divisiones 06 y 19 Refinería,
   división 03 Pesca, divisiones 07–08 Minas Varias, divisiones 01–02 Agroindustria,
   resto de 10–32 Industrias Varias). El código vive en `src/common/industrias.py`.
4. **Deflación simple**: el VA se deflacta con el IPP de producción; no hay doble
   deflación (precio de insumos).

## Qué se identifica y qué se publica

Catorce categorías industriales: siete manufactureras, una de refino y extracción de
petróleo y gas, y seis primarias o extractivas. Fuera quedan comercio, servicios,
transporte, construcción y sector público: el balance no los separa como demanda
industrial. `Producción de Metanol` se suma a Petroquímica porque el RETC no puede
separarlas (ambas son CIIU 2011).

Dos pruebas deciden la publicación: (a) **combustión capturada**, medida como energía
implícita en el CO₂ fósil sobre la energía que el BNE asigna a la industria
(`cobertura_energetica`, resumida en `captura_retc`: sí / parcial / no / excede);
(b) **CO₂ no concentrado** en una sola planta.

| Industria | Cobertura | RETC | Publica física | Motivo |
|---|---:|:---:|:---:|---|
| Papel y Celulosa | 56% | sí | sí | Cartocor declaró 3,05 Mt en 2024; capada a 5,8 kt |
| Industria Láctea | 71% | sí | sí | 2023 capado (Osorno, 1,98 Mt → 10,2 kt) |
| Refinería y Extracción Petróleo y Gas | 66% | sí | sí | solo 2024: el ítem del BNE cae 53% entre ediciones |
| Cemento | 22% | parcial | sí | física con reserva; económica **no**: el VBP cubre 4 plantas |
| Azúcar | 92% | sí | **no** | una sola planta explica 99,96% del CO₂ fósil: es un caso |
| Industrias Varias | 26% | parcial | **no** | cajón residual de 6 divisiones |
| Pesca | 24% | parcial | **no** | el RETC no captura todo el combustible de la flota |
| Hierro | 14% | parcial | **no** | una planta explica 99% del CO₂ fósil |
| Minas Varias | 11% | parcial | **no** | una planta explica 78% del CO₂ fósil |
| Siderurgia | 7% | no | **no** | Huachipato no declara carbón ni coque |
| Salitre | 4% | no | **no** | cobertura mínima |
| Agroindustria | 1% | no | **no** | la ENIA no cubre las divisiones 01–02 |
| Cobre | 0,3% | no | **no** | el RETC captura 42 kt de CO₂ donde el BNE asigna 206.000 TJ |
| Petroquímica (con metanol) | 249% | excede | **no** | el RETC declara 3× la energía que el BNE asigna a la división 20 + metanol |

**El hallazgo de Cobre**: es el ítem industrial más grande del balance (206.000 TJ,
39% de la energía de las 14 categorías) y el RETC le imputa 42 kt de CO₂, un
0,2 tCO₂/TJ imposible. La gran minería del cobre no declara su combustión al RETC.
Cualquier inventario que use esa fuente subestima el sector en más de un orden de
magnitud.

Las columnas `publicable_fisica`, `publicable_economica` y `captura_retc` marcan esto
en el Parquet.

## Qué captura el RETC

El RETC es un registro de establecimientos sobre los umbrales del D.S. 138/2005, no un
inventario industrial. Validado y ajustado, 2024 queda así:

| Grupo | Mt CO₂ | % | Filas |
|---|---:|---:|---:|
| Categorías industriales (14) | 25,20 | 56% | 8.156 |
| Generación eléctrica (CIIU 35) | 18,08 | 40% | 2.301 |
| Servicios, agua, residuos y construcción | 1,69 | 4% | 20.883 |
| **Total** | **44,97** | 100% | 31.340 |

Se calcula en `universo_retc()` y se regenera en cada corrida. Las diferencias con el
BNE no son un vacío del registro: son actividades que el registro no obliga a
declarar (la gran minería) o que declara otra unidad (la generación eléctrica, que el
balance asigna a su propio ítem).

## Tercera capa: división CIIU

La división de 2 dígitos es la unidad más fina que comparten el RETC y la ENIA. El
BNE no baja de las 14 categorías, así que ahí no hay energía: solo CO₂ por peso
producido (`emisiones_division.parquet`, 21 divisiones con VBP). Sirve para ver
dentro de Industrias Varias, no para intensidad energética.

## Limitaciones

1. **Cota superior.** El denominador cubre 10+ trabajadores; la energía del BNE
   cubre toda la industria. Sirve para comparar ramas y años, no como nivel.
2. **Solo 4 de 14 industrias publican intensidad física.** Las otras diez se
   cuantifican y se marcan con su motivo (tabla arriba). Petroquímica no cierra
   porque, aun sumando el metanol que el BNE separa, el RETC declara 3× la energía
   de la división 20; e Industrias Varias es residual.
3. **Cobre: el RETC no cubre la gran minería.** Es el ítem industrial más grande del
   BNE (206.000 TJ) y el RETC le imputa 42 kt de CO₂ (0,2 tCO₂/TJ). No publicable, y
   la advertencia sirve para cualquier inventario hecho sobre esa fuente.
4. **Siderurgia no es publicable.** Huachipato declara solo gases de subproducto:
   ~421 TJ implícitos contra 5.233 TJ del ítem `Siderurgia` del BNE. El carbón de
   los hornos de coque y el coque del alto horno no están en el RETC, y el ítem del
   BNE tampoco los incluye. Ni la intensidad física ni la económica son defendibles.
5. **Concentración en una planta.** En 2023 CMPC Laja explica 61% del CO₂ fósil de
   Papel, Enaex Río Loa 74% de Petroquímica y Huachipato 97% de Siderurgia. Se marca
   en `alerta` y se publica la sensibilidad "sin esa planta".
6. **Ajuste por cribado.** Los excesos planta-año se capan a la mediana de las otras
   dos ediciones: 2024 pierde 3,16 Mt en 19 plantas (Cartocor, 3,05) y 2023 pierde
   10,30 Mt en 52. El resto de 2023 queda sin verificar (Enaex Río Loa, por ejemplo),
   así que la serie no se lee como tendencia: **el año de referencia es 2024**. Ver
   [ficha del RETC](retc.html) y [cribado de anomalías](../resultados/retc_anomalias.html).
7. **CO₂ biogénico**: ya separado. El `tCO₂/TJ fósil` de Papel pasó de 502 (CO₂ total
   sobre TJ fósil) a 112,8 al excluir licor negro y biomasa; con Cartocor capada
   queda en 38,3.
8. **Sin región**: el BNE es nacional; la ENIA tiene región, pero la energía no.

## Reproducción

```bash
python src/normalize/retc_co2_combustible.py
python src/audit/retc_anomalias.py
python src/indicators/intensidad.py
```

Requiere haber corrido antes: `enia.py`, `bne.py`, `retc.py`, `retc_co2_combustible.py`,
`fx.py`, `ipp.py`.
