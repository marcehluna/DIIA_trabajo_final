# Comparación — `processed_cupos_2_3_2_1` (E11)

**Run ID:** `20260526_185624_processed_cupos_2_3_2_1`

## Qué cambió respecto a la corrida anterior

- **Índice:** mismo `processed` (JSONL ~707 ch., sin PDF en retrieval)
- **cupo rrs:** `3` → `2`
- **cupo call:** `2` → `3`

## Comparativa vs E10 (`processed_cupos_3_2_2_1`)

- Recall@k reglas: 0.69 → 0.76 (+0.07)
- Recall@k CALL: 0.07 → 0.20 (+0.13)
- F1 citas RRS: 0.09 → 0.22 (+0.13)
- F1 citas CALL: 0.07 → 0.07 (+0.00)
- Jaccard resp↔ctx: 0.03 → 0.02 (-0.00)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.00 → —

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.22 (-0.01)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.02 (-0.00)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.00 → —
