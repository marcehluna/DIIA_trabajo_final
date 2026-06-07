# Experimento E14: salida en inglés vs E13 (español)

Corrida **E14** (`20260606_200214_prompt_v3_en_out`) — mismo índice y cupos **E11**, prompt v3 con `--response-lang en`.

Referencia **E13** (`20260604_124747_prompt_v3_format`) — producto actual en español.

---

## Métricas agregadas

| Métrica | E13 | E14 | Δ (E14 − E13) | Lectura |
|---------|-----|-----|---------------|---------|
| R@k reglas | 0.76 | 0.76 | 0.00 | Retrieval idéntico |
| R@k CALL | 0.20 | 0.20 | 0.00 | Idem |
| **F1 RRS** | 0.22 | **0.32** | **+0.10** | Más coincidencia de códigos con golden |
| F1 CALL | 0.07 | 0.07 | 0.00 | Sin cambio |
| Jaccard resp ↔ contexto | 0.01 | **0.16** | **+0.15** | Respuesta alineada léxicamente al corpus EN |
| Jaccard resp ↔ referencia | 0.16 | 0.02 | −0.14 | Peor vs Output Ideal español (esperado) |
| **Dictamen auto** | **60%** | **40%** | **−20 pp** | Peor match con decisión del Excel |

Fuente: `report.json` → `aggregate`. Detalle en [`eval/runs/20260606_200214_prompt_v3_en_out/comparacion_vs_E13.md`](../../eval/runs/20260606_200214_prompt_v3_en_out/comparacion_vs_E13.md).

---

## Conclusiones

1. **La hipótesis “idioma del corpus” se confirma en parte:** el modelo cita con más frecuencia códigos que el evaluador puede extraer (F1 RRS ↑) y el texto se parece más a los chunks (Jaccard contexto ↑).
2. **No mejora el dictamen medido contra el golden español:** penalizar/exonerar en inglés (`Penalize boat Y`) sigue mapeando al matcher, pero más casos fallan (40% vs 60%).
3. **El producto sigue siendo E13 (español):** E14 es evidencia para el informe, no configuración por defecto.

## Cómo reproducir E14

```bash
REGATAS_LLM_BACKEND=http REGATAS_LLM_MODEL=qwen2.5:14b-instruct \
  python scripts/eval_run.py --label prompt_v3_en_out --response-lang en --lang es --plots \
  --diario-nota "E14: salida inglés vs E13"
```

Artefactos: [`eval/runs/20260606_200214_prompt_v3_en_out/`](../../eval/runs/20260606_200214_prompt_v3_en_out/)
