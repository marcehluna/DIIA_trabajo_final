# Divergencia de métricas: Recall@8 reglas RRS vs TR CALL (E0 → E11)

Al pasar de la línea base **E0** al perfil de retrieval productivo **E11**, las métricas de recuperación evolucionan en direcciones opuestas:

| Métrica | E0 (baseline) | E11 (productivo) | Cambio |
|---------|---------------|------------------|--------|
| **Recall@8 reglas RRS** | 0,41 | **0,76** | Mejora (+85 % relativo) |
| **Recall@8 TR CALL** | 0,27 | **0,20** | Caída (−26 % relativo) |

Este documento explica **por qué puede ocurrir eso** sin que el sistema esté “roto”: responde a un **cambio de diseño** en el índice y en cómo se reparten los 8 fragmentos recuperados.

---

## Qué mide cada métrica

- **Recall@8 reglas RRS:** de las reglas del RRS que el golden set espera para cada caso, ¿cuántas aparecen en al menos uno de los 8 chunks que entran al prompt?
- **Recall@8 TR CALL:** lo mismo, pero para códigos del *Call Book for Team Racing* (p. ej. B2, E1, J5).

Ambas usan el mismo `top_k = 8` y el mismo retriever léxico; lo que cambia entre E0 y E11 es **qué documentos hay en el índice** y **cómo se reparten los cupos por tipo**.

---

## Cambio principal: otro índice, otras prioridades

### E0 — baseline PDF

- Índice: **Call Book + Case Book en PDF** (por página).
- **RRS estructurado no está** en el índice → el recall de reglas es bajo: muchas reglas esperadas simplemente no pueden recuperarse.
- El Call Book completo en PDF → el recall de TR CALL es relativamente alto: hay mucho texto de calls disponible para el match léxico.

### E11 — corpus JSONL + cupos

- Índice: **solo `corpus/processed/`** (~707 chunks): reglas RRS, calls, cases y definiciones en JSONL.
- **Sin PDF** del Call Book ni del Case Book en el índice productivo.
- **Cupos 2+3+2+1** en `top_k = 8`: como máximo 2 chunks de reglas RRS, 3 de calls, 2 de cases y 1 de definiciones (por `doc_type`).

El salto E0 → E11 no es “afinar el mismo índice”: es **cambiar qué material es recuperable** y **qué tipo de fragmento se prioriza** en el contexto del LLM.

---

## Por qué suben las reglas RRS

1. **RRS entra al índice por primera vez de forma útil.** Cada regla es un chunk con número, encabezado y texto; el golden set espera reglas concretas y ahora pueden encontrarse.
2. **Mejor alineación con la unidad normativa.** El PDF del RRS no trocea por regla; el JSONL sí. Eso fue una conclusión central del EDA (sección 03).
3. **Metadatos enriquecidos** (referencias cruzadas, encabezados) ayudan al retriever léxico aun con relato en español y corpus en inglés.
4. **Cupos evitan la dilución** del Case Book: en índices *full* sin cupos (E3), mezclar JSONL + PDF empeoraba el recall de reglas; E11 equilibra qué entra al top-8.

En síntesis: E0 fallaba en reglas por **ausencia** en el índice; E11 las resuelve por **diseño del corpus**.

---

## Por qué bajan los TR CALL

1. **Se dejó de indexar el Call Book en PDF.** E0 recuperaba calls desde páginas PDF con más contexto y vocabulario; E11 usa calls desde CSV/JSONL, en chunks más compactos.
2. **Techo de cupos:** solo **3 de 8** slots pueden ser calls. Si un caso espera un call concreto y entran otros calls o tipos de chunk, el call esperado puede quedar fuera del top-8.
3. **Competencia por slots:** con RRS fuerte en el ranking, los chunks de reglas ocupan sus cupos y compiten por atención léxica con los calls. Los códigos TR CALL (B2, E1…) tienen **poca superficie textual** frente a narrativas largas en español.
4. **Mismatch léxico ES ↔ EN:** el retriever es léxico, sin embeddings semánticos en producción. Las reglas en JSONL traen más texto y metadatos; los calls, códigos cortos y definiciones técnicas en inglés, matchean peor con el relato coloquial.
5. **El golden set exige calls específicos.** No alcanza con “algún call en contexto”: la métrica pide el código esperado por caso. En E13 se observa que a veces el dictamen acierta **sin** citar el TR CALL esperado — el modelo se apoya en reglas genéricas.

En síntesis: E0 era fuerte en CALL porque el **PDF del Call Book era el protagonista** del índice; E11 prioriza **RRS y equilibrio del índice**, y el CALL paga parte del costo.

---

## ¿Es un trade-off aceptado?

Sí, en el marco de esta PoC:

- El cuello de botella en protestas suele ser **traer las reglas RRS** al contexto; sin eso, ningún prompt cierra bien el análisis.
- La caída de CALL (0,27 → 0,20) es **moderada** frente a la ganancia en reglas (0,41 → 0,76).
- E11 ya ajustó cupos respecto de E10 (más slots para CALL: de 0,07 a 0,20); aun así no recupera el nivel del baseline PDF.
- Corridas **E6–E7** (índice *full* con más PDF) mejoraron CALL pero con índice más pesado y reglas por debajo de E11; por eso no se adoptaron como productivo.

El perfil **E11 + E13** fija umbrales de regresión con piso de R@k CALL ≥ 0,18: E11 cumple, pero por poco margen respecto de E0.

---

## Lectura en una frase

**Suben las reglas** porque el índice pasó de no tener RRS estructurado a tenerlo bien segmentado; **bajan los calls** porque se reemplazó el Call Book PDF por calls JSONL compactos, con cupos limitados y competencia léxica con el resto del índice.

---

## Palancas para mejorar CALL (sin perder reglas)

| Palanca | Idea |
|---------|------|
| Más cupo CALL | Probar 2+4+1+1 u otra repartición (requiere nueva corrida y regresión). |
| Chunks de calls más ricos | Incluir en el texto del chunk señal, procedimiento y reglas vinculadas. |
| PDF selectivo | Reintroducir solo Call Book en PDF con cupos, evitando índice *full* diluido (E6–E7). |
| Retrieval híbrido | E16 igualó reglas en agregado y ayudó casos aislados; E17 empeoró citas y dictamen — no adoptado. |

Detalle de corridas: [`eval/RESUMEN_CORRIDAS_EVAL.md`](../../eval/RESUMEN_CORRIDAS_EVAL.md). Tabla agregada: [evaluación de resultados](evaluacion-de-resultados.md).
