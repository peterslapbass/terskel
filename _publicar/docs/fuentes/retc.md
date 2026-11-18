---
title: "Ficha de fuente — RETC, emisiones al aire de fuentes puntuales"
---

# Ficha de fuente — RETC, emisiones al aire de fuentes puntuales

| Campo | Valor |
|---|---|
| Institución | MMA — Registro de Emisiones y Transferencias de Contaminantes |
| Portal | https://datosretc.mma.gob.cl/ |
| API | CKAN 3: `package_show?id=emisiones-al-aire-de-fuente-puntuales` |
| Licencia | ODbL |
| Cobertura | disponible 2005–2025 · descargada 2023–2025 |
| Formato | XLSX, hojas `Resumen` y `Data` (35 columnas) |
| Unidad de observación | establecimiento × fuente × contaminante × año |
| Unidad de emisión | **t/año** (inferencia documentada, ver abajo) |
| Extracción | 2023: 20/08/2026 · 2024–2025: 01/10/2026 |

## Qué contiene

- Planta: `id_vu`, razón social, RUT, nombre, lat/lon, región, provincia, comuna.
- Clasificación: `rubro` (19 categorías RETC), `ciiu4`/`ciiu6` Rev.4.
- Fuente: `declaracion_id`, `codigo_fuente`, `tipo_fuente`, combustible primario y
  secundario (`ccf8`).
- Emisiones: 18 contaminantes, con `emision_combustible_primario`, `_secundario`,
  `emision_procesos`, `emision_total`, `emision_retc`.

## Qué captura (2024, validado y ajustado)

No es un inventario industrial: es un registro de establecimientos sobre los umbrales
del D.S. 138/2005. Del CO₂ validado del país:

| Grupo | Mt CO₂ | % | Filas |
|---|---:|---:|---:|
| 14 categorías industriales (BNE-CIIU 4) | 25,20 | 56% | 8.156 |
| Generación eléctrica (CIIU 35) | 18,08 | 40% | 2.301 |
| Servicios, agua, residuos y construcción | 1,69 | 4% | 20.883 |
| **Total** | **44,97** | 100% | 31.340 |

Las 14 categorías son las que el balance separa ([ficha de indicadores](indicadores.html)).
La generación eléctrica entra completa, planta a planta. Y la gran minería aparece sin
su combustión: **Cobre recibe 42 kt de CO₂ donde el BNE le asigna 206.000 TJ**
(0,2 tCO₂/TJ). Es la limitación más grande de la fuente para cualquier inventario
industrial, no un problema de agregación.

## Trampa: `ciiu4` no es el código

`ciiu4` trae la **glosa**, `ciiu4_id` el **código con letra de sección** (`C1391`).
Para cruzar con ENIA o BNE: usar `ciiu4_id` y quitar la letra inicial. Igual en `ciiu6`.

## Las dos columnas de emisión

- `emision_total`: estimación del sistema sectorial RUEA.
- `emision_retc`: valor validado por el MMA; se anula cuando hay `outlier_procesos`
  (ratio producto/combustible inconsistente), `outlier_consumos` (sobre el máximo
  físico 24/7/365) u `outlier_tendencias` (DBSCAN).
- **Son dos universos distintos.** `emision_total` = `primario + secundario +
  procesos` (identidad exacta, error < 1e-8), y es **3,4 veces** `emision_retc` en
  2024 (164,3 Mt contra 48,7 Mt). No es que una columna repita filas: la
  declaración sectorial y la validación del MMA no coinciden, y la brecha cambia
  por año (ratio 0,45 en 2023 → 0,30 en 2024). Para agregar por rama o país hay
  que usar `emision_retc`; `emision_total` solo sirve como estructura.
- **Un `0` en `emision_retc` no significa "no emitió"**: 9,8% de las filas tienen 0
  con estimación RUEA positiva.
- `origen_data` documenta imputaciones (`MP = MP10 = MP2.5`, `SOx ≈ SO2`).

## Unidades de emisión

Guía: *Guía metodológica para la estimación de emisiones de fuentes puntuales*
(MMA/Greenlab 2021, 195 pp.), sha256 `2dca9252…294b40`.

- Cálculo: `Emisiones = FE × NA × (1 − EA/100)`.
- `FE` por unidad de actividad (`kg/ton`, `kg/m3`, `kg/Mg`).
- Umbrales del D.S. 138/2005 en **toneladas por año**.
- GEI: IPCC 2006 con `kg C/GJ` y PCI `kcal/kg` (Tabla 4-3, p. 149).

**La guía no declara la unidad de la columna publicada.** Evidencia de t/año:
umbral normativo en t/año; `FE × NA` da masa; magnitud — 65,4 Mt CO₂ en 2023 es
consistente con ~80 Mt del sector energía (en kg serían 65 mil t: imposible).

**Decisión**: se adopta **t/año** etiquetado como *inferencia documentada*. Si fuera
kg, las cifras absolutas se dividen por 1.000; los ratios no cambian.

## Reparto por origen del CO₂

`emision_retc` no trae desglose por combustible. `src/normalize/retc_co2_combustible.py`
usa la estructura declarada para repartirlo, sin estimar nada:

```
co2_clase = emision_retc × componente_clase / (primario + secundario + procesos)
```

| Clase | Qué incluye |
|---|---|
| `co2_fosil` | GLP, gas natural, carbón, petcoke, diésel, fuel oil y gases de proceso |
| `co2_biomasa` | licor negro, biomasa, aserrín, viruta, leña, carbón vegetal, biogás, tall oil |
| `co2_proceso` | calcinación y procesos químicos, no combustión |
| `co2_otro` | aceite usado y combustible sólido alternativo (origen mixto) |

Nacional 2024: 58,4% fósil · 39,6% biomasa · 1,8% proceso · 0,2% otro. La suma de
clases reproduce `emision_retc` exactamente (control en cada ejecución). Salida:
`data/processed/retc/co2_combustible.parquet` y `reports/retc_co2_combustible.md`.

## Las ediciones no son comparables entre sí

| Edición | CO₂ nacional | Exceso demostrable | Nacional sin el exceso |
|---|---:|---:|---:|
| 2023 | 65,4 Mt | 17,0 Mt (26%) | 48,4 Mt |
| 2024 | 48,7 Mt | 3,7 Mt (7,7%) | 45,0 Mt |
| 2025 | 47,0 Mt | 0,1 Mt (0,4%) | 46,9 Mt |

**El bloque GLP de 2023 está inflado ~12×**: 16,15 Mt contra 1,32 Mt en 2024 y
1,10 Mt en 2025, con el mismo número de declaraciones (3.130 / 3.198 / 3.202). Es un
defecto del factor de emisión de esa edición, no de las empresas. Todos los casos
extremos lo comparten, como combustible primario o secundario.

Cada edición trae su propio defecto: 2023 el GLP; 2024 Cartocor (3,05 Mt, 86% del
exceso de ese año); 2025 déficits de consumidores de gas compatibles con una edición
aún abierta. El cribado está en
[cribado de anomalías](../resultados/retc_anomalias.html).

### Cómo se aplica

`src/common/calidad.py` capa los **excesos** a la mediana de las otras dos ediciones
—un valor que la misma planta declaró— y deja los déficits intactos: un consumo que
no aparece puede ser una edición sin cerrar, y subirlo sería inventar. El factor
multiplica todas las columnas de emisión de la fila, así que el reparto por origen se
conserva. 2024 pierde 3,16 Mt en 19 plantas; 2023, 10,30 Mt en 52.

El ajuste se aplica en los indicadores y en la reconversión a energía; el parquet de
la fuente (`co2_combustible.parquet`) queda con el dato declarado, más una columna
`emision_retc_declarada` cuando pasa por el ajuste.

## Limitaciones

1. Solo dos combustibles por fuente: mezcla energética subrepresentada.
2. **Las ediciones no son comparables**: 2023 trae el GLP inflado ~12×, 2024 el error
   de Cartocor y 2025 déficits de gas. Cualquier variación interanual mezcla señal y
   defecto de edición; se usa 2024 como año de referencia.
3. Nombres sucios en `tipo_fuente` y combustibles.
4. ~60% de las filas son grupos electrógenos, no proceso industrial.
5. Sin diccionario de unidades ni factores en el archivo.
6. **Un error de unidad pasa la validación**: Cartocor declaró 3,05 Mt de CO₂ en
   2024 contra 5,8 kt en 2023 y 5,7 kt en 2025 (factor 526) y `emision_retc` lo
   acepta. Se detecta por el cribado y se capa al valor de referencia; el declarado
   queda en `emision_retc_declarada`.
7. El reparto por origen hereda la mezcla declarada: si una planta declara mal su
   combustible, el split lo copia. Lo que queda exacto es el total.
8. **Huachipato no declara carbón ni coque.** La planta declara solo gases de
   subproducto (alto horno, coque, coque diluido) y diésel: 64.554 t de CO₂ en 2024.
   Implican ~421 TJ, contra 5.233 TJ del ítem `Siderurgia` del BNE. Faltan el carbón
   de los hornos de coque y el coque del alto horno, que a 97,5 t CO₂/TJ sumarían
   ~450 kt. La rama está subdeclarada por un factor 7–8 y su tCO₂/TJ de 10,9 no es
   una propiedad del acero, es un artefacto de cobertura. Por eso **Siderurgia no es
   publicable**. Ver [ficha de energía implícita](energia_implicita.html).

## Reproducción

```bash
python src/ingest/retc.py --years 2023 2024 2025   # idempotente, sha256 en manifest
python src/normalize/retc.py --years 2023 2024 2025
python src/normalize/retc_co2_combustible.py       # split fósil/biomasa/proceso
python src/audit/retc_audit.py                     # reports/retc_auditoria.md
python src/audit/retc_anomalias.py                 # cribado por edición
```

## Pendientes

- [x] Unidad de emisión documentada como t/año.
- [ ] Confirmar formalmente (RUEA/F138 o contacto MMA); el contraste con el BNE ya
      descarta un error de escala (las razones energía implícita/BNE son de orden 1).
- [x] Columna oficial: `emision_retc` (la única aditiva).
- [x] Reparto del CO₂ por origen (fósil/biomasa/proceso).
- [x] Energía implícita contrastada con el BNE por combustible.
- [x] Tratamiento de outliers por planta: cribado y capado (`src/common/calidad.py`).
- [x] Auditoría de Siderurgia: Huachipato no declara carbón ni coque.
- [x] Cribado de anomalías por edición: el GLP de 2023 está inflado ~12×.
- [x] Auditoría de Láctea 2023: Planta Osorno declaró 193× su propia serie de 2024-25.
- [ ] Verificar deriva de esquema al extender a 2005–2015.
