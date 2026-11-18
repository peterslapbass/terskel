---
title: Abierto
---

# Abierto

El sitio publica las cifras, los parquet de los que salen y los scripts que los
producen. Lo que no se publica también está dicho acá.

## Lo que sí

| Qué | Dónde | Licencia |
|---|---|---|
| Cifras, tablas y gráficos | este sitio y los parquet | CC BY 4.0 |
| Código de la cadena | [repositorio](https://github.com/peterslapbass/terskel) | MIT |
| Parquet procesados (~30 MB) | [Datos]({{ '/datos.html' | relative_url }}) | CC BY 4.0, con la fuente citada |
| Manifiesto de fuentes (URL, sha256, licencia) | [Descargas]({{ '/fuentes/descargas.html' | relative_url }}) | — |

## Lo que no

**Los archivos crudos.** Los XLSX del RETC pesan unos 60 MB por edición —180 MB en
total— y contienen datos por establecimiento de terceros. En vez del archivo, el
manifiesto entrega la URL oficial, el tamaño y el sha256: se descarga de la fuente y se
verifica el hash. Los CSV de la ENIA y el XLSX del balance sí son livianos, pero por
coherencia tampoco se copian: se referencian igual.

**Los nombres de personas.** El sitio nombra plantas como `empresa – planta`. No publica
RUT, direcciones ni coordenadas.

## Cómo citar

> Terskel (2026). *Emisiones y energía de la industria chilena, año de referencia 2024*.
> https://peterslapbass.github.io/terskel/

Para una cifra puntual, cita también la fuente primaria que aparece en su ficha. Este
sitio no es la fuente: es una lectura de fuentes públicas.

## Errores

Si una cifra está mal, el error está en el script o en el supuesto, no en el lector.
Abre un issue en el [repositorio](https://github.com/peterslapbass/terskel/issues) con
la cifra, la tabla y la edición. Cada corrección queda en el historial de commits, que
es público.

## Lo que este sitio no es

No es un inventario oficial ni un registro de cumplimiento. No reemplaza al RETC, al
Balance Nacional de Energía ni a la ENIA. Ninguna de las instituciones citadas participa
en el proyecto ni respalda sus conclusiones.

La limitación más importante está dicha en la portada y en cada tabla: **el RETC no es
un inventario industrial**. De las 44,97 Mt que valida en 2024, 25,20 Mt corresponden a
las 14 categorías industriales, 18,08 Mt a generación eléctrica y 1,69 Mt al resto. Lo
que la gran minería no declara no está en ninguna de esas tres cifras: la energía del
balance implica unos 7,6 Mt de CO₂, de los que el registro solo ve 0,04 Mt.
