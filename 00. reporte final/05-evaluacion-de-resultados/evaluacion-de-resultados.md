### 05. Evaluación de resultados

Documentación cuantitativa de la mejora obtenida mediante métricas sobre un **golden set fijo de 15 casos** (`eval/data/eval_set.json`), derivados del Case Book y validados manualmente.

**Perfil recomendado:** retrieval **E11** (léxico, cupos 2+3+2+1) + respuesta **E13** (prompt v3 español).

---

## Métricas de evaluación

Todas las métricas se calculan sobre el **golden set de 15 casos** (`eval/data/eval_set.json`), comparando lo que el sistema recupera y genera contra referencias extraídas del Excel *Casos de Regatas* (reglas RRS, TR CALL, casos, dictamen y output ideal). La implementación está en `regatas_assistant/eval/metrics.py` y `regatas_assistant/eval/refs.py`; las corridas las produce `scripts/eval_run.py`.

Las agrupamos en **cuatro familias** según qué capa del pipeline auditan: recuperación, respuesta, decisión y diagnóstico extendido.

### Recuperación (retrieval)

Estas métricas miden si el contexto que recibe el LLM contiene el material normativo esperado. Se pueden evaluar **sin llamar al modelo** (`--retrieval-only`), lo que permite iterar rápido sobre corpus, chunking y cupos.

| Métrica | Definición breve | Utilidad |
|---------|------------------|----------|
| **Recall@k reglas** | Fracción de números de regla RRS esperados que aparecen en al menos uno de los `k` chunks recuperados (por defecto `k=8`). | Indica si el índice y el retriever traen las normas del golden set al prompt. Fue la métrica clave para decidir ingesta JSONL y cupos (E10→E11). |
| **Recall@k CALL** | Igual para códigos TR CALL esperados (p. ej. B2, E1). | Mide cobertura del Call Book. Baja si el corpus no incluye calls o si los cupos priorizan otras fuentes. |
| **Recall@k CASE** | Igual para identificadores de caso del Case Book. | Complementa CALL cuando el golden set espera precedentes de caso; útil tras incorporar `cases.jsonl`. |

**Por qué importan:** si el recall es bajo, ningún prompt mejorará la respuesta: el modelo no ve la norma relevante. Separar retrieval de generación nos permitió aislar la mejora E0→E11 sin confundirla con cambios de prompt.

### Respuesta y citas

Requieren una corrida **completa** (retrieval + LLM). Evalúan si el informe cita correctamente lo recuperado y si se ancla al contexto.

| Métrica | Definición breve | Utilidad |
|---------|------------------|----------|
| **Precisión / recall / F1 citas RRS** | Conjunto de reglas citadas en la respuesta vs reglas esperadas; F1 balancea citas correctas y omisiones. | Mide trazabilidad normativa en el informe. Mejora con prompt v3 (formato de viñetas) y con parser ampliado en `refs.py`. |
| **Precisión / recall / F1 citas CALL** | Igual para TR CALL en la respuesta. | Detecta si el modelo enlaza el incidente con la señal o procedimiento del Call Book. |
| **F1 citas CASE** | Igual para casos del Case Book (cuando el golden set los declara). | Complemento menor en esta PoC; reservado para casos con precedente explícito. |
| **Jaccard respuesta↔contexto** | Solapamiento léxico (tokens ≥3 letras) entre la respuesta y el texto de los chunks recuperados. | Proxy de **faithfulness léxica**: respuesta anclada al contexto. Sensible al idioma (ES vs EN del corpus); subió fuerte en E14. |
| **Jaccard respuesta↔referencia** | Solapamiento léxico entre la respuesta y el *output ideal* del Excel. | Aproxima cercanía al informe humano de referencia; útil para comparar estilo y cobertura, no solo citas. |

**Por qué importan:** con recall alto (E11) el cuello de botella pasó a la **generación**. F1 y Jaccard permiten ver si el LLM *usa* el contexto recuperado y si el formato del prompt hace las citas auditables.

### Decisión (dictamen)

| Métrica | Definición breve | Utilidad |
|---------|------------------|----------|
| **Acierto dictamen** (`verdict_match`) | Coincidencia de la categoría de decisión normalizada (p. ej. penalizar, sin penalización, exonerar) entre la línea `Decisión:` del modelo y el golden set. | Métrica de **utilidad práctica** para la comisión: no basta citar reglas; hay que cerrar la protesta. Pasó de 0 % (E0–E11) a 60 % con prompt v3 (E13). |
| **Coincidencia barcos penalizados** | Igualdad del conjunto de embarcaciones penalizadas extraídas de la decisión. | Refinamiento del dictamen; se reporta cuando el golden set declara barcos concretos. |

**Por qué importan:** en regatas el entregable es una resolución accionable. El dictamen automático es una aproximación (el Excel y el parser no capturan toda la matices del lenguaje), pero sirve para comparar prompts y detectar regresiones.

### Diagnóstico extendido de retrieval

Métricas derivadas de `retrieval_hits.json` / `retrieval_hits_detail.csv` (script `aggregate_retrieval_hits.py`). Operan **ítem a ítem** (cada regla o CALL esperada por caso), no solo promedios.

| Métrica | Definición breve | Utilidad |
|---------|------------------|----------|
| **Tasa en contexto** (RRS / CALL) | % de referencias esperadas presentes en los chunks recuperados. | Equivalente granular al recall@k; desglosado por tipo y por caso. |
| **Tasa en respuesta** (cita) | % de referencias esperadas citadas en el informe del LLM. | Aísla la capa de generación respecto del contexto ya recuperado. |
| **Tasa pipeline** | % de referencias que están **tanto en contexto como citadas** en la respuesta. | Resume el flujo completo RAG: recuperar *y* reflejar en el informe. |
| **Matriz contexto→cita (A / B / C / D)** | Clasificación por ítem: **A** contexto sí + cita sí; **B** contexto sí + cita no; **C** contexto no + cita sí; **D** ninguno. | Diagnóstico fino: **B** sugiere mejorar prompt; **C** posible alucinación; **D** fallo de retrieval o de todo el pipeline. |
| **Rank del primer hit / MRR** | Posición del primer chunk que contiene la referencia; MRR promedia el recíproco del rank. | Indica si las normas relevantes quedan arriba en `top_k` o enterradas en posiciones bajas. |
| **Citas espurias** | Reglas o CALL mencionados en la respuesta pero no esperados en el golden set. | Control de precisión: evitar que el modelo “rellene” con normas irrelevantes. |

**Por qué importan:** los promedios de recall ocultan casos problemáticos (p. ej. regla 21.2 en caso 7). La matriz y el rank guiaron la lectura de dilución en E3 y la validación del híbrido en E16.

### Faithfulness (fidelidad al contexto)

Métrica **opcional** calculada con un LLM como juez (`regatas_assistant/eval/faithfulness.py`, script `score_faithfulness.py`):

| Métrica | Definición breve | Utilidad |
|---------|------------------|----------|
| **Faithfulness rate** | Fracción de afirmaciones atómicas extraídas de la respuesta marcadas como *supported* por los chunks recuperados (incluye *unknown* en el denominador). | Evalúa si cada frase del informe está respaldada por evidencia, más allá del solapamiento léxico. |
| **Faithfulness rate estricta** | Igual, pero solo cuenta *supported* vs *not_supported* (excluye *unknown*). | Versión más exigente; usada en el barrido E0 vs E12 (E12 ≈ 57 % / 82 % estricta). |

**Por qué importa:** el Jaccard puede ser bajo con buenas citas normativas (idiomas distintos, paráfrasis). Faithfulness complementa con verificación semántica por afirmación, aunque tiene costo de LLM adicional y cierta variabilidad del juez.

### Cómo leer las métricas en conjunto

```text
Retrieval (R@k)  →  ¿llegó la norma al prompt?
F1 / matriz B    →  ¿el LLM la citó si estaba en contexto?
Dictamen         →  ¿cerró la protesta como el golden set?
Jaccard / faithfulness  →  ¿el texto se sostiene en la evidencia recuperada?
```

En la práctica usamos **R@k reglas y CALL** para regresión de índice y cupos (umbrales E11), y **F1 RRS, F1 CALL y dictamen** para regresión de prompt (umbrales E13). Las métricas extendidas y faithfulness se reservan para análisis cualitativo y comparativas del informe.

---

## Resumen del trabajo con las corridas

Las evaluaciones se organizaron en **18 corridas numeradas (E0–E17, sin E5)**. En cada una se varió **una o pocas dimensiones** — corpus, cupos de retrieval, prompt o backend de embeddings — manteniendo el resto constante para aislar el efecto del cambio. El objetivo general fue pasar de una línea base con solo PDF (E0) a un perfil productivo que recupere bien las reglas RRS y cierre dictámenes auditables.

### Línea base y diagnóstico (E0–E2)

| ID | Qué buscábamos |
|----|----------------|
| **E0** | Fijar la **línea base oficial**: Call Book + Case Book en PDF, Qwen en español, sin RRS estructurado. Referencia histórica del proyecto (`v0.1.0-baseline`). |
| E1 | Validar que las **métricas de retrieval** son reproducibles **sin costo de LLM** (`--retrieval-only`). |
| E2 | Probar un índice con **RRS en PDF + Case** (sin Call Book) y medir el impacto en recall de CALL. |

### Ingesta y dilución del índice (E3–E4)

| ID | Qué buscábamos |
|----|----------------|
| E3 | Incorporar **RRS desde JSONL** al índice *full* (JSONL + PDF, ~1389 chunks) y ver si mejora el contexto normativo. |
| E4 | Aislar el índice **solo processed** (RRS + definiciones, sin PDF) para medir si alcanza sin Call/Case. |

### Índice mixto con cupos (E6–E7)

| ID | Qué buscábamos |
|----|----------------|
| E6 | Mitigar la **dilución** de E3 repartiendo `top_k=8` en cupos **4+4** (JSONL vs PDF). |
| E7 | Optimizar cupos en índice full: **3 slots JSONL + 5 PDF** para recuperar más CALL sin perder reglas. |

### Corpus JSONL puro (E8–E11)

| ID | Qué buscábamos |
|----|----------------|
| E8 | Construir índice **solo JSONL** con RRS + calls CSV (sin PDF). |
| E9 | Sumar **cases.jsonl** al processed (~707 chunks) y ver si mejora el conjunto. |
| E10 | Introducir **cupos por tipo de documento** (3+2+2+1) en JSONL puro y disparar recall de reglas. |
| **E11** | Ajustar cupos a **2+3+2+1** (más CALL) y fijar el **perfil de retrieval productivo**. |

### Calidad de respuesta y formato (E12–E14)

| ID | Qué buscábamos |
|----|----------------|
| E12 | Probar **prompt v2** con metadatos JSONL v2 en contexto; mismo motor RAG que E11. |
| **E13** | Validar **prompt v3** (plantilla fija, viñetas, línea `Decisión:`) como referencia de **respuesta en español**. |
| E14 | Mismo retrieval E11 pero **salida en inglés** (`--response-lang en`) para probar alineación léxica con corpus EN. |

### Retrieval híbrido (E15–E17)

| ID | Qué buscábamos |
|----|----------------|
| E15 | Prototipo **híbrido léxico+semántico** sin fallback cuando no hay overlap de tokens. |
| E16 | Híbrido con **fallback semántico** (relato ES / corpus EN); solo retrieval. |
| E17 | Híbrido + prompt v3 completo; decidir si reemplaza al léxico E11. **Resultado: no adoptar.** |

### Lectura integradora

El avance principal tiene **dos capas**. De E0 a E11 el salto es casi todo en **recuperación** (R@k reglas de 0.41 a 0.76). De E11 a E13 el índice no cambia; mejora la **respuesta medible** (dictamen automático al 60 %). E14 y E17 quedan documentados como experimentos que no sustituyen el perfil español E13.

---

## Evolución gráfica de las métricas

Gráficos de línea en draw.io (una pestaña por métrica): [`evolucion-metricas-corridas.drawio`](evolucion-metricas-corridas.drawio).

| Pestaña | Contenido |
|---------|-----------|
| Índice | Resumen del recorrido E0→E17 por familia de métrica |
| R@k reglas / R@k CALL | Evolución de recuperación; umbral E11 |
| F1 RRS / F1 CALL | Citas en respuesta; umbral E13 |
| Jaccard resp↔ctx / resp↔ref | Anclaje léxico al contexto y al Excel |
| Dictamen | Salto con prompt v3 (E12–E13); umbral 50 % |

En cada gráfico: línea de referencia E0 (cuando aplica), marcadores destacados en **E11** y **E13**, y `n/a` en corridas solo retrieval (E1, E2, E15, E16).

---

## Tabla de métricas por corrida

Golden set: **15 casos**. Retrieval léxico `top_k=8` salvo E15–E17 (híbrido). LLM: **Qwen 2.5 14B** en corridas completas; **llama3** en E1, E2, E15 y E16 (solo retrieval).

| ID | Etiqueta | Índice / corpus | Modo | R@k reglas | R@k CALL | F1 RRS | F1 CALL | Jaccard resp↔ctx | Jaccard resp↔ref | Dictamen | Rol |
|----|----------|-----------------|------|------------|----------|--------|---------|------------------|------------------|----------|-----|
| **E0** | `baseline_call_case_qwen_es` | Call+Case PDF (~894 ch.) | completo | 0.41 | 0.27 | 0.22 | 0.13 | 0.03 | 0.13 | 0 % | Línea base histórica |
| E1 | `baseline_retrieval` | Call+Case PDF | solo retrieval | 0.41 | 0.27 | — | — | — | — | — | Diagnóstico retrieval |
| E2 | `rrs_case_retrieval` | RRS PDF + Case | solo retrieval | 0.20 | 0.00 | — | — | — | — | — | Diagnóstico sin Call |
| E3 | `ingesta_rrs_jsonl` | JSONL + PDF full (~1389 ch.) | completo | 0.28 | 0.07 | 0.20 | 0.07 | 0.05 | 0.12 | 0 % | Dilución sin cupos |
| E4 | `rrs_only` | Solo RRS+def JSONL | completo | 0.13 | 0.00 | 0.06 | 0.00 | 0.02 | 0.13 | 0 % | Solo processed insuficiente |
| E6 | `full_cupos_4_4` | JSONL + PDF + cupos 4+4 | completo | 0.39 | 0.13 | 0.13 | 0.07 | 0.04 | 0.13 | 0 % | Mitiga dilución E3 |
| E7 | `full_cupos_3_5` | JSONL + PDF + cupos 3+5 | completo | 0.39 | 0.20 | 0.14 | 0.07 | 0.04 | 0.13 | 0 % | Mejor CALL en full |
| E8 | `rrs_calls_jsonl` | RRS + calls JSONL (~578 ch.) | completo | 0.20 | 0.13 | 0.14 | 0.13 | 0.04 | 0.12 | 0 % | JSONL sin cupos |
| E9 | `rrs_calls_cases_jsonl` | RRS + calls + cases JSONL (~707 ch.) | completo | 0.20 | 0.13 | 0.16 | 0.13 | 0.05 | 0.12 | 0 % | +cases sin mejora clara |
| E10 | `processed_cupos_3_2_2_1` | JSONL ~707 ch., cupos 3+2+2+1 | completo | 0.69 | 0.07 | 0.09 | 0.07 | 0.03 | 0.13 | 0 % | Salto en reglas, CALL bajo |
| **E11** | `processed_cupos_2_3_2_1` | JSONL ~707 ch., cupos 2+3+2+1 | completo | **0.76** | 0.20 | 0.25 | 0.07 | 0.02 | 0.12 | 0 % | **Retrieval productivo** |
| E12 | `prompt_v2_cot` | Índice E11 | completo | 0.76 | 0.20 | 0.20 | 0.13 | 0.01 | 0.13 | 60 % | Puente prompt v2 |
| **E13** | `prompt_v3_format` | Índice E11 | completo | **0.76** | 0.20 | 0.22 | 0.07 | 0.01 | 0.16 | **60 %** | **Producto actual (ES)** |
| E14 | `prompt_v3_en_out` | Índice E11 | completo | 0.76 | 0.20 | 0.32 | 0.07 | 0.16 | 0.02 | 40 % | Experimento salida EN |
| E15 | `hybrid_retrieval` | Índice E11 | solo retrieval | 0.60 | 0.13 | — | — | — | — | — | Híbrido sin fallback |
| E16 | `hybrid_retrieval` | Índice E11 | solo retrieval | 0.76 | 0.20 | — | — | — | — | — | Híbrido con fallback |
| E17 | `hybrid_prompt_v3` | Índice E11 | completo | 0.76 | 0.20 | 0.13 | 0.07 | 0.01 | 0.16 | 47 % | Híbrido + v3 (no adoptar) |

**Notas sobre la tabla**

- **R@k reglas / CALL:** fracción de referencias del golden set presentes en los 8 chunks recuperados (recall@k).
- **F1 RRS / CALL:** concordancia de citas en la respuesta del LLM vs golden set (parser de `refs.py`).
- **Jaccard resp↔ctx / resp↔ref:** solapamiento léxico respuesta–contexto recuperado y respuesta–output ideal del Excel.
- **Dictamen:** coincidencia gruesa de la decisión (protesta admitida / desestimada / etc.) con el golden set.
- Los valores provienen del [diario de pruebas](../../eval/DIARIO_PRUEBAS.md) (corridas E0–E17). En E12/E13 el F1 de la corrida original subestimaba citas por formato; con el parser ampliado, E11 ≈ 0.25, E13 ≈ 0.22.

**Umbrales de regresión** (perfil `production`, `regatas_assistant/profiles.py`): R@k reglas ≥ 0.70, R@k CALL ≥ 0.18, F1 RRS ≥ 0.18, F1 CALL ≥ 0.06, dictamen ≥ 50 %.

---
### Conclusiones sobre la evolución de métricas

La mejora del sistema no es un único salto, sino **dos capas encadenadas**. De **E0 a E11** el avance es casi todo en **recuperación**: R@k reglas pasa de 0.41 a **0.76** (+85 % relativo), lo que indica que el contexto que recibe el LLM suele incluir ya las normas RRS del golden set. En CALL el índice productivo queda en **0.20** frente a **0.27** del baseline PDF: se pierde un poco de recall de Call Book al pasar a JSONL+cupos, pero se gana un índice más compacto (~707 chunks) y mucho más fuerte en reglas, que es el cuello de botella en protestas. En **E11** el F1 de citas en respuesta (≈0.25 con parser actual) es del mismo orden que E0 (0.22): con mejor contexto, el modelo *podría* citar mejor, pero el **prompt heredado** no obligaba un formato parseable ni una línea `Decisión:` clara, y el **dictamen automático seguía en 0 %** — señal de que el problema ya no era “no encontrar la norma”, sino “no cerrar el dictamen de forma medible”.

**E14 (inglés):** con el mismo R@k, el F1 RRS sube ~**+0.10** respecto a E13 y el solapamiento respuesta↔contexto ~**15×** (de ~0.01 a ~0.16), coherente con redactar en el idioma del corpus. A cambio, el dictamen automático baja (40% vs 60%) y el Jaccard vs Output Ideal español cae: las métricas de “cita exacta” mejoran en parte porque el parser ahora reconoce `Rule`/`Decision`, pero el criterio de decisión del Excel sigue en español. **Conclusión E14:** útil para faithfulness/contexto; **no** sustituye E13 para el informe del curso.

De **E11 a E13** las métricas de retrieval **no se mueven** (mismo índice y cupos); el progreso es de **respuesta y trazabilidad**. El dictamen sube a **60 %** de coincidencia gruesa con el golden set, y el F1 RRS permanece estable (~0.22) una vez alineado el parser con las viñetas del prompt v3. E12 fue el puente (mismo R@k, dictamen ya mejora con v2; el F1=0 de la corrida fue un artefacto de evaluación, no de ausencia de citas). En conjunto, **E13 combina el techo de recuperación logrado en E11 con un formato de salida que las métricas y el informe pueden auditar**: R@k alto + F1 razonable + dictamen > 0. Lectura práctica: si en una corrida futura cae R@k, hay que mirar corpus, chunking o cupos; si R@k se mantiene y caen F1 o dictamen, hay que mirar prompt y postproceso, no el índice. Comparado con E0, el producto actual recupera **casi el doble de reglas esperadas** en top-8 y acierta el **dictamen automático en el 60 %** de los casos del golden set, a costa de un CALL ligeramente menor en recall — trade-off aceptado para la PoC con 15 casos.

En este punto del trabajo, **E11 + E13** es la mejor elección no porque sea perfecta en todas las métricas, sino porque es la única combinación que **cumple los umbrales de regresión en retrieval y respuesta** y alinea las tres dimensiones que el golden set exige: traer las normas al contexto (E11), cerrar un dictamen medible (E13) y hacerlo en **español**, coherente con el relato del usuario y el Excel de referencia. Alternativas descartadas quedan documentadas: el baseline E0 no recupera RRS; los índices *full* sin cupos diluyen reglas; E10 sacrifica CALL; E14 mejora citas léxicas pero pierde dictamen; E17 no supera a E13 en F1 ni decisión pese al híbrido. Además, el par E11+E13 está **fijado en código** (`REGATAS_PROFILE=production`, `profiles.py`) y respaldado por regresión automática — es el perfil reproducible que la PoC entrega hoy, con margen claro para mejoras futuras (más casos en el golden set, refinamiento de prompt) sin reabrir la búsqueda de índice ni de backend de retrieval.

## Comparativas detalladas

- **[Comparativa citas golden set vs E13](comparativa-citas-golden-set-vs-e13.md)** — tabla caso a caso (perfil productivo, español).
- **[Comparativa citas golden set vs E14](comparativa-citas-golden-set-vs-e14.md)** — mismo golden set con salida en inglés.
- **[E13 vs E14 (salida inglés)](comparativa-e13-vs-e14-salida-ingles.md)** — métricas agregadas del experimento `--response-lang en`.
- **[E13 vs E17 (retrieval híbrido)](comparativa-e13-vs-e17-retrieval-hibrido.md)** — experimento `embedding_backend=hybrid`; **no** adoptado (perfil sigue E13).
- Resumen narrativo y timeline: [`eval/RESUMEN_CORRIDAS_EVAL.md`](../../eval/RESUMEN_CORRIDAS_EVAL.md).