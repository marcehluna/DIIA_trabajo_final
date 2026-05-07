# Tarea pendiente

## ID

`BL-2026-006`

## Epic

`EPIC-2026-003` — ver `./EPIC-2026-003 - recuperacion-hibrida-y-semantica.md`

## Título

Priorización por disciplina (metadato `discipline`)

## Objetivo

Dado que el Case Book cubre múltiples formatos, agregar metadatos de **Discipline** para diferenciar casos generales de casos específicos que podrían aparecer en apéndices, habilitando priorización/filtros en la recuperación.

## Contexto

Si el retriever mezcla indiscriminadamente documentos de distintas “disciplinas” (general vs apéndices/formatos específicos), puede devolver resultados menos útiles para consultas generales. Un metadato `discipline` permite ajustar ranking/boosting y mejorar precisión sin perder cobertura.

## Criterios de aceptación

- [ ] Se define un esquema de `discipline` (valores permitidos y significado). Ej.: `general`, `appendix`, `match-racing`, etc. (según el corpus real).
- [ ] Se implementa asignación de `discipline` a documentos/chunks de forma consistente (por reglas del parser, ubicación/encabezados, o fuente).
- [ ] El metadato se persiste junto al documento/chunk (en el store de indexado/metadata).
- [ ] Hay fixtures/tests que cubren al menos: un caso general y un caso de apéndice/formatos específicos.
- [ ] Se valida en retrieval que una consulta “general” prioriza `discipline=general` (boosting) y que aún se pueden recuperar otras disciplinas cuando corresponde.

## Plan

- Relevar qué “disciplinas” existen efectivamente en el Case Book/corpus y cómo se identifican (apéndices, encabezados, secciones).
- Definir taxonomía `discipline` y reglas de asignación (heurísticas determinísticas primero).
- Integrar la asignación al pipeline de ingestión/chunking.
- Agregar tests automatizados con fixtures representativos.
- Ajustar retrieval: filtro opcional o boosting por `discipline` + evaluación con consultas de ejemplo.

## Enlaces

- Issue (si existe):
- Docs / referencias:

