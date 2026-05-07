# Backlog (local)

Este directorio complementa (no reemplaza) la gestión principal de trabajo en **GitHub Issues + Project**.

## ¿Para qué sirve?

- Mantener un **backlog versionado** dentro del repo (útil para trabajo offline, revisión histórica en commits, o cuando no querés abrir una issue todavía).
- Registrar tareas pequeñas o ideas que luego pueden “promocionarse” a una Issue.

## Flujo recomendado

- Crear una nueva entrada en `backlog/backlog.md`.
- Alternativa: crear un archivo por tarea en `backlog/tareas-pendientes/`.
- Cuando una tarea esté lista para ejecutarse: crear Issue (plantilla “Tarea”) y copiar el link en el ítem del backlog.
- Al terminar: marcar como **Hecho** en el backlog y cerrar la Issue (si aplica).

## Convenciones de IDs

Usá IDs cortos y estables para poder referenciarlos en commits:

- Formato sugerido: `BL-YYYY-NNN` (ej.: `BL-2026-001`)
- Milestones locales: `M-YYYY-NNN` (ej.: `M-2026-001`) en `backlog/milestones/`

