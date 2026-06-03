# Corrida ingesta RRS (CSV → JSONL) — resumen para el informe final

**Identificador:** `20260525_214113_ingesta_rrs_jsonl`  
**Etiqueta:** `ingesta_rrs_jsonl`  
**Fecha de ejecución (UTC):** 2026-05-25T21:52:50  
**Referencia de comparación:** `eval/corrida baseline/` (tag git `v0.1.0-baseline`, run `20260525_185138_baseline_call_case_qwen_es`)

Esta corrida evalúa la **primera iteración de ingesta estructurada**: reglas RRS y definiciones desde CSV convertidos a JSONL (`corpus/processed/`), **más** Call Book y Case Book en PDF con el troceo por página heredado del baseline. El golden set, el modelo y el prompt se mantienen iguales; solo cambia la composición del índice y la carga vía `REGATAS_LOAD_PROCESSED=1`.

---

## 1. Objetivo

1. Medir el impacto de **indexar el RRS por regla** (469 chunks + 26 definiciones) sobre las mismas 15 historias de protesta.
2. Comparar de forma reproducible contra la línea base **sin alterar** los artefactos en `eval/corrida baseline/`.
3. Documentar hallazgos para orientar la siguiente iteración (retriever, `top_k`, troceo Call/Case, deduplicación en CSV).

---

## 2. Alcance de la corrida

| Dimensión | Configuración |
|-----------|----------------|
| **Corpus indexado** | **RRS** (`corpus/processed/rrs_rules.jsonl`, 469 filas desde `scripts/rrs_reglas_2025_2028.csv`) + **definiciones** (26) + Call Book + Case Book (PDF) |
| **Ingesta RRS** | Offline: `python scripts/build_corpus_processed.py` → JSONL; runtime: `load_processed_jsonl=True` |
| **Ingesta PDF** | Igual que baseline: `pypdf`, por página, `chunk_size=900`, `overlap=120` |
| **Índice total** | **1389** fragmentos (469 RRS + 26 definiciones + 894 PDF) |
| **Recuperación** | Léxico (`REGATAS_EMBEDDING_BACKEND=lexical`), `top_k=8` |
| **LLM** | Ollama `qwen2.5:14b-instruct`, prompt ES, estrategia `cot` |
| **Golden set** | Mismo `eval/data/eval_set.json` (snapshot en `eval_set_snapshot.json`) |

**Sin cambios en esta corrida:** embeddings semánticos, reranking por tipo de documento, troceo Call por código CALL, aumento de `top_k`, ajuste de prompt.

---

## 3. Procedimiento reproducible

### 3.1 Generar corpus procesado (si no existe)

```bash
python scripts/build_corpus_processed.py
# → corpus/processed/rrs_rules.jsonl, definitions.jsonl, MANIFEST.json
```

### 3.2 Ejecutar evaluación

```bash
REGATAS_ACTIVITY_CONSOLE=0 \
REGATAS_LLM_BACKEND=http \
REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
REGATAS_SYSTEM_PROMPT_LANG=es \
REGATAS_LOAD_PROCESSED=1 \
python scripts/eval_run.py \
  --label ingesta_rrs_jsonl \
  --lang es \
  --model qwen2.5:14b-instruct \
  --plots
```

### 3.3 Post-proceso retrieval

```bash
python scripts/export_retrieval_hits_csv.py \
  "eval/runs/20260525_214113_ingesta_rrs_jsonl/retrieval_hits.json"

python scripts/aggregate_retrieval_hits.py \
  "eval/runs/20260525_214113_ingesta_rrs_jsonl" \
  --label ingesta_rrs_jsonl \
  --compare "eval/corrida baseline" \
  --label-compare baseline
```

### 3.4 Comparación agregada

```bash
python scripts/compare_eval_runs.py \
  "eval/corrida baseline" \
  "eval/runs/20260525_214113_ingesta_rrs_jsonl"
```

---

## 4. Qué significa «RRS» en esta corrida (diferencia con baseline)

| Pregunta | Baseline | Esta corrida |
|----------|----------|----------------|
| ¿RRS en el índice? | No | **Sí** — un chunk por fila del CSV (`chunk_id` tipo `rrs\|16.2`) |
| ¿De dónde pueden salir hits de reglas? | Solo Call/Case | **RRS JSONL**, Call/Case o respuesta del LLM |
| ¿Recall reglas mide texto del reglamento? | Indirecto (vía Call/Case) | **También** presencia en chunks `rrs\|…` |

En `retrieval_hits_detail.csv` de esta corrida hay **4 hits** con `chunk_id` que empieza por `rrs|` (p. ej. caso 5: `rrs|16.2`; caso 4: `rrs|12`, `rrs|18.3`). El resto de hits de reglas siguen pudiendo venir de Call/Case.

**Nota sobre subreglas:** el CSV no tiene fila independiente para todas las variantes del golden set (p. ej. `18.2(a)(2)`); el matcher puede dar hit en un chunk `rrs|18.2` o `rrs|18.3` si el texto del fragmento menciona la subnumeración.

---

## 5. Resultados agregados

### 5.1 Métricas globales (report.json)

| Métrica | Baseline | Ingesta RRS JSONL | Δ |
|---------|----------|-------------------|---|
| Recall@8 reglas (media) | **0,41** | **0,28** | **−0,13** |
| Recall@8 CALL (media) | **0,27** | **0,07** | **−0,20** |
| F1 citas RRS (media) | **0,22** | **0,20** | −0,02 |
| F1 citas CALL (media) | **0,13** | **0,07** | −0,06 |
| Jaccard respuesta↔contexto | **0,03** | **0,05** | +0,02 |
| Jaccard respuesta↔referencia | **0,13** | **0,12** | −0,01 |
| Acierto dictamen (automático) | **0,00** | **0,00** | 0,00 |

### 5.2 Tasas sobre ítems esperados del golden set (`retrieval_hits_agg.csv`)

| Tipo | Métrica | Baseline | Esta corrida | Δ |
|------|---------|----------|--------------|---|
| RRS (n=27) | En contexto | 40,7 % (11) | 29,6 % (8) | −11 pp |
| RRS | Citado en respuesta | 22,2 % (6) | 14,8 % (4) | −7 pp |
| RRS | Contexto + cita OK | 14,8 % (4) | 11,1 % (3) | −4 pp |
| CALL (n=15) | En contexto | 26,7 % (4) | 6,7 % (1) | −20 pp |
| CALL | Citado en respuesta | 13,3 % (2) | 6,7 % (1) | −7 pp |
| CALL | Contexto + cita OK | 13,3 % (2) | 6,7 % (1) | −7 pp |

### 5.3 Matriz contexto → cita (42 ítems: 27 reglas + 15 CALL)

| Celda | Significado | Baseline | Esta corrida |
|-------|-------------|----------|--------------|
| **A** | contexto sí, cita sí | 6 (14 %) | 4 (10 %) |
| **B** | contexto sí, cita no | 9 (21 %) | 5 (12 %) |
| **C** | contexto no, cita sí | 2 (5 %) | 1 (2 %) |
| **D** | contexto no, cita no | 25 (60 %) | 32 (76 %) |

Gráficos: `plots_retrieval/04_matriz_contexto_cita_torta.png`, `05_comparacion_corridas.png`.

### 5.4 Ranking (solo ítems con hit en contexto)

| | Baseline (n=15) | Esta corrida (n=9) |
|--|-----------------|---------------------|
| Rank 1 | 27 % | 44 % |
| Rank ≥ 4 | ~47 % | ~33 % (menos ítems con hit) |

Con menos recuperación global, la distribución de rank no es directamente comparable; ver `03_distribucion_rank_torta.png`.

---

## 6. Resultados por caso (resumen)

| ID | Título (abrev.) | R@k reglas | R@k CALL | F1 RRS | F1 CALL | Notas |
|----|-----------------|------------|----------|--------|---------|-------|
| 1 | Orzada sin espacio | 0,00 | 0,00 | 0,00 | 0,00 | Sin mejora |
| 2 | Sobre-rotación | 0,50 | 0,00 | 0,00 | 0,00 | Peor que baseline en reglas (era 1,0) |
| 3 | Retraso solapamiento | 0,00 | 0,00 | 0,00 | 0,00 | Citas espurias (31, etc.) |
| 4 | Espacio marca / virada | **1,00** | 0,00 | 0,00 | 0,00 | Hits `rrs\|12`, `rrs\|18.3` (no siempre la subregla exacta) |
| 5 | Anti-Hunt | **1,00** | **1,00** | **1,00** | **1,00** | **Mejor caso** — `rrs\|16.2` en rank 1 |
| 6 | Incapacidad espacio | 0,00 | 0,00 | 0,00 | 0,00 | Peor que baseline (CALL ya no recupera) |
| 7 | Penalización en curso | 0,00 | 0,00 | 0,00 | 0,00 | — |
| 8 | Sin regla 18.4 TR | 0,00 | 0,00 | 0,00 | 0,00 | Peor que baseline |
| 9 | Virada en zona | 0,67 | 0,00 | 0,50 | 0,00 | Similar recall reglas |
| 10 | Contacto / virada | **1,00** | 0,00 | 0,50 | 0,00 | Recall reglas alto; CALL pierde |
| 11 | The Trap | 0,00 | 0,00 | 0,00 | 0,00 | — |
| 12 | Antideportivo | 0,00 | 0,00 | 0,00 | 0,00 | Peor que baseline |
| 13 | Trasluchada regla 17 | 0,00 | 0,00 | **1,00** | 0,00 | Cita 17 sin contexto (celda C) |
| 14 | Barco terminó regata | 0,00 | 0,00 | 0,00 | 0,00 | Peor que baseline |
| 15 | Virada en proa | 0,00 | 0,00 | 0,00 | 0,00 | Cita espuria `7.3(c)` |

Detalle completo: `results_comparison_por_caso.csv`, `retrieval_hits_detail.csv`.

---

## 7. Análisis

### 7.1 Resultado principal: dilución del índice con retriever léxico

Añadir **495 chunks** normativos (RRS + definiciones) al índice **sin cambiar** `top_k=8` ni el esquema de scoring redujo la probabilidad de que Call Book y Case Book — y en la práctica también muchas reglas del golden set — entren en el contexto.

Hipótesis confirmada por datos:

- Recall@k reglas **baja** (0,41 → 0,28) pese a tener texto oficial por regla.
- Recall@k CALL **cae fuerte** (0,27 → 0,07): los fragmentos CALL compiten con cientos de chunks RRS con vocabulario solapado («rule», números, «mark», etc.).
- Solo **4** de los 8 hits RRS en contexto provienen de `chunk_id` `rrs|…`; el resto sigue siendo Call/Case.

**Conclusión:** la ingesta por regla es **necesaria pero no suficiente**; hace falta retrieval que priorice tipo de fuente o aumente/recupere más candidatos antes de truncar a 8.

### 7.2 Casos donde la ingesta RRS ayuda

- **Caso 5:** pipeline casi ideal (recall y F1 = 1,0); primer chunk `rrs|16.2`. Demuestra que, cuando el retriever coloca la regla correcta arriba, el LLM puede alinear citas.
- **Casos 4 y 10:** recall de reglas alto con chunks RRS en el top-8; la generación aún no reproduce bien el golden (F1 RRS bajo o parcial).

### 7.3 Generación y dictamen

- F1 citas RRS apenas cambia (−0,02): el cuello de botella de esta iteración es **recuperación**, no redacción.
- `verdict_accuracy` sigue en 0 % (matcher automático insuficiente; igual que baseline).
- Persisten **citas espurias** (16 filas «citado, no en golden» en el detalle): el modelo lista números de regla genéricos (p. ej. «15», «30») sin anclaje al golden.

### 7.4 Calidad del CSV / chunks duplicados

El CSV aporta **469** entradas con **412** `numero_regla` únicos; duplicados (p. ej. varias filas `18.2` por apéndices) generan `rrs|18.2#1`, … y ruido en el índice. Conviene consolidar por regla «canónica» del golden set en una siguiente versión del build.

---

## 8. Próximos pasos recomendados (orden sugerido)

| Prioridad | Acción | Métrica objetivo |
|-----------|--------|------------------|
| 1 | Subir `REGATAS_TOP_K` o retrieval híbrido (RRS + PDF por consulta) | ↑ Recall reglas y CALL |
| 2 | Boost / filtro por `doc_type` (forzar al menos N chunks `rrs` y M `pdf`) | ↑ Hits `rrs\|`, ↑ CALL en contexto |
| 3 | Embeddings semánticos (consulta en español) | ↑ Recall en casos con R@k = 0 |
| 4 | Troceo Call/Case por CALL/caso (JSONL) | ↑ Recall CALL sin diluir RRS |
| 5 | Deduplicar y alinear CSV con numeración del golden set | Menos chunks redundantes |

---

## 9. Archivos de esta carpeta

| Archivo | Uso |
|---------|-----|
| `INFORME_CORRIDA_INGESTA_RRS.md` | Este documento |
| `report.json` | Datos completos por caso |
| `results_comparison.md` / `results_comparison_por_caso.csv` | Tablas esperado vs métricas |
| `retrieval_hits_detail.csv` | Matriz contexto/cita y `chunk_id` (incl. `rrs\|`) |
| `retrieval_hits_agg.csv` | Tasas agregadas RRS vs CALL |
| `plots/` | Gráficos métricas generales |
| `plots_retrieval/` | Tasas, matriz, rank, **comparación vs baseline** (`05_…`) |
| `summary.txt` | Resumen corto de consola |
| `DATA_MANIFEST.md` | Índice de artefactos |
| `eval_set_snapshot.json` | Golden set congelado |

**Baseline intacto:** todos los archivos bajo `eval/corrida baseline/` permanecen sin modificación; la comparación es lectura cruzada entre carpetas.

---

## 10. Conclusión

La primera integración del RRS vía **CSV → JSONL** demuestra que el sistema **puede** recuperar y citar reglas desde chunks dedicados (caso 5), pero en conjunto la corrida **no supera** la baseline bajo retriever léxico y `top_k=8`: empeoran recall de reglas (−13 pp) y de CALL (−20 pp), y aumenta la celda **D** de la matriz (más ítems sin contexto ni cita).

Para el informe final: presentar esta corrida como **evidencia de que indexar el RRS es un paso obligatorio**, y que la **siguiente ganancia** vendrá del **ranking** (más candidatos, priorización por fuente o semántica), no de revertir la ingesta estructurada.

---

*Trabajo Final — Asistente de protestas en regatas (PoC DIIA). Comparación formal vs `INFORME_CORRIDA_BASELINE.md` y tag `v0.1.0-baseline`.*
