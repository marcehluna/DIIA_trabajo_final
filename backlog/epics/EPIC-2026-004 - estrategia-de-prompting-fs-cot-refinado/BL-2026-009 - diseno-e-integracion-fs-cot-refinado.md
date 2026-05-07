# Tarea pendiente

## ID

`BL-2026-009`

## Epic

`EPIC-2026-004` — ver `./EPIC-2026-004 - fase-4-estrategia-de-prompting-fs-cot-refinado.md`

## Título

Diseño e integración de FS‑CoT refinado (estructura del prompt + validación)

## Objetivo

Definir e integrar una estrategia de prompting **FS‑CoT refinado** que use ejemplos curated (few-shot) y reglas de comportamiento para guiar razonamiento consistente, con un set de validación reproducible para evitar regresiones.

## Contexto

Además de “qué ejemplos” usar, es crítico definir “cómo” se usan: cuándo se aplican, cómo evitar sobreajuste, cómo mantener consistencia de formato y cómo validar. Esta tarea arma la estructura de prompt y el harness básico de evaluación.

## Criterios de aceptación

- [ ] Se define una estructura clara de prompt (secciones, orden, estilo) para FS‑CoT refinado.
- [ ] Se especifican reglas de uso: cuándo aplicar ejemplos, cómo manejar incertidumbre, cómo citar reglas/casos (si corresponde).
- [ ] La implementación permite actualizar ejemplos sin tocar lógica (separación “contenido” vs “plantilla”).
- [ ] Existe un set de evaluación reproducible (lista de prompts + criterios esperados) que cubre al menos:
  - [ ] protesta pese a infracción previa
  - [ ] obligación de espacio en marca y finalización al salir de zona
  - [ ] un caso “diferente” para verificar generalización
- [ ] Se documenta el proceso de mantenimiento (cómo agregar un nuevo ejemplo y cómo validar).

## Plan

- Definir el formato objetivo de respuesta (idioma, estructura, nivel de detalle).
- Diseñar plantilla de prompt FS‑CoT refinado (system/developer/user roles según arquitectura).
- Integrar en el punto de construcción del prompt del sistema.
- Armar suite mínima de evaluación (manual o script) con criterios de aceptación.
- Iterar sobre fallos: ajustar plantilla y ejemplos hasta pasar la validación.

## Enlaces

- Issue (si existe):
- Docs / referencias:

