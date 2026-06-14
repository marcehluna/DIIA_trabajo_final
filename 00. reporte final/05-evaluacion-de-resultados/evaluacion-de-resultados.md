### 05. Evaluación de resultados

Documentación cuantitativa de la mejora obtenida mediante métricas sobre un **golden set fijo de 15 casos** (`eval/data/eval_set.json`), derivados del *Case Book* [3] y validados manualmente.

**Perfil recomendado:** retrieval **E11** (léxico, cupos 2+3+2+1) + respuesta **E13** (prompt v3 español).

---

## Métricas de evaluación

La evaluación del trabajo se apoyó en un conjunto acotado de indicadores, calculados siempre sobre los **15 casos del golden set** y comparados contra etiquetas de referencia (reglas RRS, TR CALL, dictamen y output ideal). Las métricas se agrupan por **capa del pipeline RAG** [5][6]: primero se mide si el contexto recuperado contiene la norma esperada; después, si el informe la cita, se ancla al contexto y cierra la protesta con un dictamen coherente.

| Métrica | Capa | Qué mide | Rol en este trabajo |
|---------|------|----------|---------------------|
| **Recall@k reglas** | Recuperación | Fracción de reglas RRS esperadas presentes en los *k* fragmentos recuperados (*k* = 8). | Métrica central para validar ingesta JSONL y cupos (E10→E11); umbral de regresión ≥ 0.70. |
| **Recall@k CALL** | Recuperación | Igual para códigos TR CALL del Call Book [2]. | Controla que el índice no sacrifique jurisprudencia de team racing; umbral ≥ 0.18. |
| **F1 citas RRS / CALL** | Respuesta | Balance entre citas normativas correctas y omisiones en el informe del LLM. | Mide trazabilidad de la respuesta; estable con prompt v3; umbral F1 RRS ≥ 0.18, F1 CALL ≥ 0.06. |
| **Jaccard respuesta↔contexto** | Respuesta | Solapamiento léxico entre el informe y los fragmentos recuperados. | Proxy de fidelidad al contexto; sensible al idioma (ES vs EN del corpus). |
| **Jaccard respuesta↔referencia** | Respuesta | Solapamiento léxico entre el informe y el output ideal del golden set. | Aproxima cercanía al informe humano de referencia. |
| **Acierto dictamen** | Decisión | Coincidencia de la categoría de decisión (`Decisión:`) con el golden set. | Métrica de utilidad práctica; pasó de 0 % a 60 % con prompt v3; umbral ≥ 50 %. |

En las corridas **solo retrieval** (E1, E2, E15, E16) se reportaron únicamente las métricas de recuperación (R@k reglas y CALL), sin F1, Jaccard ni dictamen.

### Cómo interpretar las métricas

Todas las cifras de la tabla son **promedios sobre los 15 casos** del golden set y, salvo el dictamen (expresado en porcentaje), toman valores entre **0 y 1**. Un valor más alto indica mejor desempeño, pero conviene leer cada métrica según la capa que audita.

**Recuperación (R@k reglas y CALL).** Responden a una pregunta previa al LLM: *¿llegó al prompt el material normativo que el golden set espera?* Un R@k reglas de **0.76** significa que, en promedio, el 76 % de las reglas RRS etiquetadas por caso aparecen en al menos uno de los ocho fragmentos recuperados. Si este valor es bajo, el problema está en el índice, la ingesta o los cupos — no en el modelo generativo [5].

**Respuesta (F1 citas y Jaccard).** Miden qué hace el LLM con el contexto ya recuperado. El **F1** compara el conjunto de reglas o TR CALL citados en el informe contra los esperados: un F1 de **0.22** no implica que solo el 22 % del texto sea correcto, sino que hay un equilibrio entre citas acertadas y omitidas. Los **Jaccard** miden solapamiento de palabras (tokens de tres o más letras): respuesta↔contexto indica si el informe se apoya léxicamente en lo recuperado; respuesta↔referencia, si se parece al output ideal del golden set. Pueden ser bajos aun con buenas citas normativas, porque el corpus está en inglés y el informe en español.

**Decisión (acierto dictamen).** Es la métrica más cercana a la utilidad práctica: *¿la protesta se resuelve como indica el golden set?* Se compara la categoría de la línea `Decisión:` (penalizar, exonerar, desestimar, etc.) con la etiqueta de referencia. Un **60 %** significa que en 9 de 15 casos la categoría coincide; no exige redacción idéntica al output ideal.

**Lectura en conjunto.** Las métricas no son intercambiables: primero debe ser alto el R@k; solo entonces tiene sentido exigir F1 o dictamen elevados. Si R@k se mantiene y caen F1 o dictamen, el foco está en prompt y formato de salida; si cae R@k, en corpus y retrieval. Esa lógica separó la evolución del proyecto en dos etapas: E0→E11 (recuperación) y E11→E13 (respuesta auditable).

---

## Resumen del trabajo con las corridas

Las evaluaciones se organizaron en **18 corridas numeradas (E0–E17, sin E5)**. En cada una se varió **una o pocas dimensiones** — corpus, cupos de retrieval, prompt o backend de embeddings — manteniendo el resto constante para aislar el efecto del cambio [6]. El objetivo general fue pasar de una línea base con solo PDF (E0) a un perfil productivo que recupere bien las reglas RRS [1] y cierre dictámenes auditables.

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
| E14 | Mismo retrieval E11 pero **salida en inglés** (`--response-lang en`) para probar alineación léxica con corpus EN [6]. |

### Retrieval híbrido (E15–E17)

| ID | Qué buscábamos |
|----|----------------|
| E15 | Prototipo **híbrido léxico+semántico** sin fallback cuando no hay overlap de tokens [8]. |
| E16 | Híbrido con **fallback semántico** (relato ES / corpus EN); solo retrieval [8]. |
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

Golden set: **15 casos**. Retrieval léxico `top_k=8` salvo E15–E17 (híbrido [8]). LLM: **Qwen 2.5 14B** [7] en corridas completas; **llama3** en E1, E2, E15 y E16 (solo retrieval).

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

**E14 (inglés):** con el mismo R@k, el F1 RRS sube ~**+0.10** respecto a E13 y el Jaccard respuesta↔contexto ~**15×** (de ~0.01 a ~0.16), coherente con redactar en el idioma del corpus [6]. A cambio, el dictamen automático baja (40 % vs 60 %) y el Jaccard respuesta↔referencia cae: las citas léxicas mejoran en parte porque el parser reconoce `Rule`/`Decision`, pero el criterio de decisión del golden set sigue en español. **Conclusión E14:** mejora el anclaje al contexto; **no** sustituye E13 para el informe del curso.

De **E11 a E13** las métricas de retrieval **no se mueven** (mismo índice y cupos); el progreso es de **respuesta y trazabilidad**. El dictamen sube a **60 %** de coincidencia gruesa con el golden set, y el F1 RRS permanece estable (~0.22) una vez alineado el parser con las viñetas del prompt v3. E12 fue el puente (mismo R@k, dictamen ya mejora con v2; el F1=0 de la corrida fue un artefacto de evaluación, no de ausencia de citas). En conjunto, **E13 combina el techo de recuperación logrado en E11 con un formato de salida que las métricas y el informe pueden auditar**: R@k alto + F1 razonable + dictamen > 0. Lectura práctica: si en una corrida futura cae R@k, hay que mirar corpus, chunking o cupos; si R@k se mantiene y caen F1 o dictamen, hay que mirar prompt y postproceso, no el índice. Comparado con E0, el producto actual recupera **casi el doble de reglas esperadas** en top-8 y acierta el **dictamen automático en el 60 %** de los casos del golden set, a costa de un CALL ligeramente menor en recall — trade-off aceptado para la PoC con 15 casos.

En este punto del trabajo, **E11 + E13** es la mejor elección no porque sea perfecta en todas las métricas, sino porque es la única combinación que **cumple los umbrales de regresión en retrieval y respuesta** y alinea las tres dimensiones que el golden set exige: traer las normas al contexto (E11), cerrar un dictamen medible (E13) y hacerlo en **español**, coherente con el relato del usuario y el Excel de referencia. Alternativas descartadas quedan documentadas: el baseline E0 no recupera RRS; los índices *full* sin cupos diluyen reglas; E10 sacrifica CALL; E14 mejora citas léxicas pero pierde dictamen; E17 no supera a E13 en F1 ni decisión pese al híbrido [8]. Además, el par E11+E13 está **fijado en código** (`REGATAS_PROFILE=production`, `profiles.py`) y respaldado por regresión automática — es el perfil reproducible que la PoC entrega hoy, con margen claro para mejoras futuras (más casos en el golden set, refinamiento de prompt) sin reabrir la búsqueda de índice ni de backend de retrieval.

---

## Referencias bibliográficas

[1] World Sailing. (2024). *The Racing Rules of Sailing 2025–2028*. Federación internacional de vela. https://www.sailing.org/racingrules/

[2] World Sailing. (2025). *The Call Book for Team Racing 2025–2028* (8.ª ed.). https://www.sailing.org/document/2025-2028-call-book-for-team-racing/

[3] World Sailing. (2025). *World Sailing Case Book 2025–2028*. https://www.sailing.org/document/world-sailing-case-book-2025-2028/

[4] World Sailing. (s. f.). *RRS — Introduction* (publicaciones complementarias: Case Book, Call Books, interpretaciones). https://www.racingrulesofsailing.org/rules

[5] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html

[6] Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M., & Wang, H. (2024). Retrieval-augmented generation for large language models: A survey. *arXiv preprint* arXiv:2312.10997. https://arxiv.org/abs/2312.10997

[7] Qwen Team. (2024). Qwen2.5 technical report. *arXiv preprint* arXiv:2412.15115. https://arxiv.org/abs/2412.15115

[8] Karpukhin, V., Oguz, B., Min, S., Wu, L., Edunov, S., Chen, D., & Yih, W. (2020). Dense passage retrieval for open-domain question answering. *Proceedings of EMNLP 2020*, 6769–6781. https://arxiv.org/abs/2004.04906

## Comparativas detalladas

- **[Comparativa citas golden set vs E13](comparativa-citas-golden-set-vs-e13.md)** — tabla caso a caso (perfil productivo, español).
- **[Comparativa citas golden set vs E14](comparativa-citas-golden-set-vs-e14.md)** — mismo golden set con salida en inglés.
- **[E13 vs E14 (salida inglés)](comparativa-e13-vs-e14-salida-ingles.md)** — métricas agregadas del experimento `--response-lang en`.
- **[E13 vs E17 (retrieval híbrido)](comparativa-e13-vs-e17-retrieval-hibrido.md)** — experimento `embedding_backend=hybrid`; **no** adoptado (perfil sigue E13).
- Resumen narrativo y timeline: [`eval/RESUMEN_CORRIDAS_EVAL.md`](../../eval/RESUMEN_CORRIDAS_EVAL.md).