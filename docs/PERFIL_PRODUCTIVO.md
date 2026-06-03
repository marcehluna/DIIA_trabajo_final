# Perfil productivo RAG (post-eval E11)

Configuración por defecto de la PoC tras las corridas E0–E11. La línea base histórica (E0, solo PDF) sigue disponible con `REGATAS_PROFILE=baseline`.

## Perfil `production` (defecto)

| Parámetro | Valor | Origen eval |
|-----------|--------|-------------|
| Corpus | `processed` — JSONL ~707 ch. | E8–E11 |
| Cupos retrieval | **2+3+2+1** (RRS / CALL / CASE / DEF) | **E11** |
| Embeddings | `lexical` (léxico) | Corridas E0–E11 |
| LLM | Qwen ES (`cot`) | E0/E11 |

Sin variables de entorno, `Settings.from_env()` aplica este perfil.

### Arranque recomendado

```bash
# 1. Corpus JSONL
python scripts/ensure_corpus_processed.py --build

# 2. App o eval (perfil production implícito)
REGATAS_LLM_BACKEND=http REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
  REGATAS_SYSTEM_PROMPT_LANG=es \
  python app.py
```

### Regresión (umbrales E11)

Tras cambiar ingesta o retrieval:

```bash
python scripts/eval_run.py --label regression --lang es
python scripts/regression_eval.py eval/runs/<run_id>
```

Umbrales en `regatas_assistant/profiles.py` (R@k reglas ≥ 0.70, R@k CALL ≥ 0.18, F1 RRS ≥ 0.18).

## Recuperación híbrida (léxica + semántica)

**Compatible con cupos por `doc_type`:** los cupos envuelven el retriever interno; en modo `hybrid` cada pool usa RRF (léxico + semántica) antes de fusionar por cupo.

```bash
export REGATAS_EMBEDDING_BACKEND=hybrid
export REGATAS_HYBRID_SEMANTIC_BACKEND=local   # o http (requiere API key)
# opcional: REGATAS_HYBRID_RRF_K=60
```

Mantener cupos de producción:

```bash
export REGATAS_RETRIEVAL_QUOTAS=1
export REGATAS_RETRIEVAL_QUOTA_BY_DOCTYPE=1
# cupos 2+3+2+1 ya vienen con REGATAS_PROFILE=production
```

Validar con `eval_run` antes de dar por cerrado el cambio a híbrido (las métricas E11 son con léxico).

## Prompting (v2, alineado a JSONL)

Los system/user prompts en `regatas_assistant/prompts.py` exigen:

- Citas con **Regla**, **TR CALL**, **Case** según encabezados del contexto recuperado.
- Cierre con **`Decisión: …`** (formato del golden set).
- Solo normas presentes en los fragmentos recuperados.

Tras cambiar prompts, conviene una corrida eval de regresión (F1 citas, dictamen).

**Metadatos en contexto (JSONL v2):** los encabezados de cada fragmento pueden incluir `Sección:`, `Reglas:` (vinculadas) y `pp.` (PDF). Regenerar con `python scripts/build_corpus_processed.py`. Ver `corpus/processed/README.md`.

## Otros perfiles

| `REGATAS_PROFILE` | Uso |
|-------------------|-----|
| `production` | JSONL + cupos E11 (defecto) |
| `baseline` | Solo PDF Call+Case, sin cupos (E0) |
| `legacy` | `full` JSONL+PDF sin cupos (E3) |

Cualquier variable `REGATAS_*` explícita **sobreescribe** el perfil.

## Referencias

- Ingesta: `docs/RAG_RECONSTRUCCION_RRS.md`, `corpus/processed/README.md`
- Eval: `eval/DIARIO_PRUEBAS.md`, corrida E11 `eval/runs/20260526_185624_processed_cupos_2_3_2_1/`
- Timeline: `eval/docs/timeline_corridas_eval.html`
- Informe final: `docs/REGISTRO_TRABAJO_INFORME_FINAL.md`
