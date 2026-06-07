# Resumen de corridas de evaluación (E0–E17)

Golden set fijo: **15 casos** (`eval/data/eval_set.json`). Por defecto: Qwen2.5 ES, retrieval léxico `top_k=8`, modo completo (retrieval + LLM).

**Referencias de producción:** retrieval = **E11** · respuesta (prompt v3) = **E13**. Tabla automática: [`DIARIO_PRUEBAS.md`](DIARIO_PRUEBAS.md). Timeline: [`docs/timeline_corridas_eval.html`](docs/timeline_corridas_eval.html).

**Nota F1 RRS:** En E12/E13 el F1 de la corrida original subestimaba citas por formato; con el parser ampliado (`refs.py`) y `rescore_eval_citations.py`, E12 ≈ **0.20**, E13 ≈ **0.22**, E11 ≈ **0.25**.

---

## Línea temporal y objetivo de cada cambio

| ID | Etiqueta | Objetivo del cambio | Qué cambió vs la corrida anterior |
|----|----------|---------------------|-----------------------------------|
| **E0** | `baseline_call_case_qwen_es` | **Línea base oficial** del proyecto (tag `v0.1.0-baseline`). | Call Book + Case Book en PDF; Qwen ES; sin RRS en índice; sin cupos. |
| E1 | `baseline_retrieval` | Validar **métricas de retrieval** sin costo de LLM. | Mismo índice E0; `--retrieval-only`; modelo llama3 (solo diagnóstico). |
| E2 | `rrs_case_retrieval` | Probar índice con **RRS PDF + Case** (sin Call). | Sustituye PDFs; sigue solo retrieval; CALL cae a 0. |
| E3 | `ingesta_rrs_jsonl` | Incorporar **RRS desde JSONL** al índice *full* (JSONL + PDF). | ~1389 chunks; sin cupos; **dilución**: R@k reglas baja vs E0. |
| E4 | `rrs_only` | Aislar calidad del índice **solo processed** (RRS+def). | Sin PDF Call/Case; peor que mezcla full. |
| E6 | `full_cupos_4_4` | Mitigar dilución E3 con **cupos 4+4** en índice full. | Vuelve JSONL+PDF; reglas casi recuperan nivel E0. |
| E7 | `full_cupos_3_5` | Optimizar cupos en full: **más slots PDF** para CALL. | Cupos 3 JSONL + 5 PDF; mejor R@k CALL que E6. |
| E8 | `rrs_calls_jsonl` | Índice **solo JSONL** (RRS + calls CSV), sin PDF. | ~578 ch.; F1 CALL razonable; reglas bajas. |
| E9 | `rrs_calls_cases_jsonl` | Sumar **cases.jsonl** al processed. | ~707 ch.; sin mejora clara vs E8. |
| E10 | `processed_cupos_3_2_2_1` | Cupos por **doc_type** en JSONL puro. | 3+2+2+1; gran salto R@k reglas; CALL bajo. |
| **E11** | `processed_cupos_2_3_2_1` | **Perfil retrieval productivo**: más cupo CALL. | Mismo índice ~707 ch.; **R@k reglas 0.76**, CALL 0.20. |
| E12 | `prompt_v2_cot` | Probar **prompt v2** + metadatos JSONL v2 en contexto. | Mismo índice/cupos E11; citas y `Decisión:` en prompt; R@k = E11. |
| **E13** | `prompt_v3_format` | **Prompt v3** (plantilla fija, §4 Resolución, viñetas). | Mismo retrieval E11; **dictamen auto 60%**; F1 RRS ~0.22 (parser). |
| E14 | `prompt_v3_en_out` | **Prompt v3 con salida en inglés** (`--response-lang en`). | Mismo índice E11; hipótesis alineación corpus EN; F1 RRS **0.32**; dictamen 40%. |
| E15 | `hybrid_retrieval` | Prototipo híbrido (sin fallback semántico). | Solo retrieval; R@k reglas **0.60** — descartado. |
| E16 | `hybrid_retrieval` | Híbrido retrieval-only (fallback semántico ES→EN). | R@k reglas **0.76** (= E11); caso 7 recupera 21.2. |
| E17 | `hybrid_prompt_v3` | Híbrido + prompt v3 completo (vs E13). | R@k = E13; **F1 0.13**, dictamen **47%** — **no** productivo. |

*(No hay E5: numeración salta de E4 a E6 en el diario.)*

---

## Lectura por bloques

### Baseline y diagnóstico (E0–E2)

- **E0** fija el comparador histórico: buen CALL en PDF, reglas RRS débiles (no están en el índice).
- **E1/E2** confirman que las métricas de retrieval son reproducibles sin generación; E2 muestra que quitar Call del corpus destruye R@k CALL.

### Ingesta y dilución (E3–E4)

- **E3** demuestra que mezclar JSONL+PDF sin cupos **empeora** reglas respecto a E0.
- **E4** confirma que solo RRS no alcanza para CALL ni para un producto completo.

### Índice full con cupos (E6–E7)

- **E6–E7** exploran recuperar nivel baseline en índice mixto; E7 mejora CALL pero el índice sigue pesado (~1389 ch.) y reglas no superan JSONL+cupos finales.

### Solo JSONL processed (E8–E11)

- **E8–E9** validan el corpus processed mínimo; **E10** introduce cupos por tipo y dispara recall de reglas.
- **E11** ajusta cupos a **2+3+2+1** y equilibra CALL; es la configuración de `REGATAS_PROFILE=production` hoy.

### Prompting (E12–E13)

- **E12**: mismo motor RAG que E11; cambia instrucciones y formato de salida (v2). Retrieval idéntico; mejora faithfulness vs E0 en barrido; F1 RRS en corrida = 0 fue **artefacto de parser**, no de citas ausentes.
- **E13**: plantilla v3 alineada a métricas y JSONL; **dictamen automático** pasa a 60%; citas medibles con parser v3. Es la referencia de **calidad de respuesta** en regresión (español).

### Salida en inglés (E14)

- **E14**: mismo retrieval; informe en inglés (`Rule …`, `Decision:`). **F1 RRS +0.10 vs E13** y **Jaccard contexto +0.15**; **dictamen baja a 40%** y Jaccard vs Excel cae. Mejor trazabilidad léxica al corpus, peor alineación al golden en español. **No** reemplaza E13 como perfil productivo.

### Retrieval híbrido (E15–E17)

- **E16** (retrieval-only): con fallback semántico cuando no hay overlap léxico (relato ES / corpus EN), **iguala E11** en R@k medio y **arregla caso 7** (21.2 en top-8).
- **E17** (híbrido + prompt v3): mismo R@k agregado que E13, pero **F1 RRS −0.09** y **dictamen 47%** (−13 pp). Mejor contexto en casos aislados no se traduce en mejores citas ni decisiones.
- **Decisión:** mantener **E11 léxico + E13**; híbrido documentado como experimento, no configuración por defecto.

---

## Métricas clave (referencia rápida)

| ID | R@k reglas | R@k CALL | F1 RRS* | Dictamen | Rol |
|----|------------|----------|---------|----------|-----|
| E0 | 0.41 | 0.27 | 0.22 | 0% | Baseline histórico |
| E11 | 0.76 | 0.20 | 0.25 | 0% | Retrieval productivo |
| E12 | 0.76 | 0.20 | 0.20 | 60% | Prompt v2 (intermedio) |
| E13 | 0.76 | 0.20 | 0.22 | 60% | **Producto actual (prompt v3 ES)** |
| E14 | 0.76 | 0.20 | 0.32 | 40% | Prompt v3 salida EN (experimento) |
| E16 | 0.76 | 0.20 | — | — | Híbrido solo retrieval |
| E17 | 0.76 | 0.20 | 0.13 | 47% | Híbrido + v3 (experimento; no adoptar) |

\*F1 RRS con parser actual (`rescore_eval_citations.py` si el `report.json` es anterior al parser).

### Conclusiones sobre la evolución de métricas

La mejora del sistema no es un único salto, sino **dos capas encadenadas**. De **E0 a E11** el avance es casi todo en **recuperación**: R@k reglas pasa de 0.41 a **0.76** (+85 % relativo), lo que indica que el contexto que recibe el LLM suele incluir ya las normas RRS del golden set. En CALL el índice productivo queda en **0.20** frente a **0.27** del baseline PDF: se pierde un poco de recall de Call Book al pasar a JSONL+cupos, pero se gana un índice más compacto (~707 chunks) y mucho más fuerte en reglas, que es el cuello de botella en protestas. En **E11** el F1 de citas en respuesta (≈0.25 con parser actual) es del mismo orden que E0 (0.22): con mejor contexto, el modelo *podría* citar mejor, pero el **prompt heredado** no obligaba un formato parseable ni una línea `Decisión:` clara, y el **dictamen automático seguía en 0 %** — señal de que el problema ya no era “no encontrar la norma”, sino “no cerrar el dictamen de forma medible”.

**E14 (inglés):** con el mismo R@k, el F1 RRS sube ~**+0.10** respecto a E13 y el solapamiento respuesta↔contexto ~**15×** (de ~0.01 a ~0.16), coherente con redactar en el idioma del corpus. A cambio, el dictamen automático baja (40% vs 60%) y el Jaccard vs Output Ideal español cae: las métricas de “cita exacta” mejoran en parte porque el parser ahora reconoce `Rule`/`Decision`, pero el criterio de decisión del Excel sigue en español. **Conclusión E14:** útil para faithfulness/contexto; **no** sustituye E13 para el informe del curso.

De **E11 a E13** las métricas de retrieval **no se mueven** (mismo índice y cupos); el progreso es de **respuesta y trazabilidad**. El dictamen sube a **60 %** de coincidencia gruesa con el golden set, y el F1 RRS permanece estable (~0.22) una vez alineado el parser con las viñetas del prompt v3. E12 fue el puente (mismo R@k, dictamen ya mejora con v2; el F1=0 de la corrida fue un artefacto de evaluación, no de ausencia de citas). En conjunto, **E13 combina el techo de recuperación logrado en E11 con un formato de salida que las métricas y el informe pueden auditar**: R@k alto + F1 razonable + dictamen > 0. Lectura práctica: si en una corrida futura cae R@k, hay que mirar corpus, chunking o cupos; si R@k se mantiene y caen F1 o dictamen, hay que mirar prompt y postproceso, no el índice. Comparado con E0, el producto actual recupera **casi el doble de reglas esperadas** en top-8 y acierta el **dictamen automático en el 60 %** de los casos del golden set, a costa de un CALL ligeramente menor en recall — trade-off aceptado para la PoC con 15 casos.

---

## Regresión tras cambios de código

```bash
python scripts/eval_run.py --label mi_cambio --lang es
python scripts/rescore_eval_citations.py eval/runs/<run_id>   # si comparás F1 de citas
python scripts/regression_eval.py eval/runs/<run_id>            # producción completa (E13+)
python scripts/regression_eval.py eval/runs/<run_id> --mode retrieval   # solo índice/cupos (E11)
```

La corrida **E11** no cumple umbrales de *respuesta* (prompt sin v3 → dictamen 0%); usar `--mode retrieval` al validar solo cambios de índice.

Umbrales en `regatas_assistant/profiles.py`:

| Grupo | Métrica | Piso | Referencia |
|-------|---------|------|------------|
| Retrieval | R@k reglas | ≥ 0.70 | E11 |
| Retrieval | R@k CALL | ≥ 0.18 | E11 |
| Respuesta | F1 RRS | ≥ 0.18 | E13 |
| Respuesta | F1 CALL | ≥ 0.06 | E13 |
| Respuesta | Dictamen | ≥ 0.50 | E13 |

Ver también [`docs/PERFIL_PRODUCTIVO.md`](../docs/PERFIL_PRODUCTIVO.md).
