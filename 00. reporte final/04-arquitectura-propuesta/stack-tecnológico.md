### Stack tecnológico

Inventario de tecnologías de la PoC de protestas náuticas, separado en **camino productivo** (perfil E11 + E13) y **evaluación de resultados** (golden set, métricas y regresión). Las versiones de librerías Python provienen de [`requirements.txt`](../../requirements.txt); las de modelos y servicios, de [`.env.example`](../../.env.example) y [`docs/PERFIL_PRODUCTIVO.md`](../../docs/PERFIL_PRODUCTIVO.md).

---

## Stack productivo (E11 + E13)

Componentes que intervienen en el despliegue y uso de la PoC: preparación del corpus, consulta RAG en tiempo real (`app.py`) y generación del informe.

| Componente | Tecnología | Versión | Rol |
|------------|------------|---------|-----|
| Lenguaje | Python | 3.x | Runtime del paquete `regatas_assistant` y scripts de ingesta. |
| Paquete de dominio | `regatas_assistant` | PoC (repo) | Núcleo RAG: ingesta, retrieval, prompts, LLM y orquestación (`pipeline.py`). |
| Interfaz de usuario | Gradio | ≥ 4.44.0 | UI web para ingresar el relato de protesta y mostrar el informe (`app.py`). |
| Modelo de lenguaje | Qwen2.5 Instruct | `qwen2.5:14b-instruct` | Generación del informe estructurado (CoT, español) a partir del contexto recuperado. |
| Servidor LLM local | Ollama | — | Servicio HTTP en `http://127.0.0.1:11434`; API compatible con OpenAI Chat Completions. |
| Cliente HTTP LLM | `openai` (SDK Python) | ≥ 1.40.0 | Cliente que invoca `/v1/chat` de Ollama; desacopla el pipeline del proveedor concreto. |
| Estrategia de prompting | CoT + plantilla v3 | E13 (`prompts.py`) | System/user prompts fijos: viñetas de citas, secciones `##` y línea `Decisión:` al final. |
| Retrieval | Índice léxico (BM25-like) | E11 | Ranking por relevancia léxica sobre chunks en RAM; `top_k=8`. |
| Cupos por tipo de documento | Política de cuotas | 2+3+2+1 | Distribución fija: RRS / TR CALL / Case / definiciones en cada consulta. |
| Backend de embeddings | Léxico | `lexical` | Backend por defecto; sin vector DB externa ni embeddings densos. |
| Persistencia del corpus | JSONL v2 | ~707 chunks | Archivos en `corpus/processed/` (`rrs.jsonl`, `calls.jsonl`, `cases.jsonl`, definiciones). |
| Extracción PDF (ingesta offline) | pdfplumber | ≥ 0.11.0 | Lectura y extracción de texto desde PDF normativos al construir el índice. |
| Extracción PDF (respaldo) | pypdf | ≥ 4.0.0 | Lectura alternativa de PDF en ingesta offline. |
| Build de corpus | `scripts/build_corpus_processed.py` | — | Genera JSONL desde CSV/PDF; no corre en cada consulta del usuario. |
| Configuración | Variables `REGATAS_*` + `.env` | perfil `production` | Centraliza corpus, cupos, modelo LLM, idioma y backends (`config.py`, `profiles.py`). |
| Índice en runtime | `list[TextChunk]` en memoria | singleton | Estado compartido entre ingesta y retrieval; sin base de datos ni almacén vectorial. |

---

## Stack de evaluación de resultados

Componentes usados **solo** para medir, comparar y validar el sistema contra el golden set; no participan en la consulta interactiva de `app.py`.

| Componente | Tecnología | Versión | Rol |
|------------|------------|---------|-----|
| Golden set | `eval/data/eval_set.json` | 15 casos | Ground truth: relatos, reglas, TR CALL, casos, dictamen y output ideal. |
| Fuente del golden set | Excel *Casos de Regatas* | — | Origen manual de etiquetas; convertido a JSON con `scripts/build_eval_set.py`. |
| Construcción del golden set | pandas + openpyxl | ≥ 2.0.0 / ≥ 3.1.0 | Lectura del Excel y serialización a `eval_set.json` (`regatas_assistant/eval/golden.py`). |
| Corrida batch | `scripts/eval_run.py` | — | Ejecuta el pipeline sobre los 15 casos y escribe artefactos en `eval/runs/`. |
| Módulos de evaluación | `regatas_assistant/eval/*` | — | Runner, métricas (R@k, F1, Jaccard), parser de citas y dictamen (`refs.py`, `metrics.py`). |
| Regresión automática | `scripts/regression_eval.py` | umbrales E11+E13 | Compara una corrida contra pisos mínimos de retrieval y respuesta. |
| Re-score de citas | `scripts/rescore_eval_citations.py` | — | Recalcula F1 de citas con el parser vigente sin re-inferir el LLM. |
| Comparación entre corridas | `scripts/compare_eval_runs.py` | — | Tablas delta entre dos carpetas de `eval/runs/`. |
| Agregación retrieval | `scripts/aggregate_retrieval_hits.py` | — | Resumen de hits por tipo de documento y por caso. |
| Gráficos de métricas | Matplotlib + `scripts/plot_eval_run.py` | ≥ 3.7.0 | PNG por corrida (recall, F1, Jaccard, heatmaps) bajo `eval/runs/<id>/plots/`. |
| Tablas de revisión | `build_eval_results_table.py`, `build_eval_review_table.py` | — | Markdown comparativo esperado vs obtenido para el informe. |
| Diario de experimentos | `eval/DIARIO_PRUEBAS.md` + `update_diario_pruebas.py` | E0–E17 | Registro narrativo de cada corrida y delta vs anterior. |
| Faithfulness (opcional) | `scripts/score_faithfulness.py` | — | Verificación claim-a-claim con LLM juez; complementa Jaccard, no bloquea producción. |
| Retrieval híbrido (experimento) | `sentence-transformers` + RRF | ≥ 2.2.0 | Backend probado en E15–E17; evaluado con `eval_run`, no adoptado en productivo. |
| Análisis numérico | NumPy | ≥ 1.24.0 | Cálculo de métricas agregadas y estadísticas en reportes de eval. |

---

## Notas

- **Ollama** y **Qwen2.5** no figuran en `requirements.txt`: se instalan por separado; la versión del modelo se fija con `REGATAS_LLM_MODEL`. El mismo modelo se usa en productivo y en eval (inferencia real en corridas completas).
- **Herramientas de EDA e ingesta exploratoria** (spaCy, `transformers`, tiktoken, SciPy/KDE en notebooks) apoyaron el diseño del corpus y el chunking, pero no forman parte ni del runtime productivo ni del pipeline de evaluación batch.
- El perfil **`baseline`** (E0) se evalúa con el mismo stack de evaluación, pero su corpus (solo PDF Call+Case, sin cupos) es una línea base histórica, no el productivo actual.
