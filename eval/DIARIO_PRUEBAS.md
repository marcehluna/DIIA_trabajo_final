# Diario de pruebas — evaluación RAG (asistente de protestas)

Documento **generado automáticamente** al finalizar cada `eval_run.py`. No editar a mano las secciones §1–§4; usar `eval/diario_runs.json` (`nota_usuario`) o `--diario-nota` si hace falta aclarar algo.

**Última regeneración:** 2026-06-06 17:57 (local)

**Golden set fijo (15 casos):** `docs/Casos de Regatas.xlsx` → `eval/data/eval_set.json`.

**Línea base oficial:** **E0** — `eval/corrida baseline/`, tag git `v0.1.0-baseline`.

---

## 1. Tabla maestra de corridas

| ID | Fecha (UTC) | Etiqueta | Run ID | Índice RAG | LLM | Modo | R@k reglas | R@k CALL | F1 RRS | F1 CALL | Carpeta |
|----|-------------|----------|--------|------------|-----|------|------------|----------|--------|---------|---------|
| **E0** | 2026-05-25 | `baseline_call_case_qwen_es` | `20260525_185138_base…` | Call+Case PDF (~894 ch.) | qwen2.5:14b-instruct | completo | 0.41 | 0.27 | 0.22 | 0.13 | [`eval/corrida baseline`](eval/corrida%20baseline/) |
| E1 | 2026-05-25 | `baseline_retrieval` | `20260525_184355_base…` | Call+Case PDF (~894 ch.) | llama3 | solo retrieval | 0.41 | 0.27 | — | — | [`eval/runs/20260525_184355_baseline_retrieval/`](runs/20260525_184355_baseline_retrieval/) |
| E2 | 2026-05-25 | `rrs_case_retrieval` | `20260525_184445_rrs_…` | Call+Case PDF (~894 ch.) | llama3 | solo retrieval | 0.20 | 0.00 | — | — | [`eval/runs/20260525_184445_rrs_case_retrieval/`](runs/20260525_184445_rrs_case_retrieval/) |
| E3 | 2026-05-25 | `ingesta_rrs_jsonl` | `20260525_214113_inge…` | RRS JSONL+def (~495 ch.) + Call+Case PDF (~894 ch.) ≈1389 ch. | qwen2.5:14b-instruct | completo | 0.28 | 0.07 | 0.20 | 0.07 | [`eval/runs/20260525_214113_ingesta_rrs_jsonl/`](runs/20260525_214113_ingesta_rrs_jsonl/) |
| E4 | 2026-05-25 | `rrs_only` | `20260525_220816_rrs_…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.13 | 0.00 | 0.06 | 0.00 | [`eval/runs/20260525_220816_rrs_only/`](runs/20260525_220816_rrs_only/) |
| E6 | 2026-05-25 | `full_cupos_4_4` | `20260525_223713_full…` | RRS JSONL+def (~495 ch.) + Call+Case PDF (~894 ch.) ≈1389 ch. | qwen2.5:14b-instruct | completo | 0.39 | 0.13 | 0.13 | 0.07 | [`eval/runs/20260525_223713_full_cupos_4_4/`](runs/20260525_223713_full_cupos_4_4/) |
| E7 | 2026-05-25 | `full_cupos_3_5` | `20260525_225609_full…` | RRS JSONL+def (~495 ch.) + Call+Case PDF (~894 ch.) ≈1389 ch. | qwen2.5:14b-instruct | completo | 0.39 | 0.20 | 0.14 | 0.07 | [`eval/runs/20260525_225609_full_cupos_3_5/`](runs/20260525_225609_full_cupos_3_5/) |
| E8 | 2026-05-25 | `rrs_calls_jsonl` | `20260525_231904_rrs_…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.20 | 0.13 | 0.14 | 0.13 | [`eval/runs/20260525_231904_rrs_calls_jsonl/`](runs/20260525_231904_rrs_calls_jsonl/) |
| E9 | 2026-05-25 | `rrs_calls_cases_jsonl` | `20260525_234431_rrs_…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.20 | 0.13 | 0.16 | 0.13 | [`eval/runs/20260525_234431_rrs_calls_cases_jsonl/`](runs/20260525_234431_rrs_calls_cases_jsonl/) |
| E10 | 2026-05-26 | `processed_cupos_3_2_2_1` | `20260526_000249_proc…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.69 | 0.07 | 0.09 | 0.07 | [`eval/runs/20260526_000249_processed_cupos_3_2_2_1/`](runs/20260526_000249_processed_cupos_3_2_2_1/) |
| E11 | 2026-05-26 | `processed_cupos_2_3_2_1` | `20260526_185624_proc…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.76 | 0.20 | 0.25 | 0.07 | [`eval/runs/20260526_185624_processed_cupos_2_3_2_1/`](runs/20260526_185624_processed_cupos_2_3_2_1/) |
| E12 | 2026-06-03 | `prompt_v2_cot` | `20260603_183901_prom…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.76 | 0.20 | 0.20 | 0.13 | [`eval/runs/20260603_183901_prompt_v2_cot/`](runs/20260603_183901_prompt_v2_cot/) |
| E13 | 2026-06-04 | `prompt_v3_format` | `20260604_124747_prom…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.76 | 0.20 | 0.22 | 0.07 | [`eval/runs/20260604_124747_prompt_v3_format/`](runs/20260604_124747_prompt_v3_format/) |
| E14 | 2026-06-06 | `prompt_v3_en_out` | `20260606_200214_prom…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.76 | 0.20 | 0.32 | 0.07 | [`eval/runs/20260606_200214_prompt_v3_en_out/`](runs/20260606_200214_prompt_v3_en_out/) |
| E15 | 2026-06-06 | `hybrid_retrieval` | `20260606_203312_hybr…` | RRS JSONL+def (~495 ch.), solo processed | llama3 | solo retrieval | 0.60 | 0.13 | — | — | [`eval/runs/20260606_203312_hybrid_retrieval/`](runs/20260606_203312_hybrid_retrieval/) |
| E16 | 2026-06-06 | `hybrid_retrieval` | `20260606_203610_hybr…` | RRS JSONL+def (~495 ch.), solo processed | llama3 | solo retrieval | 0.76 | 0.20 | — | — | [`eval/runs/20260606_203610_hybrid_retrieval/`](runs/20260606_203610_hybrid_retrieval/) |
| E17 | 2026-06-06 | `hybrid_prompt_v3` | `20260606_203922_hybr…` | RRS JSONL+def (~495 ch.), solo processed | qwen2.5:14b-instruct | completo | 0.76 | 0.20 | 0.13 | 0.07 | [`eval/runs/20260606_203922_hybrid_prompt_v3/`](runs/20260606_203922_hybrid_prompt_v3/) |

---

## 2. Métricas de retrieval (golden set)

| ID | RRS contexto | RRS pipeline | CALL contexto | CALL pipeline | Hits `rrs\|` | A | B | C | D |
|----|--------------|--------------|---------------|---------------|-------------|---|---|---|---|
| E0 | 40.7 % | 14.8 % | 26.7 % | 13.3 % | 0 | 6 | 9 | 2 | 25 |
| E1 | — | — | — | — | — | 0 | 0 | 0 | 0 |
| E2 | — | — | — | — | — | 0 | 0 | 0 | 0 |
| E3 | 29.6 % | 11.1 % | 6.7 % | 6.7 % | 4 | 4 | 5 | 1 | 32 |
| E4 | 14.8 % | 0.0 % | 0.0 % | 0.0 % | 4 | 0 | 4 | 2 | 36 |
| E6 | 37.0 % | 7.4 % | 13.3 % | 6.7 % | 2 | 3 | 9 | 1 | 29 |
| E7 | 37.0 % | 7.4 % | 20.0 % | 6.7 % | 2 | 3 | 10 | 1 | 28 |
| E8 | 22.2 % | 7.4 % | 13.3 % | 13.3 % | 4 | 4 | 4 | 1 | 33 |
| E9 | 22.2 % | 11.1 % | 13.3 % | 13.3 % | 4 | 5 | 3 | 1 | 33 |
| E10 | 74.1 % | 11.1 % | 6.7 % | 6.7 % | 2 | 4 | 17 | 0 | 21 |
| E11 | 77.8 % | 18.5 % | 20.0 % | 6.7 % | 1 | 6 | 18 | 0 | 18 |
| E12 | 77.8 % | 0.0 % | 20.0 % | 13.3 % | 1 | 2 | 22 | 0 | 18 |
| E13 | 77.8 % | 7.4 % | 20.0 % | 6.7 % | 1 | 3 | 21 | 0 | 18 |
| E14 | 77.8 % | 29.6 % | 20.0 % | 6.7 % | 1 | 9 | 15 | 0 | 18 |
| E15 | 59.3 % | 0.0 % | 13.3 % | 0.0 % | 2 | 0 | 18 | 0 | 24 |
| E16 | 74.1 % | 0.0 % | 20.0 % | 0.0 % | 2 | 0 | 23 | 0 | 19 |
| E17 | 74.1 % | 11.1 % | 20.0 % | 6.7 % | 2 | 4 | 19 | 0 | 19 |

---

## 3. Detalle por corrida (auto + comparativas)

### E0 — `baseline_call_case_qwen_es`

**Run ID:** `20260525_185138_baseline_call_case_qwen_es`  
**Carpeta:** `eval/corrida baseline`  

#### Qué cambió respecto a la corrida anterior

- **PDFs:** `['2025-2028-RRS-with-Changes-and-Corrections.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']` → `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']`
- **modelo LLM:** `llama3` → `qwen2.5:14b-instruct`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.20 → 0.41 (+0.21)
- Recall@k CALL: 0.00 → 0.27 (+0.27)
- F1 citas RRS: — → 0.22
- F1 citas CALL: — → 0.13
- Jaccard resp↔ctx: — → 0.03
- Jaccard resp↔ref: — → 0.13
- Dictamen auto: — → 0.00
- Faithfulness: — → 0.37
- Faithfulness estricta: — → 0.72

#### Configuración

- Índice: Call+Case PDF (~894 ch.)
- `corpus_sources`: `pdf`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Recuperación RRS en contexto aceptable para esta configuración.


---

### E1 — `baseline_retrieval`

**Run ID:** `20260525_184355_baseline_retrieval`  
**Carpeta:** `eval/runs/20260525_184355_baseline_retrieval`  

#### Qué cambió respecto a la corrida anterior

- Primera corrida registrada en el diario (sin anterior).

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.41 (+0.00)
- Recall@k CALL: 0.27 → 0.27 (+0.00)
- F1 citas RRS: 0.22 → —
- F1 citas CALL: 0.13 → —
- Jaccard resp↔ctx: 0.03 → —
- Jaccard resp↔ref: 0.13 → —
- Dictamen auto: 0.00 → —
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: Call+Case PDF (~894 ch.)
- `corpus_sources`: `pdf`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Solo retrieval: validación de métricas sin generación LLM.


---

### E2 — `rrs_case_retrieval`

**Run ID:** `20260525_184445_rrs_case_retrieval`  
**Carpeta:** `eval/runs/20260525_184445_rrs_case_retrieval`  

#### Qué cambió respecto a la corrida anterior

- **PDFs:** `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']` → `['2025-2028-RRS-with-Changes-and-Corrections.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.41 → 0.20 (-0.21)
- Recall@k CALL: 0.27 → 0.00 (-0.27)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.20 (-0.21)
- Recall@k CALL: 0.27 → 0.00 (-0.27)
- F1 citas RRS: 0.22 → —
- F1 citas CALL: 0.13 → —
- Jaccard resp↔ctx: 0.03 → —
- Jaccard resp↔ref: 0.13 → —
- Dictamen auto: 0.00 → —
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: Call+Case PDF (~894 ch.)
- `corpus_sources`: `pdf`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Solo retrieval: validación de métricas sin generación LLM.


---

### E3 — `ingesta_rrs_jsonl`

**Run ID:** `20260525_214113_ingesta_rrs_jsonl`  
**Carpeta:** `eval/runs/20260525_214113_ingesta_rrs_jsonl`  

#### Qué cambió respecto a la corrida anterior

- **Fuentes corpus:** `pdf` → `full`
- **JSONL processed:** `None` → `True`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.41 → 0.28 (-0.13)
- Recall@k CALL: 0.27 → 0.07 (-0.20)
- F1 citas RRS: 0.22 → 0.20 (-0.02)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.05 (+0.02)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.28 (-0.13)
- Recall@k CALL: 0.27 → 0.07 (-0.20)
- F1 citas RRS: 0.22 → 0.20 (-0.02)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.05 (+0.02)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.) + Call+Case PDF (~894 ch.) ≈1389 ch.
- `corpus_sources`: `full`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Recall de reglas por debajo del baseline; revisar ranking o cupos por fuente.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E4 — `rrs_only`

**Run ID:** `20260525_220816_rrs_only`  
**Carpeta:** `eval/runs/20260525_220816_rrs_only`  

#### Qué cambió respecto a la corrida anterior

- **Fuentes corpus:** `full` → `processed`
- **PDFs:** `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']` → `[]`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.28 → 0.13 (-0.14)
- Recall@k CALL: 0.07 → 0.00 (-0.07)
- F1 citas RRS: 0.20 → 0.06 (-0.14)
- F1 citas CALL: 0.07 → 0.00 (-0.07)
- Jaccard resp↔ctx: 0.05 → 0.02 (-0.02)
- Jaccard resp↔ref: 0.12 → 0.13 (+0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.13 (-0.28)
- Recall@k CALL: 0.27 → 0.00 (-0.27)
- F1 citas RRS: 0.22 → 0.06 (-0.16)
- F1 citas CALL: 0.13 → 0.00 (-0.13)
- Jaccard resp↔ctx: 0.03 → 0.02 (-0.00)
- Jaccard resp↔ref: 0.13 → 0.13 (+0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Recall de reglas por debajo del baseline; revisar ranking o cupos por fuente.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E6 — `full_cupos_4_4`

**Run ID:** `20260525_223713_full_cupos_4_4`  
**Carpeta:** `eval/runs/20260525_223713_full_cupos_4_4`  

#### Qué cambió respecto a la corrida anterior

- **Fuentes corpus:** `processed` → `full`
- **PDFs:** `[]` → `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']`
- **cupos retrieval:** `None` → `True`
- **cupo processed:** `None` → `4`
- **cupo PDF:** `None` → `4`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.13 → 0.39 (+0.26)
- Recall@k CALL: 0.00 → 0.13 (+0.13)
- F1 citas RRS: 0.06 → 0.13 (+0.07)
- F1 citas CALL: 0.00 → 0.07 (+0.07)
- Jaccard resp↔ctx: 0.02 → 0.04 (+0.02)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.39 (-0.02)
- Recall@k CALL: 0.27 → 0.13 (-0.13)
- F1 citas RRS: 0.22 → 0.13 (-0.10)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.04 (+0.01)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.) + Call+Case PDF (~894 ch.) ≈1389 ch.
- `corpus_sources`: `full`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Recuperación RRS en contexto aceptable para esta configuración.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E7 — `full_cupos_3_5`

**Run ID:** `20260525_225609_full_cupos_3_5`  
**Carpeta:** `eval/runs/20260525_225609_full_cupos_3_5`  

#### Qué cambió respecto a la corrida anterior

- **cupo processed:** `4` → `3`
- **cupo PDF:** `4` → `5`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.39 → 0.39 (+0.00)
- Recall@k CALL: 0.13 → 0.20 (+0.07)
- F1 citas RRS: 0.13 → 0.14 (+0.01)
- F1 citas CALL: 0.07 → 0.07 (+0.00)
- Jaccard resp↔ctx: 0.04 → 0.04 (-0.01)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.39 (-0.02)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.14 (-0.08)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.04 (+0.01)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.) + Call+Case PDF (~894 ch.) ≈1389 ch.
- `corpus_sources`: `full`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Recuperación RRS en contexto aceptable para esta configuración.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E8 — `rrs_calls_jsonl`

**Run ID:** `20260525_231904_rrs_calls_jsonl`  
**Carpeta:** `eval/runs/20260525_231904_rrs_calls_jsonl`  

#### Qué cambió respecto a la corrida anterior

- **Fuentes corpus:** `full` → `processed`
- **PDFs:** `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']` → `[]`
- **cupos retrieval:** `True` → `False`
- **cupo processed:** `3` → `None`
- **cupo PDF:** `5` → `None`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.39 → 0.20 (-0.19)
- Recall@k CALL: 0.20 → 0.13 (-0.07)
- F1 citas RRS: 0.14 → 0.14 (+0.01)
- F1 citas CALL: 0.07 → 0.13 (+0.07)
- Jaccard resp↔ctx: 0.04 → 0.04 (+0.01)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.20 (-0.21)
- Recall@k CALL: 0.27 → 0.13 (-0.13)
- F1 citas RRS: 0.22 → 0.14 (-0.08)
- F1 citas CALL: 0.13 → 0.13 (+0.00)
- Jaccard resp↔ctx: 0.03 → 0.04 (+0.01)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Recall de reglas por debajo del baseline; revisar ranking o cupos por fuente.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E9 — `rrs_calls_cases_jsonl`

**Run ID:** `20260525_234431_rrs_calls_cases_jsonl`  
**Carpeta:** `eval/runs/20260525_234431_rrs_calls_cases_jsonl`  

#### Qué cambió respecto a la corrida anterior

- Misma configuración de corpus/retriever/LLM que la corrida anterior; variación solo en resultados estocásticos o artefactos.

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.20 → 0.20 (+0.00)
- Recall@k CALL: 0.13 → 0.13 (+0.00)
- F1 citas RRS: 0.14 → 0.16 (+0.02)
- F1 citas CALL: 0.13 → 0.13 (+0.00)
- Jaccard resp↔ctx: 0.04 → 0.05 (+0.01)
- Jaccard resp↔ref: 0.12 → 0.12 (+0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.20 (-0.21)
- Recall@k CALL: 0.27 → 0.13 (-0.13)
- F1 citas RRS: 0.22 → 0.16 (-0.06)
- F1 citas CALL: 0.13 → 0.13 (+0.00)
- Jaccard resp↔ctx: 0.03 → 0.05 (+0.02)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Recall de reglas por debajo del baseline; revisar ranking o cupos por fuente.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E10 — `processed_cupos_3_2_2_1`

**Run ID:** `20260526_000249_processed_cupos_3_2_2_1`  
**Carpeta:** `eval/runs/20260526_000249_processed_cupos_3_2_2_1`  

#### Qué cambió respecto a la corrida anterior

- **cupos retrieval:** `False` → `True`
- **cupos por tipo:** `None` → `True`
- **cupo rrs:** `None` → `3`
- **cupo call:** `None` → `2`
- **cupo case:** `None` → `2`
- **cupo def:** `None` → `1`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.20 → 0.69 (+0.49)
- Recall@k CALL: 0.13 → 0.07 (-0.07)
- F1 citas RRS: 0.16 → 0.09 (-0.07)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.05 → 0.03 (-0.02)
- Jaccard resp↔ref: 0.12 → 0.13 (+0.00)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: — → 0.00

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.69 (+0.28)
- Recall@k CALL: 0.27 → 0.07 (-0.20)
- F1 citas RRS: 0.22 → 0.09 (-0.14)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.03 (-0.00)
- Jaccard resp↔ref: 0.13 → 0.13 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → 0.00 (-0.37)
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Mejora de recall de reglas respecto al baseline.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E11 — `processed_cupos_2_3_2_1`

**Run ID:** `20260526_185624_processed_cupos_2_3_2_1`  
**Carpeta:** `eval/runs/20260526_185624_processed_cupos_2_3_2_1`  

#### Qué cambió respecto a la corrida anterior

- **PDFs:** `[]` → `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']`
- **cupo rrs:** `3` → `2`
- **cupo call:** `2` → `3`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.69 → 0.76 (+0.07)
- Recall@k CALL: 0.07 → 0.20 (+0.13)
- F1 citas RRS: 0.09 → 0.25 (+0.17)
- F1 citas CALL: 0.07 → 0.07 (+0.00)
- Jaccard resp↔ctx: 0.03 → 0.02 (-0.00)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.00 → —

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.25 (+0.03)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.02 (-0.00)
- Jaccard resp↔ref: 0.13 → 0.12 (-0.01)
- Dictamen auto: 0.00 → 0.00 (+0.00)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Mejora de recall de reglas respecto al baseline.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E12 — `prompt_v2_cot`

**Run ID:** `20260603_183901_prompt_v2_cot`  
**Carpeta:** `eval/runs/20260603_183901_prompt_v2_cot`  

#### Qué cambió respecto a la corrida anterior

- **PDFs:** `['The-Call-Book-for-Team-Racing-2025-2028.pdf', 'WS-Case-Book-2025-2028-v2025-07.pdf']` → `[]`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.76 → 0.76 (+0.00)
- Recall@k CALL: 0.20 → 0.20 (+0.00)
- F1 citas RRS: 0.25 → 0.20 (-0.05)
- F1 citas CALL: 0.07 → 0.13 (+0.07)
- Jaccard resp↔ctx: 0.02 → 0.01 (-0.02)
- Jaccard resp↔ref: 0.12 → 0.13 (+0.02)
- Dictamen auto: 0.00 → 0.60 (+0.60)
- Faithfulness: — → 0.57
- Faithfulness estricta: — → 0.82

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.20 (-0.02)
- F1 citas CALL: 0.13 → 0.13 (+0.00)
- Jaccard resp↔ctx: 0.03 → 0.01 (-0.02)
- Jaccard resp↔ref: 0.13 → 0.13 (+0.00)
- Dictamen auto: 0.00 → 0.60 (+0.60)
- Faithfulness: 0.37 → 0.57 (+0.20)
- Faithfulness estricta: 0.72 → 0.82 (+0.10)

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Mejora de recall de reglas respecto al baseline.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E13 — `prompt_v3_format`

**Run ID:** `20260604_124747_prompt_v3_format`  
**Carpeta:** `eval/runs/20260604_124747_prompt_v3_format`  

#### Qué cambió respecto a la corrida anterior

- Misma configuración de corpus/retriever/LLM que la corrida anterior; variación solo en resultados estocásticos o artefactos.

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.76 → 0.76 (+0.00)
- Recall@k CALL: 0.20 → 0.20 (+0.00)
- F1 citas RRS: 0.20 → 0.22 (+0.02)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.01 → 0.01 (+0.00)
- Jaccard resp↔ref: 0.13 → 0.16 (+0.03)
- Dictamen auto: 0.60 → 0.60 (+0.00)
- Faithfulness: 0.57 → —
- Faithfulness estricta: 0.82 → —

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.22 (-0.00)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.01 (-0.02)
- Jaccard resp↔ref: 0.13 → 0.16 (+0.03)
- Dictamen auto: 0.00 → 0.60 (+0.60)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Mejora de recall de reglas respecto al baseline.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E14 — `prompt_v3_en_out`

**Run ID:** `20260606_200214_prompt_v3_en_out`  
**Carpeta:** `eval/runs/20260606_200214_prompt_v3_en_out`  

#### Qué cambió respecto a la corrida anterior

- **idioma respuesta:** `None` → `en`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.76 → 0.76 (+0.00)
- Recall@k CALL: 0.20 → 0.20 (+0.00)
- F1 citas RRS: 0.22 → 0.32 (+0.10)
- F1 citas CALL: 0.07 → 0.07 (+0.00)
- Jaccard resp↔ctx: 0.01 → 0.16 (+0.14)
- Jaccard resp↔ref: 0.16 → 0.02 (-0.15)
- Dictamen auto: 0.60 → 0.40 (-0.20)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.32 (+0.09)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.16 (+0.13)
- Jaccard resp↔ref: 0.13 → 0.02 (-0.12)
- Dictamen auto: 0.00 → 0.40 (+0.40)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `lexical`, top_k=8
- Hallazgo (auto): Mejora de recall de reglas respecto al baseline.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E15 — `hybrid_retrieval`

**Run ID:** `20260606_203312_hybrid_retrieval`  
**Carpeta:** `eval/runs/20260606_203312_hybrid_retrieval`  

#### Qué cambió respecto a la corrida anterior

- **embedding:** `lexical` → `hybrid`
- **modelo LLM:** `qwen2.5:14b-instruct` → `llama3`
- **idioma respuesta:** `en` → `es`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.76 → 0.60 (-0.16)
- Recall@k CALL: 0.20 → 0.13 (-0.07)
- F1 citas RRS: 0.32 → —
- F1 citas CALL: 0.07 → —
- Jaccard resp↔ctx: 0.16 → —
- Jaccard resp↔ref: 0.02 → —
- Dictamen auto: 0.40 → —

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.60 (+0.19)
- Recall@k CALL: 0.27 → 0.13 (-0.13)
- F1 citas RRS: 0.22 → —
- F1 citas CALL: 0.13 → —
- Jaccard resp↔ctx: 0.03 → —
- Jaccard resp↔ref: 0.13 → —
- Dictamen auto: 0.00 → —
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `hybrid`, top_k=8
- Hallazgo (auto): Solo retrieval: validación de métricas sin generación LLM.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E16 — `hybrid_retrieval`

**Run ID:** `20260606_203610_hybrid_retrieval`  
**Carpeta:** `eval/runs/20260606_203610_hybrid_retrieval`  

#### Qué cambió respecto a la corrida anterior

- Misma configuración de corpus/retriever/LLM que la corrida anterior; variación solo en resultados estocásticos o artefactos.

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.60 → 0.76 (+0.16)
- Recall@k CALL: 0.13 → 0.20 (+0.07)

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → —
- F1 citas CALL: 0.13 → —
- Jaccard resp↔ctx: 0.03 → —
- Jaccard resp↔ref: 0.13 → —
- Dictamen auto: 0.00 → —
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `hybrid`, top_k=8
- Hallazgo (auto): Solo retrieval: validación de métricas sin generación LLM.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

### E17 — `hybrid_prompt_v3`

**Run ID:** `20260606_203922_hybrid_prompt_v3`  
**Carpeta:** `eval/runs/20260606_203922_hybrid_prompt_v3`  
**Nota:** E17: retrieval híbrido + prompt v3 (E13); vs E11 léxico  

#### Qué cambió respecto a la corrida anterior

- **modelo LLM:** `llama3` → `qwen2.5:14b-instruct`

#### Comparativa vs corrida anterior

- Recall@k reglas: 0.76 → 0.76 (+0.00)
- Recall@k CALL: 0.20 → 0.20 (+0.00)
- F1 citas RRS: — → 0.13
- F1 citas CALL: — → 0.07
- Jaccard resp↔ctx: — → 0.01
- Jaccard resp↔ref: — → 0.16
- Dictamen auto: — → 0.47

#### Comparativa vs E0 (baseline)

- Recall@k reglas: 0.41 → 0.76 (+0.34)
- Recall@k CALL: 0.27 → 0.20 (-0.07)
- F1 citas RRS: 0.22 → 0.13 (-0.09)
- F1 citas CALL: 0.13 → 0.07 (-0.07)
- Jaccard resp↔ctx: 0.03 → 0.01 (-0.02)
- Jaccard resp↔ref: 0.13 → 0.16 (+0.03)
- Dictamen auto: 0.00 → 0.47 (+0.47)
- Faithfulness: 0.37 → —
- Faithfulness estricta: 0.72 → —

#### Configuración

- Índice: RRS JSONL+def (~495 ch.), solo processed
- `corpus_sources`: `processed`
- Retrieval: `hybrid`, top_k=8
- Hallazgo (auto): Mejora de recall de reglas respecto al baseline.

- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`

---

## 4. Comparación rápida vs E0 (solo corridas con LLM)

| ID | Δ recall reglas | Δ recall CALL | Δ F1 RRS | Δ F1 CALL |
|----|-----------------|---------------|----------|-----------|
| E3 | -0.13 | -0.20 | -0.02 | -0.07 |
| E4 | -0.28 | -0.27 | -0.16 | -0.13 |
| E6 | -0.02 | -0.13 | -0.10 | -0.07 |
| E7 | -0.02 | -0.07 | -0.08 | -0.07 |
| E8 | -0.21 | -0.13 | -0.08 | +0.00 |
| E9 | -0.21 | -0.13 | -0.06 | +0.00 |
| E10 | +0.28 | -0.20 | -0.14 | -0.07 |
| E11 | +0.34 | -0.07 | +0.03 | -0.07 |
| E12 | +0.34 | -0.07 | -0.02 | +0.00 |
| E13 | +0.34 | -0.07 | -0.00 | -0.07 |
| E14 | +0.34 | -0.07 | +0.09 | -0.07 |
| E17 | +0.34 | -0.07 | -0.09 | -0.07 |

## 5. Registro automático

Tras cada corrida, `eval_run.py` ejecuta:

1. `export_retrieval_hits_csv.py` (si hay `retrieval_hits.json`)
2. `aggregate_retrieval_hits.py` con `--compare` al baseline
3. `compare_eval_runs.py` vs `eval/corrida baseline`
4. Regeneración de este archivo

Comando manual:

```bash
python scripts/update_diario_pruebas.py eval/runs/<run_id>
# o solo regenerar todo:
python scripts/update_diario_pruebas.py --all
```

Nota opcional en la corrida:

```bash
python scripts/eval_run.py --label mi_prueba --diario-nota "Probamos top_k=16" ...
```

## 6. Scripts relacionados

| Script | Uso |
|--------|-----|
| `scripts/eval_run.py` | Corrida + actualiza diario |
| `scripts/update_diario_pruebas.py` | Solo regenerar diario |
| `scripts/compare_eval_runs.py` | Δ entre dos report.json |
| `scripts/aggregate_retrieval_hits.py` | Gráficos retrieval |

---

*Fin del diario autogenerado.*
