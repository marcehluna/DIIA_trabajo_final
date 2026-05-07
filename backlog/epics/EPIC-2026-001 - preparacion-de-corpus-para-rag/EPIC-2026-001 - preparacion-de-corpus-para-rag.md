# Épica

## ID

`EPIC-2026-001`

## Milestone

`M-2026-001` — ver `backlog/milestones/M-2026-001 - preparacion-de-datos-para-la-ingesta.md`

## Título

Preparación del corpus para RAG (segmentación + limpieza + enriquecimiento semántico)

## Objetivo

Mejorar la calidad del corpus previo a embeddings y recuperación (RAG) mediante:

- segmentación consistente por caso/documento
- limpieza de ruido bibliográfico no semántico
- enriquecimiento de etiquetas/abreviaturas para preservar significado en contexto

## Alcance

- Incluye: procesamiento de texto (parser/regex/enriquecimiento), pruebas con fixtures, documentación de supuestos.
- No incluye: cambios de modelo de embeddings, tuning de retrieval/reranking, UI/experiencia conversacional.

## Criterios de éxito (del conjunto)

- [ ] Los documentos quedan correctamente **segmentados** y estructurados (un caso = un documento) con secciones internas relevantes.
- [ ] Se reduce ruido en embeddings (eliminación de referencias bibliográficas y tokens “no consultables” por el usuario).
- [ ] El corpus preserva significado técnico en texto (mapeo de etiquetas como `P`/`S` cuando corresponde).
- [ ] Hay pruebas automatizadas y fixtures que cubren variantes reales del material.

## Tareas incluidas

- [ ] `BL-2026-001` — Segmentación del Case Book por “CASES” (`CASE \d+`)
  - Archivo: `./BL-2026-001 - segmentacion-case-book-por-cases.md`
- [ ] `BL-2026-002` — Limpieza de ruido bibliográfico (códigos tipo `GBR 1962/25`)
  - Archivo: `./BL-2026-002 - limpieza-ruido-bibliografico.md`
- [ ] `BL-2026-003` — Mapeo de etiquetas de barcos (P/S y otras)
  - Archivo: `./BL-2026-003 - mapeo-etiquetas-barcos.md`

## Enlaces

- Issue (si existe):
- Docs / referencias:

