## 5.5 Conclusiones sobre la Evolución de las Métricas

A partir del análisis sistemático de las corridas experimentales y la documentación del diario de pruebas, se consolidan las siguientes conclusiones metodológicas y de ingeniería de software respecto a la evolución del sistema RAG:

### 5.5.1 El Progreso Tecnológico como un Fenómeno Bicapa

La evidencia empírica demuestra que la optimización del asistente inteligente no se comportó como un salto cuantitativo aislado, sino como la maduración secuencial de dos capas operativas fuertemente acopladas:

- **Optimización de la Capa de Recuperación (E0 a E11):** El primer ciclo evolutivo se concentró de forma exclusiva en robustecer la zapata de conocimiento. El indicador *Recall@k* de las reglas generales del RRS escaló de un débil 0.41 a un sobresaliente **0.76** (un incremento del 85 % relativo frente a la línea base E0), lo que confirma de forma matemática que el contexto inyectado al prompt suele incluir ya las normas regulatorias esperadas por el *Golden Set*.
- **El Compromiso de Diseño en el Recobrado del Call Book:** En el balanceo del índice, el *Recall@k* de los códigos CALL se situó en **0.20** en el perfil productivo frente al 0.27 original del PDF crudo. Este desvío marginal constituyó un compromiso táctico (*trade-off*) plenamente aceptado: se sacrificó una fracción menor de recall en la jurisprudencia del Call Book a cambio de consolidar un índice sustancialmente más compacto (~707 chunks) y drásticamente más fuerte en el recobrado de reglas generales, neutralizando el principal cuello de botella detectado en el dominio de las protestas náuticas.
- **Saturación del Prompt Heredado (Hito E11):** Al alcanzar la corrida E11, el indicador F1-score de citas en la respuesta (≈ 0.25) se situaba en el mismo orden de magnitud que la línea base E0 (0.22) y el dictamen automático permanecía en **0 %**. Este diagnóstico evidenció que contar con un contexto rico en información resulta estéril si el prompt no obliga al modelo a adoptar un formato de salida estructurado y citable, localizando la ineficiencia en la capa de generación y no en el índice de búsqueda.
- **Optimización de la Capa de Respuesta y Trazabilidad (E11 a E13):** Durante este segundo ciclo, los indicadores de recuperación permanecieron estáticos debido a que se mantuvo el mismo índice y política de cuotas. El progreso se localizó en la ingeniería de instrucciones (prompt v3), logrando elevar la coincidencia del dictamen automatizado al **60 %** del total de casos y estabilizando el F1-score de las reglas en un 0.22 tras alinear el parser programático con las viñetas estructuradas de la salida.

### 5.5.2 Balance de los Experimentos Alternativos Descartados

- **Evaluación de la Salida en Idioma Inglés (E14):** Forzar la respuesta en el idioma nativo del corpus (E14) incrementó el F1-score del RRS en un +0.10 y elevó el solapamiento léxico respuesta-contexto unas 15 veces (Jaccard de 0.01 a 0.16). No obstante, esta alineación gramatical reducía la precisión del dictamen al 40 % y deterioraba la similitud semántica frente al *Output Ideal* escrito en español. Aunque el experimento E14 demostró ser un proxy valioso para auditorías de fidelidad conceptual (*faithfulness*), fue descartado debido a que sacrificaba la utilidad práctica del informe de arbitraje local.
- **Evaluación de la Recuperación Híbrida Vectorial (E15 a E17):** El uso de embeddings híbridos puros sin funciones de contingencia (E15) dañó el recall debido a la asimetría idiomática de las consultas. Si bien la introducción de un soporte semántico (*fallback*) igualó los techos de recuperación de la búsqueda léxica (E16), la ejecución integrada de todo el pipeline con el prompt v3 (experimento E17) provocó regresiones en la capa de generación, deprimiendo el dictamen correcto al 47 %. En consecuencia, se rechazó la adopción del motor híbrido en producción.

### 5.5.3 Justificación y Consolidación del Perfil de Producción

La integración unificada de las configuraciones **E11** y **E13** constituye la opción óptima para el despliegue del sistema. Aunque no exhibe valores perfectos en el espectro completo de las métricas crudas, representa la única arquitectura capaz de satisfacer simultáneamente los umbrales de regresión mandatorios y alinear las tres dimensiones operativas exigidas por el dominio: traer las normas aplicables al prompt (E11), resolver el dictamen de forma auditable (E13) y emitir el veredicto final en idioma español.

Las alternativas técnicas evaluadas a lo largo de la investigación quedan descartadas y debidamente documentadas bajo los siguientes criterios de ingeniería:

1. El baseline histórico E0 no recupera las reglas esenciales del RRS.
2. Los índices masivos en bruto (*full*) sin cupos provocan la dilución semántica de la jurisprudencia.
3. La configuración E10 sacrifica críticamente el recall del Call Book.
4. El experimento E14 maximiza las métricas léxicas pero daña la precisión de la toma de decisiones.
5. La variante híbrida E17 introduce inestabilidad analítica y no supera al enfoque léxico enriquecido en la resolución del conflicto.

El par productivo seleccionado se encuentra plenamente consolidado en el software (REGATAS_PROFILE=production, profiles.py) y respaldado por pruebas de regresión automáticas en el entorno de integración continua. Esta rigidez de diseño proporciona un entorno de ejecución altamente reproducible, fijando una base sólida para futuras expansiones del conocimiento —tales como la ampliación del *Golden Set* o el refinamiento fino de las instrucciones del modelo— sin necesidad de reabrir la arquitectura del índice ni el motor de recuperación core.

### 5.5.4 Guía de Diagnóstico Práctico para Mantenimiento Evolutivo

A partir de las lecciones aprendidas en la matriz de experimentos, se define una heurística de lectura técnica para aislar fallas funcionales ante futuras modificaciones en el código fuente:

- **Falla en R@k** → Inspeccionar corpus, ingesta o cupos documentales.
- **Falla en F1-score o dictamen** → Inspeccionar ingeniería de prompts o postproceso.

Esta heurística condensa la lección principal del ciclo experimental: recuperación y generación maduraron en fases distintas y emiten señales métricas diferentes. Ante una regresión, conviene leer primero R@k (reglas y TR CALL) frente a F1 de citas y dictamen en la misma corrida; si el contexto recuperado se mantiene pero caen el veredicto o las citas parseables, el trabajo debe concentrarse en prompt y postproceso —no en reabrir corpus, ingesta ni cupos. Corridas con `--mode retrieval` permiten confirmar ese diagnóstico sin volver a inferir el LLM. El hito E11 lo ilustró de forma contundente: con retrieval alto y dictamen automático en 0 %, el cuello de botella ya no estaba en el índice. Para futuras evoluciones del sistema, esa demarcación acota el radio de cambio, reduce rework y preserva el par E11+E13 como núcleo validado mientras se itera en instrucciones, parser de citas o ampliación del golden set.
