# Comparación — `processed_cupos_3_2_2_1` (E10)

**Run ID:** `20260526_000249_processed_cupos_3_2_2_1`

## Qué cambió respecto a la corrida anterior

- **cupos retrieval:** `False` → `True`
- **cupos por tipo:** `None` → `True`
- **cupo rrs:** `None` → `3`
- **cupo call:** `None` → `2`
- **cupo case:** `None` → `2`
- **cupo def:** `None` → `1`

## Comparativa vs E9 (`rrs_calls_cases_jsonl`)

- Recall@k reglas: 0.20 → 0.69 (+0.49)
- Recall@k CALL: 0.13 → 0.07 (-0.07)
- F1 citas RRS: 0.16 → 0.09 (-0.07)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.05 → 0.03 (-0.02)
- Jaccard resp↔ref: 0.12 → 0.13 (+0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.69 (+0.28)
- Recall@k CALL: 0.27 → 0.07 (-0.20)
- F1 citas RRS: 0.22 → 0.09 (-0.14)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.03 (-0.00)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
