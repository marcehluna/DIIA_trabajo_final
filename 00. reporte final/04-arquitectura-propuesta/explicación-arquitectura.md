### Explicación de la arquitectura RAG

Guía de lectura del diagrama funcional [`arquitectura-rag.drawio`](arquitectura-rag.drawio). Describe la PoC de asistente de protestas náuticas en su perfil productivo: retrieval léxico con cupos 2+3+2+1 y respuesta con prompt estructurado en español.

---

## Qué muestra el diagrama

El diagrama divide la solución en **tres franjas horizontales**, de arriba hacia abajo. Cada franja corresponde a un momento distinto del ciclo de vida: primero se **prepara** el conocimiento normativo, luego se **consulta** cuando alguien analiza una protesta, y por último se **mide** el sistema cuando cambia el código o la configuración. Las flechas discontinuas indican dependencias que cruzan capas —por ejemplo, el índice construido offline alimenta el retrieval en tiempo real, y el mismo motor RAG que usa la interfaz también corre en evaluación.

Leer el diagrama de arriba hacia abajo equivale a seguir el flujo completo: *de las fuentes oficiales al informe de protesta, y de ahí a las métricas que validan que el sistema sigue funcionando*.

---

## Capa 1 — Preparación del corpus (offline)

Antes de que un usuario abra la aplicación, el sistema necesita un índice de normas recuperable. Esa preparación ocurre **fuera** de cada consulta.

A la izquierda aparecen las **fuentes**: documentos PDF del Call Book y Case Book (formato oficial de World Sailing) y tablas estructuradas con reglas del RRS y definiciones, derivadas del análisis exploratorio del corpus. Los PDF aportan jurisprudencia de team racing y precedentes; las tablas permiten tratar **cada regla como una unidad** citable, algo que el PDF del RRS no garantiza por sí solo.

Esas fuentes entran al **pipeline de ingesta**, que extrae texto, limpia ruido, asigna metadatos y segmenta el contenido. El resultado es un **corpus procesado y tipado** —RRS, TR CALL, CASE y definiciones— con unos **700 fragmentos** en el perfil actual, cada uno con referencia normativa y contexto asociado.

Al **arrancar** la aplicación, el sistema carga ese corpus y lo materializa como **índice en memoria**: una lista de fragmentos listos para buscar. No hay base de datos ni almacén vectorial externo; el retrieval léxico opera sobre la memoria del proceso en ejecución.

El recuadro de **perfiles** configura qué corpus utilizar y con qué parámetros por defecto. En producción solo entra el corpus procesado; un perfil de línea base conserva la configuración histórica (solo PDF) para comparar evoluciones. Los perfiles actúan sobre la carga offline, pero condicionan todo lo que sigue.

**Idea clave de esta capa:** sin ingesta previa no hay contexto de calidad; sin índice en memoria no hay consulta rápida.

---

## Capa 2 — Consulta RAG en tiempo real

Es el camino que recorre cada protesta cuando alguien usa la PoC. Un **usuario** —capitán, comisión o juez— redacta en la **interfaz web** el relato de la protesta y del protestado. Esa entrada no va directo al modelo: primero pasa por el recuadro central del **pipeline de protestas**, que orquesta el flujo RAG paso a paso.

1. **Componer consulta.** Se unen ambos relatos en un único texto de búsqueda, con los términos que el retrieval necesita para hacer coincidencia léxica.
2. **Recuperación.** Sobre el índice en memoria (flecha discontinua desde la capa 1), un ranking **léxico** selecciona los ocho fragmentos más relevantes. No se relee el corpus en cada consulta: se usa la lista ya cargada.
3. **Cupos por tipo.** De esos ocho espacios se reservan **dos para RRS, tres para TR CALL, dos para CASE y uno para definición**. Así ningún tipo de documento monopoliza el contexto cuando hay cientos de reglas en el índice.
4. **Formatear contexto.** Los fragmentos elegidos se presentan con cabeceras legibles que identifican regla, call o caso, para que el modelo sepa qué está citando.
5. **Prompt en español.** Se arma la instrucción al modelo con estrategia de razonamiento paso a paso: citar normas, argumentar y cerrar con una decisión explícita en formato fijo.
6. **Modelo de lenguaje.** Un servicio local ejecuta el LLM (Qwen 2.5 14B vía Ollama) y devuelve el texto generado.
7. **Respuesta estructurada.** Vuelve a la interfaz un informe con citas RRS / TR CALL / CASE, rationale y decisión.

En paralelo, la **consola de actividad** (línea discontinua desde el recuperador) registra qué fragmentos se obtuvieron y qué modelo se usó, para auditar el contexto sin revisar registros del servidor.

**Idea clave de esta capa:** el LLM no “sabe” el reglamento de memoria; cada respuesta se **ancla** a fragmentos recuperados del índice. Si el retrieval falla, el informe carece de base normativa aunque el modelo redacte bien.

---

## Capa 3 — Evaluación offline (golden set)

La tercera franja no participa en el uso cotidiano de la demo, pero es la que **validó** las capas anteriores. Contiene un **conjunto fijo de quince casos reales** —el golden set— con relatos, reglas esperadas, TR CALL, dictamen y respuesta ideal de referencia.

Un proceso de evaluación batch invoca el **mismo pipeline de protestas** que la interfaz (flecha «mismo pipeline» desde la capa 2), caso por caso, con o sin inferencia del modelo (modo solo recuperación para probar el índice). Sobre cada corrida se calculan **métricas**: recall de reglas y CALL en el contexto, precisión de citas, solapamiento léxico y coincidencia de dictamen.

La **regresión** compara esas métricas contra umbrales mínimos acordados para recuperación y respuesta. Si una modificación futura rompe un piso definido, el cambio se detecta antes de dar por cerrada la evolución.

**Idea clave de esta capa:** no mide un sistema distinto al productivo; mide el **mismo flujo** bajo entradas fijas y criterios repetibles.

---

## Cómo encajan las tres capas

| Relación | Qué significa en la práctica |
|----------|------------------------------|
| Capa 1 → Capa 2 | El índice en memoria alimenta el recuperador en cada consulta. Actualizar el corpus implica regenerar el índice y reiniciar la aplicación. |
| Capa 2 → Capa 3 | La evaluación reutiliza el pipeline de protestas; las métricas reflejan el comportamiento real de la demo, no un sustituto simplificado. |
| Perfiles → todo | El perfil productivo fija corpus, cupos y prompt validados; el perfil de línea base permite comparar contra la versión inicial sin reescribir la lógica. |

En una lectura rápida del diagrama, conviene seguir **dos hilos**:

- **Hilo productivo (capas 1 y 2):** fuentes → corpus procesado → índice → usuario → recuperación con cupos → prompt → modelo local → informe.
- **Hilo de validación (capa 3):** golden set → mismo pipeline → métricas → regresión.

---

## Lectura en una frase

La arquitectura prepara normas náuticas en un índice compacto y tipado, recupera en cada consulta los fragmentos más pertinentes bajo cupos fijos, genera con un LLM local un informe citado y auditable en español, y verifica periódicamente —con el mismo motor— que recuperación y respuesta siguen cumpliendo los objetivos medidos en evaluación.

Para el detalle de módulos, tablas por componente y diagrama técnico del código, ver [`arquitectura-propuesta.md`](arquitectura-propuesta.md) y [`arquitectura-tecnica.drawio`](arquitectura-tecnica.drawio).
