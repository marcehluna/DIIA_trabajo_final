# Milestones (locales)

Los milestones locales permiten definir **entregas/objetivos verificables** y mantener trazabilidad con épicas/tareas dentro del repositorio.

## Convención de IDs

- Formato sugerido: `M-YYYY-NNN` (ej.: `M-2026-001`)

## Trazabilidad (cómo se considera “cumplido”)

- Un milestone se considera **cumplido** cuando **todas** las épicas listadas en ese milestone están completas (y, por transitividad, sus tareas).
- Cada épica debe declarar su milestone en `## Milestone` apuntando al archivo del milestone.

## Archivos

- Crear un archivo por milestone usando `template.md`.

