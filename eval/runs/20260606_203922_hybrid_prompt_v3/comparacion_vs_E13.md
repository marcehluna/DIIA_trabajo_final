# Comparación — `hybrid_prompt_v3` (E17)

**Run ID:** `20260606_203922_hybrid_prompt_v3`

## Qué cambió respecto a E13

- **embedding_backend:** `lexical` → `hybrid` (RRF léxico + semántica local; fallback semántico si consulta ES sin overlap)
- **Prompt / LLM:** igual que E13 (prompt v3, Qwen ES, cupos E11)

## Comparativa vs E13 (`prompt_v3_format`)

| Métrica | E13 | E17 | Δ (E17 − E13) | Lectura |
|---------|-----|-----|---------------|---------|
| R@k reglas | 0.76 | 0.76 | 0.00 | Retrieval agregado igual |
| R@k CALL | 0.20 | 0.20 | 0.00 | Idem |
| **F1 RRS** | 0.22 | **0.13** | **−0.09** | Peor trazabilidad de citas |
| F1 CALL | 0.07 | 0.07 | 0.00 | Sin cambio |
| Jaccard resp ↔ referencia | 0.16 | 0.16 | ~0 | Similar |
| **Dictamen auto** | **60%** | **47%** | **−13 pp** | No pasa umbral regresión (50%) |

### Casos con cambio relevante

| Caso | E13 → E17 | Nota |
|------|-----------|------|
| 7 | R@k 0 → **1.0**; dictamen ✓ → ✗ | Recupera 21.2 en contexto; el LLM no la cita ni acierta decisión |
| 8 | R@k +0.33; F1 +0.33 | Mejora parcial |
| 15 | R@k 1.0 → 0; F1 0.8 → 0 | Regresión fuerte por ranking semántico |
| 10, 14 | dictamen ✓ → ✗ | Regresión |

## Decisión

**No adoptar E17 como perfil productivo.** Mantener **E11 léxico + E13 prompt v3**.

El híbrido queda como experimento documentado (mejora retrieval puntual, peor respuesta agregada).
