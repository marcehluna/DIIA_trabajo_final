# Comparación `rrs_only` vs baseline

| | **Baseline** | **RRS only** (`processed`) |
|--|--------------|----------------------------|
| Run ID | `20260525_185138_baseline_call_case_qwen_es` | `20260525_220816_rrs_only` |
| Índice | Call + Case PDF (894 chunks) | Solo JSONL RRS + definiciones (495 chunks) |
| `corpus_sources` | — (pdf implícito) | `processed` |

## Métricas agregadas (Δ = RRS only − baseline)

| Métrica | Baseline | RRS only | Δ |
|---------|----------|----------|---|
| Recall@8 reglas (media) | 0,411 | 0,133 | **−0,278** |
| Recall@8 CALL (media) | 0,267 | 0,000 | **−0,267** |
| F1 citas RRS | 0,222 | 0,060 | −0,162 |
| F1 citas CALL | 0,133 | 0,000 | −0,133 |
| Jaccard resp↔contexto | 0,029 | 0,024 | −0,005 |
| Jaccard resp↔referencia | 0,131 | 0,132 | +0,001 |
| Acierto dictamen | 0,00 | 0,00 | 0,00 |

## Retrieval sobre golden set (`retrieval_hits_agg`)

| Tipo | En contexto (baseline) | En contexto (RRS only) |
|------|------------------------|-------------------------|
| RRS (27 ítems) | 40,7 % (11) | 14,8 % (4) |
| CALL (15 ítems) | 26,7 % (4) | **0 %** (0) |

Matriz contexto→cita (42 ítems):

| Celda | Baseline | RRS only |
|-------|----------|----------|
| A (ctx+cita) | 6 | 0 |
| B (ctx, no cita) | 9 | 4 |
| C (no ctx, cita) | 2 | 2 |
| D (ninguno) | 25 | 36 |

Hits con `chunk_id` `rrs|…`: baseline **0** | RRS only **4** (todos los hits RRS vienen del reglamento indexado).

## Lectura

- Sin Call/Case, **CALL cae a 0** por diseño; no comparar recall CALL con baseline.
- Recall de reglas **baja** respecto al baseline que recuperaba reglas vía Call/Case (41 % → 13 %): el retriever léxico + consulta en español sobre texto RRS en inglés sigue siendo limitante.
- Casos con recall reglas = 1 en RRS only: **4** y **5** (chunks `rrs|…` en top-8).
- Gráfico barras: `plots_retrieval/05_comparacion_corridas.png`.

## Comandos de reproducción

```bash
REGATAS_CORPUS_SOURCES=processed REGATAS_CORPUS_FILES= \
  REGATAS_LOAD_PROCESSED=1 REGATAS_LLM_BACKEND=http \
  REGATAS_LLM_MODEL=qwen2.5:14b-instruct REGATAS_SYSTEM_PROMPT_LANG=es \
  python scripts/eval_run.py --label rrs_only --lang es --plots

python scripts/compare_eval_runs.py "eval/corrida baseline" \
  "eval/runs/20260525_220816_rrs_only"
```
