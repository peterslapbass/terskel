---
title: Resultados
---

# Resultados

Cinco reportes que salen directo de los parquet, sin edición manual. Cada tabla trae su
unidad y su cobertura; cada cifra se puede rastrear hasta la ficha de la fuente.

- **[Indicadores de intensidad]({{ '/resultados/indicadores_intensidad.html' | relative_url }})**
  — las 14 categorías industriales con energía del balance, CO₂ declarado, cobertura,
  intensidad física (tCO₂/TJ) e intensidad económica (TJ y tCO₂ por billón de CLP
  de 2019), más los tres agregados.
- **[Escenarios 2030]({{ '/resultados/escenarios_2030.html' | relative_url }})**
  — cuatro escenarios de identidad contable sobre las cuatro ramas publicables, el
  tornado de sensibilidades y la comparación contra 2024.
- **[Cribado de anomalías del RETC]({{ '/resultados/retc_anomalias.html' | relative_url }})**
  — las 278 planta-año que superan diez veces su propia mediana, con el factor aplicado.
- **[Reparto del CO₂ por origen]({{ '/resultados/retc_co2_combustible.html' | relative_url }})**
  — cuánto del CO₂ es combustión, cuánto biomasa y cuánto proceso, por industria.
- **[Energía implícita en el CO₂]({{ '/resultados/retc_energia_implicita.html' | relative_url }})**
  — la puerta de entrada a la cobertura: qué energía implica el CO₂ declarado, con qué
  factor, y cuánto se aparta del balance.

## Resumen ejecutivo

**44,97 Mt** CO₂ validado total. **25,20 Mt** (56%) correspondientes a las 14 categorías
industriales. **18,08 Mt** (40%) a generación eléctrica. **1,69 Mt** (4%) a servicios,
agua, residuos y construcción. Solo **4** categorías industriales son publicables:
Papel y Celulosa, Cemento, Láctea y Refinería.

## Cómo leer las tablas

### Cobertura
Energía implícita en el CO₂ declarado sobre energía del balance. Es un contraste entre
dos fuentes, no una medida de cumplimiento.

### Captura del RETC
La cobertura resumida en cuatro estados —`sí` (50–150%), `parcial` (10–50%), `no`
(<10%), `excede` (>150%). Es un diagnóstico, no un filtro.

### Publicable
Solo cuando la combustión está capturada y el CO₂ no se concentra en una sola planta.
Es un juicio explícito, con el motivo escrito al lado cuando es «no».

El detalle de cada definición está en la
[ficha de indicadores]({{ '/fuentes/indicadores.html' | relative_url }}) y el de cada
escenario en la [ficha de escenarios]({{ '/fuentes/escenarios.html' | relative_url }}).

## Reglas de publicación

### Regla 1: Cada cifra debe tener ficha
Número, unidad, cobertura, supuestos y limitaciones deben aparecer juntos. Un dato
aislado sin ficha no es público.

### Regla 2: El año de referencia es 2024
Solo se publican indicadores y escenarios con 2024 como año base. 2023 y 2025 sirven
para contraste y detección de anomalías.

### Regla 3: No se imputan valores faltantes
Ausencias de datos se marcan como huecos. La única excepción es el ajuste contra la
misma planta en la edición anterior.

### Regla 4: Las fuentes no comparten unidad de análisis
RETC cuenta establecimientos, BNE cuenta ítems de consumo, ENIA cuenta establecimientos
industriales. El puente CIIU a 4 dígitos no cubre todas las categorías.

## Lectura y límites

### RETC no es inventario
El RETC es un registro de establecimientos que superan los umbrales del D.S.
138/2005, no un inventario de combustión por industria.

### Gran minería no declara
Cobre y otras divisiones de gran minería no declaran su combustión en el RETC,
por eso aparece con cifras bajas que no reflejan el consumo real.

### 2023 no es tendencia
El año de referencia es 2024. 2023 se usa para detección de anomalías, no para
construir series temporales comparables (el cribado ya capó su bloque GLP y la
edición arrastra reducciones artefacto).

### Refinería corte de fuente
El ítem del BNE para refinería pasó de 49.193 a 22.981 TJ entre ediciones, así
que su serie tampoco es comparable año a año.
