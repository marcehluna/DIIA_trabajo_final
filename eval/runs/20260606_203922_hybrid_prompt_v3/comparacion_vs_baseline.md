# Comparación — `hybrid_prompt_v3` (E17)

**Run ID:** `20260606_203922_hybrid_prompt_v3`

## Qué cambió respecto a la corrida anterior

- **modelo LLM:** `llama3` → `qwen2.5:14b-instruct`

## Comparativa vs E16 (`hybrid_retrieval`)

- Recall@k reglas: 0.76 → 0.76 (+0.00)
- Recall@k CALL: 0.20 → 0.20 (+0.00)
- F1 citas RRS: — → 0.13
- F1 citas CALL: — → 0.07
- Jaccard resp↔ctx: — → 0.01
- Jaccard resp↔ref: — → 0.16
- Dictamen auto: — → 0.47

## Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.13 (-0.09)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.01 (-0.02)
- Jaccard resp↔ref: 0.13 → 0.16 (+0.03)
- Dictamen auto: 0.00 → 0.47 (+0.47)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —
