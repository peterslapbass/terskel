# Terskel: verificación de datos y revisión de notas

Fecha: 17-11-2026
Fuentes: `data/processed/retc/anomalias.parquet` y `docs/notas/*.md` del repositorio clonado (`/home/claude/peterslapbass/terskel`).

## 1. Verificación de las 31 de 85 plantas (2023)

Confirmado con el parquet:
- Plantas marcadas como anómalas en 2023: **85**, todas distintas (una por `id_vu`).
- De ellas, **31** tienen el GLP como combustible principal. Coincide con la nota.
- El exceso de esas 31 plantas suma **14,3 Mt** de CO₂. La nota dice 16,15 Mt de GLP en total; la diferencia es normal, porque el total incluye plantas no marcadas.

Matiz:
- Las 31 plantas pertenecen a **13 códigos CIIU distintos**. Eso respalda que no comparten sector, pero no que sean un grupo homogéneo: solo significa que el denominador común es el combustible.
- "Mismo tamaño y región" no lo comprobé. La nota lo afirma; no lo verifiqué en el parquet.

Esto no confirma la causa. Confirma el patrón: el GLP domina las anomalías de 2023, no las demás ediciones.

## 2. Notas revisadas: afirmaciones que superan la evidencia

### `docs/notas/cartocor-527-veces.md`
- "**No es un cambio de proceso**": es una inferencia razonable, pero se presenta como cierta. Mejor: "es poco probable que sea un cambio de proceso".
- "**No multiplica por 527 su combustión**": el factor 527 compara el valor de 2024 con 2023 de la misma planta, pero no sabemos su combustión real. Se debe decir "su declaración".
- "**Error**" y "**valor imposible**": el texto explicado lo dice sin matiz. Se puede sostener que el valor es inconsistente con su propia serie, pero no que sea imposible.
- Lo que sí está bien sustentado: la planta, las cifras declaradas (3.049.178 / 5.791 / 5.719 t), el factor 527 y la capa `emision_retc` como fuente de la cifra. Estos datos se pueden verificar en el parquet.

### `docs/notas/ediciones-no-comparables.md`
- "**Exceso demostrable**" (tabla): "demostrable" es excesivo. El exceso es "exceso respecto a la mediana de las otras dos ediciones", que es una regla, no una demostración.
- "**Una caída de 18,4 Mt ... la produce el archivo**": se afirma la causa. Mejor: "la caída es compatible con defectos del archivo; no lo podemos descartar sin verificarlo".
- "**Eso agregó 17 Mt de CO₂ que no existían realmente**" (texto explicado): mismo problema que en la nota del GLP. Corregir.
- "**Los cambios que ves no son reales: son errores del registro**" (texto explicado): sobreafirmado.
- "**la mitad de ellos consumidores de gas natural**" (2025): no lo verifiqué. Antes de publicarlo hay que comprobarlo.

## 3. Patrón común

En las tres notas (GLP, Cartocor, ediciones), el texto técnico es prudente y el explicado no lo es. El problema está en el paso de "anomalía medible" a "error del registro, no realidad industrial". La regla de corrección es razonable como criterio operativo, pero no prueba causas.

Propuesta: usar "anomalía", "exceso respecto a la mediana", "inconsistente con su propia serie" y "hipótesis: defecto de la edición". Evitar "error", "no existe", "imposible" y "no es real" hasta verificarlo.

## 4. Qué queda pendiente

- Obtener el factor de emisión de GLP por edición del RETC (no está en el repositorio).
- Obtener el consumo de GLP del BNE para 2023 y 2024.
- Verificar la afirmación "la mitad de consumidores de gas natural" en 2025.
- Verificar "mismo tamaño y región" para las 31 plantas de GLP de 2023.
