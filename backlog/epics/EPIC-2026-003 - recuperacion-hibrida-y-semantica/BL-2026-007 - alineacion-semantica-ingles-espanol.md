# Tarea pendiente

## ID

`BL-2026-007`

## Epic

`EPIC-2026-003` — ver `./EPIC-2026-003 - recuperacion-hibrida-y-semantica.md`

## Título

Alineación semántica Inglés–Español (Tesauro técnico multilingüe)

## Objetivo

Dado que el relato del usuario es en español y el Case Book está en inglés, crear un **Tesauro Técnico Multilingüe** (ej.: “Keep Clear” ↔ “Mantenerse alejado”, “Tacking” ↔ “Virando”) para cerrar la brecha idiomática durante la búsqueda vectorial, especialmente en modelos locales.

## Contexto

La recuperación semántica puede degradarse cuando consulta y corpus están en distintos idiomas. Un tesauro de equivalencias y variantes (términos técnicos, sinónimos, frases) permite expansión de consulta, enriquecimiento de chunks y/o metadatos de términos normalizados.

## Criterios de aceptación

- [ ] Se define un formato versionable para el tesauro (por ejemplo YAML/JSON/CSV) con: término, idioma, equivalencias, variantes y notas.
- [ ] Incluye un set inicial de términos técnicos de regatas (mínimo: maniobras, derechos de paso, acciones típicas, frases clave como “keep clear”).
- [ ] Existe una estrategia de uso clara en retrieval: expansión de query en español hacia inglés (y/o viceversa) y normalización.
- [ ] Hay pruebas/ejemplos reproducibles que muestren mejora: queries en español recuperan pasajes en inglés relevantes sin introducir ruido excesivo.
- [ ] Se documenta cómo mantener/extender el tesauro (criterios para agregar términos y validar).

## Plan

- Relevar un glosario inicial (RRS + vocabulario típico del Case Book) y priorizar términos de alta frecuencia/impacto.
- Definir formato del tesauro y convención de normalización (lowercase, lemas, multiword).
- Implementar un componente de “expansión” (query → términos equivalentes) y decidir dónde se aplica (pre-retrieval, metadata, ambos).
- Agregar tests/experimentos con consultas reales en español y verificación de resultados.
- Iterar el tesauro según errores de recuperación (falsos positivos/negativos).

## Enlaces

- Issue (si existe):
- Docs / referencias:

