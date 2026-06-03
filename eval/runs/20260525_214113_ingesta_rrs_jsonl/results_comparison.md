# Comparación esperado vs corrida `ingesta_rrs_jsonl`

Run ID: `20260525_214113_ingesta_rrs_jsonl`  
Modelo: `qwen2.5:14b-instruct`  
Corpus: `The-Call-Book-for-Team-Racing-2025-2028.pdf, WS-Case-Book-2025-2028-v2025-07.pdf`

## Agregados

| Métrica | Valor |
|---------|-------|
| mean_recall_at_k_rules | 0.28 |
| mean_recall_at_k_calls | 0.07 |
| mean_citation_f1_rrs | 0.20 |
| mean_citation_f1_calls | 0.07 |
| mean_token_jaccard_answer_context | 0.05 |
| mean_token_jaccard_answer_reference | 0.12 |
| verdict_accuracy | 0.00 |

## Por caso

| ID | Reglas esp. | Recall reglas | CALL esp. | Recall CALL | F1 RRS | F1 CALL | Jaccard ctx | Dictamen |
|----|-------------|---------------|-----------|-------------|--------|---------|-------------|----------|
| 1 | 16.1 | 0.00 | A3 | 0.00 | 0.00 | 0.00 | 0.00 | ✗ |
| 2 | 11, 13 | 0.50 | B2 | 0.00 | 0.00 | 0.00 | 0.01 | ✗ |
| 3 | 11, 15 | 0.00 | B1 | 0.00 | 0.00 | 0.00 | 0.09 | ✗ |
| 4 | 18.2(a)(2), 12, 18.2(d) | 1.00 | E1 | 0.00 | 0.00 | 0.00 | 0.19 | ✗ |
| 5 | 16.2 | 1.00 | D2 | 1.00 | 1.00 | 1.00 | 0.02 | ✗ |
| 6 | 18.2(a), 18.2(d) | 0.00 | E2 | 0.00 | 0.00 | 0.00 | 0.02 | ✗ |
| 7 | 21.2 | 0.00 | L2 | 0.00 | 0.00 | 0.00 | 0.08 | ✗ |
| 8 | 18.2(a)(1), D1.1, 18.4 | 0.00 | J5 | 0.00 | 0.00 | 0.00 | 0.05 | ✗ |
| 9 | 12, 13, 15 | 0.67 | E6 | 0.00 | 0.50 | 0.00 | 0.09 | ✗ |
| 10 | 13 | 1.00 | D4 | 0.00 | 0.50 | 0.00 | 0.09 | ✗ |
| 11 | 11, 18.2 | 0.00 | J9 | 0.00 | 0.00 | 0.00 | 0.01 | ✗ |
| 12 | 10, D2.3(f) | 0.00 | L1 | 0.00 | 0.00 | 0.00 | 0.00 | ✗ |
| 13 | 17 | 0.00 | G3 | 0.00 | 1.00 | 0.00 | 0.01 | ✗ |
| 14 | D1.1(e) | 0.00 | K1 | 0.00 | 0.00 | 0.00 | 0.01 | ✗ |
| 15 | 13, 15 | 0.00 | D3 | 0.00 | 0.00 | 0.00 | 0.05 | ✗ |
