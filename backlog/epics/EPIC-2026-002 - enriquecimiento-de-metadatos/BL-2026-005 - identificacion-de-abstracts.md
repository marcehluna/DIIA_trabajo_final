# Tarea pendiente

## ID

`BL-2026-005`

## Epic

`EPIC-2026-002` — ver `./EPIC-2026-002 - enriquecimiento-de-metadatos.md`

## Título

Identificación de “Abstracts” (indexado separado de resúmenes del inicio del libro)

## Objetivo

Indexar por separado los resúmenes del inicio del libro (“abstracts”). Estos resúmenes son ideales para una recuperación rápida porque conectan directamente una regla con el núcleo de la interpretación del caso (ej.: “Un barco con derecho de paso no necesita actuar hasta que sea claro que el otro no se mantiene alejado”).

## Contexto

Los abstracts suelen ser texto más denso y “consultable” que el caso completo. Si se indexan como documentos/chunks independientes con metadatos (por ejemplo reglas referenciadas y/o case_id), pueden mejorar la precisión y velocidad de recuperación, y servir como “primer hit” en respuestas del RAG.

## Criterios de aceptación

- [ ] Se identifica y extrae el bloque de abstracts del inicio del libro, separándolo del resto del contenido.
- [ ] Cada abstract se convierte en un documento/chunk independiente, manteniendo trazabilidad (ej.: `case_id` o referencia al caso).
- [ ] Cuando el abstract menciona reglas, se extraen y normalizan (reutilizando el extractor de reglas si aplica) y se guardan en metadatos.
- [ ] Se definen fixtures con al menos: un abstract típico, un abstract sin regla explícita y variaciones de formato/encabezados.
- [ ] Prueba de integración (o experimento reproducible) muestra que queries por regla o interpretación recuperan abstracts relevantes (y luego el caso completo si corresponde).

## Plan

- Relevar el formato real del bloque de abstracts (cómo empiezan/terminan; cómo se delimitan por caso).
- Implementar parser/segmentación específica para abstracts (y un esquema `{abstract_text, case_id?, referenced_rules?}`).
- Integrar al pipeline de indexado como “fuente/colección” separada o como tipo de documento distinto.
- Agregar tests automatizados y documentación del formato asumido.
- Validar impacto en recuperación: evaluar si el retriever trae abstracts ante consultas por regla/interpretación.

## Enlaces

- Issue (si existe):
- Docs / referencias:

