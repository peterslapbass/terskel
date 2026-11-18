# Terskel: revisión de subpáginas y repositorio (anexo a la revisión de portada)

Fecha: 17-11-2026
Repositorio clonado (solo lectura, shallow): /home/claude/peterslapbass/terskel
Subpáginas: no pude leerlas por la web (la herramienta de fetch rechazó las URL). El repositorio sí permite revisar el mismo contenido en su fuente (`docs/*.md`).

## 1. Qué cambia respecto a la revisión anterior

La revisión de portada seguía siendo válida, pero no alcanzaba para evaluar el hallazgo GLP. Con el repositorio se ve que el problema de rigor no está solo en la portada: aparece repetido en la nota, en la ficha de fuente, en los informes generados y en el código de auditoría.

## 2. Dónde se afirma como hecho lo que es hipótesis

| Archivo | Afirmación | Problema |
|---|---|---|
| `docs/notas/glp-2023-inflado.md` (bloque técnico) | "Es un factor de emisión de esa edición, no una conducta de las empresas." | Se asume la causa sin tener el factor de 2023 en el repositorio. |
| `docs/notas/glp-2023-inflado.md` (bloque explicado) | "En 2023, ese factor estaba mal calculado y era 12 veces más alto." | Igual: afirma la causa y su magnitud exacta. |
| `docs/notas/glp-2023-inflado.md` (explicado) | "Las 17 Mt de CO₂ ... no existen realmente. Es un error del archivo." | Sobrepasa la evidencia: el repositorio no prueba que esas toneladas sean falsas. |
| `docs/index.md` líneas 59-60 | "El factor de emisión del GLP en 2023 estaba inflado" y "el registro se equivocó" | Titular y portada sin matiz. |
| `docs/fuentes/retc.md`, sección "Las ediciones no son comparables" | "Es un defecto del factor de emisión de esa edición, no de las empresas." | Repite la afirmación sin fuente. |
| `reports/retc_anomalias.md` y `docs/resultados/retc_anomalias.md` | "Es un defecto del factor de emisión de esa edición, no de una empresa: afecta a cualquier usuario de GLP." | Sin evidencia del factor por edición. |
| `src/audit/retc_anomalias.py` (texto generado) | Mismo texto que el informe | El código genera la afirmación en cada corrida. |

## 3. Qué dice el repositorio y qué no puede verificar

- **Factor de GLP en el repositorio**: `data/reference/factores_emision_combustible.csv` tiene un único valor para GLP (17,2 kg C/GJ, "Guía RETC Tabla 4-3"). No hay factor por edición. Por tanto, el repositorio **no puede confirmar ni descartar** que el factor de 2023 fuera distinto.
- **Consumo físico de GLP**: `retc` solo trae CO₂ calculado, no volúmenes de GLP por año. Tampoco hay en el repositorio el consumo del Balance Nacional de Energía para GLP en 2023 y 2024 que permita contrastar la afirmación "el consumo no cambió".
- **Regla de corrección**: `FACTOR = 10` en `src/audit/retc_anomalias.py` es un umbral elegido, no una prueba. La corrección (capar el exceso a la mediana de las otras dos ediciones) es un supuesto que la nota presenta como "lo que hicimos", sin discutir su efecto sobre la conclusión.
- **Número de plantas**: la nota dice "mismo número de plantas"; las cifras son 1.503, 1.536 y 1.501 (diferencia de ~2%). Es casi igual, pero conviene decirlo con la cifra.
- **"31 de las 85 plantas"**: no lo pude verificar sin abrir `data/processed/retc/anomalias.parquet`. No lo doy por comprobado.

## 4. Mismo patrón en otros casos (oportunidad de consistencia)

La nota de Cartocor (`docs/notas/cartocor-527-veces.md`) y la de ediciones no comparables usan el mismo tono de causa cerrada. Conviene revisarlas con el mismo criterio. No las leí completas en esta pasada.

## 5. Propuesta de redacción para el hallazgo (versión consistente)

**Titular**: "Anomalía en el CO₂ de GLP declarado en 2023"

**Cuerpo**:
> "El CO₂ atribuido al gas licuado en la edición 2023 del RETC es 12 veces el de 2024 y 2025, con prácticamente el mismo número de declarantes. Lo más probable es un problema en el factor de emisión o en la unidad de esa edición. Esta explicación es una hipótesis: el repositorio no incluye el factor de 2023 ni los volúmenes de GLP para verificarla. Por eso usamos 2024 como año de referencia y tratamos 2023 solo como contraste."

**Corrección de la cifra "17 Mt no existen"**: sustituir por "Si la hipótesis se confirma, 17 Mt de ese año corresponden a un error de registro; mientras no se verifique, se mantienen como excedente ajustado, no como emisión descartada."

## 6. Cambios concretos (para la próxima versión del sitio)

1. Cambiar el titular y el texto de `docs/notas/glp-2023-inflado.md` (ambos bloques) a la redacción de §5.
2. Quitar "defecto del factor" de `docs/fuentes/retc.md`, `docs/resultados/retc_anomalias.md` y de la plantilla que genera `src/audit/retc_anomalias.py`.
3. Quitar "las 17 Mt no existen" y "es un error del archivo".
4. Añadir una sección "Hipótesis y verificación pendiente" en la nota, con H1–H5 de la revisión anterior y el estado de cada una.
5. Incluir el factor de emisión por edición en `data/reference/` si se obtiene del RETC/MMA; si no, documentar que no está disponible.
6. Publicar las cifras crudas de GLP por edición (16,15 / 1,32 / 1,10 Mt; 3.130 / 3.198 / 3.202 declaraciones) con su fuente exacta, para que el lector vea el dato sin depender de la interpretación.

## 7. Pendiente

- Leer las subpáginas web (si la herramienta de fetch las permite, o revisando `docs/*.md` directamente).
- Revisar `data/processed/retc/anomalias.parquet` para confirmar las 31 de 85 plantas.
- Obtener el factor de GLP de la edición 2023 del RETC y el consumo de GLP del BNE para 2023 y 2024.
