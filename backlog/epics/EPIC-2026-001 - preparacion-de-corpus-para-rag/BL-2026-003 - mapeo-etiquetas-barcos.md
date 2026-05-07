# Tarea pendiente

## ID

`BL-2026-003`

## Epic

`EPIC-2026-001` — ver `./EPIC-2026-001 - preparacion-de-corpus-para-rag.md`

## Título

Mapeo de etiquetas de barcos (A, B, C, P, S, W, L, I, O) a definiciones técnicas

## Objetivo

Construir una función que reemplace y/o asocie las etiquetas genéricas de barcos (`A`, `B`, `C`, `P`, `S`, `W`, `L`, `I`, `O`) con sus definiciones técnicas dentro de cada chunk, para mejorar la comprensión del RAG (por ejemplo: en Regla 10, entender que `S` es **estribor** y `P` es **babor**).

## Contexto

En el material de regatas, los esquemas y descripciones usan letras para referirse a barcos/roles (p. ej. `P`/`S`). Sin un mapeo semántico, los embeddings pueden tratar estas letras como tokens sin significado, degradando recuperación y respuestas del RAG cuando el usuario pregunta por “barco de estribor/babor” y el texto fuente usa letras.

## Criterios de aceptación

- [ ] Existe una función de mapeo que, dado un chunk, **anota** o **expande** las etiquetas (`A,B,C,P,S,W,L,I,O`) con su definición técnica (por ejemplo agregando “(barco de estribor)”).
- [ ] El mapeo es **context-aware** cuando aplica (p. ej. `P`/`S` en el contexto de la **Regla 10**), evitando reemplazos incorrectos fuera de contexto.
- [ ] La transformación es estable: no rompe el texto ni altera significados (se conserva el original o se mantiene trazabilidad del texto base).
- [ ] Se cubren casos con múltiples etiquetas en el mismo chunk y repeticiones.
- [ ] Hay tests/fixtures que validan: chunk con Regla 10 (mapeo correcto), chunk sin contexto (no mapear o mapear solo si es seguro), y un caso de falso positivo (letras usadas como enumeración u otra cosa).
- [ ] Se documenta el diccionario/reglas de mapeo (qué significa cada etiqueta y bajo qué condiciones se aplica).

## Plan

- Relevar en el corpus ejemplos reales de uso de `A,B,C,P,S,W,L,I,O` y determinar significados por regla/diagrama.
- Definir estrategia: “expansión inline” vs “metadatos añadidos al chunk” (o ambas).
- Implementar función de enriquecimiento con heurísticas de contexto (mención de regla, encabezados, patrones cercanos).
- Integrar al pipeline de chunking/enriquecimiento antes de embeddings.
- Agregar tests automatizados con fixtures representativos y documentación del mapeo.

## Enlaces

- Issue (si existe):
- Docs / referencias:

