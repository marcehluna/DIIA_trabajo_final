# Comparativa de citas normativas: golden set vs respuesta (E14)

Análisis **caso a caso** de las **15 protestas** del golden set frente a la corrida **E14** (`prompt_v3_en_out`, salida en inglés con `--response-lang en`, mismo índice E11).

**Fuente:** `eval/runs/20260606_200214_prompt_v3_en_out/report.json` · parser de citas (`Rule …`, `Decision:`).

**Comparar con productivo:** [E13 (español)](comparativa-citas-golden-set-vs-e13.md) · [métricas agregadas E13 vs E14](comparativa-e13-vs-e14-salida-ingles.md).

---

## Tabla por caso

| Caso | Título (abrev.) | Reglas esperadas | Reglas citadas | CALL esperado | CALL citado | R@k reglas | R@k CALL | F1 RRS | F1 CALL | Dictamen OK |
|------|-----------------|------------------|----------------|---------------|-------------|------------|----------|--------|---------|-------------|
| 1 | Orzada brusca sin espacio | 16.1 | 17, 16.1 | A3 | A3 | 1.00 | 1.00 | 0.67 | 1.00 | No |
| 2 | Sobre-rotación barlovento | 11, 13 | 16.1, 11 | B2 | — | 1.00 | 1.00 | 0.50 | 0.00 | Sí |
| 3 | Retraso solapamiento desde atrás | 11, 15 | 10, 15 | B1 | — | 0.50 | 0.00 | 0.50 | 0.00 | No |
| 4 | Espacio de marca y virada | 18.2(a)(2), 12, 18.2(d) | 18.2, 18.2(a)(2) | E1 | — | 1.00 | 0.00 | 0.40 | 0.00 | No |
| 5 | Cambio rumbo Anti-Hunt | 16.2 | 16.2 | D2 | 3* | 1.00 | 1.00 | 1.00 | 0.00 | Sí |
| 6 | Incapacidad dar espacio marca | 18.2(a), 18.2(d) | 18.2, 12, 18.2(a)(2) | E2 | — | 1.00 | 0.00 | 0.00 | 0.00 | No |
| 7 | Interferencia en penalización | 21.2 | 15 | L2 | — | 0.00 | 0.00 | 0.00 | 0.00 | No |
| 8 | Eliminación Regla 18.4 TR | 18.2(a)(1), D1.1, 18.4 | 18, 16.1 | J5 | A3 | 0.33 | 0.00 | 0.00 | 0.00 | No |
| 9 | Virada libre por proa en zona | 12, 13, 15 | 18 | E6 | A3 | 1.00 | 0.00 | 0.00 | 0.00 | No |
| 10 | Contacto antes de virada | 13 | 17 | D4 | A3 | 1.00 | 0.00 | 0.00 | 0.00 | Sí |
| 11 | Frenado en la marca (Trap) | 11, 18.2 | 18 | J9 | — | 1.00 | 0.00 | 0.00 | 0.00 | Sí |
| 12 | Contacto antideportivo | 10, D2.3(f) | 17, 14 | L1 | A3 | 0.50 | 0.00 | 0.00 | 0.00 | No |
| 13 | Trasluchada Regla 17 | 17 | 17 | G3 | A1 | 1.00 | 0.00 | 1.00 | 0.00 | No |
| 14 | Interferencia barco terminado | D1.1(e) | 17 | K1 | A2 | 0.00 | 0.00 | 0.00 | 0.00 | Sí |
| 15 | Virada en proa maniobra evasiva | 13, 15 | 15, 10, 14, 13 | D3 | — | 1.00 | 0.00 | 0.67 | 0.00 | Sí |

\*CALL `3` en caso 5 no es código TR CALL válido.

---

## Resumen agregado (E14)

| Métrica | E14 | E13 (ref.) | Δ |
|---------|-----|------------|---|
| Media F1 RRS | **0.32** | 0.22 | +0.10 |
| Media F1 CALL | 0.07 | 0.07 | 0.00 |
| Media R@k reglas | 0.76 | 0.76 | 0.00 |
| Media R@k CALL | 0.20 | 0.20 | 0.00 |
| Jaccard resp ↔ contexto | **0.16** | 0.01 | +0.15 |
| Jaccard resp ↔ referencia | 0.02 | 0.16 | −0.14 |
| Dictamen automático acertado | **6 / 15 (40 %)** | 9 / 15 (60 %) | −20 pp |
| Casos con F1 RRS = 1.0 | 2 / 15 | 1 / 15 | +1 |
| Casos con F1 RRS = 0.0 | 8 / 15 | 10 / 15 | −2 |

---

## Lectura vs E13

1. **F1 RRS sube** (0.32 vs 0.22): el parser reconoce mejor `Rule …` y hay más coincidencia de códigos; casos 5 y 13 llegan a F1 = 1.0.
2. **Dictamen baja** (40 % vs 60 %): el matcher de decisión sigue orientado al golden en español; varias resoluciones en inglés (`Exonerate`, `Penalize`) no alinean con el Excel aunque el razonamiento sea parecido (caso 1: exonerar B vs penalizar Y).
3. **Mismo patrón de “citas vecinas”**: 18, 17, 14 siguen apareciendo donde el ideal pide otras reglas; el idioma no elimina la divergencia argumental.
4. **CALL:** Persiste el sesgo a **A3** en inglés; F1 CALL no mejora respecto a E13.

---

## Uso en el informe

E14 **no** reemplaza E13 como perfil productivo: confirma mejor anclaje léxico al corpus EN, pero empeora el dictamen medido contra el golden español. Ver [`eval/RESUMEN_CORRIDAS_EVAL.md`](../../eval/RESUMEN_CORRIDAS_EVAL.md) (sección E14).
