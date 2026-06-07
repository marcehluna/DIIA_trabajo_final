### 03. EDA y descubrimientos

Análisis exploratorio del corpus normativo en `corpus/` (tres PDF oficiales: RRS, Call Book y Case Book) realizado **antes** de fijar ingesta, chunking y retrieval. Los gráficos y tablas detalladas están en [`Metricas.docx`](Metricas.docx); esta sección resume las **métricas exploradas**, qué miden y **para qué decisiones** sirvieron.

**Corpus analizado**

| Documento | Páginas | Caracteres (pdfplumber) |
|-----------|---------|-------------------------|
| RRS 2025–2028 | 160 | ~233 000 |
| Call Book Team Racing | 111 | ~121 000 |
| Case Book WS 2025–2028 | 328 | ~428 500 |

En conjunto: **~599 páginas** y **~782 000 caracteres**. El Case Book concentra más del 55 % del volumen.

---

## Métricas de volumen y forma del texto

### Longitud por página (caracteres + KDE)

**Qué mide:** distribución de `len(texto)` por página en cada PDF (histograma de densidad + curva KDE).

**Utilidad:** los tres libros tienen perfiles muy distintos — páginas cortas con tablas y señales en el RRS frente a bloques largos de casos en el Case Book. Confirmó que **no existe un único tamaño de chunk óptimo** para todo el corpus en bruto y que el troceo debe respetar la unidad normativa (regla, TR CALL, case), no solo la geometría de la página.

### Páginas por tipo de documento

**Qué mide:** conteo de páginas y reparto relativo entre RRS, Call y Case.

**Utilidad:** cuantifica el peso de cada fuente en el índice. Explica por qué, sin cupos, un ranking global favorece el volumen del Case Book y diluye señales del Call Book — hallazgo que luego se observó en la corrida E3.

### Caracteres por bloques de 10 páginas (pypdf vs pdfplumber limpio)

**Qué mide:** suma de caracteres en ventanas de 10 páginas, comparando extracción **pypdf** (crudo) frente a **pdfplumber** con la misma limpieza que `regatas_assistant/ingestion.py` (espacios colapsados, `strip`, retirada de referencias bibliográficas tipo `GBR 1962/25`).

**Utilidad:** valida que el pipeline de producción **reduce ruido sin recortar cuerpo normativo** de forma agresiva y justifica alinear el EDA con el código de ingesta real, no con un extractor arbitrario.

---

## Métricas léxicas y de idioma

### Stop words (inglés) por documento

**Qué mide:** porcentaje de tokens alfabéticos (`[A-Za-z]+`) que pertenecen a `regatas_assistant/stopwords_en.txt` (lista reelaborada desde scikit-learn, conservando términos normativos como `call`, `must`, `may`).

**Resultado orientativo:** ~**44–49 %** de stopwords según documento (RRS ~47 %, Call ~44 %, Case ~49 %).

**Utilidad:** confirma que el corpus está en **inglés** mientras los relatos de protesta son en **español**. Anticipó el desafío ES→EN del retrieval léxico y motivó, más adelante, el experimento E14 (salida en inglés) y el fallback semántico del híbrido E16 — sin sustituir el índice JSONL como solución principal.

### Frecuencia de términos por documento (sin stopwords)

**Qué mide:** tokens léxicos (3+ letras, misma regex que el retriever) más frecuentes por PDF, excluyendo stopwords.

**Utilidad:** revela el vocabulario dominante de cada libro (señales, procedimientos, casos) y ayuda a interpretar por qué ciertas consultas en español aún recuperan fragmentos útiles cuando el índice incluye `referenced_rules` y encabezados estructurados en JSONL.

---

## Métricas de contexto y tokenización (Qwen)

Todas usan el tokenizer de **`Qwen/Qwen2.5-14B-Instruct`** (misma familia que el LLM de evaluación), contando tokens **sin** tokens especiales — coherente con estimar chunking y embeddings.

### Cobertura con ventana de 512 tokens

**Qué mide:**

- Tokens totales por documento completo.
- **% del documento que cabe en una sola ventana de 512 tokens** (= `min(512, T) / T`).
- % de páginas individuales con ≤512 tokens.

**Resultados orientativos:** casi todas las **páginas** entran en 512 tokens (RRS 99,4 %, Call 97,3 %, Case 90,5 %), pero el **documento entero** solo ocupa 0,5–1,6 % en una ventana — el resto exige chunking obligatorio.

**Utilidad:** dimensiona el problema RAG: el límite no es una página aislada sino el **libro completo**. Justifica `top_k=8` y la necesidad de un índice fragmentado en lugar de pasar PDFs enteros al LLM.

### Brecha producción (caracteres) vs tokenizer (tokens)

**Qué mide:** sobre chunks reales de `load_corpus_chunks()` con defaults de producción (**900 caracteres / 120 solapamiento**, troceo por página), calcula p50/p90/p95 de tokens Qwen, % de chunks >512 tokens y ratio caracteres→tokens (~0,24 tok/char).

**Resultados (índice solo-PDF, ~1 247 chunks):**

| PDF | Chunks | p50 tok | p90 tok | % chunks >512 |
|-----|--------|---------|---------|---------------|
| RRS | 353 | 194 | 229 | 0 % |
| Call Book | 200 | 198 | 241 | 0,5 % |
| Case Book | 694 | 193 | 225 | 0 % |
| **Global** | **1 247** | **193** | **231** | **0,1 %** |

**Utilidad:** muestra que el chunking por página en caracteres **casi nunca trunca** embeddings a 512 tokens; el problema de calidad RAG no es longitud sino **granularidad semántica** (varias normas o un caso entero en un mismo fragmento).

---

## Métricas de segmentación y estructura normativa

### Ventana deslizante en tokens (512 / solape 128)

**Qué mide:** chunks sintéticos por ventana de 512 tokens con stride 384 sobre texto limpio; distribución de longitudes (p50/p90/p95), cantidad de chunks y **% de redundancia por solapamiento** en el índice.

**Hallazgo:** con ventana fija, p50 = p90 = p95 = **512** en los tres PDF — muchos chunks pegados al techo, sin alineación a reglas o calls.

**Utilidad:** demuestra que trocear “a ciegas” por tokens **no preserva unidades citables**. Refuerza la decisión de pasar a JSONL con **un registro por regla / call / case** en lugar de optimizar solo `chunk_size`.

### Delimitadores de dominio (`Rule n`, `CASE n`)

**Qué mide:** conteo de patrones regex `Rule \d+` y `CASE \d+` en el texto limpio de cada PDF.

**Utilidad:** cuantifica cuánta estructura normativa es **detectable pero no explotable** en PDF plano; respalda la ingesta estructurada desde CSV donde cada `ref_id` es explícito.

---

## Métricas de calidad de extracción PDF

### Páginas pobres, caracteres problemáticos y artefactos

**Qué mide (texto bruto pdfplumber):**

| Métrica | Interpretación |
|---------|----------------|
| **% páginas casi vacías** (<50 caracteres) | Fallos de OCR, páginas gráficas o extracción pobre |
| **% U+FFFD** | Carácter de reemplazo Unicode — PDF dañado o fuente incorrecta |
| **% controles ASCII** | Basura de codificación |
| **Guiones de línea /10k chars** | Palabras partidas por salto de línea en el PDF |
| **% líneas muy cortas** | Fragmentación por columnas o encabezados |

**Resultados:**

| Documento | % pág. vacías | % U+FFFD | Guion+NL /10k |
|-----------|---------------|----------|---------------|
| RRS | 2,50 | 0 | 0,60 |
| Call Book | 0,90 | 0 | 0,66 |
| Case Book | 7,32 | 0 | 0,86 |

**Utilidad:** la extracción es **usable** (sin U+FFFD masivo); el Case Book tiene más páginas pobres, coherente con su mezcla de diagramas y casos. La limpieza de guiones y espacios en `ingestion.py` queda justificada, pero no se detectó necesidad de descartar fuentes enteras.

---

## Métricas orientadas al retrieval

### Cobertura para recuperación híbrida

**Qué mide** sobre chunks de producción (`load_corpus_chunks`, 900/120):

1. **Riqueza léxica por fragmento** — cantidad de términos léxicos (3+ letras) por chunk; vocabulario global del índice (~**4 164** términos distintos en ~1 247 chunks).
2. **Distribución de longitud léxica** por PDF de origen.
3. **Proxy de embeddings** — tokens Qwen por chunk respecto del techo 512.

**Utilidad:** caracteriza el índice desde la óptica del **LexicalRetriever** (solapamiento de tokens) y del encoder semántico. Permitió anticipar que el léxico es viable con vocabulario acotado y chunks homogéneos (~190–230 tokens), y documentó la base del experimento híbrido E15–E17 — que no superó al léxico puro en productivo.

---

## Síntesis: del EDA a las decisiones del proyecto

| Hallazgo del EDA | Decisión posterior |
|------------------|-------------------|
| PDF no alinea chunks con reglas/calls/cases | Corpus **JSONL** tipado (`corpus/processed/`, ~707 unidades) |
| Volumen y heterogeneidad entre libros | **Cupos por `doc_type`** (2+3+2+1, E11) |
| Chunks en caracteres no truncan embeddings | Mantener **900/120** para PDF residual; priorizar JSONL por unidad normativa |
| Corpus EN vs consulta ES | Retrieval **léxico** + evaluación sistemática; híbrido opt-in |
| Extracción PDF aceptable | Reutilizar **pdfplumber/pypdf** con limpieza de `ingestion.py` |

El EDA no reemplazó la evaluación con golden set (sección 05 del reporte), pero **redujo el espacio de búsqueda**: mostró que mejorar RAG en protestas náuticas pasaba menos por afinar un número mágico de `chunk_size` y más por **estructurar el corpus** y **equilibrar qué entra en el `top_k`**.

Para el detalle gráfico de cada métrica, ver [`Metricas.docx`](Metricas.docx). Las implicaciones en el diseño del sistema se desarrollan en [justificación de la solución](../02-justificacion-de-la-solucion/justificacion-de-la-solucion.md#eda-del-corpus-normativo).
