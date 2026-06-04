# Comparativa E0 vs E12 — material citabile para el informe final

Documento de **referencia consolidada** (junio 2026) con métricas, interpretación y rutas a artefactos. Complementa [`REGISTRO_TRABAJO_INFORME_FINAL.md`](REGISTRO_TRABAJO_INFORME_FINAL.md) y el diario [`eval/DIARIO_PRUEBAS.md`](../eval/DIARIO_PRUEBAS.md).

**Golden set:** 15 casos, `eval/data/eval_set.json` (relato = columna Input de `docs/Casos de Regatas.xlsx`).

---

## 1. Definición de las corridas comparadas

| ID | `run_id` / carpeta | Configuración resumida |
|----|-------------------|------------------------|
| **E0** | `eval/corrida baseline/` (`20260525_185138_baseline_call_case_qwen_es`) | Solo PDF Call Book + Case Book; sin RRS JSONL; sin cupos por `doc_type`; Qwen ES, CoT |
| **E12** | `eval/runs/20260603_183901_prompt_v2_cot/` | Índice `processed` JSONL v2 (~707 ch.) + cupos **2+3+2+1** (perfil E11); **prompts v2** + metadatos en encabezados; Qwen ES, CoT |

**Nota:** E12 comparte **retrieval/índice con E11**; el salto respecto a E0 viene sobre todo del corpus JSONL + cupos. El cambio de **prompt v2** en E12 afecta métricas de **citas** (formato de salida), no el recall@k (igual que E11: R@k reglas 0.76, CALL 0.20).

---

## 2. Métricas agregadas (15 casos)

Fuente: `report.json` → `aggregate` en cada carpeta de corrida.

| Métrica | E0 | E12 | Δ (E12 − E0) | Lectura breve |
|---------|-----|-----|--------------|---------------|
| **Recall@k reglas RRS** | 0.411 | **0.756** | +0.345 | E12 recupera mucho mejor las reglas esperadas |
| **Recall@k CALL** | **0.267** | 0.200 | −0.067 | E0 sigue mejor en Call Book (PDF) |
| **F1 citas RRS** (respuesta) | **0.222** | 0.000* | −0.222 | *Artefacto: prompt v2 no usa formato que parsea `refs.py` |
| **F1 citas CALL** | 0.133 | 0.133 | 0.000 | Empate |
| **Jaccard resp ↔ contexto** | 0.029 | 0.009 | −0.020 | **No** implica peor calidad (véase §4) |
| **Jaccard resp ↔ Output Ideal** | 0.131 | 0.134 | +0.003 | Casi igual (~13% léxico compartido) |
| **Acierto dictamen** (automático) | 0.000 | 0.000 | 0.000 | Matcher insuficiente en ambas |
| **Faithfulness** (media) | 0.367 | **0.566** | +0.199 | E12: más afirmaciones soportadas por el contexto |
| **Faithfulness estricta** | 0.722 | **0.825** | +0.103 | Entre supported/not_supported, E12 gana |

---

## 3. Faithfulness (barrido completo, jun 2026)

**Método:** LLM juez en dos pasos (extraer afirmaciones → verificar vs chunks recuperados). Parser robusto (lotes de 6, fallback claim-a-claim). Modelo juez: `qwen2.5:14b-instruct` (Ollama).

| Alcance | E0 media | E12 media | E12 > E0 (por caso) |
|---------|----------|-----------|---------------------|
| 15 casos (barrido completo) | **37%** | **57%** | **9 / 15** |
| Piloto casos 1–2 (referencia) | ~59% (44% + 73%) / 2 | ~49% (14% + 83%) / 2 | Mixto; muestra no representativa |

**Conclusión faithfulness:** Con los 15 casos, E12 muestra respuestas **más ancladas al contexto recuperado** que E0, aunque el solapamiento léxico (Jaccard) sea menor.

**Artefactos:**

| Archivo | Contenido |
|---------|-----------|
| `eval/faithfulness_e0_e12_comparison.csv` | 15 filas, columnas `E0_*` / `E12_*` |
| `eval/faithfulness_all_runs_by_case.csv` | 30 filas (ambas corridas) |
| `eval/corrida baseline/faithfulness_by_case.csv` | Detalle E0 |
| `eval/runs/20260603_183901_prompt_v2_cot/faithfulness_by_case.csv` | Detalle E12 |
| `*/faithfulness_claims_detail.csv` | Cada afirmación + veredicto |

**Regenerar:** `python scripts/run_faithfulness_barrido.py` (~98 min, 15+15 casos).

---

## 4. Token overlap (Jaccard léxico)

**Definición** (`regatas_assistant/eval/metrics.py`): tokens = palabras ≥3 letras; Jaccard = |A∩B| / |A∪B|.

| Comparación | E0 (media) | E12 (media) | ¿Bajar es mejor? |
|-------------|------------|-------------|------------------|
| Respuesta ↔ **contexto recuperado** | 0.029 | 0.009 | **No.** Bajo en E12 refleja ES respuesta / EN contexto y otro estilo, no peor RAG |
| Respuesta ↔ **Output Ideal** (golden) | 0.131 | 0.134 | **Subir** sería más parecido al ideal; ambas ~13% |

**Por caso (contexto):** E12 > E0 solo en **2/15** casos (6 y 11). Caídas fuertes en 5, 9, 10 (Δ ≈ −0.06 a −0.07).

**Por caso (referencia):** E12 > E0 en **7/15** casos; media casi plana.

**Dónde leer:** `metrics_long.csv` (`token_jaccard_answer_*`), `results_comparison_por_caso.csv`, gráficos `plots/05_jaccard_respuesta_contexto.png`, `06_jaccard_respuesta_referencia.png`.

---

## 5. ¿El modelo da mejores respuestas en E12 que en E0?

### Sí, con matices (texto sugerido para el informe)

**E12 es preferible** si el criterio es:

- Recuperar **reglas RRS** en el contexto (R@k 0.76 vs 0.41).
- Respuestas **más fundamentadas** en el material recuperado (faithfulness 57% vs 37%).
- Desplegar el **stack productivo** (JSONL, metadatos, cupos E11).

**No se puede afirmar “mejores respuestas en todo”** porque:

- **CALL** se recupera peor (0.20 vs 0.27).
- **F1 citas RRS** en E12 = 0 por **formato de salida** (prompt v2), no necesariamente por ausencia de razonamiento.
- **Dictamen automático** = 0% en ambas; validación humana pendiente.
- **Similitud al Output Ideal** (~13% Jaccard) no mejora de forma relevante.

**Frase de cierre recomendada:**

> E12 mejora el subsistema de recuperación normativa (RRS) y la fidelidad de las respuestas al contexto entregado al LLM; la calidad del dictamen final y la citación evaluable requieren alinear el prompt con el formato del golden set y revisión manual de casos representativos.

---

## 6. E12 vs E11 (evitar confusión en citas)

| Aspecto | E11 | E12 |
|---------|-----|-----|
| Índice / cupos | processed 2+3+2+1 | Igual |
| R@k reglas / CALL | 0.76 / 0.20 | Igual (misma corrida de retrieval) |
| Prompt | CoT “clásico” | **Prompts v2** + metadatos JSONL |
| F1 citas RRS | ~0.22 | 0.00 (parser) |
| Faithfulness | No medido en corrida original | 57% (barrido posterior) |

Carpeta E11: `eval/runs/20260526_185624_processed_cupos_2_3_2_1/`.

---

## 7. Limitaciones metodológicas (para capítulo de discusión)

1. **Golden set:** 15 casos; parser heurístico de etiquetas desde Excel.
2. **F1 citas:** sensible al formato de la respuesta (`extract_rrs_rules` en `refs.py`).
3. **Dictamen:** `verdict_accuracy` busca patrones en texto; no refleja calidad umpire real.
4. **Jaccard:** métrica léxica; penaliza ES/EN sin reflejar equivalencia semántica.
5. **Faithfulness:** costoso (LLM juez); depende del modelo y del parseo JSON (mitigado jun 2026).
6. **E12:** mezcla cambio de **pipeline** (E11) y cambio de **prompt**; desagregar en futura corrida `prompt_v2` sobre E11 sin cambiar índice.

---

## 8. Comandos y scripts útiles

```bash
# Comparar dos report.json (incluye jaccard y recall)
python scripts/compare_eval_runs.py eval/corrida\ baseline/report.json \
  eval/runs/20260603_183901_prompt_v2_cot/report.json

# Tabla por caso (jaccard, citas, recall)
python scripts/build_eval_results_table.py eval/runs/20260603_183901_prompt_v2_cot

# Faithfulness + CSV
python scripts/run_faithfulness_barrido.py
python scripts/run_faithfulness_barrido.py --skip-score   # solo exportar CSV
```

---

## 9. Referencias cruzadas

| Tema | Documento |
|------|-----------|
| Registro maestro del proyecto | `docs/REGISTRO_TRABAJO_INFORME_FINAL.md` |
| Perfil productivo E11 | `docs/PERFIL_PRODUCTIVO.md` |
| Diario corridas E0–E12 | `eval/DIARIO_PRUEBAS.md` |
| Timeline visual | `eval/docs/timeline_corridas_eval.html` |
| Metodología eval | `eval/README.md` |

*Última actualización: 2026-06-04.*
