# Terskel: sugerencias

Fecha: 17-11-2026
Base: revisión de la portada, del repositorio clonado y del parquet de anomalías. Las sugerencias son propuestas; no se han aplicado al repositorio.

## 1. Rigor y redacción (prioridad alta)

1. **Separar hallazgo, hipótesis y causa en cada nota.** Usar tres bloques fijos: "Qué observamos" (cifras crudas), "Qué creemos" (hipótesis, con su estado) y "Qué falta para confirmarlo". Así el lector ve qué es dato y qué es interpretación.
2. **Unificar el vocabulario.** Usar "anomalía", "exceso respecto a la mediana de las otras dos ediciones", "inconsistente con su propia serie" e "hipótesis". Evitar "error", "no existe", "imposible" y "no es real" hasta verificarlo. Aplica a la portada, la nota del GLP, Cartocor, ediciones no comparables, la ficha de RETC y los informes generados por `src/audit/retc_anomalias.py`.
3. **Que el código no escriba conclusiones.** El texto de `retc_anomalias.py` que dice "es un defecto del factor de emisión" se genera en cada corrida. Conviene que el código genere solo cifras y que la interpretación quede en la nota.
4. **Tono del texto explicado.** Hoy el explicado es más categórico que el técnico. Propuesta: que ambos usen las mismas afirmaciones, y que solo cambie el nivel de detalle.

## 2. Verificación pendiente (prioridad alta)

5. **Factor de GLP por edición.** Es lo que más cambiaría la conclusión. Si el RETC o el MMA publican la guía o los factores de cada edición, incluirlos en `data/reference/` con su fuente exacta.
6. **Consumo de GLP del BNE (2023 y 2024).** Permite contrastar si el consumo físico cambió. Hoy el repositorio no lo tiene.
7. **Verificar "la mitad de consumidores de gas natural" (2025).** Hoy es una afirmación sin comprobar en la nota de ediciones.
8. **Verificar "mismo tamaño y región" (31 plantas de GLP en 2023).** Lo afirma la nota; no lo comprobé en el parquet.
9. **Sensibilidad de la regla de corrección.** Probar el umbral de 10× y el de 1.000 t de materialidad con valores de 5× y 20×. Si la conclusión cambia mucho, eso debe decirse en la nota.

## 3. Transparencia del método

10. **Publicar las cifras antes y después del ajuste** en la misma tabla, con el número de plantas afectadas. Hoy el lector ve el "ajustado" sin ver cuánto se movió.
11. **Documentar la regla en una sola página.** Hoy está repartida entre `calidad.py`, las notas y la ficha de RETC. Una página con la regla, el umbral, la materialidad y el ejemplo de Cartocor ayudaría.
12. **Fecha de revisión y canal de corrección** en cada nota, no solo en la portada.

## 4. Portada y navegación

13. **Quitar el duplicado** del bloque "Fuente y alcance" y el pie del modo explicado.
14. **Renombrar "Datos técnicos completos"** a "Fichas y detalles", para no confundirlo con "Datos".
15. **Explicar "Terskel"** en una línea.
16. **Revisar "Notas de datos" vacío** en la vista renderizada; confirmar si es un problema del modo o de maquetación.
17. **Decidir el modo por defecto**, y mover las instrucciones del modo a la cabecera o a un tooltip.
18. **Unificar la jerarquía de encabezados** (`#`, `##`, `###`).
19. **Quitar el dólar observado** de las fuentes si la portada no lo usa.

## 5. Orden sugerido

1. Corregir la redacción del GLP y de Cartocor (puntos 1–2), porque es lo que más riesgo tiene.
2. Conseguir el factor por edición y el consumo de GLP (puntos 5–6). Con eso se puede decidir si la hipótesis se confirma o se descarta.
3. Ajustar la portada y la navegación (puntos 13–19).
4. Publicar la regla de corrección y su sensibilidad (puntos 9–11).

Si quieres, puedo redactar las versiones corregidas de la nota del GLP y de Cartocor con estos criterios, o preparar la lista de cambios para aplicar al repositorio.
