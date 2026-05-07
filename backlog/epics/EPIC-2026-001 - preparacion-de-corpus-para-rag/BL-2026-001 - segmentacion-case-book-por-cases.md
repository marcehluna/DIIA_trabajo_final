# Tarea pendiente

## ID

`BL-2026-001`

## Epic

`EPIC-2026-001` — ver `./EPIC-2026-001 - preparacion-de-corpus-para-rag.md`

## Título

Segmentación del Case Book por “CASES” (parser por `CASE \d+`)

## Objetivo

Implementar un parser que detecte el patrón `CASE \d+` como delimitador de documento único y extraiga subsecciones internas **Rules**, **Facts**, **Question** y **Decision** para estructurar el Case Book.

## Contexto

El Case Book contiene múltiples casos concatenados. Para mejorar el procesamiento (indexado / búsqueda / RAG), necesitamos separar cada caso en un documento individual y, dentro de cada caso, capturar sus secciones relevantes.

## Criterios de aceptación

- [ ] El parser detecta correctamente cada nuevo caso usando el patrón `CASE \d+` (sin perder contenido entre delimitadores).
- [ ] Para cada caso, se extraen las subsecciones: **Rules**, **Facts**, **Question**, **Decision** (cuando existan) y se preserva el texto completo de cada una.
- [ ] Si alguna subsección no existe o está vacía, el parser lo representa de forma explícita (por ejemplo, campo ausente o `null`) sin fallar.
- [ ] Se conserva el **texto completo del caso** (raw) además de las subsecciones (para trazabilidad).
- [ ] Se definen pruebas/fixtures con al menos: un caso “completo”, un caso con secciones faltantes y un caso con variaciones de formato (espacios/saltos de línea).

## Plan

- Relevar el formato real del Case Book (variantes de encabezados y separadores).
- Implementar segmentación por regex robusta para `CASE \d+` (con captura de número y límites).
- Implementar extracción de secciones internas (Rules/Facts/Question/Decision) con tolerancia a variaciones.
- Definir el esquema de salida (por ejemplo: `{case_id, raw_text, rules, facts, question, decision}`) y serialización (JSON/objeto).
- Agregar pruebas automatizadas con fixtures representativos.

## Enlaces

- Issue (si existe):
- Docs / referencias:

