# Épica

## ID

`EPIC-2026-004`

## Milestone

`M-YYYY-NNN` — (link en `backlog/milestones/`, si aplica)

## Título

FASE 4 — Estrategia de Prompting (FS‑CoT Refinado)

## Objetivo

Mejorar la calidad de razonamiento y consistencia de respuestas mediante una estrategia de prompting con **Few‑Shot + CoT refinado** basada en casos del Case Book, incorporando ejemplos representativos al *System Prompt* (o a un componente de prompt equivalente) y validando el comportamiento en escenarios clave.

## Alcance

- Incluye: selección/curación de ejemplos, diseño de estructura de prompt, integración en el sistema, pruebas manuales/automáticas con prompts de evaluación.
- No incluye: cambios en el corpus/ingestión (salvo los mínimos necesarios para referenciar casos), ni cambio de modelo LLM.

## Criterios de éxito (del conjunto)

- [ ] El modelo aplica criterios coherentes en situaciones típicas (protesta pese a infracción previa; fin de obligación de dar espacio en marca).
- [ ] Los ejemplos few-shot son trazables a casos reales y están redactados para generalizar (no “overfit” al texto literal).
- [ ] Hay un set de evaluación reproducible (prompts + expected behaviors) para validar regresiones.

## Tareas incluidas

- [ ] `BL-2026-008` — Actualización de ejemplos few-shot (Casos 1 y 2)
  - Archivo: `./BL-2026-008 - actualizacion-de-ejemplos-few-shot.md`
- [ ] `BL-2026-009` — Diseño e integración de FS‑CoT refinado (estructura + validación)
  - Archivo: `./BL-2026-009 - diseno-e-integracion-fs-cot-refinado.md`

## Enlaces

- Issue (si existe):
- Docs / referencias:

