### 06. Conclusiones

Reflexión crítica sobre el proceso, limitaciones encontradas y aprendizajes del trabajo.

---

## Síntesis del logro

Dentro del marco de la **Diplomatura en Inteligencia Artificial Aplicada (DIIA)**, el **Taller de Trabajo Final** tomó una PoC de asistente RAG para protestas náuticas — desarrollada en la materia de **Procesamiento de Lenguaje Natural (PLN)** — y la llevó a un **perfil productivo reproducible**: retrieval **E11** (corpus JSONL estructurado, cupos 2+3+2+1, retriever léxico) y respuesta **E13** (prompt v3 en español, formato auditable con citas y línea `Decisión:`).

Frente a la línea base **E0** (solo Call Book y Case Book en PDF, sin RRS en el índice), el sistema actual **duplica** el recall de reglas RRS en top-8 (0.41 → 0.76) y pasa de un **dictamen automático inexistente** (0 %) a una coincidencia gruesa del **60 %** con el golden set de 15 casos. No se trata de un producto listo para comisión de regata en producción, sino de una **PoC evaluada** que demuestra que un pipeline RAG local puede acelerar el análisis normativo de protestas de Team Racing cuando el corpus está bien segmentado y la salida del modelo está acotada por diseño.

El entregable integra más que código: análisis exploratorio del corpus (sección 03), justificación de decisiones por evidencia (sección 02), arquitectura funcional y técnica (sección 04), 18 corridas de evaluación documentadas E0–E17 (sección 05) y regresión automatizada en `profiles.py`. Esa trazabilidad resultó tan relevante como las métricas finales para cerrar el trabajo final de la DIIA.

---

## Reflexión crítica sobre el proceso

### De intuición a diseño por evidencia

El punto de partida (E0) ya funcionaba como demo: Gradio, chunking de PDF, retrieval léxico y Qwen en español. El salto del Taller no consistió en reescribir la arquitectura, sino en **instalar un método de mejora**: golden set fijo, métricas por capa, corridas que aíslan una variable a la vez y umbrales de regresión. Sin ese marco, la incorporación de RRS al índice (E3) podría haberse interpretado erróneamente como un empeoramiento del sistema, cuando en realidad el contexto se **diluía** al mezclar ~1 389 chunks sin cupos.

La lección metodológica más sólida del proyecto es **separar retrieval de generación**. Las corridas E1 y E16 (`--retrieval-only`) permitieron iterar índice, ingesta y cupos sin costo de LLM; E12–E13 demostraron que, una vez fijado E11, el cuello de botella ya no era «encontrar la norma» sino «cerrar un informe parseable». Esa lectura en dos capas evitó optimizar el prompt mientras el índice seguía fallando, o viceversa.

### El EDA como filtro de hipótesis — y fricción con el trabajo previo

Antes de las corridas masivas, el análisis exploratorio del corpus (sección 03) acotó el espacio de búsqueda: el PDF del RRS no segmenta por regla; el Case Book domina el volumen; el troceo por página o por ventana fija de tokens no alinea unidades normativas. El EDA no reemplazó la evaluación con golden set, pero **orientó** hacia JSONL tipado y cupos por `doc_type` en lugar de perseguir un `chunk_size` óptimo universal.

Una fricción relevante del proceso fue **definir y revisar métricas de EDA** cuando parte del corpus y del pipeline ya provenían de la materia PLN: hubo que reconciliar análisis nuevo con decisiones heredadas (chunking por página, índice solo PDF) sin repetir trabajo ni contradecir lo ya construido. En retrospectiva, invertir tiempo en entender los datos antes de tunear hiperparámetros de RAG resultó rentable; la dificultad estuvo en acordar qué del EDA **cambiaba** el diseño y qué solo **documentaba** la línea base.

### Iteración disciplinada, documentación y criterio de cierre

Las 18 corridas (E0–E17, sin E5) no constituyen ruido documental: registran **por qué** se descartaron alternativas razonables. El índice *full* con cupos (E6–E7) recuperó parte del baseline pero quedó pesado frente a JSONL puro; la salida en inglés (E14) mejoró citas léxicas pero degradó el dictamen medido en español; el retrieval híbrido (E15–E17) igualó o mejoró casos aislados sin superar a E13 en F1 ni decisión.

Paralelamente, la **documentación sistemática de cada corrida** — diario, métricas, comparativas, informes por run — resultó **laboriosa y consumidora de tiempo**, casi tanto como ejecutar los experimentos. Otro desafío metodológico fue **decidir cuándo detener la experimentación**: con hardware local, cada corrida completa (15 casos × LLM) imponía un costo de tiempo que limitaba el barrido de variantes; el cierre en E11+E13 se basó en umbrales de regresión cumplidos y en experimentos posteriores (E14, E17) que no justificaron reabrir el perfil productivo, no en agotar todas las combinaciones posibles.

### Artefactos de evaluación y honestidad metodológica

El proyecto también evidenció aprendizajes sobre **cómo medir**. En E12/E13 el F1 RRS de la corrida original subestimaba citas porque el parser no reconocía el formato del prompt; tras ampliar `refs.py`, las métricas reflejaron mejor la realidad. Ese episodio obligó a distinguir entre «el modelo no cita» y «la evaluación no parsea». La incorporación de `rescore_eval_citations.py`, faithfulness opcional y matrices contexto→cita (A/B/C/D) refuerza que las métricas son **instrumentos** sujetos a revisión, no verdades absolutas.

### Alcance académico, dominio náutico y despliegue operativo

El trabajo se desarrolló en forma individual, con alcance de PoC de diplomatura: LLM local (Ollama + Qwen), interfaz Gradio, índice en memoria, golden set derivado del Excel *Casos de Regatas*. La **experiencia propia como regatista** funcionó como validación informal de dominio — interpretación de incidentes, priorización de reglas y lectura de dictámenes — pero **no** sustituyó una validación con comisión de regata ni con volumen de protestas de un campeonato. La reflexión crítica admite que el éxito medido es **interno al protocolo de evaluación acordado**; extrapolar a campo requiere otro ciclo de validación humana institucional.

---

## Limitaciones encontradas

### Cobertura y representatividad del golden set

El conjunto de evaluación tiene **15 casos**, extraídos del Case Book y validados manualmente contra el Excel *Casos de Regatas*. Es suficiente para comparar configuraciones y detectar regresiones, pero **no** para estimar desempeño en producción ni cubrir la diversidad de incidentes en agua. Casos como el 7 (regla 21.2) o el 14 (D1.1(e)) siguen siendo puntos débiles pese al recall agregado alto. Un 60 % de acierto en dictamen automático implica que **cuatro de cada diez** protestas del golden set no cierran como la referencia humana.

### Brecha idioma corpus ↔ relato ↔ métricas

El corpus normativo está en **inglés**; los relatos y el golden set en **español**. El retriever léxico funciona porque el índice JSONL enriquece headers, referencias cruzadas y metadatos, pero la brecha persiste en Jaccard respuesta↔contexto (muy bajo en E13) y en la lectura de faithfulness. E14 mostró que redactar en inglés alinea léxicamente al corpus pero **perjudica** el dictamen medido contra referencias en español. El multilingüismo no quedó resuelto de forma unificada; se priorizó coherencia con el relato del usuario y el informe del curso.

### Recall de Call Book y citas TR CALL

Al priorizar reglas RRS (cuello de botella principal), el perfil E11 acepta un **R@k CALL de 0.20**, por debajo del baseline PDF E0 (0.27). En la comparativa caso a caso de E13, muchas respuestas **no citan** el TR CALL esperado aunque a veces aciertan el dictamen — señal de que el modelo apoya la decisión en reglas genéricas o en contexto parcial. Las citas espurias (códigos tipo `M10`, `A3` fuera de lugar) indican que la trazabilidad normativa sigue siendo frágil en casos complejos.

### Dependencia del formato de salida y del parser

El salto de dictamen 0 % → 60 % está ligado al **prompt v3** y a un parser de citas y decisiones que reconoce viñetas y la línea `Decisión:`. Cambios de redacción del LLM, temperatura o modelo pueden romper métricas sin que cambie la calidad sustantiva del razonamiento. El sistema es auditable **en la medida en que el modelo obedece la plantilla** — no garantiza corrección jurídica.

### Infraestructura, tiempo de cómputo y escalabilidad

La PoC carga el índice en RAM al arranque y ejecuta inferencia en **hardware local**. Las corridas completas de evaluación — especialmente las que invocan el LLM para los 15 casos del golden set — constituyeron una **limitación práctica** por el tiempo que consumían, lo que condicionó cuántos experimentos era viable ejecutar y reforzó la necesidad de corridas `--retrieval-only` cuando solo cambiaba el índice. No se contempla multiusuario, versionado de corpus en caliente ni integración con sistemas de gestión de regatas. El híbrido semántico quedó como experimento opt-in por costo computacional y por regresiones observadas en E17. Para un despliegue institucional harían falta API estable, autenticación, trazas persistentes y revisión humana obligatoria del dictamen.

### Rol del asistente respecto del juez

El diseño asume que la IA **asiste** al comité, no lo reemplaza. Aun con R@k alto y dictamen parcialmente correcto, faltan verificación de hechos, confrontación de versiones contradictorias y aplicación de criterios de ponderación que un IU humano aporta. La limitación no es solo técnica sino **de gobernanza**: sin un flujo de aprobación humana, un 40 % de error en dictamen automático sería inaceptable en competencia oficial.

---

## Aprendizajes del proceso

### Sobre RAG en dominios normativos especializados

En corpus legales o reglamentarios, el rendimiento de RAG depende menos del modelo generativo elegido (se mantuvo Qwen entre E0 y E13) y más de **cómo se representa el conocimiento**. Un chunk por regla, un call o un case superó la intuición inicial sobre tamaños de ventana en PDF. Los cupos por tipo de documento son un mecanismo simple pero efectivo para evitar que el Case Book — más del 55 % del volumen — opaque señales del Call Book y del RRS. La experiencia náutica del autor orientó qué incidentes y qué normas eran prioritarios al armar el golden set y al leer respuestas fuera de las métricas automáticas.

### Sobre evaluación de sistemas generativos

La construcción del golden set, la definición de métricas por capa y la automatización de regresión permitieron **operacionalizar** conceptos como «buena respuesta»: recall de contexto, F1 de citas, dictamen, faithfulness y matrices de diagnóstico responden preguntas distintas. Ninguna sola métrica basta. La regresión en `test_production_profile.py` convirtió criterios acordados en **contratos ejecutables** — un aprendizaje transferible a otros proyectos de IA aplicada.

### Sobre iteración, documentación y costo de experimentar

El diario de corridas (`eval/DIARIO_PRUEBAS.md`, `eval/RESUMEN_CORRIDAS_EVAL.md`) y el registro de trabajo del informe evitaron perder el hilo entre experimentos. Documentar E14 y E17 como «no adoptados» con la misma rigurosidad que E11 y E13 facilita defender decisiones ante revisores meses después. **La memoria del proyecto es parte del entregable**; su costo en tiempo fue elevado, pero resultó indispensable para no confundir correlaciones con mejoras reales y para fijar el momento de cierre.

### Sobre el vínculo PLN → Taller (DIIA)

La materia **PLN** aportó el esqueleto funcional (pipeline, Gradio, CoT, stack local). El **Taller de Trabajo Final** aportó **ingeniería de datos y evaluación**: ingesta reproducible, perfiles de configuración, separación baseline/productivo. El aprendizaje integrador de la DIIA es que una demo de PLN y un sistema evaluable difieren en corpus, métricas y disciplina de cambio — no solo en pulir prompts. Retomar trabajo previo exige explicitar qué se conserva, qué se mide de nuevo y qué se descarta con evidencia.

### Sobre trabajo individual y experto de dominio

Al desarrollarse el proyecto en solitario, las funciones de desarrollo, evaluación, documentación y criterio náutico recayeron en una misma persona. Eso agilizó decisiones, pero concentró el riesgo de sesgo: la validación de dominio como regatista no equivale a consenso de un comité de protestas. Para un producto aplicable, el siguiente paso natural es **separar** validación técnica (métricas, regresión) de validación operativa (jueces, comisión, escenarios reales).

---

## Perspectiva y trabajo futuro

El horizonte deseable del proyecto no es solo académico: **apuntar a un producto aplicable** en el ecosistema de regatas — club, comisión de protestas o circuito de Team Racing — con flujo de revisión humana obligatoria. Las mejoras de mayor impacto probable, dado lo aprendido, son:

1. **Piloto con usuarios reales** — comisión o jueces de club probando informes E13 sobre protestas reales o simulacros, con feedback cualitativo además del golden set.
2. **Ampliar y diversificar el golden set** — más casos, dictámenes revisados por un IU, cobertura de TR CALL y casos límite (p. ej. regla 21.2).
3. **Refinar citas TR CALL** — cupos, enriquecimiento de chunks de calls o postproceso de citas, sin sacrificar el recall de reglas logrado en E11.
4. **Infraestructura de despliegue** — API, autenticación, trazas persistentes e integración con formularios de protesta, reduciendo dependencia de corridas lentas en hardware local.

El retrieval híbrido con fallback semántico (E16) merece revisión si se priorizan casos con poco solapamiento léxico ES–EN, pero solo si la capa de respuesta no regresa como en E17. A mediano plazo, confrontación de relatos contradictorios, extracción estructurada de entidades náuticas y trazas explicativas persistentes alinearían la PoC con el problema original del capítulo 1 (subjetividad narrativa y cuello de botella operativo). La base técnica y el marco de evaluación ya están para sostener ese siguiente ciclo sin rehacer el proyecto desde cero.

---

## Cierre

El asistente de protestas náuticas del Taller de Trabajo Final de la DIIA no resuelve el arbitraje humano, pero **reduce incertidumbre en el pipeline RAG**: demuestra que se puede recuperar la norma relevante, generar un informe estructurado en español y medir si el sistema mejora o empeora con cada cambio. Las limitaciones — golden set pequeño, brecha bilingüe, dictamen parcial, tiempo de cómputo local, validación de dominio sin comisión externa — definen con claridad qué quedó probado y qué no. Esa frontera entre logro y pendiente es, en sí misma, el resultado maduro de un trabajo final basado en evidencia, con una proyección explícita hacia un asistente útil en la práctica regatística.
