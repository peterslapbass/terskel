---
title: "Ficha — Escenarios 2030 (energía y CO₂)"
---

# Ficha — Escenarios 2030 (energía y CO₂)

| Campo | Valor |
|---|---|
| Base | 2024 observado, ajustado por el cribado de ediciones · 4 ramas manufactureras |
| Horizonte | 2030 (6 años) |
| Método | identidad contable con palancas explícitas y `g` por rama, sin estimación estadística |
| Parámetros | `data/reference/escenarios_parametros.csv` (editable, versionado) |
| Salida | `data/processed/scenarios/escenarios_2030.parquet` · `reports/escenarios_2030.md` |
| Estado | calculado; sustituye a una proyección que los datos no permiten |

## Motor

```
energía(t) = energía(2024) × (1+g_rama)^n × (1−mi)^n
CO₂(t)     = Σ origen: fósil × (1+g_rama)^n × (1−mi)^n × (1−mf)^n
                        biomasa, proceso y otro × (1+g_rama)^n × (1−mi)^n
```

`mf` actúa **solo sobre el CO₂ de combustión fósil**. La biomasa es biogénica y el
CO₂ de proceso depende del clínker, no del combustible: ninguno de los dos baja
por cambiar de combustible.

`g` es un **vector por rama**, no un escalar. Eso permite que la estructura
productiva cambie, que es lo que un escenario sectorial tiene que poder hacer.

## Palancas

| Palanca | Central | Rango | Base |
|---|---:|---|---|
| `g` Papel y Celulosa | +3,03%/año | 0 a 4% | calibrado para que el agregado ponderado por VBP quede en 2,0% |
| `g` Siderurgia | 0,00%/año | −2 a +2% | rama plana; Huachipato no declara carbón ni coque |
| `g` Cemento | −3,00%/año | −6 a 0% | consolidación: 6 a 4 establecimientos en la ENIA |
| `g` Industria Láctea | +1,00%/año | 0 a 3% | sector en expansión (+5,6% de VBP real en 2024) |
| `mi` | 1,50%/año | 0,5 a 2,5% | programas de eficiencia energética (Ley 21.305) |
| `mf` | 1,00%/año | 0 a 2% | sustitución de combustibles y electrificación, rango conservador |

`n = 2030 − 2024 = 6`. Con `n = 0` o palancas en cero el motor devuelve el dato
de 2024 exacto; esa es la puerta de coherencia que corre en cada ejecución.

## Escenarios

| Nombre | Vector `g` | `mi` | `mf` | Lectura |
|---|---|---:|---:|---|
| Congelado | central | 0 | 0 | la actividad crece por rama, nada más cambia |
| Eficiencia | central | 1,5% | 0 | solo baja la energía por peso producido |
| Descarbonización | central | 1,5% | 1,0% | además cambia el mix (combustible y electricidad) |
| Recomposición sectorial | alternativo | 1,5% | 1,0% | Cemento −5% y Siderurgia −2%; Papel +2,5% y Láctea +1,5% |

## Resultado 2030

| Escenario | Energía (TJ) | CO₂ (t) | vs 2024 |
|---|---:|---:|---:|
| Observado 2024 | 122.647 | 18.541.413 | — |
| Congelado | 141.642 | 21.861.029 | +17,9% |
| Eficiencia | 129.363 | 19.965.858 | +7,7% |
| Descarbonización | 129.363 | 19.848.959 | +7,1% |
| Recomposición sectorial | 124.425 | 19.204.706 | +3,6% |

## Supuestos

1. **`g` por rama, declarado.** El vector central se calibra para que el agregado
   ponderado por VBP quede en 2,0%/año, el mismo valor de la versión escalar. No se
   estima: la ENIA tiene dos años y sus variaciones por rama son artefactos de
   muestra (Cemento pasa de 6 a 4 establecimientos; Papel crece 51% en el
   denominador).
2. **`mf` es agregado y solo fósil.** Resume sustitución de combustibles,
   electrificación y eficiencia de conversión en un solo número por rama, y se
   aplica únicamente a la fracción fósil. Aplicarlo al total (versión anterior)
   reducía también el CO₂ biogénico y de proceso, sin mecanismo que lo explicara.
3. **Cemento sin intensidad económica.** Entra en energía y CO₂ (datos sólidos),
   pero su VBP en la ENIA cubre 4 plantas y no se usa como denominador.

## Limitaciones

- No es una proyección: es un ejercicio de sensibilidad sobre el nivel de 2024.
- **La recomposición mueve poco el total.** Papel concentra el 94% del CO₂ de las
  cuatro ramas; Cemento y Siderurgia suman 14,5% del VBP. Contraerlas cambia la
  estructura y deja el agregado casi igual: es un resultado, no un defecto.
- Siderurgia parte de un CO₂ subcubierto por el RETC (13,8 tCO₂/TJ): su nivel base
  es una cota inferior.
- Los rangos de `g`, `mi` y `mf` son juicio experto, no estimaciones econométricas.
- No hay escenario de demanda eléctrica ni de precio de combustibles: el motor es
  de cantidades físicas, no de mercado.
- El año base es 2024 y está ajustado: 2023 trae el bloque GLP inflado ~12× y 2024
  el error de Cartocor (3,05 Mt, capado). La serie histórica no es una tendencia.

## Reproducción

```bash
python src/scenarios/escenarios.py
```

Requiere `data/processed/indicators/intensidad_rama.parquet` (ver
[ficha de indicadores](indicadores.html)).
