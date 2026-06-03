# Corpus pre-procesado (JSONL)

Artefactos generados desde los CSV estructurados del RRS. **No editar a mano** los `.jsonl`; regenerar con el script.

## Generar

```bash
python scripts/build_corpus_processed.py
```

Fuentes:

- `scripts/rrs_reglas_2025_2028.csv` → `rrs_rules.jsonl` (un chunk por regla/subregla)
- `scripts/definitions.csv` → `definitions.jsonl`
- `scripts/call_book_calls.csv` → `calls.jsonl`
- `scripts/case_book_cases.csv` → `cases.jsonl`

## Esquema JSONL v2 (`processed_record_v2`)

Cada línea es un JSON con campos comunes y metadatos del CSV (no editar a mano; regenerar con el script):

| Campo | Uso |
|-------|-----|
| `doc_type` | `rrs` \| `definition` \| `call` \| `case` |
| `ref_id` | Código (regla, CALL, case, definición) |
| `title`, `text` | Título y cuerpo del fragmento |
| `section` | Sección del libro (p. ej. `SECTION A – …`) |
| `referenced_rules` | Lista de reglas RRS vinculadas (CSV `reglas` + inferencia en texto) |
| `rrs_tipo` | `regla` \| `definicion` \| … (solo RRS) |
| `page_start`, `page_end` | Páginas en el PDF fuente (calls/cases) |
| `lang` | Idioma del fragmento (`en`) |

`MANIFEST.json` declara `"version": 2` y `"schema": "processed_record_v2"`.

En runtime, `TextChunk.header_line()` expone metadatos al LLM, p. ej. `Sección: …`, `Reglas: 13, 17`, `pp. 8-9`.

## Carga en runtime

Controlado por `REGATAS_CORPUS_SOURCES`:

| Valor | Índice |
|-------|--------|
| `processed` | **Solo** JSONL de esta carpeta (reconstrucción fase 1) |
| `pdf` | Solo PDFs (`REGATAS_CORPUS_FILES`) |
| `full` | JSONL + PDFs Call/Case |
| `production` (defecto app) | Igual que `processed` + cupos E11 vía `REGATAS_PROFILE` |

Reconstrucción **solo RRS** (sin Call/Case):

```bash
export REGATAS_CORPUS_SOURCES=processed
export REGATAS_CORPUS_FILES=
python scripts/rebuild_rag_rrs_only.py
```

Ver `docs/RAG_RECONSTRUCCION_RRS.md`.

Baseline histórico (sin RRS): `REGATAS_CORPUS_SOURCES=pdf` y `REGATAS_LOAD_PROCESSED=0`.

## Identificadores de chunk

- RRS: `rrs|{numero_regla}` (ej. `rrs|16.1`); si hay varias filas CSV con el mismo número, `rrs|16.1#1`, …
- Definición: `definition|{id}`
- PDF: `{archivo}|p{página}|#{índice}` (sin cambios)
