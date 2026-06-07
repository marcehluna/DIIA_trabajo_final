# Experimento E17: retrieval híbrido vs E13 (productivo)

Corrida **E17** (`20260606_203922_hybrid_prompt_v3`) — mismo índice/cupos **E11** y prompt v3 que **E13**, con `REGATAS_EMBEDDING_BACKEND=hybrid` (léxico + `all-MiniLM-L6-v2`, RRF; fallback semántico cuando el relato ES no matchea léxicamente el corpus EN).

Referencia **E13** (`20260604_124747_prompt_v3_format`) — perfil productivo actual.

---

## Métricas agregadas

| Métrica | E13 | E17 | Δ | Lectura |
|---------|-----|-----|---|---------|
| R@k reglas | 0.76 | 0.76 | 0.00 | Sin mejora media en recuperación |
| R@k CALL | 0.20 | 0.20 | 0.00 | Idem |
| **F1 RRS** | **0.22** | 0.13 | −0.09 | Citas peor |
| F1 CALL | 0.07 | 0.07 | 0.00 | Idem |
| Jaccard resp ↔ referencia | 0.16 | 0.16 | ~0 | Similar |
| **Dictamen auto** | **60%** | **47%** | **−13 pp** | Por debajo del umbral productivo |

Fuente: `report.json` → `aggregate`. Detalle en [`eval/runs/20260606_203922_hybrid_prompt_v3/comparacion_vs_E13.md`](../../eval/runs/20260606_203922_hybrid_prompt_v3/comparacion_vs_E13.md).

---

## Conclusión y recomendación

1. **El híbrido resuelve casos de retrieval “sin overlap”** (ej. caso 7: R@k reglas 0 → 1.0 con `call|L2`), pero **no mejora el sistema completo**.
2. **Cambia el mix de chunks** (regresiones en casos 9, 10, 14, 15) y el LLM **no aprovecha** el mejor contexto para citar (caso 7: F1=0 pese a R@k=1).
3. **Recomendación del proyecto:** permanecer en **E11 retrieval léxico + E13 prompt v3**. E15–E17 quedan como evidencia de que el cuello de botella principal no es solo el índice léxico, sino **selección de citas y dictamen** con el prompt actual.

## Corridas relacionadas (solo retrieval)

| ID | Run | R@k reglas | Nota |
|----|-----|------------|------|
| E15 | `20260606_203312_hybrid_retrieval` | 0.60 | Híbrido sin fallback semántico (abortado) |
| E16 | `20260606_203610_hybrid_retrieval` | 0.76 | Híbrido retrieval-only; igual media que E11 |

## Reproducir E17

```bash
REGATAS_LLM_BACKEND=http REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
  python scripts/eval_run.py --label hybrid_prompt_v3 \
  --embedding-backend hybrid --lang es --plots
```

Artefactos: [`eval/runs/20260606_203922_hybrid_prompt_v3/`](../../eval/runs/20260606_203922_hybrid_prompt_v3/)
