# Indicadores de intensidad — energía y emisiones (2023–2024)

Dos familias separadas. **Económica** (`econ_*`): por peso de producto, CLP
constantes de 2019 (VBP de la ENIA deflactado con el IPP por división).
**Física** (`fis_*`): por unidad física (TJ, ocupado).

## Por rama, 2024 (manufactura)

| Rama | TJ | TJ fósil | VBP real | tCO₂ | tCO₂ fósil | TJ/billón CLP2019 | tCO₂/billón CLP2019 | tCO₂/TJ total | tCO₂/TJ fósil |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Industrias Varias | 112,854 | 103,457 | 28.4 | 3,603,503 | 1,648,523 | 3,974 | 126,896 | 31.9 | 15.9 |
| Papel y Celulosa | 105,252 | 40,838 | 3.5 | 17,485,123 | 1,564,747 | 29,725 | 4,938,108 | 166.1 | 38.3 |
| Cemento | 10,487 | 10,487 | 0.1 | 747,603 | 213,794 | 157,393 | 11,220,589 | 71.3 | 20.4 |
| Petroquímica | 8,947 | 8,947 | 7.1 | 1,506,165 | 1,501,857 | 1,266 | 213,094 | 168.3 | 167.9 |
| Siderurgia | 5,233 | 5,233 | 0.8 | 65,740 | 56,960 | 6,403 | 80,431 | 12.6 | 10.9 |
| Industria Láctea | 1,675 | 1,675 | 1.7 | 242,946 | 75,855 | 992 | 143,921 | 145.1 | 45.3 |
| Azúcar | 1,190 | 1,190 | — | 106,187 | 106,187 | — | — | 89.2 | 89.2 |

`VBP real` en billones de CLP de 2019. `tCO₂` es `emision_retc` **ajustado por el
cribado de ediciones** (`src/common/calidad.py`): la planta-año marcada como exceso se
capa a la mediana de las otras dos ediciones, un valor que esa misma planta declaró. En
2024 quita 3,16 Mt en 19 plantas; en 2023, 9,18 Mt en 49. No se imputa
ningún valor externo. El desglose fósil/biomasa/proceso viene de
`co2_combustible.parquet`, que reparte el total con la estructura declarada.
`emision_total` (RUEA) no se usa para agregar: es 3,4 veces el validado (164 Mt contra
48,7 Mt en 2024).

## Las 14 industrias identificables

La granularidad máxima no la fija el RETC —trae CIIU a 4 dígitos para todo el
país— sino el BNE: su tabla de equivalencia `BNE-CIIU 4` define 14 categorías
industriales. Siete son manufactureras, una es refino y extracción de petróleo y gas,
y seis primarias o extractivas. Fuera quedan comercio, servicios, transporte,
construcción y sector público, que el balance no separa como demanda industrial.
`Producción de Metanol` se suma a Petroquímica porque el RETC no puede separarlas:
ambas son CIIU 2011.

La columna **cobertura** es la energía implícita en el CO₂ fósil sobre la que el BNE
asigna a la industria: mide si el RETC captura la combustión que esa industria
declara consumir. `RETC` la resume en cuatro estados: **sí** (50–150%), **parcial**
(10–50%), **no** (<10%) y **excede** (>150%: se declara más energía que la que el
balance asigna). Es un diagnóstico, no un filtro.

Solo cuatro industrias pasan las dos pruebas —combustión capturada y CO₂ no
concentrado en una planta—: Papel, Cemento, Láctea y Refinería. Las otras diez se
publican aquí con su cifra y su motivo, no como indicador.

| Industria | TJ | tCO₂ | tCO₂/TJ fósil | Cobertura | RETC | Publica | Nota |
|---|---:|---:|---:|---:|:---:|:---:|---|
| Cobre | 205,998 | 41,633 | 0.2 | 0.3% | no | no | el RETC captura ~0,2 tCO₂/TJ de los 206.000 TJ del BNE: falta casi toda la combustión |
| Industrias Varias | 112,854 | 3,603,503 | 15.9 | 26.0% | parcial | no | cajón residual de 7 divisiones: no es una industria |
| Papel y Celulosa | 105,252 | 17,485,123 | 38.3 | 56.3% | sí | sí |  |
| Refinería y Extracción Petróleo y Gas Natural | 22,981 | 925,223 | 40.3 | 65.8% | sí | sí | solo 2024: el ítem del BNE cae 53% entre ediciones (49.193 → 22.981 TJ) |
| Agroindustria | 19,511 | 100,632 | 1.0 | 1.4% | no | no | cobertura 1%: la ENIA no cubre las divisiones 01-02, no hay contraparte |
| Minas Varias | 16,390 | 103,610 | 6.3 | 10.5% | parcial | no | cobertura 11% y una planta explica 78% del CO₂ fósil |
| Cemento | 10,487 | 747,603 | 20.4 | 21.7% | parcial | sí | VBP de la ENIA cubre 4 plantas: solo intensidad física |
| Salitre | 8,968 | 23,720 | 2.6 | 4.2% | no | no | cobertura de energía implícita 4% del BNE |
| Petroquímica | 8,947 | 1,506,165 | 167.9 | 248.7% | excede | no | con metanol incluido el BNE asigna 8.947 TJ: el RETC declara 3× esa energía |
| Pesca | 8,685 | 170,780 | 17.7 | 24.0% | parcial | no | cobertura de energía implícita 24%: el RETC no captura todo el combustible de la flota |
| Hierro | 5,898 | 80,246 | 13.6 | 14.0% | parcial | no | cobertura 14% y una planta explica 99% del CO₂ fósil |
| Siderurgia | 5,233 | 65,740 | 10.9 | 6.8% | no | no | Huachipato no declara el carbón ni el coque; el RETC captura ~8% de la energía |
| Industria Láctea | 1,675 | 242,946 | 45.3 | 71.3% | sí | sí |  |
| Azúcar | 1,190 | 106,187 | 89.2 | 91.6% | sí | no | una sola planta explica 99,96% del CO₂ fósil: es un caso, no una industria |

## Qué captura el RETC (2024)

El RETC no es un inventario industrial: es un registro de establecimientos que
superan los umbrales del D.S. 138/2005. Por eso la mayor parte de su CO₂ validado no
es industria: es generación eléctrica declarada planta a planta.

| Grupo | Mt CO₂ | % del validado | Filas |
|---|---:|---:|---:|
| Categorías industriales (14) | 25.20 | 56% | 8,156 |
| Generación eléctrica (CIIU 35) | 18.08 | 40% | 2,301 |
| Servicios, agua, residuos y construcción | 1.69 | 4% | 20,883 |
| **Total** | **44.97** | 100% | **31,340** |

Las **14 categorías** son las que el balance separa; la generación eléctrica entra
completa y el resto son servicios, agua, residuos, comercio y construcción. Lo que
falta no es un vacío del registro: **la gran minería no declara su combustión**, por
eso Cobre aparece con 42 kt donde el BNE le asigna 206.000 TJ.

### Nota importante
Las tres primeras fuentes (RETC, BNE, ENIA) no comparten unidad de análisis. El RETC
cuenta establecimientos, el balance cuenta ítems de consumo y la ENIA cuenta
establecimientos industriales. El puente es la clasificación CIIU a 4 dígitos, con una
categoría —Petroquímica— donde el puente no alcanza y se declara.

## Serie 2023–2024 (ramas publicables)

| Rama | TJ 2023 | TJ 2024 | Var. | tCO₂ 2023 | tCO₂ 2024 | Var. |
|---|---:|---:|---:|---:|---:|---:|
| Papel y Celulosa | 103,361 | 105,252 | +1.8% | 15,515,929 | 17,485,123 | +12.7% |
| Refinería y Extracción Petróleo y Gas Natural | 49,193 | 22,981 | -53.3% | 893,874 | 925,223 | +3.5% |
| Cemento | 10,652 | 10,487 | -1.6% | 786,218 | 747,603 | -4.9% |
| Industria Láctea | 2,278 | 1,675 | -26.5% | 313,277 | 242,946 | -22.5% |

Las variaciones no son variaciones ambientales cuando una sola planta domina el
CO₂ de la rama: ver las alertas de calidad. Y **2023 no se lee como tendencia**:
el cribado ya capó su bloque GLP (16,15 Mt declarados contra 1,32 Mt en 2024) y la
edición arrastra una reducción de 9,2 Mt; el año de referencia es 2024
(ver `reports/retc_anomalias.md`). Refinería arrastra además un corte de fuente: el
ítem del BNE pasa de 49.193 a 22.981 TJ entre ediciones, así que su serie tampoco se
compara.

## Emisiones y VBP por división CIIU, 2024

La división de 2 dígitos es la unidad más fina que comparten el RETC (CIIU del
establecimiento) y la ENIA (VBP por división). El BNE no baja de las 14 categorías,
así que aquí no hay energía: solo CO₂ por peso producido.

| División | Rama principal | tCO₂ | VBP real | tCO₂/billón CLP2019 |
|---|---|---:|---:|---:|
| 17 | Papel y Celulosa | 17,485,123 | 3.5 | 4,938,108 |
| 10 | Industrias Varias | 1,600,427 | 16.5 | 96,841 |
| 20 | Petroquímica | 1,506,165 | 7.1 | 213,094 |
| 16 | Industrias Varias | 1,420,390 | 2.2 | 643,864 |
| 23 | Industrias Varias | 1,041,517 | 1.5 | 702,749 |
| 13 | Industrias Varias | 257,376 | 0.2 | 1,600,846 |
| 24 | Industrias Varias | 251,292 | 1.2 | 212,004 |
| 11 | Industrias Varias | 64,159 | 3.8 | 16,755 |
| 32 | Industrias Varias | 43,534 | 0.1 | 514,728 |
| 22 | Industrias Varias | 37,717 | 1.7 | 22,595 |
| 25 | Industrias Varias | 19,166 | 1.1 | 16,851 |
| 31 | Industrias Varias | 18,865 | 0.3 | 54,267 |
| 21 | Industrias Varias | 8,613 | 0.9 | 9,632 |
| 30 | Industrias Varias | 881 | 0.0 | 40,205 |
| 15 | Industrias Varias | 659 | 0.0 | 18,775 |
| 14 | Industrias Varias | 371 | 0.1 | 6,282 |
| 18 | Industrias Varias | 238 | 0.1 | 1,668 |
| 28 | Industrias Varias | 161 | 0.7 | 233 |
| 29 | Industrias Varias | 90 | 0.1 | 1,079 |
| 27 | Industrias Varias | 23 | 0.4 | 58 |

## Alertas de calidad

- 2023 · Azúcar: CO₂ fósil concentrado en una planta (100%: PLANTA ÑUBLE - IANSAGRO)
- 2023 · Cobre: CO₂ fósil concentrado en una planta (63%: MOLYMETNOS)
- 2023 · Hierro: CO₂ fósil concentrado en una planta (98%: PLANTA DE PELLETS)
- 2023 · Minas Varias: CO₂ fósil concentrado en una planta (72%: FAENA SALAR DEL CARMEN)
- 2023 · Papel y Celulosa: CO₂ fósil concentrado en una planta (61%: CMPC CELULOSA PLANTA LAJA)
- 2023 · Petroquímica: CO₂ fósil concentrado en una planta (74%: ENAEX PLANTA RIO LOA)
- 2023 · Salitre: CO₂ fósil concentrado en una planta (96%: ACF BAQUEDANO S.A.)
- 2023 · Siderurgia: CO₂ fósil concentrado en una planta (97%: COMPAÑÍA SIDERÚRGICA HUACHIPATO)
- 2024 · Azúcar: CO₂ fósil concentrado en una planta (100%: PLANTA ÑUBLE - IANSAGRO)
- 2024 · Cobre: CO₂ fósil concentrado en una planta (60%: CAMPAMENTO SALARES NORTE)
- 2024 · Hierro: CO₂ fósil concentrado en una planta (99%: PLANTA DE PELLETS)
- 2024 · Minas Varias: CO₂ fósil concentrado en una planta (78%: FAENA SALAR DEL CARMEN)
- 2024 · Papel y Celulosa: CO₂ fósil concentrado en una planta (59%: CMPC PULP SA PLANTA PACIFICO)
- 2024 · Salitre: CO₂ fósil concentrado en una planta (58%: PLANTA DE NITRATOS Y PRODUCTOS DERIVADOS DE SALES)
- 2024 · Siderurgia: CO₂ fósil concentrado en una planta (98%: COMPAÑÍA SIDERÚRGICA HUACHIPATO)

## Sensibilidad a la planta dominante, 2024

| Rama | Planta dominante | Peso en CO₂ fósil | tCO₂/TJ fósil | Sin esa planta |
|---|---|---:|---:|---:|
| Papel y Celulosa | CMPC PULP SA PLANTA PACIFICO | 59% | 38.3 | 15.8 |

Cuando una planta explica más de la mitad del CO₂ fósil de la rama, su valor
individual decide la intensidad. La columna "sin esa planta" muestra cuánto del
número depende de un solo dato.

## Lectura y límites

### El denominador y la energía
El denominador (`VBP`) cubre solo establecimientos de 10+ trabajadores; la energía
del BNE cubre toda la industria. Las razones son una **cota superior** de la
intensidad verdadera y sirven para comparar ramas y años, no como nivel.

### Qué ramas publican intensidad física
Solo Papel y Celulosa, Cemento y Láctea publican intensidad física. `Siderurgia`
queda fuera: Huachipato declara únicamente gases de subproducto (alto horno, coque)
y ningún carbón ni coque mineral, así que el RETC captura ~8% de la energía de la
rama. `Petroquímica` declara ~200 TJ para toda la división 20 y `Industrias Varias`
es el cajón residual: tampoco son publicables.

### `tCO₂/TJ fósil`
Usa solo el CO₂ de combustión fósil (excluye biomasa y procesos) sobre la energía
fósil del BNE: es la intensidad de carbono del mix fósil y ahora es comparable
entre ramas, incluida Papel y Celulosa.

### `tCO₂/TJ total`
Incluye biomasa y proceso sobre la energía total: mide cuánto CO₂ sale por unidad
de energía usada, sin juzgar el origen.

### Deflación del VBP
Deflación simple del VBP con IPP de producción; el VA se deflacta con el mismo
índice (supuesto, no doble deflación).

### IPP de la división
Los denominadores usan el IPP de la división correspondiente; cuando la división
no publica IPP se usa el total de manufactura.

### `publicable_economica` y Cemento
`publicable_economica` deja fuera a Cemento: la ENIA trae solo 4 plantas de la
clase 2394 (0,11 billones de VBP), así que su intensidad económica está inflada.
