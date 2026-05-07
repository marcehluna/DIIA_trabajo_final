# Tarea pendiente

## ID

`BL-2026-008`

## Epic

`EPIC-2026-004` — ver `./EPIC-2026-004 - fase-4-estrategia-de-prompting-fs-cot-refinado.md`

## Título

Actualización de ejemplos few-shot (curación desde el Case Book para el System Prompt)

## Objetivo

Revisar y curar ejemplos del Case Book para incluirlos como **few-shot** en el *System Prompt* (o prompt base), priorizando:

- **Caso 1**: enseñar que un barco mantiene su derecho a protestar incluso si cometió una infracción previa.
- **Caso 2**: reforzar la lógica de cuándo termina la obligación de dar espacio en marca (por ejemplo, cuando el barco deja la zona).

## Contexto

Los ejemplos few-shot bien elegidos ayudan a estabilizar criterios y reducen respuestas inconsistentes. La clave es redactarlos de manera generalizable (regla/criterio → aplicación) y alinearlos con la forma de consulta del usuario.

## Criterios de aceptación

- [ ] Se identifican y extraen del Case Book los fragmentos relevantes de **Caso 1** y **Caso 2** (con trazabilidad: IDs, citas o links).
- [ ] Se redactan ejemplos few-shot “limpios” (input → respuesta esperada) que enseñen el **criterio** y no dependan de detalles irrelevantes.
- [ ] Los ejemplos incluyen el contexto mínimo necesario y un estilo consistente con la respuesta final deseada (idioma, tono, formato).
- [ ] Se valida manualmente con prompts de prueba que el modelo aplica:
  - [ ] derecho a protestar pese a infracción previa (Caso 1)
  - [ ] fin de obligación de dar espacio en marca al salir de zona (Caso 2)
- [ ] Se documenta dónde viven los ejemplos (archivo/ruta) y cómo actualizarlos.

## Plan

- Relevar el texto de los Casos 1 y 2 y extraer el “núcleo” que se quiere enseñar.
- Diseñar formato de ejemplo (pregunta del usuario → razonamiento/criterio → respuesta final), alineado al prompt base.
- Incorporar los ejemplos al lugar donde se construye el prompt (System Prompt o plantilla equivalente).
- Definir un set pequeño de prompts de evaluación y correr una validación antes/después.

## Enlaces

- Issue (si existe):
- Docs / referencias:

