# Épica

## ID

`EPIC-2026-007`

## Milestone

`M-YYYY-NNN` — (link en `backlog/milestones/`, si aplica)

## Título

Definir e implementar mecanismo de persistencia del RAG

## Objetivo

Definir y poner en producción un **mecanismo de persistencia** para el índice RAG (embeddings y metadatos asociados a chunks), de modo que no sea necesario recompute completo en cada arranque y se pueda versionar o migrar el almacén según el corpus.

## Alcance

- Incluye: elección de formato de persistencia (por ejemplo almacén vectorial embebido o archivo local versionable), carga incremental o rebuild controlado, invalidación cuando cambie el corpus, documentación operativa.
- No incluye: rediseño completo del modelo de recuperación ni cambios de prompting salvo los estrictamente necesarios para integrar la persistencia.

## Criterios de éxito (del conjunto)

- [ ] Tras un reinicio del servicio, el retriever puede **reutilizar** el índice persistido sin re-embedding completo obligatorio (salvo configuración explícita de rebuild).
- [ ] Existe un procedimiento claro para **reconstruir** el índice cuando cambien los PDF o los parámetros de chunking/embeddings.
- [ ] La persistencia es **trazable** (ubicación, versión del corpus o hash de fuentes si aplica).

## Tareas incluidas

- [ ] (pendiente) Definir tareas `BL-YYYY-NNN` y enlazarlas aquí.

## Enlaces

- Issue (si existe):
- Docs / referencias:
