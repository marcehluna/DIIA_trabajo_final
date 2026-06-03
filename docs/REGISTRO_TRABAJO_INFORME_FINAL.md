# Registro de trabajo — informe final (DIIA)

Documento **vivo** para acumular decisiones, cambios de código, corridas de evaluación y conclusiones. Usarlo como fuente al redactar el informe del Taller de Trabajo Final.

**Reglas de uso**

1. Tras cada sesión relevante, agregar una entrada en la [bitácora cronológica](#bitácora-cronológica) (más abajo).
2. No duplicar métricas completas: enlazar `eval/DIARIO_PRUEBAS.md`, carpetas `eval/runs/` o `report.json`.
3. El diario de corridas (`eval/DIARIO_PRUEBAS.md`) sigue generándose solo con `eval_run.py`; este registro es **narrativa + decisiones de producto**.

**Índice rápido**

| Sección | Para el informe |
|---------|-----------------|
| [Resumen ejecutivo](#resumen-ejecutivo) | Introducción / conclusiones |
| [Corridas E0–E11](#corridas-de-evaluación-e0e11) | Metodología y resultados |
| [Código y arquitectura](#cambios-en-código-y-arquitectura) | Implementación |
| [Perfil productivo](#integración-perfil-productivo-e11) | Configuración desplegada |
| [Recuperación híbrida](#recuperación-híbrida) | Trabajo futuro / EPIC-003 |
| [Faithfulness](#faithfulness-pausado) | Limitaciones |
| [Artefactos](#índice-de-artefactos) | Anexos |
| [Pendientes](#pendientes-para-el-informe) | Trabajo futuro |
| [Bitácora](#bitácora-cronológica) | Línea de tiempo del proyecto |

---

## Resumen ejecutivo

**Problema:** asistente RAG para protestas náuticas; baseline (E0) indexaba solo PDF Call+Case (~894 chunks), sin RRS estructurado.

**Línea de trabajo:**

1. Ingesta estructurada CSV → JSONL (RRS, definiciones, calls, cases).
2. Evaluación sistemática con golden set de 15 casos (`eval/data/eval_set.json`).
3. Cupos de retrieval por tipo de documento para evitar dilución (469 reglas vs calls/cases).
4. Configuración productiva alineada con la mejor corrida (**E11**).
5. Preparación para retrieval híbrido (léxico + semántica) sin romper cupos.

**Configuración productiva adoptada (E11):** índice `processed` (~707 ch.), cupos **2+3+2+1**, retrieval léxico, Qwen ES. Referencia: `eval/runs/20260526_185624_processed_cupos_2_3_2_1/`.

**Métricas clave vs E0 (baseline):**

| Métrica | E0 | E11 | Δ |
|---------|-----|-----|---|
| R@k reglas | 0.41 | 0.76 | +0.35 |
| R@k CALL | 0.27 | 0.20 | −0.07 |
| F1 RRS | 0.22 | 0.22 | ≈0 |
| F1 CALL | 0.13 | 0.07 | −0.07 |

**Interpretación para el informe:** la ingesta JSONL + cupos **mejora fuertemente la recuperación de reglas RRS**; CALL aún no supera al baseline PDF — candidato a E12 (mixto JSONL + PDF con cupos 3+5, ya probado parcialmente en E7).

---

## Corridas de evaluación (E0–E11)

| ID | Fecha | Label | Idea central | R@k reglas | R@k CALL |
|----|-------|-------|--------------|------------|----------|
| **E0** | 25-may | `baseline_call_case_qwen_es` | Línea base PDF, sin cupos | 0.41 | 0.27 |
| E1 | 25-may | `baseline_retrieval` | Solo retrieval, validar métricas | 0.41 | 0.27 |
| E2 | 25-may | `rrs_case_retrieval` | PDF RRS+Case, sin Call | 0.20 | 0.00 |
| E3 | 25-may | `ingesta_rrs_jsonl` | Full sin cupos → dilución | 0.28 | 0.07 |
| E4 | 25-may | `rrs_only` | Solo processed RRS+def | 0.13 | 0.00 |
| E6 | 25-may | `full_cupos_4_4` | Full + cupos 4+4 | 0.39 | 0.13 |
| E7 | 25-may | `full_cupos_3_5` | Full + cupos 3 JSONL + 5 PDF | 0.39 | 0.20 |
| E8 | 25-may | `rrs_calls_jsonl` | JSONL sin cupos | 0.20 | 0.13 |
| E9 | 25-may | `rrs_calls_cases_jsonl` | +cases, sin cupos | 0.20 | 0.13 |
| E10 | 26-may | `processed_cupos_3_2_2_1` | Cupos 3+2+2+1 | 0.69 | 0.07 |
| **E11** | 26-may | `processed_cupos_2_3_2_1` | Más CALL (3 vs 2) | **0.76** | **0.20** |

- **Timeline visual:** `eval/docs/timeline_corridas_eval.html`, `eval/docs/timeline_corridas_eval.drawio`
- **Tabla y detalle auto:** `eval/DIARIO_PRUEBAS.md`
- **Mapeo run_id ↔ E#:** `eval/diario_runs.json`
- **Informes por corrida:** `eval/corrida baseline/INFORME_CORRIDA_BASELINE.md`, `eval/runs/20260525_214113_ingesta_rrs_jsonl/INFORME_CORRIDA_INGESTA_RRS.md`

*E5 no utilizado en el diario.*

---

## Cambios en código y arquitectura

### Ingesta y corpus

| Componente | Descripción |
|------------|-------------|
| `regatas_assistant/corpus_processed.py` | CSV → JSONL v2 (rrs, definitions, calls, cases + metadatos) |
| `regatas_assistant/chunk_metadata.py` | Listas de reglas, sufijos de encabezado para el prompt |
| `scripts/build_corpus_processed.py` | Build de `corpus/processed/*.jsonl` |
| `scripts/extract_call_book_csv.py`, `extract_case_book_csv.py` | Extracción desde PDF |
| `regatas_assistant/ingestion.py` | Modos `processed` \| `pdf` \| `full` |
| `corpus/processed/` | Artefactos versionados + `MANIFEST.json` |

### Retrieval

| Componente | Descripción |
|------------|-------------|
| `regatas_assistant/rag/retriever.py` | Léxico, semántico (http/local), **híbrido RRF**, cupos multi-pool y por `doc_type` |
| `regatas_assistant/config.py` | Variables `REGATAS_*`, cupos, perfiles |

### Evaluación

| Componente | Descripción |
|------------|-------------|
| `regatas_assistant/eval/` | Golden set, métricas, runner, diario auto |
| `scripts/eval_run.py` | Corrida completa + plots + comparación baseline |
| `scripts/compare_eval_runs.py`, `plot_eval_run.py`, `aggregate_retrieval_hits.py` | Análisis post-corrida |
| `scripts/regression_eval.py` | Umbrales mínimos vs E11 |
| `regatas_assistant/eval/faithfulness.py` + `scripts/score_faithfulness.py` | LLM juez (experimental, ver abajo) |

### Perfil productivo (2026-05-26)

| Archivo | Cambio |
|---------|--------|
| `regatas_assistant/profiles.py` | **Nuevo** — perfiles `production`, `baseline`, `legacy`; umbrales regresión E11 |
| `regatas_assistant/config.py` | Defaults producción; `REGATAS_PROFILE`; `hybrid_*` |
| `scripts/ensure_corpus_processed.py` | **Nuevo** — verificación/build JSONL |
| `docs/PERFIL_PRODUCTIVO.md` | **Nuevo** — guía operativa |
| `.env.example` | Perfil production + bloque híbrido |

---

## Integración perfil productivo (E11)

**Defecto de la app** (sin `.env` o con `REGATAS_PROFILE=production`):

- `REGATAS_CORPUS_SOURCES=processed`
- Cupos retrieval: RRS=2, CALL=3, CASE=2, DEF=1
- `REGATAS_EMBEDDING_BACKEND=lexical`

**Baseline histórico:** `REGATAS_PROFILE=baseline` → solo PDF E0.

**Regresión:** `python scripts/regression_eval.py <carpeta_corrida>` (umbrales en `profiles.py`).

---

## Recuperación híbrida

- **Implementado:** `REGATAS_EMBEDDING_BACKEND=hybrid` + `REGATAS_HYBRID_SEMANTIC_BACKEND=local|http`.
- **Compatibilidad:** los cupos por `doc_type` envuelven el retriever interno; cada pool aplica RRF (léxico + semántica) antes de fusionar.
- **Nota para el informe:** métricas E11 son con léxico; híbrido requiere nueva corrida eval antes de afirmar mejoras cuantitativas.

---

## Faithfulness (reactivado — parser y verificación por lotes)

- Módulo `faithfulness.py` y flag `--faithfulness` en `eval_run.py`; post-corrida: `scripts/score_faithfulness.py`.
- **Problema E0/E10:** la extracción de claims funcionaba; fallaba el **parseo JSON del paso 2** (verificación en lote) → todo `unknown` y 0%.
- **Ajuste 2026-06:** parser tolerante (fences, JSON truncado, comas finales), reintentos, lotes de 6 claims, fallback **claim-a-claim** con JSON simple.
- Validar con: `python scripts/score_faithfulness.py eval/runs/<id> --cases 1` antes de corrida completa.

---

## Índice de artefactos

| Tipo | Ruta |
|------|------|
| Golden set | `eval/data/eval_set.json` |
| Diario corridas | `eval/DIARIO_PRUEBAS.md` |
| Baseline E0 | `eval/corrida baseline/` |
| Mejor corrida E11 | `eval/runs/20260526_185624_processed_cupos_2_3_2_1/` |
| Reconstrucción RRS | `docs/RAG_RECONSTRUCCION_RRS.md` |
| Perfil productivo | `docs/PERFIL_PRODUCTIVO.md` |
| Este registro | `docs/REGISTRO_TRABAJO_INFORME_FINAL.md` |
| Tag git baseline | `v0.1.0-baseline` |

---

## Pendientes para el informe

- [ ] Corrida **E12** (sugerida): JSONL + Case PDF, cupos 3+5 — recuperar CALL hacia nivel E0 sin perder reglas.
- [ ] Eval con **retrieval híbrido** vs E11 léxico.
- [ ] Correr **faithfulness** en corrida completa (E11 o E12) tras validación caso 1 (~79% supported).
- [ ] **Prompting / citas** (EPIC-004): F1 CALL bajo pese a mejor R@k en E11.
- [ ] **Dictamen automático** (verdict_accuracy 0%): parser o criterio del golden.
- [ ] Persistencia de índice (milestone backlog).
- [ ] Redactar informe final usando secciones de este registro + anexos en `eval/runs/`.

---

## Bitácora cronológica

*Agregar entradas nuevas **arriba** de esta línea (más reciente primero).*

### 2026-05-26 — Metadatos en corpus RAG (JSONL v2 + encabezados)

**Qué se hizo**

- Nuevo `regatas_assistant/chunk_metadata.py` (`parse_rule_list`, `infer_referenced_rules`, `metadata_suffix`).
- `corpus_processed.py`: `ProcessedRecord` v2 persiste `section`, `referenced_rules`, `rrs_tipo`, `page_start/end`, `lang` desde CSV.
- `ingestion.TextChunk` y `header_line()` muestran `Sección:`, `Reglas:`, `pp.` en el contexto del LLM.
- Regenerado `corpus/processed/*.jsonl` + `MANIFEST.json` schema `processed_record_v2` (~680 chunks con reglas referenciadas).
- Prompts: nota sobre metadatos tras el código del encabezado.

**Por qué**

- El CSV ya tenía `reglas` y `seccion` pero no llegaban al índice ni al prompt; mejora citas CALL/CASE sin cambiar cupos E11.

**Siguiente paso sugerido**

- Corrida eval `prompt_v2_cot`; opcional paso D: boost retrieval por `referenced_rules` (EPIC-2026-002).

**Referencias**

- `corpus/processed/README.md`, `backlog/epics/EPIC-2026-002`

---

### 2026-05-26 — Prompts alineados a corpus processed (v2)

**Qué se hizo**

- Actualización de `regatas_assistant/prompts.py` (CoT y Few-Shot CoT, ES/EN):
  - Protocolo de uso del contexto con encabezados `[RRS — Regla …]`, `[TR CALL …]`, `[CASE …]`.
  - Formato de citas explícitas para métricas de eval (`Regla X.Y`, `TR CALL C`, `Case N`).
  - Cierre obligatorio de §4 con línea `Decisión: Penalizar a X.` (alineado al golden set).
  - Anti-alucinación: no citar normas ausentes del contexto recuperado.

**Por qué**

- E11 mejoró R@k pero F1 CALL y dictamen automático siguen bajos; el prompt no reflejaba el índice JSONL ni el formato de citas del evaluador.

**Validación sugerida**

- Corrida eval con `--label prompt_v2_cot` y comparar F1 citas y `verdict_accuracy` vs E11.

---

### 2026-05-26 — Perfil productivo E11 + registro para informe

**Qué se hizo**

- Integración en código del perfil **production** (defaults = corrida E11).
- Nuevo `regatas_assistant/profiles.py`, `scripts/ensure_corpus_processed.py`, `scripts/regression_eval.py`.
- Recuperación **híbrida** (RRF léxico + semántica), compatible con cupos.
- Documentación: `docs/PERFIL_PRODUCTIVO.md`, actualización `.env.example`, `README.md`, `eval/README.md`, `docs/RAG_RECONSTRUCCION_RRS.md`.
- Timeline HTML regenerado/sincronizado con Draw.io (E11, guía de métricas antes del timeline).
- Creación de este archivo `docs/REGISTRO_TRABAJO_INFORME_FINAL.md`.

**Por qué**

- Cerrar el ciclo eval → producción sin depender solo de variables ad hoc en cada corrida.
- Dejar trazabilidad para el informe final del trabajo.

**Referencias**

- Corrida E11: `20260526_185624_processed_cupos_2_3_2_1`
- Comparativa vs E10: `eval/runs/20260526_185624_processed_cupos_2_3_2_1/comparacion_vs_E10.md`

---

### 2026-05-26 — Corrida E11 (`processed_cupos_2_3_2_1`)

**Qué se hizo**

- Eval completa 15 casos, cupos 2+3+2+1 (más CALL que E10).
- Diario y comparaciones auto vs E0 y E10.

**Resultado**

- R@k reglas 0.76, R@k CALL 0.20, F1 RRS 0.22 — mejor balance processed que E10.

**Referencias**

- `eval/runs/20260526_185624_processed_cupos_2_3_2_1/`

---

### 2026-05-26 — Corrida E10 (`processed_cupos_3_2_2_1`)

**Qué se hizo**

- Primera corrida con cupos por doc_type en índice solo JSONL (3+2+2+1).

**Resultado**

- R@k reglas 0.69 (salto grande vs E0); CALL 0.07 (muy bajo).

**Referencias**

- `eval/runs/20260526_000249_processed_cupos_3_2_2_1/`

---

### 2026-05-25 — Corridas E3–E9 (ingesta, full, JSONL)

**Qué se hizo**

- E3: ingesta RRS JSONL en índice full sin cupos → regresión retrieval.
- E4: solo RRS processed.
- E6/E7: full con cupos 4+4 y 3+5.
- E8/E9: ampliación JSONL (calls, cases) sin cupos → sin mejora vs dilución.

**Aprendizaje**

- Cupos y/o separación de fuentes son necesarios cuando el índice crece.

**Referencias**

- `eval/DIARIO_PRUEBAS.md` §3
- `eval/runs/20260525_214113_ingesta_rrs_jsonl/INFORME_CORRIDA_INGESTA_RRS.md`

---

### 2026-05-25 — Baseline E0 y ramas E1–E2

**Qué se hizo**

- E0: Call+Case PDF, Qwen ES — línea base oficial (`v0.1.0-baseline`).
- E1/E2: solo retrieval (llama3) para validar pipeline de métricas.

**Referencias**

- `eval/corrida baseline/`
- `eval/corrida baseline/INFORME_CORRIDA_BASELINE.md`

---

### (Plantilla) YYYY-MM-DD — Título breve

**Qué se hizo**

- …

**Por qué / decisión**

- …

**Resultado / métricas** (si aplica)

- …

**Referencias**

- Archivos, run_id, commits: …

---

*Fin del registro. Mantener sincronizado con el repositorio al cerrar cada hito.*
