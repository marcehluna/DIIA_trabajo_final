# Comparación — `rrs_calls_cases_jsonl` (E9)

**Run ID:** `20260525_234431_rrs_calls_cases_jsonl`

## Qué cambió respecto a la corrida anterior

- Misma configuración de corpus/retriever/LLM que la corrida anterior; variación solo en resultados estocásticos o artefactos.

## Comparativa vs E8 (`rrs_calls_jsonl`)

- Recall@k reglas: 0.20 → 0.20 (+0.00)
- Recall@k CALL: 0.13 → 0.13 (+0.00)
- F1 citas RRS: 0.14 → 0.16 (+0.02)
- F1 citas CALL: 0.13 → 0.13 (+0.00)
- Jaccard resp↔ctx: 0.04 → 0.05 (+0.01)
- Jaccard resp↔ref: 0.12 → 0.12 (+0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.20 (-0.21)
- Recall@k CALL: 0.27 → 0.13 (-0.13)
- F1 citas RRS: 0.22 → 0.16 (-0.06)
- F1 citas CALL: 0.13 → 0.13 (+0.00)
- Jaccard resp↔ctx: 0.03 → 0.05 (+0.02)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
