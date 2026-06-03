# Comparación — `full_cupos_4_4` (E5)

**Run ID:** `20260525_223713_full_cupos_4_4`

## Qué cambió respecto a la corrida anterior

- **Fuentes corpus:** `processed` → `full`
- **PDFs:** `[]` → `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']`
- **cupos retrieval:** `None` → `True`
- **cupo RRS:** `None` → `4`
- **cupo PDF:** `None` → `4`

## Comparativa vs E4 (`rrs_only`)

- Recall@k reglas: 0.13 → 0.39 (+0.26)
- Recall@k CALL: 0.00 → 0.13 (+0.13)
- F1 citas RRS: 0.06 → 0.13 (+0.07)
- F1 citas CALL: 0.00 → 0.07 (+0.07)
- Jaccard resp↔ctx: 0.02 → 0.04 (+0.02)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.39 (-0.02)
- Recall@k CALL: 0.27 → 0.13 (-0.13)
- F1 citas RRS: 0.22 → 0.13 (-0.10)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.04 (+0.01)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)
