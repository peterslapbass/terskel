---
title: Un código de moneda que valía 900 veces
date: 2026-11-12
---

# Un código de moneda que valía 900 veces

<div class="tech-only">
<p><strong>Qué encontramos.</strong> La ENIA trae el valor bruto de producción en una columna de moneda codificada (<code>A005</code>): 4 y 5. El descriptor del INE no la documenta en la base actual. Al cruzar los valores con el tipo de cambio del BCCh, la aritmética la resuelve:</p>

<table>
<tr><th>Código</th><th>Interpretación</th><th>Razón implícita</th></tr>
<tr><td>4</td><td>miles de CLP</td><td>≈ 1</td></tr>
<tr><td>5</td><td>miles de USD</td><td>≈ 906</td></tr>
</table>

<p>El tipo de cambio promedio de 2024 fue 943,58 CLP/USD, así que 906 es consistente con «miles de dólares» y no con otra cosa: un 4% de diferencia, explicable por mezcla de meses y por el desfase entre el precio y el tipo de cambio.</p>

<p><strong>Qué significa.</strong> Sin decodificar, una fila en dólares se lee como pesos: el VBP de esa planta queda <strong>900 veces</strong> más chico y su intensidad —CLP por TJ, o tCO₂ por CLP— queda 900 veces más grande. Como la columna no trae diccionario, el error es silencioso y no afecta a todas las plantas por igual: solo a las que declaran en dólares.</p>

<p><strong>Qué hicimos.</strong> Decodificamos 4 = miles de CLP, 5 = miles de USD, y multiplicamos por el tipo de cambio anual del BCCh antes de deflactar con el IPP. Se conserva la columna original y se agrega el valor en CLP con nombre explícito.</p>

<p><strong>Qué queda.</strong> Confirmar el código con el INE. La evidencia es aritmética, no documental, y está declarada como inferencia en la ficha de la ENIA. Si el código fuera otro, todos los indicadores económicos se mueven; los físicos no.</p>

<p><strong>Cómo se reproduce.</strong> <code>python src/normalize/enia.py</code> y la ficha <a href="{{ '/fuentes/enia.html' | relative_url }}">ENIA</a>.</p>
</div>

<div class="plain-only">
<h3>¿Por qué algunos valores de producción parecen 900 veces más chicos?</h3>

<p>En palabras simples: <strong>algunas plantas declaran en dólares y otras en pesos, pero el registro no deja claro cuál es cuál</strong>.</p>

<p><strong>¿Qué pasó?</strong> La encuesta industrial (ENIA) tiene una columna llamada <code>A005</code> que indica si los valores están en miles de pesos chilenos o en miles de dólares. El problema es que el INE no documenta bien qué significa cada código. Cuando cruzamos los valores con el tipo de cambio del Banco Central, descubrimos que el código 4 significa miles de pesos chilenos y el código 5 significa miles de dólares.</p>

<p><strong>¿Qué significa esto?</strong> Si una planta declara en dólares y alguien lee ese número como si fuera pesos, el valor bruto de producción parecerá 900 veces más chico de lo que realmente es. Y si calculas intensidad energética o emisiones por unidad de producción, el resultado estará 900 veces más grande. Es un error silencioso: no afecta a todas las plantas, solo a las que declaran en dólares.</p>

<p><strong>¿Qué hicimos?</strong> Decodificamos la columna: el 4 significa miles de pesos chilenos, el 5 significa miles de dólares. Multiplicamos los valores en dólares por el tipo de cambio anual del Banco Central antes de ajustarlos por inflación. Conservamos la columna original para que quede claro de dónde salió cada número.</p>

<p><strong>¿Qué queda por hacer?</strong> Confirmar con el INE que el código es correcto. Por ahora, nuestra conclusión se basa en aritmética, no en un documento oficial que lo confirme. Si el código fuera diferente, todos los indicadores económicos cambiarían, aunque los físicos (CO₂ y energía) no se ven afectados.</p>
</div>