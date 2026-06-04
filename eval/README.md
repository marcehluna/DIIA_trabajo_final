# Evaluación del asistente (golden set)

Conjunto de **15 casos** desde `docs/Casos de Regatas.xlsx` (columna **Input** = relato; etiquetas desde **Output Ideal**).

**Resumen narrativo (E0–E13):** [`eval/RESUMEN_CORRIDAS_EVAL.md`](RESUMEN_CORRIDAS_EVAL.md) — objetivo y delta de cada corrida (lectura humana).

**Diario de todas las corridas (E0, E1, …):** [`eval/DIARIO_PRUEBAS.md`](DIARIO_PRUEBAS.md) — se **regenera solo** al final de cada `eval_run.py` (cambios vs corrida anterior + comparativa vs E0). Opcional: `--diario-nota "…"`.

**Registro narrativo (informe final):** [`docs/REGISTRO_TRABAJO_INFORME_FINAL.md`](../docs/REGISTRO_TRABAJO_INFORME_FINAL.md) — decisiones, código y bitácora; complementa el diario automático.

**Comparativa E0 vs E12 (citabile):** [`docs/INFORME_CITAS_E0_vs_E12.md`](../docs/INFORME_CITAS_E0_vs_E12.md) — métricas, faithfulness, Jaccard, conclusiones y CSV.

**Timeline visual:** [Draw.io](docs/timeline_corridas_eval.drawio) · [HTML navegable](docs/timeline_corridas_eval.html) — línea temporal E0→E13, métricas y guía integrada.

## 1. Generar golden set

```bash
python scripts/build_eval_set.py
```

Salida: `eval/data/eval_set.json`

## Perfil productivo (defecto) vs línea base E0

| | **Producción (E11)** | **Baseline (E0)** |
|--|----------------------|-------------------|
| Perfil | `REGATAS_PROFILE=production` (defecto) | `REGATAS_PROFILE=baseline` |
| Corpus | JSONL `processed` + cupos 2+3+2+1 | PDF Call+Case |
| Doc | `docs/PERFIL_PRODUCTIVO.md` | `eval/corrida baseline/` |

Regresión tras cambios (umbrales E11 retrieval + E13 respuesta): `python scripts/regression_eval.py <carpeta_corrida>` — ver [`RESUMEN_CORRIDAS_EVAL.md`](RESUMEN_CORRIDAS_EVAL.md).

## Línea base histórica (E0)

| Parámetro | Valor |
|-----------|--------|
| Corpus | Call Book + Case Book (sin RRS) |
| Ingesta | Producción actual (`chunk_size=900`, `overlap=120`, por página) |
| LLM | Qwen vía Ollama (`qwen2.5:14b-instruct`) |
| Prompt | Español (`REGATAS_SYSTEM_PROMPT_LANG=es`, estrategia `cot`) |

Corrida de referencia:

```bash
REGATAS_ACTIVITY_CONSOLE=0 \
REGATAS_LLM_BACKEND=http \
REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
REGATAS_SYSTEM_PROMPT_LANG=es \
python scripts/eval_run.py --label baseline_call_case_qwen_es --lang es --plots
```

Resultados: `eval/corrida baseline/` (run_id: `20260525_185138_baseline_call_case_qwen_es`)

Tag git de referencia: `v0.1.0-baseline`

## Ingesta RRS desde CSV → JSONL (v0.2)

```bash
# 1. Generar artefactos (desde scripts/*.csv)
python scripts/build_corpus_processed.py

# 2. Correr eval (carga JSONL + PDFs Call/Case por defecto)
REGATAS_ACTIVITY_CONSOLE=0 REGATAS_LLM_BACKEND=http \
  REGATAS_LLM_MODEL=qwen2.5:14b-instruct REGATAS_SYSTEM_PROMPT_LANG=es \
  python scripts/eval_run.py --label ingesta_rrs_jsonl --lang es --plots

# 3. Comparar con baseline
python scripts/aggregate_retrieval_hits.py "eval/runs/<run_id>" \
  --compare "eval/corrida baseline"
```

Sin JSONL (solo PDFs, como baseline): `REGATAS_LOAD_PROCESSED=0`.

Documentación: `corpus/processed/README.md`

## Tablas de revisión

```bash
# Etiquetas esperadas (golden set)
python scripts/build_eval_review_table.py
# → eval/data/golden_set_review.md

# Esperado vs métricas de una corrida
python scripts/build_eval_results_table.py "eval/corrida baseline"
# → eval/corrida baseline/results_comparison.md
```

## Gráficos

```bash
python scripts/plot_eval_run.py eval/runs/<run_id>
# → eval/runs/<run_id>/plots/*.png
```

O con `--plots` en `eval_run.py` (genera al finalizar).

## Faithfulness (fidelidad al contexto)

Mide si **cada afirmación** de la respuesta está respaldada por los **fragmentos recuperados** (LLM-as-judge en dos pasos: extracción de claims + verificación).

**En corrida nueva** (más lento: ~2 llamadas LLM × 15 casos):

```bash
REGATAS_LLM_BACKEND=http REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
  python scripts/eval_run.py --label mi_prueba --lang es --faithfulness
```

**Sobre corrida ya guardada** (sin re-ejecutar RAG ni generación):

```bash
REGATAS_LLM_BACKEND=http REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
  python scripts/score_faithfulness.py "eval/corrida baseline"
# o: eval/runs/<run_id>
```

Salida en `report.json` → `cases[].metrics.response.faithfulness` y agregados `mean_faithfulness_rate` / `mean_faithfulness_rate_strict` en `aggregate`. También filas en `metrics_long.csv`.

| Campo | Significado |
|-------|-------------|
| `faithfulness_rate` | supported / total claims |
| `faithfulness_rate_strict` | supported / (supported + not_supported), excluye `unknown` |
| `claims[]` | Detalle por afirmación: veredicto, `evidence_ids`, rationale |

## 2. Correr evaluación

Solo recuperación (rápido, sin LLM):

```bash
REGATAS_ACTIVITY_CONSOLE=0 python scripts/eval_run.py --label baseline --retrieval-only
```

Recuperación + respuesta del LLM (usá el mismo `.env` que `app.py`):

```bash
REGATAS_LLM_BACKEND=http REGATAS_ACTIVITY_CONSOLE=0 \
  python scripts/eval_run.py --label baseline_v1
```

Comparar ingesta: repetí con otra etiqueta y distinto `REGATAS_CORPUS_FILES` / chunking, por ejemplo:

```bash
REGATAS_CORPUS_FILES="2025-2028-RRS-with-Changes-and-Corrections.pdf,WS-Case-Book-2025-2028-v2025-07.pdf" \
  REGATAS_CHUNK_SIZE=700 REGATAS_CHUNK_OVERLAP=200 \
  python scripts/eval_run.py --label rrs_case_chunks_v2
```

## 3. Resultados

Cada corrida crea `eval/runs/<timestamp>_<label>/` (o carpeta dedicada como `eval/corrida baseline/`):

| Archivo | Contenido |
|---------|-----------|
| `report.json` | Config, respuestas, chunks, métricas, `metrics.extended` (schema v2) |
| `metrics_long.csv` | Datos en formato largo para pandas/gráficos extra |
| `retrieval_hits.json` | Detalle de aciertos por regla/CALL esperada |
| `chunks_summary.csv` | Metadatos de cada chunk recuperado |
| `eval_set_snapshot.json` | Copia del golden set usado |
| `DATA_MANIFEST.md` | Índice de archivos y gráficos posibles |
| `summary.txt` | Resumen legible en consola |

Enriquecer una corrida ya guardada (sin re-llamar al LLM):

```bash
python scripts/enrich_eval_report.py "eval/corrida baseline"
```

## Re-score de citas (sin re-ejecutar LLM)

Tras ampliar el parser en `regatas_assistant/eval/refs.py` (p. ej. viñetas `**Regla 16.1**`, `**Case N**` del prompt v3):

```bash
python scripts/rescore_eval_citations.py eval/runs/<run_id>
```

Actualiza `report.json`, `metrics_long.csv`, `summary.txt` y plots en la carpeta de la corrida.

## Métricas

**Recuperación**

- `recall_at_k_rules`: % reglas esperadas presentes en top-k chunks
- `recall_at_k_calls`: % TR CALL esperados en top-k (útil si indexás Call Book)

**Respuesta** (requiere LLM real, no stub)

- `citation_rrs` / `citation_calls`: precision, recall, F1 de citas vs esperado
- `token_jaccard_answer_context`: solapamiento léxico respuesta ↔ contexto recuperado
- `token_jaccard_answer_reference`: solapamiento respuesta ↔ output ideal del Excel
- `verdict_match`: coincidencia gruesa de dictamen (penalizar / sin penalización / exonerar)

## Notas

- Las reglas y calls del ground truth se **parsean** del texto ideal; revisá `eval_set.json` si algún caso quedó incompleto.
- Si el corpus no incluye Call Book, `recall_at_k_calls` y `citation_calls` serán bajos por diseño.
- Para comparar antes/después de ingesta: **mismo** `eval_set.json`, mismo modelo/prompt, solo cambia configuración de corpus/chunks.
