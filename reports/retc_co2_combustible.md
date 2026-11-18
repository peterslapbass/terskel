# Split del CO₂ del RETC por origen (2025)

Método: el desglose declarado (`emision_combustible_primario`, `_secundario`,
`emision_procesos`) se clasifica por combustible y reparte proporcionalmente el
total validado (`emision_retc`). No se estima nada: la suma de las clases es
exactamente el total.

## Nacional

| Año | Total validado | Fósil | Biomasa | Proceso | Otro | Sin clase |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 65,440,032 | 47,564,621 (72.7%) | 16,864,397 (25.8%) | 941,844 (1.4%) | 69,170 | 0 |
| 2024 | 48,712,437 | 28,432,091 (58.4%) | 19,314,220 (39.6%) | 882,746 (1.8%) | 77,121 | 6,259 |
| 2025 | 47,015,627 | 26,257,289 (55.8%) | 19,688,617 (41.9%) | 979,963 (2.1%) | 89,759 | 0 |

`Proceso` es CO₂ de calcinación y procesos químicos, no de combustión. Por eso
la intensidad `tCO₂ fósil/TJ fósil` lo excluye y el `tCO₂ total` lo incluye.

## Combustibles principales (2025)

| Combustible primario | CO₂ fósil | CO₂ biomasa | CO₂ proceso |
|---|---:|---:|---:|
| LICOR NEGRO | 187,992 | 13,162,707 | 0 |
| CARBON BITUMINOSO PULVERIZADO | 10,763,790 | 0 | 0 |
| GAS NATURAL | 7,189,610 | 0 | 160,414 |
| BIOMASA COMBUSTIBLE | 45,254 | 6,137,232 | 394 |
| CARBON SUB BITUMINOSO | 2,839,757 | 0 | 0 |
| GAS DE REFINERIA | 1,116,094 | 0 | 0 |
| GAS LICUADO DE PETROLEO | 1,102,716 | 0 | 1,870 |
| COKE DE PETROLEO (PETCOKE) | 617,304 | 0 | 468,656 |
| PETROLEO N 2 (DIESEL) | 834,424 | 0 | 2,903 |
| PROPANO | 829,579 | 0 | 0 |
| PETROLEO N 6 | 285,681 | 12,139 | 344,507 |
| CARBON BITUMINOSO | 254,933 | 4,784 | 1,215 |

## Límites

- El reparto es **proporcional a lo declarado**, no medido: si una planta declara
  mal su mezcla, el split hereda el error. Lo que se conserva exacto es el total.
- `emision_total` (declarado) es 3,4 veces `emision_retc` (validado). Se usa el
  validado como total y el declarado solo como estructura.
- `otro` (aceite usado, combustible sólido alternativo) y `sin_clase` quedan
  fuera de fósil y biomasa por convención, no por evidencia.
