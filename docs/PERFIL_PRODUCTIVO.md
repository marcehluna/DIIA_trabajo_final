# Perfil productivo RAG (E11 retrieval + E13 respuesta)

Configuración por defecto de la PoC tras las corridas E0–E13. **Retrieval** validado en **E11** (cupos 2+3+2+1); **prompt y formato de respuesta** en **E13** (v3). La línea base histórica (E0, solo PDF) sigue disponible con `REGATAS_PROFILE=baseline`.

Resumen narrativo de corridas: [`eval/RESUMEN_CORRIDAS_EVAL.md`](../eval/RESUMEN_CORRIDAS_EVAL.md).

## Perfil `production` (defecto)

| Parámetro | Valor | Origen eval |
|-----------|--------|-------------|
| Corpus | `processed` — JSONL ~707 ch. | E8–E11 |
| Cupos retrieval | **2+3+2+1** (RRS / CALL / CASE / DEF) | **E11** |
| Embeddings | `lexical` (léxico) | Corridas E0–E11 |
| LLM | Qwen ES (`cot`) | E0/E11/E13 |
| Prompt | v3 (plantilla fija, viñetas, `Decisión:`) | **E13** (código en `prompts.py`) |

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

### Regresión (umbrales E11 + E13)

Tras cambiar ingesta, retrieval, prompts o parser de citas:

```bash
python scripts/eval_run.py --label regression --lang es
python scripts/rescore_eval_citations.py eval/runs/<run_id>   # F1 citas con parser actual
python scripts/regression_eval.py eval/runs/<run_id>
# solo cambios de índice/cupos (corrida tipo E11, sin prompt v3):
python scripts/regression_eval.py eval/runs/<run_id> --mode retrieval
```

Umbrales en `regatas_assistant/profiles.py`:

| Grupo | Métrica | Piso | Referencia eval |
|-------|---------|------|-----------------|
| Retrieval | R@k reglas | ≥ 0.70 | E11 |
| Retrieval | R@k CALL | ≥ 0.18 | E11 |
| Respuesta | F1 RRS | ≥ 0.18 | E13 |
| Respuesta | F1 CALL | ≥ 0.06 | E13 |
| Respuesta | Dictamen | ≥ 0.50 | E13 |

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

## Prompting (v3, alineado a JSONL y métricas eval)

`regatas_assistant/prompts.py` (CoT y Few-Shot):

- **Plantilla fija** al final del mensaje de usuario (cuatro `##` exactos).
- §2: viñetas `- **Regla X.Y** —`, `- **TR CALL C** —`, `- **Case N** —`.
- §4: **`## 4. Resolución de la protesta`**; última línea `Decisión: Penalizar a X.` / etc.
- Encabezados JSONL v2 (`Reglas:` en `[TR CALL …]`).

Corrida sugerida: `python scripts/eval_run.py --label prompt_v3_format --lang es --plots` (retrieval = E11).

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
- Eval: `eval/RESUMEN_CORRIDAS_EVAL.md`, `eval/DIARIO_PRUEBAS.md`
- Corridas ref.: E11 `eval/runs/20260526_185624_processed_cupos_2_3_2_1/`, E13 `eval/runs/20260604_124747_prompt_v3_format/`
- Timeline: `eval/docs/timeline_corridas_eval.html`
- Informe final: `docs/REGISTRO_TRABAJO_INFORME_FINAL.md`
