# Divergencia de métricas: Recall@8 reglas RRS vs TR CALL (E0 → E11)

Al pasar de la línea base **E0** al perfil de retrieval productivo **E11**, las métricas de recuperación evolucionan en direcciones opuestas:

| Métrica | E0 (baseline) | E11 (productivo) | Cambio |
|---------|---------------|------------------|--------|
| **Recall@8 reglas RRS** | 0,41 | **0,76** | Mejora (+85 % relativo) |
| **Recall@8 TR CALL** | 0,27 | **0,20** | Caída (−26 % relativo) |

Este documento explica **por qué puede ocurrir eso** sin que el sistema esté “roto”: responde a un **cambio de diseño** en el índice y en cómo se reparten los 8 fragmentos recuperados.

---

## Qué mide cada métrica

- **Recall@8 reglas RRS:** de las reglas del RRS [1] que el golden set espera para cada caso, ¿cuántas aparecen en al menos uno de los 8 chunks que entran al prompt?
- **Recall@8 TR CALL:** lo mismo, pero para códigos del *Call Book for Team Racing* [2] (p. ej. B2, E1, J5).

Ambas usan el mismo `top_k = 8` y el mismo retriever léxico; lo que cambia entre E0 y E11 es **qué documentos hay en el índice** y **cómo se reparten los cupos por tipo** [4][5].

---

## Cambio principal: otro índice, otras prioridades

### E0 — baseline PDF

- Índice: **Call Book + Case Book en PDF** [2][3] (por página).
- **RRS estructurado no está** en el índice [1] → el recall de reglas es bajo: muchas reglas esperadas simplemente no pueden recuperarse.
- El Call Book completo en PDF [2] → el recall de TR CALL es relativamente alto: hay mucho texto de calls disponible para el match léxico.

### E11 — corpus JSONL + cupos

- Índice: **solo `corpus/processed/`** (~707 chunks): reglas RRS, calls, cases y definiciones en JSONL.
- **Sin PDF** del Call Book [2] ni del Case Book [3] en el índice productivo.
- **Cupos 2+3+2+1** en `top_k = 8`: como máximo 2 chunks de reglas RRS, 3 de calls, 2 de cases y 1 de definiciones (por `doc_type`) [5].

El salto E0 → E11 no es “afinar el mismo índice”: es **cambiar qué material es recuperable** y **qué tipo de fragmento se prioriza** en el contexto del LLM.

---

## Por qué suben las reglas RRS

1. **RRS entra al índice por primera vez de forma útil** [1]. Cada regla es un chunk con número, encabezado y texto; el golden set espera reglas concretas y ahora pueden encontrarse.
2. **Mejor alineación con la unidad normativa.** El PDF del RRS no trocea por regla; el JSONL sí. Eso fue una conclusión central del EDA (sección 03) [5].
3. **Metadatos enriquecidos** (referencias cruzadas, encabezados) ayudan al retriever léxico aun con relato en español y corpus en inglés [4][5].
4. **Cupos evitan la dilución** del Case Book [3]: en índices *full* sin cupos (E3), mezclar JSONL + PDF empeoraba el recall de reglas; E11 equilibra qué entra al top-8 [5].

En síntesis: E0 fallaba en reglas por **ausencia** en el índice; E11 las resuelve por **diseño del corpus**.

---

## Por qué bajan los TR CALL

1. **Se dejó de indexar el Call Book en PDF** [2]. E0 recuperaba calls desde páginas PDF con más contexto y vocabulario; E11 usa calls desde CSV/JSONL, en chunks más compactos.
2. **Techo de cupos:** solo **3 de 8** slots pueden ser calls [5]. Si un caso espera un call concreto y entran otros calls o tipos de chunk, el call esperado puede quedar fuera del top-8.
3. **Competencia por slots:** con RRS fuerte en el ranking, los chunks de reglas ocupan sus cupos y compiten por atención léxica con los calls. Los códigos TR CALL (B2, E1…) tienen **poca superficie textual** frente a narrativas largas en español.
4. **Mismatch léxico ES ↔ EN:** el retriever es léxico, sin embeddings semánticos en producción [4]. Las reglas en JSONL traen más texto y metadatos; los calls, códigos cortos y definiciones técnicas en inglés, matchean peor con el relato coloquial [5].
5. **El golden set exige calls específicos.** No alcanza con “algún call en contexto”: la métrica pide el código esperado por caso. En E13 se observa que a veces el dictamen acierta **sin** citar el TR CALL esperado — el modelo se apoya en reglas genéricas.

En síntesis: E0 era fuerte en CALL porque el **PDF del Call Book era el protagonista** del índice; E11 prioriza **RRS y equilibrio del índice**, y el CALL paga parte del costo.

---

## ¿Es un trade-off aceptado?

Sí, en el marco de esta PoC:

- El cuello de botella en protestas suele ser **traer las reglas RRS** al contexto; sin eso, ningún prompt cierra bien el análisis [4].
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
| Retrieval híbrido | E16 igualó reglas en agregado y ayudó casos aislados; E17 empeoró citas y dictamen — no adoptado [6]. |

Detalle de corridas: [`eval/RESUMEN_CORRIDAS_EVAL.md`](../../eval/RESUMEN_CORRIDAS_EVAL.md). Tabla agregada: [evaluación de resultados](evaluacion-de-resultados.md).

---

## Referencias bibliográficas

[1] World Sailing. (2024). *The Racing Rules of Sailing 2025–2028*. Federación internacional de vela. https://www.sailing.org/racingrules/

[2] World Sailing. (2025). *The Call Book for Team Racing 2025–2028* (8.ª ed.). https://www.sailing.org/document/2025-2028-call-book-for-team-racing/

[3] World Sailing. (2025). *World Sailing Case Book 2025–2028*. https://www.sailing.org/document/world-sailing-case-book-2025-2028/

[4] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html

[5] Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M., & Wang, H. (2024). Retrieval-augmented generation for large language models: A survey. *arXiv preprint* arXiv:2312.10997. https://arxiv.org/abs/2312.10997

[6] Karpukhin, V., Oguz, B., Min, S., Wu, L., Edunov, S., Chen, D., & Yih, W. (2020). Dense passage retrieval for open-domain question answering. *Proceedings of EMNLP 2020*, 6769–6781. https://arxiv.org/abs/2004.04906
