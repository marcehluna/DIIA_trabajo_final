# Tarea pendiente

## ID

`BL-2026-004`

## Epic

`EPIC-2026-002` — ver `./EPIC-2026-002 - enriquecimiento-de-metadatos.md`

## Título

Inyección de referencias cruzadas (reglas mencionadas en `Rules` → metadatos)

## Objetivo

Extraer mediante RegEx todas las reglas mencionadas en la sección **Rules** de cada caso (ej.: `Rule 10`, `Rule 14`) y guardarlas como una lista en los metadatos del documento/chunk.

Objetivo funcional: si el usuario menciona “Regla 18”, el recuperador debe traer no solo el reglamento (RRS), sino también los casos del Case Book asociados a esa regla.

## Contexto

Hoy la asociación “caso ↔ regla” está implícita en el texto. Al convertir esas menciones a metadatos explícitos (por ejemplo `referenced_rules: [10, 14]`), se habilita filtrado/boosting y recuperación más confiable por consultas centradas en reglas.

## Criterios de aceptación

- [ ] Se extraen menciones a reglas desde la sección **Rules** (no desde cualquier parte del texto), soportando variaciones comunes (mayúsculas/minúsculas, espacios, plural, puntuación).
- [ ] Las reglas se normalizan a una forma canónica (por ejemplo: números enteros, o strings tipo `RRS-10`), y se deduplican.
- [ ] Se guardan como lista en metadatos del documento/chunk (definir clave, ej.: `referenced_rules`).
- [ ] Hay fixtures con: una regla, múltiples reglas, reglas repetidas, y un caso sin reglas (lista vacía).
- [ ] Prueba de integración (o experimento reproducible) demuestra que una query “Regla X” recupera casos asociados además del RRS.

## Plan

- Confirmar el formato real de la sección **Rules** en el Case Book y definir el patrón de extracción.
- Implementar extractor y normalizador (parser → lista de reglas).
- Integrar al pipeline de generación de documentos/chunks (agregar metadatos).
- Agregar tests automatizados con fixtures.
- Validar impacto en recuperación: filtro/boosting por `referenced_rules` y comparación antes/después.

## Enlaces

- Issue (si existe):
- Docs / referencias:

