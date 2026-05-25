# Corrida baseline

Línea de referencia para comparar mejoras de ingesta.

| Parámetro | Valor |
|-----------|--------|
| `run_id` | `20260525_185138_baseline_call_case_qwen_es` |
| `schema_version` | `2` (reporte enriquecido) |
| Corpus | Call Book + Case Book (sin RRS) |
| Modelo | `qwen2.5:14b-instruct` |
| Prompt | Español, CoT |

## Informe para el trabajo final

**`INFORME_CORRIDA_BASELINE.md`** — objetivo, procedimiento, resultados, análisis y protocolo de comparación. Incluye **§4.1**: el RRS **no** está en el índice; las métricas «RRS» son reglas de referencia del golden set y menciones en Call/Case/respuesta.

## Archivos (datos completos para gráficos)

| Archivo | Uso |
|---------|-----|
| `report.json` | **Fuente maestra**: relatos, query, respuesta LLM, output ideal, chunks (texto completo), métricas y `metrics.extended` |
| `metrics_long.csv` | Serie larga caso × métrica (recall@1…@k, MRR, F1, Jaccard, etc.) |
| `retrieval_hits.json` | Por regla/CALL esperada: ¿hubo hit?, rank, chunk_id |
| `retrieval_hits_detail.csv` | Mismo contenido en formato Excel (una fila por ítem esperado) |
| `retrieval_hits_resumen_casos.csv` | Vista resumida por caso (conteos aciertos/contexto/citas) |
| `retrieval_hits_agg.csv` | Tasas agregadas (contexto, cita, pipeline, MRR, citas espurias) |
| `retrieval_hits_por_caso_agg.csv` | Tasas por caso (RRS/CALL) para comparar corridas |
| `plots_retrieval/*.png` | 4 gráficos desde `retrieval_hits_detail.csv` |
| `chunks_summary.csv` | Cada fragmento recuperado: fuente, página, longitud, refs detectadas |
| `eval_set_snapshot.json` | Golden set congelado al momento de la corrida |
| `results_comparison.md` | Tabla esperado vs métricas |
| `results_comparison_meta.csv` | Metadatos de corrida + métricas agregadas (Excel) |
| `results_comparison_por_caso.csv` | Misma tabla por caso, con columnas extra (precision, MRR, citas) |
| `summary.txt` | Resumen agregado |
| `DATA_MANIFEST.md` | Índice de datos y gráficos posibles |
| `plots/*.png` | 8 gráficos ya generados |

## Regenerar sidecars (sin LLM)

Si actualizás el módulo de enriquecimiento:

```bash
python scripts/enrich_eval_report.py "eval/corrida baseline"
```

## Agregar métricas y gráficos de retrieval

```bash
python scripts/aggregate_retrieval_hits.py "eval/corrida baseline"

# Tras una nueva corrida (comparar con baseline):
python scripts/aggregate_retrieval_hits.py "eval/runs/<nueva>" \
  --compare "eval/corrida baseline" --label-compare ingesta_v2
```

Gráficos en `plots_retrieval/`:

1. `01_tasas_por_tipo.png` — contexto / cita / pipeline (RRS vs CALL)
2. `02_tasas_por_caso.png` — las 4 tasas por caso
3. `03_distribucion_rank.png` — rank del primer hit (histograma)
3b. `03_distribucion_rank_torta.png` — misma distribución en torta con %
4. `04_matriz_contexto_cita.png` — matriz 2×2 contexto → cita (barras)
4b. `04_matriz_contexto_cita_torta.png` — misma matriz en torta con %
5. `05_comparacion_corridas.png` — solo con `--compare`
