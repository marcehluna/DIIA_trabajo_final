# Épica

## ID

`EPIC-2026-003`

## Milestone

`M-YYYY-NNN` — (link en `backlog/milestones/`, si aplica)

## Título

Recuperación Híbrida y Semántica

## Objetivo

Mejorar la recuperación (RAG) combinando señales semánticas y estructuradas (metadatos), para priorizar resultados más relevantes según el tipo de contenido y el contexto de consulta.

## Alcance

- Incluye: definición/extracción de metadatos útiles para retrieval, estrategias de priorización (filtros/boosting), validación con consultas representativas.
- No incluye: cambio de modelo base (LLM) ni rediseño completo de infraestructura (salvo ajustes incrementales necesarios).

## Criterios de éxito (del conjunto)

- [ ] Se dispone de metadatos consistentes para diferenciar tipos/formats del Case Book y apéndices.
- [ ] La recuperación prioriza fuentes correctas según la intención (general vs específico), manteniendo cobertura.
- [ ] Hay pruebas/experimentos reproducibles que muestren mejora (cualitativa o cuantitativa) en consultas típicas.

## Tareas incluidas

- [ ] `BL-2026-006` — Priorización por disciplina (metadato `discipline`)
  - Archivo: `./BL-2026-006 - priorizacion-por-disciplina.md`
- [ ] `BL-2026-007` — Alineación semántica Inglés–Español (tesauro técnico)
  - Archivo: `./BL-2026-007 - alineacion-semantica-ingles-espanol.md`

## Enlaces

- Issue (si existe):
- Docs / referencias:

