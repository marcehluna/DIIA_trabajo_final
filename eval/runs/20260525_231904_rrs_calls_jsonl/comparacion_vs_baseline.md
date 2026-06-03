# Comparación — `rrs_calls_jsonl` (E8)

**Run ID:** `20260525_231904_rrs_calls_jsonl`

## Qué cambió respecto a la corrida anterior

- **Fuentes corpus:** `full` → `processed`
- **PDFs:** `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']` → `[]`
- **cupos retrieval:** `True` → `False`
- **cupo RRS:** `3` → `None`
- **cupo PDF:** `5` → `None`

## Comparativa vs E7 (`full_cupos_3_5`)

- Recall@k reglas: 0.39 → 0.20 (-0.19)
- Recall@k CALL: 0.20 → 0.13 (-0.07)
- F1 citas RRS: 0.14 → 0.14 (+0.01)
- F1 citas CALL: 0.07 → 0.13 (+0.07)
- Jaccard resp↔ctx: 0.04 → 0.04 (+0.01)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.20 (-0.21)
- Recall@k CALL: 0.27 → 0.13 (-0.13)
- F1 citas RRS: 0.22 → 0.14 (-0.08)
- F1 citas CALL: 0.13 → 0.13 (+0.00)
- Jaccard resp↔ctx: 0.03 → 0.04 (+0.01)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
