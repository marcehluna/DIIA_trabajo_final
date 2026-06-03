# Reconstrucción del RAG — fase 1 (solo RRS desde CSV)

Objetivo: **índice nuevo** construido únicamente con material derivado del reglamento:

- `scripts/rrs_reglas_2025_2028.csv` → `corpus/processed/rrs_rules.jsonl`
- `scripts/definitions.csv` → `corpus/processed/definitions.jsonl`

**Sin** Call Book ni Case Book en esta fase. Se incorporarán después con el mismo patrón (pre-proceso → JSONL → `REGATAS_CORPUS_SOURCES=full`).

## Pasos

### 1. Generar artefactos

```bash
python scripts/build_corpus_processed.py
# o todo-en-uno con verificación:
python scripts/rebuild_rag_rrs_only.py
```

### 2. Activar modo solo-RRS

```bash
export REGATAS_CORPUS_SOURCES=processed
export REGATAS_CORPUS_FILES=
export REGATAS_LOAD_PROCESSED=1
```

| Variable | Valor fase 1 | Efecto |
|----------|----------------|--------|
| `REGATAS_CORPUS_SOURCES` | `processed` | Solo JSONL (RRS + definiciones) |
| `REGATAS_CORPUS_FILES` | vacío | No carga PDFs aunque existan en `corpus/` |
| `REGATAS_LOAD_PROCESSED` | `1` | Lee `corpus/processed/*.jsonl` |

### 3. Probar carga

```bash
python scripts/rebuild_rag_rrs_only.py
# Esperado: ~469 rrs + ~26 definition = ~495 chunks, pdf = 0
```

### 4. Evaluación (cuando corresponda)

```bash
REGATAS_CORPUS_SOURCES=processed REGATAS_CORPUS_FILES= \
  REGATAS_LLM_BACKEND=http REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
  python scripts/eval_run.py --label rrs_only --lang es --plots
```

Comparar contra `eval/corrida baseline/` interpretando que el baseline tenía Call+Case y **esta fase solo RRS** — las métricas de CALL bajarán por diseño hasta integrar Call/Case en fase 2.

## Modos de corpus (`REGATAS_CORPUS_SOURCES`)

| Modo | Contenido del índice |
|------|----------------------|
| `processed` | Solo JSONL (RRS + definiciones) — **fase 1** |
| `pdf` | Solo PDFs (`REGATAS_CORPUS_FILES`) — equivalente baseline sin RRS |
| `full` | JSONL + PDFs — corrida `ingesta_rrs_jsonl` anterior |

## Retrieval por cupos

Con `REGATAS_RETRIEVAL_QUOTAS=1`, el retriever toma hasta `QUOTA_PROCESSED` chunks del pool RRS/definiciones y hasta `QUOTA_PDF` del pool PDF (por defecto mitad y mitad de `REGATAS_TOP_K`).

```bash
export REGATAS_RETRIEVAL_QUOTAS=1
export REGATAS_RETRIEVAL_QUOTA_PROCESSED=4   # opcional
export REGATAS_RETRIEVAL_QUOTA_PDF=4         # opcional (solo con full)
```

## Corpus pre-procesado (CSV → JSONL)

| Fuente | Script extracción | CSV revisable | JSONL |
|--------|-------------------|---------------|-------|
| RRS | (manual / existente) | `scripts/rrs_reglas_2025_2028.csv` | `rrs_rules.jsonl` |
| Definiciones | — | `scripts/definitions.csv` | `definitions.jsonl` |
| Call Book TR | `scripts/extract_call_book_csv.py` | `scripts/call_book_calls.csv` | `calls.jsonl` |
| WS Case Book | `scripts/extract_case_book_csv.py` | `scripts/case_book_cases.csv` | `cases.jsonl` |

```bash
python scripts/extract_call_book_csv.py    # --force para regenerar
python scripts/extract_case_book_csv.py    # --force para regenerar
python scripts/build_corpus_processed.py
```

Índice solo JSONL (sin PDFs):

```bash
export REGATAS_CORPUS_SOURCES=processed
export REGATAS_CORPUS_FILES=
```

Chunks: `rrs|16.1`, `call|A3`, `case|79`, etc.

### Perfil productivo (E11 — defecto en la app)

Sin variables, `REGATAS_PROFILE=production` carga solo `processed` y cupos **2+3+2+1**. Ver `docs/PERFIL_PRODUCTIVO.md`.

```bash
python scripts/ensure_corpus_processed.py --build
# REGATAS_PROFILE=production  # implícito
```

### Cupos por tipo de documento (E10/E11)

Con índice solo `processed`, usar cupos por `doc_type` para evitar que 469 reglas ahoguen calls/cases:

```bash
export REGATAS_RETRIEVAL_QUOTAS=1
export REGATAS_RETRIEVAL_QUOTA_BY_DOCTYPE=1
export REGATAS_RETRIEVAL_QUOTA_RRS=2   # E11 (E10 usaba 3)
export REGATAS_RETRIEVAL_QUOTA_CALL=3  # E11 (E10 usaba 2)
export REGATAS_RETRIEVAL_QUOTA_CASE=2
export REGATAS_RETRIEVAL_QUOTA_DEFINITION=1
```

### Recuperación híbrica (léxica + semántica)

Compatible con cupos: `REGATAS_EMBEDDING_BACKEND=hybrid` fusiona rankings con RRF; la rama semántica es `local` u `http` (`REGATAS_HYBRID_SEMANTIC_BACKEND`). Validar con `eval_run` — las métricas E11 referencia usan léxico.

## Fases previstas

1. **Solo RRS** (este documento) — validar retrieval y citas de reglas sin dilución Call/Case.
2. **RRS + Call JSONL + Case PDF** — cupos 3+5 (E7) u otros.
3. **Persistencia** del índice en disco (EPIC persistencia RAG).

## Referencia git

- Baseline Call+Case: tag `v0.1.0-baseline`
- Ingesta mixta (RRS+PDF): commit con `corpus/processed/` y modo `full` por defecto
