# Épica

## ID

`EPIC-2026-002`

## Milestone

`M-2026-001` — ver `backlog/milestones/M-2026-001 - preparacion-de-datos-para-la-ingesta.md`

## Título

Enriquecimiento de Metadatos

## Objetivo

Enriquecer los documentos/chunks con metadatos estructurados extraídos del contenido (p. ej. referencias a reglas), para mejorar recuperación (RAG) por intención del usuario (ej.: “Regla 18”) y habilitar filtros/boosting por metadatos.

## Alcance

- Incluye: extracción por RegEx/heurísticas, normalización, esquema de metadatos, pruebas con fixtures y validación en recuperación.
- No incluye: cambios en el modelo de embeddings ni rediseño del ranking (salvo el uso de filtros/boosting simple por metadatos).

## Criterios de éxito (del conjunto)

- [ ] Los metadatos se extraen de forma consistente y trazable desde el texto fuente.
- [ ] Una consulta por regla (ej. “Regla 18”) recupera tanto el reglamento (RRS) como los casos del Case Book asociados.
- [ ] Hay tests automatizados/fixtures que cubren formatos y variantes reales.

## Tareas incluidas

- [ ] `BL-2026-004` — Inyección de referencias cruzadas (reglas mencionadas en `Rules` → metadatos)
  - Archivo: `./BL-2026-004 - inyeccion-de-referencias-cruzadas.md`
- [ ] `BL-2026-005` — Identificación de “Abstracts” (indexado separado de resúmenes)
  - Archivo: `./BL-2026-005 - identificacion-de-abstracts.md`

## Enlaces

- Issue (si existe):
- Docs / referencias:

