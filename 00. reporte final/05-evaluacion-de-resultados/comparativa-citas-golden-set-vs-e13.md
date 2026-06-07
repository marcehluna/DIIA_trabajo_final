# Comparativa de citas normativas: golden set vs respuesta (E13)

Análisis **caso a caso** de las **15 protestas** del golden set (`eval/data/eval_set.json`) frente a la corrida **E13** (`prompt_v3_format`, perfil productivo E11).

**Fuente:** `eval/runs/20260604_124747_prompt_v3_format/report.json` · parser de citas actual (`regatas_assistant/eval/refs.py`).

**Qué muestra la tabla:** reglas RRS y TR CALL **esperadas** (extraídas del Output Ideal del Excel) vs las **citadas en la respuesta** del modelo; recall de recuperación (R@k) en top-8; F1 de citas; y si el **dictamen automático** coincide con el golden set.

---

## Tabla por caso

| Caso | Título (abrev.) | Reglas esperadas | Reglas citadas | CALL esperado | CALL citado | R@k reglas | R@k CALL | F1 RRS | F1 CALL | Dictamen OK |
|------|-----------------|------------------|----------------|---------------|-------------|------------|----------|--------|---------|-------------|
| 1 | Orzada brusca sin espacio | 16.1 | 16.1 | A3 | A3 | 1.00 | 1.00 | 1.00 | 1.00 | Sí |
| 2 | Sobre-rotación barlovento | 11, 13 | 16.1, 11, 15 | B2 | — | 1.00 | 1.00 | 0.40 | 0.00 | Sí |
| 3 | Retraso solapamiento desde atrás | 11, 15 | 13, 14 | B1 | M10* | 0.50 | 0.00 | 0.00 | 0.00 | No |
| 4 | Espacio de marca y virada | 18.2(a)(2), 12, 18.2(d) | 18.2(a)(2), 14 | E1 | — | 1.00 | 0.00 | 0.40 | 0.00 | No |
| 5 | Cambio rumbo Anti-Hunt | 16.2 | 16.1 | D2 | 3* | 1.00 | 1.00 | 0.00 | 0.00 | Sí |
| 6 | Incapacidad dar espacio marca | 18.2(a), 18.2(d) | 18.2(a)(2) | E2 | A3 | 1.00 | 0.00 | 0.00 | 0.00 | Sí |
| 7 | Interferencia en penalización | 21.2 | 18.2(a)(2) | L2 | A3 | 0.00 | 0.00 | 0.00 | 0.00 | Sí |
| 8 | Eliminación Regla 18.4 TR | 18.2(a)(1), D1.1, 18.4 | 18.2(a)(2) | J5 | A3 | 0.33 | 0.00 | 0.00 | 0.00 | No |
| 9 | Virada libre por proa en zona | 12, 13, 15 | 18.2(a)(2), 14 | E6 | A3 | 1.00 | 0.00 | 0.00 | 0.00 | No |
| 10 | Contacto antes de virada | 13 | 14, 16.1 | D4 | A3 | 1.00 | 0.00 | 0.00 | 0.00 | Sí |
| 11 | Frenado en la marca (Trap) | 11, 18.2 | 15, 14, 2* | J9 | A3 | 1.00 | 0.00 | 0.00 | 0.00 | Sí |
| 12 | Contacto antideportivo | 10, D2.3(f) | 14, 16.1 | L1 | A3 | 0.50 | 0.00 | 0.00 | 0.00 | No |
| 13 | Trasluchada Regla 17 | 17 | 16.1, 17 | G3 | A3 | 1.00 | 0.00 | 0.67 | 0.00 | No |
| 14 | Interferencia barco terminado | D1.1(e) | 14, 18.2(a)(2) | K1 | A3 | 0.00 | 0.00 | 0.00 | 0.00 | Sí |
| 15 | Virada en proa maniobra evasiva | 13, 15 | 13, 14, 15 | D3 | — | 1.00 | 0.00 | 0.80 | 0.00 | Sí |

\*Códigos CALL citados que **no** son TR CALL válidos del Call Book (p. ej. `M10`, `3`) o regla `2` fuera del set esperado — posible alucinación o parseo de texto ajeno a la norma.

**Leyenda dictamen OK:** coincidencia gruesa esperada vs predicha (`penalizar` / `sin_penalizacion` / `exonerar` / `mixto`). «Sí» no implica que las citas sean correctas.

---

## Resumen agregado (E13)

| Métrica | Valor |
|---------|-------|
| Casos con F1 RRS = 1.0 | 1 / 15 |
| Casos con F1 RRS = 0.0 | 10 / 15 |
| Media F1 RRS | 0.22 |
| Media F1 CALL | 0.07 |
| Media R@k reglas | 0.76 |
| Media R@k CALL | 0.20 |
| Dictamen automático acertado | 9 / 15 (60 %) |

---

## Patrones observados

1. **Recuperación ≠ citas:** En 7 casos R@k reglas = 1.00 pero F1 RRS = 0.00 (2, 9, 10, 11, …): el contexto trae las reglas esperadas, pero el modelo **cita otras** (a menudo 14, 16.1, 18.2(a)(2)).
2. **Granularidad:** Sustitución de subreglas cercanas (16.2 → 16.1; 18.2(a) → 18.2(a)(2)) penaliza el F1 aunque el razonamiento sea parecido.
3. **CALL:** El modelo reutiliza **A3** en muchos casos donde el ideal pide otro código (B1, E1, J5…); F1 CALL bajo aun con R@k CALL razonable en algunos casos.
4. **Dictamen sin citas correctas:** Varios casos con dictamen OK y F1 RRS = 0 (10, 11, 14): el fallo está en **trazabilidad normativa**, no siempre en la decisión gruesa.
5. **Caso 1 y 15:** Mejor alineación citas ↔ golden (F1 1.0 y 0.8); útiles como contraejemplo de comportamiento deseable.

---

## Uso en el informe

- **No** interpretar F1 bajo como “respuesta inútil” sin leer el rationale y el dictamen.
- Separar **error de fondo** (dictamen No, rationale incorrecto) de **divergencia de cita** (dictamen Sí, otra norma plausible).
- Contexto ampliado: [`eval/RESUMEN_CORRIDAS_EVAL.md`](../../eval/RESUMEN_CORRIDAS_EVAL.md), [`docs/INFORME_CITAS_E0_vs_E12.md`](../../docs/INFORME_CITAS_E0_vs_E12.md).

**Regenerar tras nueva corrida:**

```bash
python scripts/rescore_eval_citations.py eval/runs/<run_id>
# Luego actualizar esta tabla desde report.json o automatizar con script.
```
