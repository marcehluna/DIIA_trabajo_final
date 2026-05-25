# Corrida baseline — resumen para el informe final

**Identificador:** `20260525_185138_baseline_call_case_qwen_es`  
**Etiqueta:** `baseline_call_case_qwen_es`  
**Fecha de ejecución (UTC):** 2026-05-25T19:04:40  

Este documento describe la **línea base** del asistente de protestas en regatas (PoC RAG + LLM), antes de cualquier mejora en la ingesta del corpus. Los resultados de corridas posteriores (p. ej. troceo por regla/caso, inclusión de RRS estructurado) deben compararse contra esta referencia **manteniendo fijas** las mismas condiciones de modelo, prompt y golden set, salvo que se documente explícitamente un cambio.

---

## 1. Objetivo

1. Establecer un **punto de partida medible** del pipeline actual en producción (ingesta por página, troceo fijo en caracteres, retriever léxico).
2. Cuantificar, sobre **15 incidentes** representativos, la calidad de **recuperación** y de **generación** (citas normativas y anclaje al contexto).
3. Dejar trazabilidad completa (datos, métricas y gráficos) para el capítulo de evaluación del trabajo final y para contrastar con iteraciones futuras.

---

## 2. Alcance de la línea base

| Dimensión | Configuración baseline |
|-----------|-------------------------|
| **Corpus indexado** | Call Book for Team Racing 2025-2028 + World Sailing Case Book 2025-2028 (**sin RRS** en el índice) |
| **Ingesta** | `pypdf`, troceo **por página**, `chunk_size=900` caracteres, `overlap=120` (valores por defecto de `Settings`) |
| **Índice** | 894 fragmentos (200 Call Book + 694 Case Book) |
| **Recuperación** | `REGATAS_EMBEDDING_BACKEND=lexical` (BM25-like por tokens), `top_k=8` |
| **LLM** | Ollama, modelo **`qwen2.5:14b-instruct`**, API compatible OpenAI en `http://127.0.0.1:11434/v1` |
| **Prompt** | System prompt en **español**, estrategia **Chain-of-Thought** (`cot`) |
| **Golden set** | 15 casos desde `docs/Casos de Regatas.xlsx` (columna **Input** = relato; etiquetas desde **Output Ideal**) |

**Fuera de alcance en esta corrida:** cambios de ingesta, inclusión del PDF/CSV del RRS, embeddings semánticos, expansión por tesauro, reranking o ajuste de prompts.

---

## 3. Procedimiento reproducible

### 3.1 Construcción del golden set

```bash
python scripts/build_eval_set.py
```

- Salida: `eval/data/eval_set.json` (copia congelada en esta carpeta como `eval_set_snapshot.json`).
- Tabla de revisión de etiquetas: `eval/data/golden_set_review.md`.

### 3.2 Ejecución de la corrida

```bash
REGATAS_ACTIVITY_CONSOLE=0 \
REGATAS_LLM_BACKEND=http \
REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
REGATAS_SYSTEM_PROMPT_LANG=es \
python scripts/eval_run.py \
  --label baseline_call_case_qwen_es \
  --lang es \
  --model qwen2.5:14b-instruct \
  --plots
```

Por cada caso el pipeline:

1. Compone la consulta a partir del relato de protesta.
2. Recupera 8 fragmentos del índice léxico.
3. Arma el prompt con contexto + relato y solicita el informe al LLM.
4. Persiste respuesta, chunks, métricas y archivos auxiliares.

### 3.3 Post-proceso y artefactos

- Enriquecimiento de métricas extendidas (recall@1…@k, MRR, detalle de hits): `python scripts/enrich_eval_report.py "eval/corrida baseline"`.
- Gráficos en `plots/` (8 PNG).
- Tablas: `results_comparison.md`, `metrics_long.csv`, `retrieval_hits.json`, `chunks_summary.csv`.

---

## 4. Métricas utilizadas

### 4.1 Aclaración importante: qué significa «RRS» en tablas y CSV

En los resultados de esta corrida aparecen columnas y filas etiquetadas como **RRS** (p. ej. `Recall reglas`, `F1 RRS`, tipo `RRS` en `retrieval_hits_detail.csv`). **Eso no implica que el PDF del Reglamento de Regatas a Vela esté ingestado en el RAG.**

| Pregunta | Respuesta en esta baseline |
|----------|----------------------------|
| ¿Está el PDF del RRS en el índice? | **No.** Solo Call Book (200 chunks) y Case Book (694 chunks). |
| ¿De qué PDF salen los fragmentos recuperados? | **Siempre** de `The-Call-Book-for-Team-Racing-2025-2028.pdf` o `WS-Case-Book-2025-2028-v2025-07.pdf` (verificable en `chunk_id` de `retrieval_hits_detail.csv` y `chunks_summary.csv`). |
| ¿Qué es entonces «regla RRS esperada»? | Número de regla extraído del **Output Ideal** del Excel (p. ej. 16.1, 11, 18.2), usado como **referencia de evaluación** (golden set), no como fuente indexada. |
| ¿Por qué hay «hits» de reglas RRS en recuperación? | Call Book y Case Book **citan y parafrasean** reglas del RRS («Rule 16», «Rule 18.2», etc.). Si un chunk del Call Book contiene «Rule 11», la métrica da hit aunque no exista chunk del RRS. |
| ¿De dónde salen reglas en la respuesta del modelo? | Del texto que Qwen genera: puede reflejar fragmentos recuperados (Call/Case) o, en algunos casos, formulaciones no alineadas al golden set (filas «citado, no en golden» en el CSV de detalle). |

**Ejemplo ilustrativo (caso 2):** se esperan reglas 11 y 13; ambas aparecen en contexto (`en_contexto_recuperado = sí`) en chunks del **Call Book** (págs. 6 y 14), no del RRS. El modelo cita el CALL B2 en la respuesta pero **no** reproduce en el informe los números de regla esperados (F1 RRS = 0).

**Lectura correcta para el informe final:** las métricas «RRS» miden **alineación con la norma de referencia del caso de prueba** y su **presencia en Call/Case o en la respuesta**, no la recuperación del texto oficial del reglamento. Cuando en iteraciones futuras se indexe el RRS (PDF o CSV por regla), la misma métrica pasará a reflejar además el acceso al **texto normativo completo** del RRS; el delta frente a esta baseline será entonces interpretable como mejora de cobertura reglamentaria directa.

### 4.2 Definición de métricas

| Métrica | Qué mide (en esta baseline) |
|---------|----------------------------|
| **Recall@k reglas** | Fracción de **números de regla esperados (golden set)** que aparecen (como «Rule N» o equivalente) en al menos uno de los 8 chunks de **Call o Case** |
| **Recall@k CALL** | Igual para códigos TR CALL esperados en chunks de Call/Case |
| **F1 citas RRS** | Concordancia entre **números de regla** citados en la respuesta del modelo y los esperados en el Excel |
| **F1 citas CALL** | Igual para TR CALL en la respuesta |
| **Jaccard resp↔contexto** | Solapamiento léxico entre respuesta y texto recuperado (proxy de anclaje al contexto; sensible al español vs inglés del corpus) |
| **Jaccard resp↔referencia** | Solapamiento léxico entre respuesta y output ideal del Excel |
| **Acierto dictamen** | Coincidencia automática de categoría de dictamen (penalizar / sin penalización / mixto); ver limitaciones en §6 |

---

## 5. Resultados agregados

| Métrica | Valor baseline |
|---------|----------------|
| Casos evaluados | 15 |
| Recall@8 reglas (media) | **0,41** |
| Recall@8 CALL (media) | **0,27** |
| F1 citas RRS (media) | **0,22** |
| F1 citas CALL (media) | **0,13** |
| Jaccard respuesta↔contexto (media) | **0,03** |
| Jaccard respuesta↔referencia (media) | **0,13** |
| Acierto dictamen (automático) | **0,00** |

### 5.1 Resultados por caso (resumen)

| ID | Título (abrev.) | Recall reglas | Recall CALL | F1 RRS | F1 CALL | Jaccard ctx |
|----|-----------------|---------------|-------------|--------|---------|-------------|
| 1 | Orzada sin espacio | 0,00 | 0,00 | 0,00 | 0,00 | 0,02 |
| 2 | Sobre-rotación barlovento | 1,00 | 1,00 | 0,00 | 1,00 | 0,02 |
| 3 | Retraso solapamiento | 0,00 | 0,00 | 0,50 | 0,00 | 0,02 |
| 4 | Espacio de marca / virada | 0,67 | 0,00 | 0,00 | 0,00 | 0,06 |
| 5 | Anti-Hunt babor-estribor | 1,00 | 1,00 | **1,00** | **1,00** | 0,07 |
| 6 | Incapacidad espacio marca | 0,00 | 1,00 | 0,00 | 0,00 | 0,01 |
| 7 | Penalización en curso | 0,00 | 0,00 | 0,00 | 0,00 | 0,02 |
| 8 | Sin regla 18.4 TR | 0,33 | 0,00 | 0,00 | 0,00 | 0,01 |
| 9 | Virada completada en zona | 0,67 | 0,00 | 0,67 | 0,00 | 0,07 |
| 10 | Contacto antes de virada | 1,00 | 1,00 | 0,50 | 0,00 | 0,07 |
| 11 | The Trap en marca | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| 12 | Antideportivo | 0,50 | 0,00 | 0,00 | 0,00 | 0,03 |
| 13 | Trasluchada regla 17 | 0,00 | 0,00 | 0,00 | 0,00 | 0,01 |
| 14 | Barco terminó regata | 1,00 | 0,00 | 0,00 | 0,00 | 0,02 |
| 15 | Virada en proa | 0,00 | 0,00 | 0,67 | 0,00 | 0,01 |

Detalle caso a caso (citas esperadas vs citadas, con `chunk_id` de origen): `retrieval_hits_detail.csv` y `retrieval_hits.json`. Tablas resumen: `results_comparison.md` / `results_comparison_por_caso.csv`.

### 5.2 Mejor y peor desempeño (referencia rápida)

- **Mejor alineación global (caso 5):** recuperación perfecta de regla y CALL, F1 RRS y F1 CALL = 1,0; ejemplo de pipeline funcionando cuando el léxico de la consulta coincide con fragmentos del Call Book.
- **Recuperación alta pero citas RRS nulas (casos 2, 10, 14):** el contexto trae material relevante (recall reglas = 1 en varios), pero el modelo no reproduce en la respuesta las reglas RRS esperadas (F1 RRS = 0).
- **Peor recuperación (casos 1, 3, 7, 11, 13, 15):** recall de reglas 0; el retriever léxico no coloca en el top-8 el fragmento que contiene la norma esperada.
- **Solo 5 de 15 casos** citan en la respuesta al menos una regla RRS del set esperado; **2 de 15** citan al menos un CALL esperado (análisis sobre `retrieval_hits.json`).

---

## 6. Análisis para el informe final

### 6.1 Desacople recuperación ↔ generación

Los resultados muestran que **recuperar** y **citar correctamente** son problemas distintos:

- En varios casos el recall de reglas o CALL es alto, pero el F1 de citas en la respuesta sigue bajo (p. ej. casos 2, 10, 14). El LLM recibe contexto en inglés y redacta en español técnico: puede razonar sin repetir el número de regla o el código CALL del golden set.
- En otros, ni siquiera llega la norma al contexto (recall 0), por lo que la generación no puede fundamentarse en el fragmento correcto (casos 1, 11, 13, 15).

Esto justifica evaluar **por separado** métricas de retrieval y de generación en comparaciones futuras.

### 6.2 Efecto del corpus sin PDF del RRS (véase §4.1)

El golden set fue definido con referencias normativas del Excel (reglas tipo RRS y TR CALL). En baseline **no hay índice del RRS**; solo Call Book y Case Book. Por eso los resultados «de reglas RRS» deben interpretarse como en §4.1, no como recuperación del reglamento oficial:

- **Recall de reglas al 41 % (media):** en menos de la mitad de los casos el número de regla esperado aparece en algún chunk de Call/Case; en el resto, la norma relevante no llega al contexto del LLM vía RAG.
- **F1 citas RRS al 22 % (media):** aunque a veces el contexto mencione reglas (casos 2, 10, 14), el informe en español **no siempre** repite el número de regla del golden set; en otros casos el modelo cita reglas no esperadas (espurias).
- **Recall CALL al 27 %:** los CALL solo se recuperan si el fragmento del Call Book contiene el código; el Case Book aporta poco para CALL.
- Ejemplo de desalineación CALL: caso 1 — esperado A3, citado E2 en la respuesta; contexto sin hit para A3.

**Implicación para mejoras de ingesta:** indexar el RRS (idealmente un chunk por regla) cambiará el significado operativo de «Recall reglas»: pasará a medir también recuperación del **texto reglamentario primario**. Hasta entonces, la baseline documenta el techo del sistema con interpretación vía Call/Case. Trocear Call por código CALL y/o tesauro ES↔EN pueden mejorar recall y F1 sin RRS, pero no sustituyen el reglamento completo.

### 6.3 Jaccard contexto muy bajo (0,03)

No indica ausencia de uso del RAG, sino **poca superposición léxica** entre respuesta en español y chunks en inglés. Para el informe conviene presentarlo como métrica complementaria, no como métrica principal de éxito.

### 6.4 Dictamen automático en 0 %

La métrica `verdict_accuracy` usa un matcher de texto sobre la sección de dictamen; las respuestas de Qwen siguen la plantilla de cuatro secciones pero no siempre reproducen la frase “Penalizar a X” del Excel. **Se recomienda revisión manual** de dictamen usando `report.json` (campo `answer`) frente a `expected.decision_text`, o ajustar el matcher en una iteración posterior.

### 6.5 Limitaciones del experimento

1. **Etiquetas automáticas** del output ideal (reglas con subíndices, CALL compuestos); revisables en `golden_set_review.md`.
2. **Retriever léxico** sin scores persistidos ni embeddings (no hay curvas de ranking por similitud semántica).
3. **Una sola corrida** por configuración (sin intervalos de confianza); la comparación antes/después se basará en el mismo golden set y mismas condiciones de LLM.
4. **Costo temporal:** ~13 minutos para 15 inferencias con Qwen 14B local.

### 6.6 Hipótesis a validar con mejoras de ingesta

| Hipótesis | Métrica principal a observar |
|-----------|------------------------------|
| Troceo por regla/caso mejora presencia de normas en contexto | ↑ Recall@k reglas y CALL |
| Índice RRS estructurado reduce citas incorrectas | ↑ F1 citas RRS, ↓ reglas espurias en `citations_in_answer` |
| Metadatos en chunk (Rule N, CALL X) mejoran match léxico | ↑ Recall en casos con recall baseline 0 |
| Tesauro / embeddings mejoran consultas en español | ↑ Recall sin cambiar troceo; posible ↑ F1 citas |

---

## 7. Protocolo de comparación con corridas futuras

Para que el informe final contraste de forma válida **baseline vs post-ingesta**:

1. **Congelar:** mismo `eval_set_snapshot.json`, mismo modelo (`qwen2.5:14b-instruct`), mismo idioma y estrategia de prompt, mismo `top_k`.
2. **Variar solo:** parámetros de ingesta y/o composición del corpus (documentar en `report.json` → `settings`).
3. **Ejecutar:** `python scripts/eval_run.py --label <nombre> --lang es --plots`.
4. **Comparar agregados:**

   ```bash
   python scripts/compare_eval_runs.py "eval/corrida baseline" eval/runs/<nueva_corrida>
   ```

5. **Reportar:** deltas en recall, F1 citas y, si aplica, gráficos de recall@k (desde `metrics_long.csv`).
6. **Retrieval detallado:** `python scripts/aggregate_retrieval_hits.py "<corrida>" --compare "eval/corrida baseline"` → `retrieval_hits_agg.csv` y `plots_retrieval/05_comparacion_corridas.png`.

---

## 8. Archivos de esta carpeta (trazabilidad)

| Archivo | Uso en el informe |
|---------|-------------------|
| `INFORME_CORRIDA_BASELINE.md` | Este resumen y análisis |
| `report.json` | Datos completos por caso (respuesta, chunks, métricas extendidas) |
| `results_comparison.md` | Tabla esperado vs métricas |
| `results_comparison_meta.csv` / `results_comparison_por_caso.csv` | Versión Excel de la comparación |
| `retrieval_hits.json` / `retrieval_hits_detail.csv` | Citas esperadas vs contexto vs respuesta; **origen del chunk** (Call/Case, nunca RRS) |
| `retrieval_hits_resumen_casos.csv` | Resumen por caso de aciertos en contexto y citas |
| `metrics_long.csv` / `chunks_summary.csv` | Gráficos adicionales |
| `eval_set_snapshot.json` | Golden set congelado |
| `plots/*.png` | Figuras métricas generales (recall, F1, Jaccard) |
| `plots_retrieval/*.png` | Figuras desde `retrieval_hits_detail.csv` (tasas, matriz, ranks) |
| `retrieval_hits_agg.csv` | Resumen numérico para comparar corridas |
| `summary.txt` | Resumen técnico corto |
| `DATA_MANIFEST.md` | Índice de datos disponibles |

---

## 9. Conclusión de la línea base

La configuración actual (**Call + Case, troceo por página 900/120, retrieval léxico, Qwen 14B, prompt ES-CoT**) ofrece un **rendimiento heterogéneo**: unos pocos casos alcanzan recuperación y citas casi perfectas (p. ej. caso 5), mientras en la mayoría falla la presencia de reglas en el contexto o su mención explícita en la respuesta.

**Punto explícito para el informe:** en esta corrida **no se ingestó el RRS**; las métricas denominadas «RRS» comparan contra **reglas de referencia del golden set** y su aparición en fragmentos de Call/Case o en la respuesta del modelo (§4.1). No deben presentarse como evaluación del reglamento indexado.

La línea base cuantifica ese punto de partida (**recall reglas 41 %, F1 citas RRS 22 %, F1 CALL 13 %**) y deja el material necesario para demostrar, en el informe final, si las mejoras de ingesta (incluido RRS en el índice) desplazan esas métricas de forma sistemática y con qué interpretación normativa corresponde cada variación.

---

*Documento generado para el Trabajo Final — Asistente de protestas en regatas (PoC DIIA). Actualizar solo si se re-ejecuta la corrida baseline con el mismo identificador o se documenta una nueva versión.*
