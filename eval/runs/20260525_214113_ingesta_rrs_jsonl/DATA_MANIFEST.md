# Datos disponibles — corrida ingesta RRS JSONL

**run_id:** `20260525_214113_ingesta_rrs_jsonl`  
**schema_version:** 2  
**casos:** 15  
**Informe:** `INFORME_CORRIDA_INGESTA_RRS.md`  
**Baseline (solo lectura):** `eval/corrida baseline/`, tag `v0.1.0-baseline`

## Archivos en esta carpeta

| Archivo | Contenido |
|---------|-----------|
| `INFORME_CORRIDA_INGESTA_RRS.md` | Resumen, comparación vs baseline, análisis |
| `report.json` | Fuente completa: relatos, respuestas, chunks, métricas y `extended` |
| `metrics_long.csv` | Una fila por caso × métrica (ideal para pandas/seaborn) |
| `retrieval_hits.json` | Por caso: regla/CALL esperada → rank del primer hit |
| `chunks_summary.csv` | Cada chunk recuperado: fuente, página, longitud, refs detectadas |
| `eval_set_snapshot.json` | Copia del golden set usado en la corrida |
| `summary.txt` / `results_comparison.md` | Resúmenes legibles |
| `plots/*.png` | Gráficos métricas generales |
| `plots_retrieval/*.png` | Tasas, matriz, rank, comparación vs baseline (`05_…`) |
| `retrieval_hits_detail.csv` / `retrieval_hits_agg.csv` | Detalle y agregados de retrieval |

## Gráficos adicionales posibles (sin re-ejecutar LLM)

- **recall_curve**: metrics_long.csv o extended.recall_curve_*
- **mrr_by_case**: metrics_long.csv (mrr_rules, mrr_calls)
- **hits_per_expected_rule**: retrieval_hits.json
- **retrieved_source_mix**: chunks_summary.csv
- **chunk_length_dist**: chunks_summary.csv
- **citation_precision_recall**: metrics.response.citation_*
- **expected_vs_found_rules**: retrieval_hits.json + citations_found
- **compare_runs_delta**: dos report.json o metrics_long.csv

## Campos en `report.json` → `cases[].metrics.extended`

- `recall_curve_rules` / `recall_curve_calls`: recall@1 … recall@k
- `mrr_rules` / `mrr_calls`: mean reciprocal rank
- `rule_hits` / `call_hits`: detalle por ítem esperado
- `retrieved_by_source`: conteo Call vs Case por consulta
- `retrieved_chunks_detail`: metadatos de cada fragmento
- `answer_refs`: citas extraídas de la respuesta
