# Tarea pendiente

## ID

`BL-2026-002`

## Epic

`EPIC-2026-001` — ver `./EPIC-2026-001 - preparacion-de-corpus-para-rag.md`

## Título

Limpieza de ruido bibliográfico (eliminar códigos de origen al final de cada caso)

## Objetivo

Usar RegEx para eliminar las referencias de origen al final de cada caso (ej.: `GBR 1962/25` o `USA 1962/87`) para evitar que “ensucien” el embedding semántico con códigos que el usuario no buscará.

## Contexto

Al final de cada caso aparecen códigos bibliográficos de referencia (país + año + identificador) que aportan poco valor semántico para búsqueda en lenguaje natural y pueden sesgar embeddings. Se requiere removerlos de forma consistente sin afectar el contenido relevante del caso.

## Criterios de aceptación

- [ ] Se detectan y eliminan referencias del tipo `AAA YYYY/NN` (ej.: `GBR 1962/25`, `USA 1962/87`) cuando aparecen **al final del caso** (con tolerancia a espacios/saltos de línea).
- [ ] La limpieza no elimina texto que no sea referencia bibliográfica (evitar falsos positivos en el cuerpo del caso).
- [ ] Se soportan variaciones razonables de formato (múltiples referencias, separadores, líneas finales vacías).
- [ ] Se agregan tests/fixtures con casos: referencia única, múltiples referencias, ausencia de referencia y un ejemplo con patrón parecido en el cuerpo del texto (no debe borrarse).
- [ ] Se documenta la RegEx final (patrón y supuestos) en la implementación o en un doc breve del módulo correspondiente.

## Plan

- Relevar ejemplos reales de “referencias de origen” en el Case Book (formatos y variaciones).
- Definir una RegEx anclada a fin de documento/caso (y/o a las últimas líneas) para minimizar falsos positivos.
- Implementar función de limpieza y aplicarla al pipeline de preparación de documentos (antes de embeddings).
- Crear fixtures y tests automatizados.
- Validar en un lote de casos que la limpieza reduce tokens “ruidosos” sin pérdida de información relevante.

## Enlaces

- Issue (si existe):
- Docs / referencias:

