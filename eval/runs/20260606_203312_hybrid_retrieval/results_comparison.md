# Comparación esperado vs corrida `hybrid_retrieval`

Run ID: `20260606_203312_hybrid_retrieval`  
Modelo: `llama3`  
Corpus: ``

## Agregados

| Métrica | Valor |
|---------|-------|
| mean_recall_at_k_rules | 0.60 |
| mean_recall_at_k_calls | 0.13 |
| mean_citation_f1_rrs | — |
| mean_citation_f1_calls | — |
| mean_token_jaccard_answer_context | — |
| mean_token_jaccard_answer_reference | — |
| verdict_accuracy | — |

## Por caso

| ID | Reglas esp. | Recall reglas | CALL esp. | Recall CALL | F1 RRS | F1 CALL | Jaccard ctx | Dictamen |
|----|-------------|---------------|-----------|-------------|--------|---------|-------------|----------|
| 1 | 16.1 | 1.00 | A3 | 1.00 | — | — | — | — |
| 2 | 11, 13 | 1.00 | B2 | 1.00 | — | — | — | — |
| 3 | 11, 15 | 0.50 | B1 | 0.00 | — | — | — | — |
| 4 | 18.2(a)(2), 12, 18.2(d) | 1.00 | E1 | 0.00 | — | — | — | — |
| 5 | 16.2 | 1.00 | D2 | 0.00 | — | — | — | — |
| 6 | 18.2(a), 18.2(d) | 1.00 | E2 | 0.00 | — | — | — | — |
| 7 | 21.2 | 0.00 | L2 | 0.00 | — | — | — | — |
| 8 | 18.2(a)(1), D1.1, 18.4 | 0.67 | J5 | 0.00 | — | — | — | — |
| 9 | 12, 13, 15 | 0.33 | E6 | 0.00 | — | — | — | — |
| 10 | 13 | 1.00 | D4 | 0.00 | — | — | — | — |
| 11 | 11, 18.2 | 0.50 | J9 | 0.00 | — | — | — | — |
| 12 | 10, D2.3(f) | 0.00 | L1 | 0.00 | — | — | — | — |
| 13 | 17 | 1.00 | G3 | 0.00 | — | — | — | — |
| 14 | D1.1(e) | 0.00 | K1 | 0.00 | — | — | — | — |
| 15 | 13, 15 | 0.00 | D3 | 0.00 | — | — | — | — |
