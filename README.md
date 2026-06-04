# DIIA — Trabajo final

Baseline para la elaboración del trabajo final de la Diplomatura en Inteligencia Artificial Aplicada (DIIA). Última versión de la PoC elaborada para la materia PLN — 02/05/2026.

**RAG en producción (E11 retrieval + E13 prompt v3):** corpus JSONL en `corpus/processed/`, cupos 2+3+2+1, perfil `production`. Ver [`docs/PERFIL_PRODUCTIVO.md`](docs/PERFIL_PRODUCTIVO.md). Evaluación: [`eval/README.md`](eval/README.md) · resumen corridas: [`eval/RESUMEN_CORRIDAS_EVAL.md`](eval/RESUMEN_CORRIDAS_EVAL.md).

**Registro para el informe final:** [`docs/REGISTRO_TRABAJO_INFORME_FINAL.md`](docs/REGISTRO_TRABAJO_INFORME_FINAL.md) · bitácora: [`docs/REGISTRO_BITACORA.md`](docs/REGISTRO_BITACORA.md) · **comparativa E0 vs E12:** [`docs/INFORME_CITAS_E0_vs_E12.md`](docs/INFORME_CITAS_E0_vs_E12.md)

## Tablero y tareas

El trabajo se organiza con **GitHub Issues** (llamamos **tareas** a los ítems de evolución mediante la plantilla «Tarea»), un **Project** tipo tablero y **Milestones** para agrupar por objetivo (ej.: *Redefinir persistencia del RAG*).

Como complemento opcional, existe un **backlog local versionado** en `backlog/` para ideas/tareas aún no creadas como Issue (o para trabajo offline).

| Recurso | Enlace |
|--------|--------|
| **Issues / nuevas tareas** | [Ir a Issues](https://github.com/marcehluna/DIIA_trabajo_final/issues) |
| **Project (tablero)** | [DIIA — Tablero de tareas](https://github.com/users/marcehluna/projects/2) · [Otros projects del repo](https://github.com/marcehluna/DIIA_trabajo_final/projects) |
| **Milestones** | [Ir a Milestones](https://github.com/marcehluna/DIIA_trabajo_final/milestones) |
| **Backlog local (opcional)** | Ver `backlog/README.md` y `backlog/backlog.md` |

### Tablero en GitHub

Ya existe el project **[DIIA — Tablero de tareas](https://github.com/users/marcehluna/projects/2)** vinculado a este repositorio. En la vista del tablero podés ajustar columnas (por ejemplo **Backlog** · **En curso** · **Hecho**) según la plantilla que prefieras.

### Milestones

Los milestones agrupan tareas por entrega u objetivo técnico. Ya hay uno de ejemplo: [Redefinir persistencia del RAG](https://github.com/marcehluna/DIIA_trabajo_final/milestone/1). Para sumar más: [Milestones](https://github.com/marcehluna/DIIA_trabajo_final/milestones) → **New milestone**. Al crear o editar una issue, asigná el milestone en la barra lateral.

### Plantillas al crear una issue

- **Bug** — errores y comportamiento incorrecto.
- **Tarea** — evolución planificada (feature, refactor, docs, etc.).

Ambas mencionan asignar milestone después de crear el ítem.

### Para quien revise el repo

Podés [abrir una issue](https://github.com/marcehluna/DIIA_trabajo_final/issues/new/choose) eligiendo plantilla; los comentarios quedan en el hilo de cada tarea.
