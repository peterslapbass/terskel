# Traspaso de sesión — Terskel (INTERACTION)

Documento para retomar el trabajo con otro agente o en otra sesión.
Última actualización: **2026-11-18**.

---

## 1. Qué es el proyecto

Sitio y base analítica reproducible sobre emisiones y energía de la industria
chilena. Integra RETC (MMA), Balance Nacional de Energía (CNE), ENIA e IPP (INE)
y dólar observado (BCCh). Principio rector: **ningún número se publica sin su
ficha, su unidad y su límite**; cada cifra sale de un parquet versionado y cada
parquet de un script del repo.

- Sitio: <https://peterslapbass.github.io/terskel/>
- Repo: <https://github.com/peterslapbass/terskel>
- Local: `C:\Users\pedro\OneDrive - COMERCIAL E INDUSTRIAL URZKEN LTDA\APPS\INTERACTION`

## 2. Estado al cierre de esta sesión

| Elemento | Estado |
|---|---|
| Rama `main` | `b533f0b`, sincronizada con `origin/main` |
| GitHub Pages | Publica desde `docs/`, responde **200** |
| `verifica.py` | 30 páginas, 0 errores |
| Build Jekyll | OK, 0 enlaces rotos |
| Datos procesados | 24,2 MB versionados |
| Crudos | **no** versionados (se re-descargan con `manifest.csv`) |

Commits de la sesión:

```
b533f0b Quitar los modos tecnico y explicado del sitio
9230d75 Aclarar que _publicar es opcional y no se versiona
c6f6c9b Restaurar proyecto completo y unificar el sitio
```

Rescate: la rama local `rescate/32774bb` apunta al commit colgante
`32774bb` (el proyecto que un `git reset` había borrado). Respaldo completo en
`C:\Users\pedro\AppData\Local\Temp\INTERACTION-2026-11-18.bundle` (204 MB).

## 3. Mapa del repositorio

```
src/
  common/       paths.py (ROOT = parents[2]), manifest.py, calidad.py, industrias.py
  ingest/       retc.py, manual.py (descarga+sha256+manifest), fx.py, ipp.py
  normalize/    retc.py, retc_co2_combustible.py, retc_energia_implicita.py,
                bne.py, enia.py, ciiu_bne.py, fx.py, ipp.py, text.py
  audit/        retc_anomalias.py, retc_audit.py, bne_resumen.py, integracion_rama.py
  indicators/   intensidad.py      -> reports/indicadores_intensidad.md
  scenarios/    escenarios.py      -> reports/escenarios_2030.md
  reports/      graficos.py (7 SVG), sitio.py (docs), verifica.py (lint),
                publicar.py (paquete _publicar/ opcional)
data/
  raw/          manifest.csv (no se versionan los crudos)
  processed/    parquet normalizado + indicators + scenarios (24,2 MB)
  reference/    insumos chicos de publicación
reports/        .md y .json/.csv generados por los scripts
docs/           sitio Jekyll (raíz de GitHub Pages, baseurl /terskel)
  resultados/   7 páginas: 6 generadas + index.md a mano
  fuentes/      fichas de fuente + descargas.md (generado)
  notas/        8 notas de datos + índice
```

## 4. Cadena de datos

Entorno: Python 3.9.13, polars 1.36.1, duckdb 1.4.4, pyarrow 18.1.0.
Ruby 4.0.9, Jekyll 4.4.1, bundler 4.1.0.

```powershell
$env:PYTHONPATH = "src"

# datos
python src/ingest/retc.py --years 2023 2024 2025
python src/normalize/retc.py --years 2023 2024 2025
python src/normalize/retc_co2_combustible.py
python src/audit/retc_anomalias.py
python src/normalize/retc_energia_implicita.py --year 2024
python src/audit/retc_audit.py
python src/normalize/bne.py --years 2023 2024
python src/audit/bne_resumen.py
python src/normalize/enia.py --years 2023 2024
python src/normalize/ciiu_bne.py
python src/ingest/fx.py;   python src/normalize/fx.py
python src/ingest/ipp.py;  python src/normalize/ipp.py
python src/audit/integracion_rama.py --year 2024

# análisis
python src/indicators/intensidad.py     # -> reports/indicadores_intensidad.md
python src/scenarios/escenarios.py      # -> reports/escenarios_2030.md

# sitio
python src/reports/graficos.py          # -> docs/assets/fig/*.svg
python src/reports/sitio.py             # -> docs/resultados/*.md, docs/datos.md, docs/fuentes/descargas.md
python src/reports/verifica.py          # lint previo a publicar

# publicación (opcional)
python src/reports/publicar.py          # -> _publicar/ (gitignored)
```

Previsualizar:

```powershell
cd docs
bundle exec jekyll build
bundle exec jekyll serve --baseurl /terskel   # http://localhost:4000/terskel/
```

## 5. Reglas que no se deben romper

1. **Dato primero.** No escribir cifras a mano en `docs/`: se regeneran.
2. **`reports/*.md` los escriben los scripts.** Si hay que cambiar prosa o
   estructura, se cambia el emisor (`intensidad.py`, `escenarios.py`,
   `retc_anomalias.py`, …), no el `.md`. Re-ejecutar la cadena sobrescribe.
3. **`docs/resultados/*.md` los escribe `sitio.py`.** La única excepción es
   `docs/resultados/index.md`, que es manual.
4. **Formato numérico chileno centralizado** en `sitio.py` (`chileniza()`):
   `1.234,5`. Los emisores trabajan en formato inglés y la conversión ocurre en
   la capa de presentación.
5. **`docs/` es la raíz de GitHub Pages** con `baseurl: /terskel`. En HTML usar
   `{{ '/ruta' | relative_url }}`; nunca hardcodear `/terskel/...`.
6. **Los crudos no se versionan.** `data/raw/*` está en `.gitignore` salvo
   `manifest.csv`, que tiene URL, fecha, sha256 y licencia.
7. **`_publicar/` no se versiona.** Es un paquete opcional que arma
   `publicar.py`.

## 6. Qué se hizo en esta sesión

- Diagnóstico completo: el repo había perdido `src/`, `data/` y `reports/` por
  un `git reset`; el contenido sobrevivía en el commit colgante `32774bb`.
- Rescate: rama `rescate/32774bb` + bundle de 204 MB en `%TEMP%`.
- Restauración de `src/`, `data/processed`, `data/reference`,
  `data/raw/manifest.csv`, `reports/`, README y documentos de revisión.
- Eliminación de `_publicar/` (24,6 MB duplicados). `LICENSE` movido a la raíz.
- `docs/resultados/index.md`: de 297 a 60 líneas; se quitaron bloques
  duplicados y un informe completo pegado por error.
- `sitio.py`: `chileniza()` para numeración chilena en todas las páginas.
- Emisores: "Nota importante" y "Lectura y límites" con subtítulos en
  intensidad; "Introducción" y límites con subtítulos en escenarios.
- Enlaces: rutas `/terskel/...` hardcodeadas → `relative_url`; enlace roto
  `../metodologia.html` corregido; BOM quitado de la nota del GLP.
- `Gemfile` estaba en UTF-16 (corrupto): reescrito en UTF-8 con `jekyll` y
  `jekyll-relative-links`.
- `requirements.txt`: `polars>=1.36`. Metodología: años de BNE/ENIA corregidos.
- `.gitignore`, `.gitattributes`; upstream de `main` → `origin/main`.
- **Sistema de modos técnico/explicado eliminado**: fuera el conmutador, el
  script, las reglas CSS y los bloques duplicados en portada, notas y fichas.
  Se conservó el contenido técnico.

## 7. Trampas conocidas

- **Los emisores pisan `reports/`.** Si se edita a mano y luego se corre la
  cadena, se pierde. Ver regla 2.
- **`verifica.py` no detecta enlaces que se salen de `baseurl`.** Normaliza
  `../` y puede dar por bueno un enlace roto en el sitio publicado. El
  comprobador real está descrito en el script temporal
  `%TEMP%\check_site.py` (recorre `_site`, resuelve `href`/`src` y verifica
  que el archivo exista). Si se perdió, rehacerlo es media página de Python.
- **Consola Windows.** PowerShell muestra los acentos como `?` (cp850/cp1252);
  los archivos están en UTF-8 válido. No "corregir" lo que se ve mal en consola.
- **Saltos de línea.** Los archivos se escriben con `newline="\n"` (LF); el
  repo local tiene `core.autocrlf=true`, así que Git avisa "LF will be replaced
  by CRLF". Es esperado.
- **`Path.write_text(newline=...)` no existe en Python 3.9.** Usar `io.open`.
- **No restaurar los crudos** (194 MB de XLSX) salvo que haga falta: se bajan
  con `ingest/manual.py` y se validan contra el sha256 del manifiesto.
- **El `.git` pesa ~204 MB** por los XLSX que estuvieron versionados alguna vez.

## 8. Verificación rápida antes de publicar

```powershell
$env:PYTHONPATH = "src"
python src/reports/sitio.py
python src/reports/verifica.py          # debe decir: ok, 30 páginas
cd docs
bundle exec jekyll build                 # debe terminar sin errores
```

Checklist manual:

- [ ] `docs/resultados/index.md` sin secciones repetidas.
- [ ] Ningún `.md` con encabezados `#` partidos en dos líneas.
- [ ] Sin `tech-only` / `plain-only` / `data-mode` en `docs/`.
- [ ] Sin rutas `/terskel/...` hardcodeadas en HTML.
- [ ] `docs/datos.md` y `docs/fuentes/descargas.md` con números chilenos.

## 9. Pendientes y ideas

- **Adelgazar historial** con `git filter-repo` (sacar los XLSX del historial;
  el repo pesa 204 MB). Requiere reescribir historia y force-push.
- **Revisar afirmaciones causales.** `src/audit/retc_anomalias.py` (~líneas
  169, 178-181) concluye "es un defecto del factor de emisión"; las notas
  usan "error"/"imposible". `terskel verificacion.md` recomienda decir
  "anomalía" / "inconsistente con su propia serie". La conclusión es
  defendible, pero conviene separar dato de interpretación.
- **Unificar el discurso de fuentes**: portada dice "cinco fuentes públicas";
  el pie lista cinco instituciones. Revisar si "tres fuentes" sobrevive en
  algún texto.
- **Histórico de notas**: `docs/notas/` tiene 8 notas; si se agrega una, debe
  llevar front matter con `title` y `date` (Jekyll las lista por fecha).
- **No hay CI.** `verifica.py` corre a mano; un workflow de GitHub Actions que
  ejecute `verifica.py` + `jekyll build` en cada push sería el siguiente paso
  natural.

## 10. Referencias internas

- `terskel revision repo.md` — revisión del repositorio y la cadena.
- `terskel sugerencias.md` — mejoras sugeridas (incluye el punto de las
  conclusiones causales).
- `terskel verificacion.md` — verificación de afirmaciones de las notas.
- `README.md` — estructura, comandos y convenciones.
- `docs/metodologia.md` — método en cuatro pasos y comandos de reproducción.
