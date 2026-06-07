### 04. Arquitectura propuesta

Dos diagramas complementarios:

| Diagrama | Enfoque |
|----------|---------|
| [`arquitectura-rag.drawio`](arquitectura-rag.drawio) | **Flujo funcional** — capas offline / tiempo real / evaluación, actores y pipeline RAG de punta a punta. |
| [`arquitectura-tecnica.drawio`](arquitectura-tecnica.drawio) | **Arquitectura técnica** — módulos de `regatas_assistant`, puntos de entrada, datos en disco y servicio externo (Ollama). |

Ambos representan el perfil productivo validado en evaluación: retrieval **E11** (léxico, cupos 2+3+2+1) y respuesta **E13** (prompt v3 en español).

- Las secciones **Arquitectura funcional** y **Descripción de componentes (funcional)** describen [`arquitectura-rag.drawio`](arquitectura-rag.drawio).
- La sección **Arquitectura técnica** describe [`arquitectura-tecnica.drawio`](arquitectura-tecnica.drawio).

---

## Arquitectura funcional

### Agrupación en capas

El diagrama organiza la solución en **tres capas horizontales**, separadas por momento de ejecución y por responsabilidad. Esa partición refleja cómo se despliega y mantiene la PoC en la práctica.

| Capa | Nombre en el diagrama | Cuándo corre | Rol en la arquitectura |
|------|------------------------|--------------|-------------------------|
| **1** | Preparación del corpus (offline) | Antes del uso; al construir o actualizar el índice | Transforma fuentes normativas heterogéneas (PDF, CSV) en un corpus estructurado y carga el índice que alimentará el retrieval. Sin esta capa no hay contexto recuperable de calidad. |
| **2** | Consulta RAG en tiempo real | Cada vez que un usuario analiza una protesta | Orquesta el flujo completo: entrada del relato → recuperación → prompt → LLM → informe. Es el **camino productivo** de la aplicación (`app.py`). |
| **3** | Evaluación offline (golden set) | Tras cambios de código o configuración; no en producción | Reutiliza el mismo pipeline para medir retrieval y respuesta contra 15 casos de referencia. Garantiza que las mejoras de las capas 1 y 2 sean **cuantificables y regresionables**. |

**Relaciones entre capas**

- La capa 1 alimenta la 2 mediante el **índice en memoria** (flecha discontinua hacia `CorpusRetriever`): el retrieval no relee disco en cada consulta, sino la lista de `TextChunk` cargada al arranque.
- La capa 3 **invoca el mismo `ProtestPipeline`** que la capa 2 (flecha «mismo pipeline»): las métricas miden el sistema real, no un mock.
- Los **perfiles** (`profiles.py`) actúan sobre la capa 1 (qué corpus cargar) y, por extensión, sobre el comportamiento de la 2 y la 3.

Dentro de la capa 2, el recuadro **ProtestPipeline** agrupa los pasos internos del orquestador RAG como subcomponentes de un único servicio de dominio, en lugar de microservicios separados — coherente con el alcance de una PoC monolítica en Python.

---

### Descripción de componentes (funcional)

#### Capa 1 — Preparación del corpus (offline)

| Elemento | Objetivo | Por qué está en la arquitectura |
|----------|----------|----------------------------------|
| **Fuentes PDF** (Call Book, Case Book) | Conservar el material oficial en el formato en que lo publica World Sailing / WS. | Fue la línea base del proyecto (E0) y sigue disponible bajo perfil `baseline`. Aporta señales TR CALL y precedentes de caso cuando el índice los incluye. |
| **Fuentes estructuradas** (CSV reglas RRS, CSV definiciones) | Representar cada regla y definición como registro con metadatos (número, sección, referencias cruzadas). | El EDA mostró que el PDF del RRS no segmenta bien por regla; el CSV permite **un chunk por norma**, clave para subir recall de reglas (E10→E11). |
| **Pipeline de ingesta** (`build_corpus_processed.py`, `ensure_corpus_processed.py`) | Extraer, limpiar, segmentar y exportar JSONL tipados desde PDF y CSV. | Centraliza la lógica de transformación fuera del runtime. Permite regenerar el corpus sin reiniciar la app y deja trazabilidad reproducible. |
| **`corpus/processed/`** (JSONL: RRS · CALL · CASE · DEF, ~707 chunks) | Persistir el corpus listo para RAG con `doc_type`, `ref_id` y metadatos v2. | Artefacto estable entre ingesta y carga. El perfil `production` usa **solo** esta carpeta (`corpus=processed`), evitando la dilución del índice *full* observada en E3. |
| **`load_corpus_chunks()`** | Leer JSONL (y PDF si el perfil lo exige) y materializar objetos `TextChunk`. | Punto único de entrada al índice; aplica `Settings` (fuentes, chunking, perfil activo). |
| **Índice en memoria** (lista de `TextChunk`) | Mantener el corpus indexable en RAM al arranque de la aplicación. | El retriever léxico opera sobre esta lista; la primera carga puede tardar, pero las consultas siguientes son inmediatas. Adecuado para una PoC local. |
| **Perfiles** (`profiles.py`: `production`, `baseline`) | Fijar umbrales y defaults de corpus, cupos y prompt según corridas de evaluación. | Encapsula la configuración **E11+E13** sin hardcodear en cada script. Permite comparar contra E0 activando `REGATAS_PROFILE=baseline`. |

#### Capa 2 — Consulta RAG en tiempo real

| Elemento | Objetivo | Por qué está en la arquitectura |
|----------|----------|----------------------------------|
| **Usuario** (capitán, comisión, juez) | Actor que describe el incidente y consume el dictamen. | Define el caso de uso: relato en español, decisión esperada en lenguaje reglamentario. |
| **Interfaz Gradio** (`app.py`) | Capturar relato de protesta y protestado; mostrar informe y consola de actividad. | Interfaz mínima viable para demostrar la PoC sin desarrollar un frontend propio. Mismo backend que usa la evaluación. |
| **Componer consulta** | Unir relato del barco que protesta y del protestado en un único texto de búsqueda. | El retrieval necesita una consulta coherente; ambos relatos aportan términos para el match léxico. |
| **CorpusRetriever** (léxico, `top_k = 8`) | Rankear chunks por solapamiento de tokens con la consulta y devolver los 8 más relevantes. | Elegido tras E0–E17: simple, reproducible y suficiente con corpus en inglés y consulta en español cuando el índice JSONL aporta las reglas. El híbrido (E15–E17) queda opt-in, no productivo. |
| **Cupos por tipo** (2 RRS + 3 CALL + 2 CASE + 1 DEF) | Reservar slots del `top_k` para cada familia documental. | Evita que un tipo (p. ej. RRS) monopolice los 8 chunks. Configuración **E11**, validada frente a E10 y al índice *full*. |
| **Formatear contexto** (`format_chunks_for_prompt()`) | Serializar chunks con cabeceras (`[RRS — Regla …]`, `[TR CALL …]`) para el prompt. | El LLM necesita contexto legible y citas parseables; los metadatos JSONL v2 mejoran trazabilidad en la respuesta. |
| **Prompt v3 (ES)** (`prompts.py`, system + user, CoT) | Instruir al modelo: citar normas, razonar y cerrar con `Decisión:` en español. | Referencia **E13**: subió dictamen automático al 60 % manteniendo retrieval de E11. El formato fijo habilita métricas de citas. |
| **HTTPChatClient** | Abstraer la llamada al modelo vía API HTTP compatible con OpenAI. | Desacopla la PoC del proveedor; en local apunta a Ollama, en otros entornos podría ser otro host sin cambiar el pipeline. |
| **Ollama — Qwen 2.5 14B** | Ejecutar el LLM localmente (`/v1/chat`). | Modelo usado en todas las corridas completas del golden set; equilibrio calidad/latencia en hardware de desarrollo. |
| **Respuesta estructurada** | Entregar citas RRS/CALL/CASE, rationale y decisión. | Producto visible para el usuario y para las métricas (F1 citas, dictamen, Jaccard). |
| **Consola de actividad** | Registrar chunks recuperados y modelo invocado durante la consulta. | Transparencia operativa: permite auditar qué contexto recibió el LLM sin leer logs del servidor. |

#### Capa 3 — Evaluación offline (golden set)

| Elemento | Objetivo | Por qué está en la arquitectura |
|----------|----------|----------------------------------|
| **Golden set** (`eval/data/eval_set.json`, 15 casos) | Ground truth de reglas, CALL, dictamen y output ideal por incidente. | Ancla objetiva para comparar corridas E0–E17 y justificar decisiones de diseño con datos. |
| **`eval_run.py`** / `analyze_trace()` | Ejecutar el pipeline caso a caso, con o sin LLM (`--retrieval-only`). | Automatiza la evaluación repetible; el modo solo-retrieval aceleró el tuning de índice y cupos. |
| **Métricas** (R@k, F1 citas, Jaccard, dictamen) | Cuantificar recuperación y calidad de respuesta. | Traducen mejoras técnicas en indicadores interpretables (ver sección 05 del reporte). |
| **Artefactos de corrida** (`eval/runs/`, `report.json`, plots) | Persistir configuración, respuestas y gráficos por experimento. | Trazabilidad del trabajo de evaluación; base del diario de pruebas y de las comparativas del informe. |
| **Regresión** (`test_production_profile.py`, umbrales E11 + E13) | Fallar CI/local si una corrida cae por debajo de los pisos acordados. | Protege el perfil productivo ante cambios futuros en ingesta, retrieval o prompts. |

#### Notas del diagrama funcional

- **Paquete `regatas_assistant`**: la leyenda del diagrama indica los módulos que implementan la lógica (`config.py`, `ingestion.py`, `rag/retriever.py`, `prompts.py`, `llm/`, `profiles.py`). La arquitectura es **código-first**: los scripts (`app.py`, `eval_run.py`) son puntos de entrada delgados.
- **Retrieval híbrido** (nota al pie del diagrama): variante léxico+semántica evaluada en E15–E17; no forma parte del perfil por defecto porque no superó a E11+E13 en F1 ni dictamen.

### Lectura del flujo end-to-end

1. **Offline:** PDF y CSV → ingesta → JSONL en `corpus/processed/` → carga según perfil → índice en memoria.
2. **Consulta:** usuario → Gradio → `ProtestPipeline` → retrieval con cupos → prompt v3 → Ollama → informe estructurado.
3. **Validación:** golden set → mismo pipeline vía `eval_run.py` → métricas y regresión.

Esa secuencia es la que el diagrama funcional resume visualmente: preparar el conocimiento, recuperarlo bajo demanda, generar una respuesta auditable y medir que el conjunto sigue cumpliendo los objetivos del taller.

---

## Arquitectura técnica

El diagrama [`arquitectura-tecnica.drawio`](arquitectura-tecnica.drawio) abstrae actores y flujos de negocio para mostrar **cómo está organizado el código**, qué datos persiste en disco y qué servicio externo consume la PoC. La solución es un **monolito Python** desplegado en local: un único paquete (`regatas_assistant`) invocado por scripts delgados, sin base de datos ni cola de mensajes.

### Agrupación técnica

| Nivel | Contenido en el diagrama | Responsabilidad |
|-------|--------------------------|-----------------|
| **Puntos de entrada** | Scripts en la raíz del repo y en `scripts/` | Arrancan procesos concretos (UI, eval batch, build de corpus, regresión) sin duplicar lógica de dominio. |
| **`regatas_assistant`** | Módulos agrupados por preocupación técnica | Núcleo reutilizable: orquestación RAG, ingesta, retrieval, LLM, prompts y evaluación. |
| **Índice runtime** | `list[TextChunk]` en RAM (singleton del pipeline) | Estado compartido entre ingesta y retrieval en cada proceso. |
| **Capa de datos** | Carpetas en filesystem + variables de entorno | Persistencia y configuración; no hay ORM ni vector DB externa. |
| **Servicio externo** | Ollama vía HTTP | Única dependencia de red obligatoria en modo productivo con LLM real. |

### Puntos de entrada

| Módulo | Objetivo | Por qué está separado del paquete |
|--------|----------|-----------------------------------|
| **`app.py`** | Servir la UI Gradio y delegar cada consulta al pipeline. | Punto de despliegue de la demo; acopla solo presentación (widgets, streaming) al dominio. |
| **`scripts/eval_run.py`** | Ejecutar el golden set y escribir artefactos en `eval/runs/`. | CLI de experimentación; parametriza corridas (`--label`, `--retrieval-only`) sin tocar `app.py`. |
| **`scripts/build_corpus_processed.py`** | Generar JSONL desde CSV/PDF de forma offline. | La ingesta pesada no bloquea el arranque de la app; se corre bajo demanda o en CI. |
| **`scripts/regression_eval.py`** | Comparar una corrida contra umbrales E11/E13. | Automatiza la validación post-cambio; consume salida de `eval_run.py`. |

Todos **invocan** el paquete `regatas_assistant`; no reimplementan retrieval ni prompts.

### Módulos de `regatas_assistant`

#### Orquestación

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`pipeline.py`** | Clase `ProtestPipeline`: compone consulta, llama retriever, arma prompt, invoca LLM y devuelve respuesta (o traza para eval). | Único coordinador del flujo RAG; `analyze()` y `analyze_trace()` comparten la misma secuencia. |

#### Configuración

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`config.py`** | Dataclass `Settings` cargada desde `REGATAS_*` y `.env`. | Centraliza corpus, cupos, backend de embeddings, modelo LLM y timeouts. |
| **`profiles.py`** | Perfiles `production` y `baseline` con defaults y umbrales de regresión. | Evita dispersar magic numbers; fija E11+E13 como configuración por defecto. |

#### Ingesta

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`ingestion.py`** | `load_corpus_chunks()`, definición de `TextChunk`, lectura opcional de PDF. | Frontera entre disco y objetos en memoria; respeta `corpus_sources` del perfil activo. |
| **`corpus_processed.py`** | Parser de JSONL v2 en `corpus/processed/`. | Separa formato de archivo de la lógica de chunking PDF. |
| **`call_book_extract.py`** / **`case_book_extract.py`** | Transformar CSV intermedios en `calls.jsonl` y `cases.jsonl`. | Encapsulan reglas de extracción por fuente normativa. |

#### Retrieval (RAG)

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`rag/retriever.py`** | `CorpusRetriever`, cupos por `doc_type`, backends léxico/híbrido. | Núcleo de recuperación validado en E11; aísla ranking del resto del pipeline. |
| **`rag/embeddings_*.py`** | Implementaciones léxica, HTTP, local y híbrida (RRF). | Permite experimentar backends sin cambiar `pipeline.py`; productivo usa `lexical`. |
| **`chunk_metadata.py`** | Sufijos de metadatos en cabeceras de chunk para el prompt. | Unifica presentación de regla, sección y páginas en el contexto del LLM. |

#### LLM

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`llm/base.py`** | Interfaz `LLMClient`. | Desacopla pipeline del proveedor concreto. |
| **`llm/chat_http_client.py`** | Cliente HTTP compatible OpenAI → Ollama `/v1/chat`. | Implementación productiva local. |
| **`llm/stub.py`** | Respuestas fijas sin red. | Acelera tests y corridas `--retrieval-only` sin costo de inferencia. |

#### Prompts

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`prompts.py`** | Plantillas system/user v3 en español, estrategia CoT, normalización de idioma. | Toda la ingeniería de prompt vive en un solo módulo versionable (E13). |

#### Evaluación

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`eval/runner.py`** | Bucle sobre golden set, invoca `analyze_trace()`, serializa `report.json`. | Orquestador de eval separado del runtime interactivo. |
| **`eval/metrics.py`** | R@k, F1, Jaccard, dictamen por caso y agregados. | Métricas reproducibles, compartidas por regresión y diario de pruebas. |
| **`eval/refs.py`** | Extracción de citas y normalización de veredicto desde texto del LLM. | Parser alineado al formato v3; crítico para F1 y dictamen automático. |
| **`eval/golden.py`** | Carga y construcción de `eval_set.json`. | Aísla ground truth del Excel del resto del runner. |
| **`eval/faithfulness.py`** | Verificación claim-a-claim con LLM juez (opcional). | Complementa Jaccard; no bloquea el flujo productivo. |

#### Transversal

| Módulo | Objetivo | Por qué está en la arquitectura |
|--------|----------|----------------------------------|
| **`activity_console.py`** | Log en UI de chunks y modelo usados. | Observabilidad sin acoplar Gradio al pipeline. |
| **`ollama_models.py`** | Listado de modelos disponibles en Ollama. | Soporte a selector de modelo en `app.py`. |

### Índice runtime

El cilindro **Índice runtime** del diagrama representa `list[TextChunk]` materializada al instanciar `ProtestPipeline.from_settings()`. La ingesta lo **puebla** una vez por proceso; el retriever lo **consulta** en cada `retrieve()` sin I/O adicional. Ese diseño es deliberado para la PoC local: simple, predecible y suficiente para ~707 chunks; un despliegue a escala requeriría vector store o caché en disco.

### Capa de datos (filesystem)

| Ruta / config | Contenido | Uso en la arquitectura |
|---------------|-----------|-------------------------|
| **`corpus/`** | PDF Call Book y Case Book | Perfil `baseline` y etapas tempranas; fuente de extractores CSV. |
| **`corpus/processed/`** | JSONL `rrs`, `calls`, `cases`, `definitions` | Corpus productivo (`corpus=processed`); escrito por build, leído por `ingestion.py`. |
| **`eval/data/`** | `eval_set.json` | Golden set fijo para todas las corridas E0–E17. |
| **`eval/runs/`** | `report.json`, CSV, plots por corrida | Salida inmutable de cada experimento. |
| **`.env` / `REGATAS_*`** | API URL, modelo, perfil, cupos, backends | Configuración sin recompilar; mismo mecanismo en app, eval y scripts. |

Las flechas **I/O** del diagrama marcan lectura/escritura de ingesta y evaluación sobre estas rutas; el pipeline en consulta no escribe en disco.

### Servicio externo

**Ollama** expone una API HTTP `/v1/chat` compatible con clientes OpenAI. `HTTPChatClient` envía system + user prompt y recibe el informe en streaming o bloque. Es externo al repositorio: la PoC asume que el daemon corre en `127.0.0.1:11434` con el modelo `qwen2.5:14b-instruct` descargado. Cambiar de proveedor implica solo ajustar URL y modelo en `Settings`, no reescribir `pipeline.py`.

### Dependencias entre módulos

El diagrama técnico resume estas relaciones (flechas sólidas = llamada directa; discontinuas = configuración, traza o I/O):

```text
app.py / eval_run.py / build_*  →  regatas_assistant
pipeline.py  →  config (settings) · rag/retriever · prompts · llm
eval/runner  →  pipeline.analyze_trace()  →  eval/metrics + eval/refs
ingestion    →  corpus/processed/  →  índice runtime
rag/retriever  →  índice runtime (retrieve)
llm/chat_http_client  →  Ollama (HTTP)
```

**Cadena productiva:** `Settings` + `profiles` definen el perfil → `ingestion` carga chunks → `retriever` selecciona top-8 con cupos → `prompts` formatea → `HTTPChatClient` genera respuesta. La evaluación reutiliza exactamente esa cadena y añade scoring sobre el golden set.
