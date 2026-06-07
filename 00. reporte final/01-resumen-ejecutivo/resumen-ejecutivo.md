### 01. Resumen ejecutivo

---

## Contexto y objetivo

Este informe documenta el trabajo final de la **Diplomatura en Inteligencia Artificial Aplicada (DIIA)**, en el marco del **Taller de Trabajo Final**. El proyecto evoluciona una PoC de asistente inteligente para **protestas náuticas en Team Racing**, desarrollada previamente en la materia de **Procesamiento de Lenguaje Natural (PLN)**, hacia un sistema **evaluable y reproducible**.

El objetivo no es reemplazar al comité de protestas ni al umpire, sino ofrecer **soporte cognitivo**: acelerar la lectura de relatos en español, recuperar normativa oficial (RRS, Call Book, Case Book) y producir un informe estructurado con citas y decisión preliminar, anclado al corpus recuperado mediante **Generación Aumentada por Recuperación (RAG)**.

---

## Problema abordado

La resolución de protestas en regatas combina relatos subjetivos en lenguaje natural con un marco normativo extenso y técnico, en gran parte en inglés. Los comités enfrentan saturación operativa al final de cada jornada, fatiga cognitiva al cruzar hechos con reglas y precedentes, y variabilidad en los fallos cuando el acceso a la jurisprudencia no es inmediato. El proyecto aborda esa brecha con un pipeline que **normaliza la entrada**, **recupera evidencia normativa** y **genera una respuesta auditable**, ejecutable en hardware local (Ollama + Qwen2.5).

---

## Enfoque de la solución

El trabajo se organizó en cinco ejes, desarrollados en las secciones 02 a 06 del reporte:

| Eje | Contenido principal |
|-----|---------------------|
| **Justificación** | Planteamiento del problema y decisiones técnicas por evidencia (corpus JSONL, cupos, prompt v3). |
| **EDA** | Análisis del corpus normativo en PDF: volumen, segmentación, calidad de extracción e implicancias para el índice. |
| **Arquitectura** | Tres capas: preparación offline del corpus, consulta RAG en tiempo real (Gradio) y evaluación offline con golden set. |
| **Evaluación** | 18 corridas (E0–E17) que aíslan cambios en ingesta, retrieval, prompt y backend; regresión automatizada. |
| **Conclusiones** | Reflexión crítica, limitaciones y proyección hacia un producto aplicable en club o comisión. |

El salto respecto de la PoC de PLN no fue reescribir la arquitectura, sino **estructurar el conocimiento** (un chunk por regla, call o case), **equilibrar la recuperación** con cupos por tipo de documento y **medir cada capa por separado** — retrieval primero, generación después.

---

## Resultados principales

La línea base **E0** (Call Book + Case Book en PDF, sin RRS estructurado) se contrastó con el perfil productivo **E11 + E13**:

| Dimensión | E0 (baseline) | E11 + E13 (productivo) |
|-----------|---------------|-------------------------|
| Corpus | PDF, sin cupos | JSONL processed (~707 chunks), cupos 2+3+2+1 |
| Recall@8 reglas RRS | 0,41 | **0,76** |
| Recall@8 TR CALL | 0,27 | 0,20 |
| F1 citas RRS (respuesta) | 0,22 | **0,22** |
| Acierto dictamen automático | 0 % | **60 %** |

La mejora se concentra en **dos capas encadenadas**: de E0 a E11, el avance es casi todo en recuperación de reglas; de E11 a E13, en formato de respuesta y trazabilidad (dictamen medible, citas parseables). El sistema cumple los **umbrales de regresión** definidos en `profiles.py` y queda fijado como `REGATAS_PROFILE=production`.

La evaluación se realizó sobre un **golden set de 15 casos** derivados del Case Book y validados contra el Excel *Casos de Regatas*. Alternativas experimentales — índice *full* sin cupos, salida en inglés (E14), retrieval híbrido (E15–E17) — quedaron documentadas y descartadas con métricas, no por intuición.

---

## Limitaciones y alcance

Se trata de una **PoC académica**, no de un despliegue en competencia oficial. El golden set es reducido; el recall de TR CALL quedó por debajo del baseline PDF; el dictamen automático acierta en seis de cada diez casos; y la validación de dominio se apoyó en experiencia náutica del autor, sin revisión de una comisión externa. Las corridas completas en hardware local limitaron la cantidad de experimentos posibles.

---

## Cierre y proyección

El entregable demuestra que, con corpus bien segmentado y salida acotada por diseño, un RAG local puede **recuperar la norma relevante**, **redactar un informe en español** y **medir mejoras de forma reproducible**. La proyección natural del trabajo es un **piloto aplicable** — club, comisión de protestas o circuito de Team Racing — con revisión humana obligatoria del dictamen, ampliación del golden set e infraestructura de despliegue. El detalle técnico, las métricas caso a caso y la reflexión sobre el proceso se desarrollan en las secciones 02 a 06 de este reporte.
