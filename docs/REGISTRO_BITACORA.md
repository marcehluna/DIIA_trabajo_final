# Bitácora rápida (append-only)

Entradas cortas para el informe final. **Registro maestro (contexto completo):** [`REGISTRO_TRABAJO_INFORME_FINAL.md`](REGISTRO_TRABAJO_INFORME_FINAL.md).

Agregar cada ítem **arriba** de la línea `<!-- NUEVAS ENTRADAS ARRIBA -->`.

---

<!-- NUEVAS ENTRADAS ARRIBA -->

| Fecha | Tipo | Resumen |
|-------|------|---------|
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
