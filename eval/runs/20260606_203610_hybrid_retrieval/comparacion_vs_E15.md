# Comparación — `hybrid_retrieval` (E16)

**Run ID:** `20260606_203610_hybrid_retrieval`

## Qué cambió respecto a la corrida anterior

- Misma configuración de corpus/retriever/LLM que la corrida anterior; variación solo en resultados estocásticos o artefactos.

## Comparativa vs E15 (`hybrid_retrieval`)

- Recall@k reglas: 0.60 → 0.76 (+0.16)
- Recall@k CALL: 0.13 → 0.20 (+0.07)

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → —
- F1 citas CALL: 0.13 → —
- Jaccard resp↔ctx: 0.03 → —
- Jaccard resp↔ref: 0.13 → —
- Dictamen auto: 0.00 → —
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —
