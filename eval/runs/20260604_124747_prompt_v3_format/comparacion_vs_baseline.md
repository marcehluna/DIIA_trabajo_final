# Comparación — `prompt_v3_format` (E13)

**Run ID:** `20260604_124747_prompt_v3_format`

## Qué cambió respecto a la corrida anterior

- Misma configuración de corpus/retriever/LLM que la corrida anterior; variación solo en resultados estocásticos o artefactos.

## Comparativa vs E12 (`prompt_v2_cot`)

- Recall@k reglas: 0.76 → 0.76 (+0.00)
- Recall@k CALL: 0.20 → 0.20 (+0.00)
- F1 citas RRS: 0.00 → 0.11 (+0.11)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.01 → 0.01 (+0.00)
- Jaccard resp↔ref: 0.13 → 0.16 (+0.03)
- Dictamen auto: 0.00 → 0.60 (+0.60)
- Faithfulness: 0.57 → —
- Faithfulness estricta: 0.82 → —

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.11 (-0.11)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.01 (-0.02)
- Jaccard resp↔ref: 0.13 → 0.16 (+0.03)
- Dictamen auto: 0.00 → 0.60 (+0.60)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —
