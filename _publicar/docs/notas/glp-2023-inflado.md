---
title: El GLP de 2023 está inflado 12×
date: 2026-11-17
---

# El GLP de 2023 está inflado 12×

### Qué observamos

El CO₂ que el RETC atribuye al gas licuado de petróleo (GLP) se multiplica por doce entre una edición y otra, sin que cambie el número de declaraciones:

| Edición | CO₂ por GLP | Declaraciones | Plantas |
|---|---|---|---|
| 2023 | 16,15 Mt | 3.130 | 1.503 |
| 2024 | 1,32 Mt | 3.198 | 1.536 |
| 2025 | 1,10 Mt | 3.202 | 1.501 |

Mismo número de fuentes, mismo número de plantas, doce veces el CO₂. Si fuera un cambio real en el consumo, las declaraciones no serían idénticas en cantidad.

<img src="/terskel/assets/fig/glp-2023.svg" alt="CO₂ declarado por GLP y número de declaraciones, 2023–2025" style="max-width: 100%; height: auto;">

### Qué creemos (hipótesis)

Hipótesis: es un problema del factor de emisión de esa edición, no una conducta de las empresas. Esta explicación es una hipótesis: el repositorio no incluye el factor de 2023 ni los volúmenes de GLP para verificarla. Por eso usamos 2024 como año de referencia y tratamos 2023 solo como contraste.

### Qué falta para confirmarlo

El factor de emisión por edición del RETC y el consumo de GLP del BNE para 2023 y 2024. Una vez obtenidos estos datos, se podrá confirmar o descartar que el factor de 2023 fue distinto.

### Cómo se reproduce

`python src/audit/retc_anomalias.py`, que escribe `data/processed/retc/anomalias.parquet` y `reports/retc_anomalias.md`.