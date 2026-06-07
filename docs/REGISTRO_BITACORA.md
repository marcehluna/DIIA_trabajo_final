# Bitácora rápida (append-only)

Entradas cortas para el informe final. **Registro maestro (contexto completo):** [`REGISTRO_TRABAJO_INFORME_FINAL.md`](REGISTRO_TRABAJO_INFORME_FINAL.md).

Agregar cada ítem **arriba** de la línea `<!-- NUEVAS ENTRADAS ARRIBA -->`.

---

<!-- NUEVAS ENTRADAS ARRIBA -->

| Fecha | Tipo | Resumen |
|-------|------|---------|
| 2026-06-06 | eval | **E17** híbrido+v3 — F1 0.13, dictamen 47%; **decisión: perfil E11+E13** (léxico) |
| 2026-06-06 | código | Retrieval híbrido: índice semántico compartido, fallback semántico sin overlap ES→EN |
| 2026-06-06 | eval | E15–E16 híbrido retrieval-only; E16 R@k 0.76, caso 7 recupera 21.2 |
| 2026-06-06 | eval | **E14** `prompt_v3_en_out` — salida EN; F1 RRS 0.32 (+0.10 vs E13), Jaccard ctx 0.16, dictamen 40% |
| 2026-06-06 | docs | Timeline E14 + tabla caso a caso E14 en informe final; `REGATAS_RESPONSE_LANG` en `.env.example` |
| 2026-06-06 | código | `REGATAS_RESPONSE_LANG` / `--response-lang en`; prompts EN_OUT; parser Rule/Decision |
| 2026-06-04 | docs | `eval/RESUMEN_CORRIDAS_EVAL.md` + regresión E11/E13 (R@k, F1, dictamen) en `profiles.py` |
| 2026-06-04 | docs | Timeline eval actualizado: E12–E13 en `timeline_corridas_eval.drawio` + HTML |
| 2026-06-04 | código | Parser citas v3 (`refs.py`): `**Regla …**`, viñetas, `**Case N**`; `rescore_eval_citations.py` — E13 F1 RRS 0.11→0.22, E11 0.22→0.25 (sin re-LLM) |
| 2026-06-04 | eval | **E13** `prompt_v3_format` — dictamen 60%, F1 RRS 0.11; R@k = E11; vs E12 F1 RRS 0→0.11 |
| 2026-06-04 | código | Prompt **v3**: plantilla fija en user template, §4 «Resolución», citas por viñeta; métricas `Decisión:` |
| 2026-06-04 | docs | `INFORME_CITAS_E0_vs_E12.md` — comparativa citabile E0/E12 (métricas, Jaccard, conclusiones) |
| 2026-06-04 | eval | Barrido faithfulness 15 casos: E0 media 37%, E12 57% (`faithfulness_e0_e12_comparison.csv`) |
| 2026-06-04 | código | CSV faithfulness (`faithfulness_by_case.csv`, comparación E0/E12) + `run_faithfulness_barrido.py` |
| 2026-06-04 | eval | Piloto faithfulness E0/E12 casos 1–2: E0 ~44%/73%; E12 ~14%/83% (por caso) |
| 2026-06-03 | código | Faithfulness: parser robusto, lotes chicos, fallback verify-one |
| 2026-06-03 | eval | **E12** `prompt_v2_cot`: R@k = E11; F1 RRS 0 (formato respuesta ≠ parser); F1 CALL 0.13 |
| 2026-05-26 | código | Metadatos RAG v2: CSV→JSONL (`referenced_rules`, `section`, páginas) + encabezados prompt |
| 2026-05-26 | código | Prompts v2: contexto JSONL, citas Regla/TR CALL/Case, línea `Decisión:` |
| 2026-05-26 | docs | Creado `REGISTRO_TRABAJO_INFORME_FINAL.md` + esta bitácora |
| 2026-05-26 | producto | Perfil `production` (E11), híbrido RRF, `regression_eval.py`, `ensure_corpus_processed.py` |
| 2026-05-26 | eval | **E11** cupos 2+3+2+1 — R@k reglas 0.76, CALL 0.20 |
| 2026-05-26 | eval | **E10** cupos 3+2+2+1 — R@k reglas 0.69, CALL 0.07 |
| 2026-05-26 | docs | Timeline HTML/Draw.io E0–E11 |
| 2026-05-25 | eval | E3–E9 ingesta/cupos/JSONL (ver diario) |
| 2026-05-25 | eval | **E0** baseline PDF + E1/E2 retrieval |
| 2026-05-25 | eval | Faithfulness E0/E10 — pausado (parseo juez) |

**Tipos:** `eval` · `código` · `docs` · `producto` · `decisión` · `pendiente`
