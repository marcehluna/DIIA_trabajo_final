### 02. Justificación de la solución

Fundamentación de las decisiones técnicas y de diseño adoptadas a lo largo del proyecto.

---
# Capítulo 1: Introducción y Planteamiento del Problema

## 1.1 Contexto del Dominio: Las Competencias de Vela y su Marco Regulatorio
Las competencias de vela de alto rendimiento, y en particular modalidades dinámicas como el *Team Racing* (regatas por equipos), constituyen un escenario deportivo de alta complejidad táctica y operativa. A diferencia de otros deportes donde las infracciones son penalizadas de forma inmediata por un árbitro con visibilidad total, en las regatas la resolución de conflictos se fundamenta en un cuerpo legal estricto y extenso: el **Reglamento de Regatas a Vela (RRS)**, emitido por la federación internacional *World Sailing* [1].

Este reglamento técnico dicta desde las prioridades de paso fundamentales hasta las interacciones cinemáticas complejas en los puntos críticos del recorrido (como el paso por las boyas). En la práctica, ante un incidente en el agua, los competidores deben presentar solicitudes de protesta que posteriormente son evaluadas por un Comité de Protestas o un cuerpo de jueces (*Umpires*), según el procedimiento de audiencias de la Parte 5 del RRS [1]. Para dictaminar un fallo, los jueces no solo aplican el RRS, sino que deben contrastar los hechos con un corpus de jurisprudencia oficial: el *Call Book for Team Racing* [2] y el *Case Book* [3], publicaciones complementarias reconocidas por World Sailing [4].

## 1.2 Planteamiento del Problema
A pesar de contar con un marco normativo robusto, el proceso tradicional de gestión y resolución de protestas enfrenta severas limitaciones operativas y cognitivas que afectan la agilidad y la equidad de las competencias. Estos obstáculos se agrupan en cuatro dimensiones críticas:

### A. Complejidad y Ambigüedad Semántica
El reglamento náutico funciona como un ordenamiento jurídico especializado. Un único incidente en el agua (por ejemplo, el cruce o aproximación de dos embarcaciones) suele activar múltiples reglas simultáneas que interactúan entre sí mediante jerarquías y excepciones (v.g., la obligación general de mantenerse alejado frente a la limitación al barco con derecho de paso cuando este cambia de rumbo). 

Debido a que los regatistas redactan sus protestas utilizando un lenguaje natural, coloquial y muchas veces subjetivo, se genera una brecha lingüística. A los comités de regata o jueces de clubes pequeños les resulta complejo y lento traducir esa narrativa informal a las estructuras normativas y técnicas exactas que exige el reglamento.

### B. Cuello de Botella Operativo en la Toma de Decisiones
Al finalizar una jornada de competencia, los comités de protesta suelen recibir un volumen crítico de formularios escritos a mano o por correo electrónico. El proceso de clasificar estos relatos, resumir los eventos cronológicamente y extraer las entidades clave —determinar con precisión qué embarcación poseía el derecho de paso y cuál la obligación de mantenerse alejada— requiere horas de trabajo manual exhaustivo. Esta saturación administrativa retrasa la publicación de los resultados oficiales del campeonato y somete a los jueces a una alta fatiga cognitiva.

### C. Inconsistencia e Interpretación Dispar de los Fallos
La resolución de protestas posee un fuerte componente de interpretación humana. Ante relatos idénticos, dos comités de jueces distintos pueden emitir dictámenes divergentes si no disponen de un acceso inmediato, indexado y ágil a la jurisprudencia oficial (*Calls* o *Cases*). Esta falta de estandarización mina la predictibilidad del arbitraje, genera percepciones de injusticia en los atletas y perjudica la integridad competitiva del deporte.

### D. La Subjetividad Narrativa como Barrera Probatoria
Gran parte de los incidentes ocurren en puntos alejados de la costa o fuera del campo visual directo de los jueces. En consecuencia, el testimonio y relato escrito de las partes involucradas se convierte en la única fuente de información disponible para reconstruir los hechos. Esta dependencia introduce contradicciones lingüísticas estructurales: es habitual que dos competidores describan la misma maniobra utilizando términos técnicos opuestos para justificar sus acciones. El proceso actual carece de herramientas que permitan comparar estas narrativas divergentes de manera sistemática y aislar los hechos consistentes para una reconstrucción lógica del escenario.

## 1.3 Justificación de la Solución Tecnológica: PLN e IA Generativa
Para mitigar estas deficiencias, este proyecto propone el desarrollo de un asistente inteligente basado en técnicas de **Procesamiento de Lenguaje Natural (PLN)** e **Inteligencia Artificial Generativa**. La tecnología no se concibe como un sustituto del criterio soberano del juez, sino como un mecanismo de aceleración y soporte cognitivo.

A través de modelos de lenguaje avanzados y una arquitectura de **Generación Aumentada por Recuperación (RAG)** [5], el sistema es capaz de "normalizar" los relatos informales en español, extrayendo los agentes y sus posiciones relativas. Posteriormente, el motor RAG contrasta dicha información con el corpus normativo oficial en inglés, anclando la generación a fragmentos recuperados en lugar de depender solo de la memoria paramétrica del modelo — enfoque que mitiga respuestas factualmente incorrectas o no sustentadas [5][8]. De este modo, se transforma un proceso lento y subjetivo en un flujo de trabajo auditable, rápido y con un alto valor pedagógico para la comunidad náutica.

## Punto de partida

El trabajo final parte de una **PoC de asistente RAG para protestas náuticas** desarrollada en la materia **Procesamiento de Lenguaje Natural (PLN)** de la Diplomatura (versión de referencia en el repositorio, mayo 2026). Esa solución inicial ya resolvía el flujo básico — interfaz Gradio [9], chunking de PDF, recuperación léxica, generación con LLM local (Qwen en español [7]) y *chain-of-thought* [6] — pero indexaba principalmente el **Call Book** y el **Case Book** en PDF, **sin RRS estructurado** en el índice y **sin cupos** de recuperación por tipo de documento.

En el Taller de Trabajo Final se tomó esa base como **línea E0** (`baseline_call_case_qwen_es`) y se iteró con evaluación sistemática hasta el perfil productivo actual: **retrieval E11** + **respuesta E13**.

---

## EDA del corpus normativo

Antes de fijar ingesta y retrieval se realizó un **análisis exploratorio** sobre los PDF oficiales en `corpus/`, documentado en la sección 03 del reporte ([`Metricas.docx`](../03-eda-y-descubrimientos/Metricas.docx)).

### Documentos analizados

| Fuente | Tipo | Páginas | Caracteres (pdfplumber) |
|--------|------|---------|-------------------------|
| `2025-2028-RRS-with-Changes-and-Corrections.pdf` | RRS | 160 | ~233 000 |
| `The-Call-Book-for-Team-Racing-2025-2028.pdf` | Call Book (Team Racing) | 111 | ~121 000 |
| `WS-Case-Book-2025-2028-v2025-07.pdf` | Case Book | 328 | ~428 500 |

En conjunto son **~599 páginas** y **~782 000 caracteres** de texto extraído. El Case Book concentra más del 55 % del volumen; el RRS aporta la mayor densidad normativa por página.

### Calidad y heterogeneidad del texto PDF

1. **Longitud por página:** histogramas + KDE muestran distribuciones muy distintas entre los tres libros (páginas cortas en señales/tablas del RRS vs bloques largos en casos del Case Book). No hay un tamaño de chunk único “óptimo” para todo el corpus en bruto.

2. **Extracción y limpieza:** se comparó **pypdf** (texto crudo) frente a **pdfplumber** [10] con la misma normalización que `regatas_assistant/ingestion.py` (espacios colapsados, `strip`, retirada de referencias bibliográficas tipo `GBR 1962/25`). La limpieza reduce ruido sin perder cuerpo normativo.

3. **Páginas pobres:** con umbral menor a 50 caracteres tras `strip`, las tasas de páginas casi vacías son bajas (RRS **2,5 %**, Call **0,9 %**, Case **7,3 %**). No se detectaron artefactos de codificación (`U+FFFD` 0 %) ni guiones de línea problemáticos en volumen relevante.

4. **Léxico:** ~**44–49 %** de los tokens alfabéticos son stopwords en inglés (`stopwords_en.txt`), coherente con un corpus normativo en inglés y relatos de protesta en español (motivo posterior del experimento E14 y del fallback semántico E16).

### Chunking y techo de embeddings (PDF)

Con los defaults de producción (**900 caracteres / 120 solapamiento**, troceo **por página**), el índice solo-PDF suma **~1 247 chunks**. En tokens Qwen:

| PDF | Chunks | p50 tok | p90 tok | % chunks > 512 tok |
|-----|--------|---------|---------|----------------------|
| RRS | 353 | 194 | 229 | 0 % |
| Call Book | 200 | 198 | 241 | 0,5 % |
| Case Book | 694 | 193 | 225 | 0 % |

Casi todos los fragmentos quedan **por debajo del techo típico de 512 tokens** para embeddings; el cuello de botella no es truncamiento sino **granularidad** (una página puede mezclar varias normas o un caso entero).

Una ventana deslizante de **512 tokens / 128 solape** sobre texto limpio produce muchos chunks en el techo (p50 = p90 = p95 = **512** en los tres PDF), señal de que el troceo ciego por página o por ventana **no alinea** unidades normativas (regla, TR CALL, case) — problema recurrente en pipelines RAG cuando la granularidad del chunk no coincide con la unidad de conocimiento [8].

### Del EDA al corpus estructurado (JSONL)

Los hallazgos motivaron pasar de PDF troceado a **unidades normativas revisables** (`corpus/processed/*.jsonl`), según `MANIFEST.json` v2:

| `doc_type` | Registros | Origen |
|------------|-----------|--------|
| RRS (`rrs`) | 469 | `rrs_reglas_2025_2028.csv` |
| Definiciones | 26 | `definitions.csv` |
| TR CALL (`call`) | 83 | `call_book_calls.csv` |
| CASE (`case`) | 129 | `case_book_cases.csv` |

Total **~707 chunks** con metadatos (`ref_id`, `section`, `referenced_rules`, páginas fuente), frente a **~1 247** en el índice PDF-only y **~1 389** en mezclas full sin cupos (corrida E3).

### Implicaciones que condicionan las decisiones siguientes

- **Ingesta estructurada** (decisión 3): el EDA mostró que el PDF solo no preserva unidades citables; el JSONL alinea chunk ↔ regla/call/case.
- **Cupos por `doc_type`** (decisión 5): con cientos de reglas RRS, un ranking global empuja calls/cases fuera del `top_k`; el EDA de volumen explica la necesidad de cupos.
- **Parámetros 900/120**: se mantienen para PDF residual y compatibilidad con la PoC PLN; el índice productivo prioriza JSONL por unidad normativa.
- **Retrieval léxico**: el análisis de vocabulario (términos sin stopwords por documento) validó que el overlap léxico es viable cuando el índice incluye `referenced_rules` y encabezados; el gap ES→EN en consultas quedó acotado por eval (E16), no por sustituir el índice.

---

## Decisiones de diseño (orden cronológico)

### 1. Fijar una línea base medible (E0)

**Decisión:** conservar la PoC de PLN como comparador histórico, etiquetada E0.

**Motivo:** sin un baseline fijo no se puede atribuir mejoras a ingesta, retrieval o prompt. E0 documenta el comportamiento heredado: buen recall de TR CALL en PDF (R@k CALL ≈ 0.27), pero **recuperación débil de reglas RRS** (R@k ≈ 0.41) porque el RRS no estaba en el índice de forma explícita.

**Artefacto:** `eval/corrida baseline/`, tag `v0.1.0-baseline`.

---

### 2. Introducir un golden set y pipeline de evaluación

**Decisión:** construir un conjunto fijo de **15 casos** desde el Excel de protestas (`eval/data/eval_set.json`) y automatizar corridas con métricas de retrieval, citas y dictamen.

**Motivo:** las protestas náuticas exigen trazabilidad normativa (RRS, TR CALL, casos). Un golden set permite comparar corridas E0–E17 con las mismas entradas y separar fallos de **recuperación** vs **generación**.

**Componentes:** `scripts/eval_run.py`, `regatas_assistant/eval/`, `eval/DIARIO_PRUEBAS.md`.

---

### 3. Ingesta estructurada: CSV → JSONL en lugar de solo PDF

**Decisión:** extraer el corpus normativo a artefactos revisables (`corpus/processed/*.jsonl`) a partir de CSV derivados de los PDF oficiales (RRS, definiciones, calls, cases).

**Motivo:** el EDA anterior mostró heterogeneidad de páginas, ruido bibliográfico y chunks que no coinciden con unidades citables; el JSONL por regla/call/case mejora metadatos (`doc_type`, `referenced_rules`, encabezados) y reduce el índice de ~1 247 (PDF) a ~707 registros auditables.

**Evolución:** fase 1 solo RRS (`RAG_RECONSTRUCCION_RRS.md`) → incorporación de calls y cases (E8–E9, ~707 chunks).

---

### 4. Rechazar la mezcla full sin cupos (E3) y priorizar índice processed

**Decisión:** abandonar el índice mixto JSONL+PDF sin restricciones (~1389 chunks, E3) y adoptar **`REGATAS_CORPUS_SOURCES=processed`** como núcleo del producto.

**Motivo:** mezclar todo el corpus en un solo pool **diluye** el recall de reglas RRS (E3 baja vs E0). Los experimentos E6–E7 con cupos en índice full recuperan parte del baseline en CALL, pero no superan el techo de reglas alcanzado con JSONL puro + cupos por tipo (E10–E11).

---

### 5. Cupos de retrieval por tipo de documento (E10 → E11)

**Decisión:** reservar slots fijos en `top_k=8` por `doc_type`: **2 RRS + 3 CALL + 2 CASE + 1 definición** (perfil E11).

**Motivo:** en un índice con cientos de reglas RRS, un ranking global empuja calls y cases fuera del contexto. Los cupos garantizan diversidad normativa en cada consulta. E10 (3+2+2+1) ya disparó R@k reglas; E11 sube el cupo CALL de 2 a 3 y equilibra recall de TR CALL sin perder reglas (R@k reglas **0.76**, R@k CALL **0.20**).

**Trade-off aceptado:** CALL recall queda por debajo del baseline PDF (0.27 → 0.20) a cambio de un índice más compacto y mucho más fuerte en reglas, que es el cuello de botella en protestas.

---

### 6. Mantener retrieval léxico (no híbrido) como defecto

**Decisión:** `REGATAS_EMBEDDING_BACKEND=lexical` en producción; el híbrido léxico+semántico (E15–E17) queda como experimento opt-in.

**Motivo:** el prototipo híbrido sin fallback (E15) empeoró R@k (0.60). Con fallback semántico para relatos en español (E16) se **iguala** E11 en agregados y se corrige el caso 7, pero la corrida completa híbrida + prompt v3 (E17) **empeora** F1 de citas y dictamen vs E13. El léxico, con índice enriquecido (header + reglas referenciadas + texto), alcanza el techo medido sin el costo de embeddings densos [11] ni regresiones en la respuesta.

---

### 7. LLM local en español con CoT

**Decisión:** mantener **Qwen2.5 14B instruct** [7] vía API HTTP (Ollama [12]), estrategia **chain-of-thought** [6] y system prompt en español.

**Motivo:** continuidad con la PoC de PLN, costo cero de inferencia en desarrollo y coherencia con el golden set y el informe del curso (relatos y decisiones en español). No se cambió el modelo entre E0 y E13 para aisolar el efecto de ingesta y prompt.

---

### 8. Evolución del prompt: v2 → v3 (E12 → E13)

**Decisión:** adoptar **prompt v3** con plantilla fija de cuatro secciones (síntesis, normas jerarquizadas, rationale, resolución), viñetas `Regla …` / `TR CALL …` y línea obligatoria `Decisión:`.

**Motivo:** con el retrieval de E11 el contexto ya traía las reglas, pero el prompt heredado de PLN no producía salida parseable: **dictamen automático 0 %** en E11. E12 (v2) demostró que el cuello de botella pasó a la **capa de respuesta**; E13 alinea formato, parser de citas (`refs.py`) y métricas. Resultado: dictamen **60 %**, F1 RRS estable (~0.22 con parser actual).

---

### 9. Mantener la respuesta en español (descartar E14 como producto)

**Decisión:** `REGATAS_RESPONSE_LANG=es` por defecto; no adoptar salida en inglés (E14) pese a mejor F1 RRS (+0.10) y mayor solapamiento respuesta↔contexto.

**Motivo:** el golden set y el criterio de dictamen están en español; E14 baja dictamen a 40 % y el Jaccard vs Output Ideal cae. La alineación léxica al corpus inglés no compensa la pérdida en decisión medible para el informe.

---

### 10. Perfiles de configuración y regresión automatizada

**Decisión:** centralizar defaults en `REGATAS_PROFILE=production` (`profiles.py`), con perfiles `baseline` (E0) y `legacy` (full sin cupos) para reproducir experimentos; umbrales de regresión contra corridas E11 (retrieval) y E13 (respuesta).

**Motivo:** evitar que variables sueltas en `.env` rompan el perfil acordado; permitir validar cambios de índice con `--mode retrieval` y cambios de prompt con regresión completa. Test unitario en `tests/test_production_profile.py`.

---

## Configuración adoptada (síntesis)

| Capa | Decisión | Referencia eval |
|------|----------|-----------------|
| Corpus | JSONL `processed`, ~707 chunks | E8–E11 |
| Retrieval | Léxico, cupos 2+3+2+1 | **E11** |
| LLM | Qwen ES, CoT | E0 / E13 |
| Prompt / formato | v3 español, `Decisión:` parseable | **E13** |
| Embeddings | Léxico (híbrido solo experimento) | E15–E17 descartados |

Detalle operativo: [`docs/PERFIL_PRODUCTIVO.md`](../../docs/PERFIL_PRODUCTIVO.md). Métricas y narrativa E0–E17: [`eval/RESUMEN_CORRIDAS_EVAL.md`](../../eval/RESUMEN_CORRIDAS_EVAL.md).

---

## Lectura integradora

La evolución no fue un único salto técnico sino **dos capas encadenadas**: de E0 a E11 el avance es casi todo en **recuperación** (R@k reglas +85 % relativo); de E11 a E13 el avance es en **respuesta auditable** (dictamen de 0 % a 60 %). La PoC de PLN aportó arquitectura y stack; el Taller aportó **corpus estructurado, evaluación rigurosa y diseño por evidencia** hasta la versión actual.

---

## Referencias bibliográficas

[1] World Sailing. (2024). *The Racing Rules of Sailing 2025–2028*. Federación internacional de vela. https://www.sailing.org/racingrules/

[2] World Sailing. (2025). *The Call Book for Team Racing 2025–2028* (8.ª ed.). https://www.sailing.org/document/2025-2028-call-book-for-team-racing/

[3] World Sailing. (2025). *World Sailing Case Book 2025–2028*. https://www.sailing.org/document/world-sailing-case-book-2025-2028/

[4] World Sailing. (s. f.). *RRS — Introduction* (publicaciones complementarias: Case Book, Call Books, interpretaciones). https://www.racingrulesofsailing.org/rules

[5] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html

[6] Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q. V., & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in large language models. *Advances in Neural Information Processing Systems*, 35, 24824–24837. https://proceedings.neurips.cc/paper/2022/hash/9d5609613524ecf4f15af0f7b31abca4-Abstract.html

[7] Qwen Team. (2024). Qwen2.5 technical report. *arXiv preprint* arXiv:2412.15115. https://arxiv.org/abs/2412.15115

[8] Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M., & Wang, H. (2024). Retrieval-augmented generation for large language models: A survey. *arXiv preprint* arXiv:2312.10997. https://arxiv.org/abs/2312.10997

[9] Abid, A., Abdalla, A., Abid, A., Khan, S., Alfozan, D., & Zou, J. (2019). Gradio: Hassle-free sharing and testing of ML models in the wild. *arXiv preprint* arXiv:1906.02569. https://arxiv.org/abs/1906.02569

[10] Vine, J. (s. f.). *pdfplumber* (biblioteca de extracción de texto PDF utilizada en el proyecto). https://github.com/jsvine/pdfplumber

[11] Karpukhin, V., Oguz, B., Min, S., Wu, L., Edunov, S., Chen, D., & Yih, W. (2020). Dense passage retrieval for open-domain question answering. *Proceedings of EMNLP 2020*, 6769–6781. https://arxiv.org/abs/2004.04906

[12] Ollama. (s. f.). *Ollama — Run large language models locally*. https://ollama.com/
