# Capítulo 2: Análisis Exploratorio de Datos (EDA) y Fase de Descubrimiento

## 2.1 Caracterización del Corpus Normativo
Antes de consolidar los procesos de ingesta, fragmentación (*chunking*) y recuperación (*retrieval*), se realizó un Análisis Exploratorio de Datos (EDA) sobre el corpus normativo de referencia. Este corpus está compuesto por tres documentos oficiales en formato PDF emitidos por *World Sailing* que rigen de forma global el arbitraje en el deporte: el Reglamento de Regatas a Vela (RRS) [1], el *Call Book for Team Racing* [2] y el *Case Book* [3].

El volumen consolidado del corpus en bruto asciende a un total de **599 páginas** y aproximadamente **782 000 caracteres** extraídos mediante herramientas programáticas. La distribución cuantitativa de las páginas por documento se detalla en la siguiente tabla y se ilustra en la **Figura 2.1**:

<table style="width:100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px;">
  <thead>
    <tr style="background-color: #f2f2f2; border-bottom: 2px solid #ddd;">
      <th style="padding: 10px; text-align: left;">Documento</th>
      <th style="padding: 10px; text-align: center;">Páginas</th>
      <th style="padding: 10px; text-align: center;">Caracteres (Extracción Limpia)</th>
      <th style="padding: 10px; text-align: center;">Representación Relativa</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid #ddd;">
      <td style="padding: 10px; text-align: left;"><strong>RRS 2025–2028</strong> (Reglamento General)</td>
      <td style="padding: 10px; text-align: center;">160</td>
      <td style="padding: 10px; text-align: center;">~233 000</td>
      <td style="padding: 10px; text-align: center;">29.8 %</td>
    </tr>
    <tr style="border-bottom: 1px solid #ddd; background-color: #f9f9f9;">
      <td style="padding: 10px; text-align: left;"><strong>Call Book for Team Racing</strong></td>
      <td style="padding: 10px; text-align: center;">111</td>
      <td style="padding: 10px; text-align: center;">~121 000</td>
      <td style="padding: 10px; text-align: center;">15.5 %</td>
    </tr>
    <tr style="border-bottom: 1px solid #ddd;">
      <td style="padding: 10px; text-align: left;"><strong>Case Book WS 2025–2028</strong></td>
      <td style="padding: 10px; text-align: center;">328</td>
      <td style="padding: 10px; text-align: center;">~428 500</td>
      <td style="padding: 10px; text-align: center;">54.7 %</td>
    </tr>
    <tr style="border-bottom: 2px solid #ddd; font-weight: bold; background-color: #e6e6e6;">
      <td style="padding: 10px; text-align: left;">Consolidado Total</td>
      <td style="padding: 10px; text-align: center;">599</td>
      <td style="padding: 10px; text-align: center;">~782 000</td>
      <td style="padding: 10px; text-align: center;">100.0 %</td>
    </tr>
  </tbody>
</table>

Como se observa, el *Case Book* concentra más del 55 % del volumen total del texto, lo que introdujo un desafío inicial: un algoritmo de ordenamiento global no indexado por tipo de documento tendería a sobre-representar los casos generales de este libro, diluyendo las señales específicas del *Call Book*, esenciales para la modalidad de regatas por equipos [4][6].

> **[CONFIGURACIÓN DE GRÁFICO 2.1]**
> * **Ubicación en Metricas.docx:** Gráfico bajo el título "Cantidad de páginas por documento".
> * **Tipo de gráfico:** Gráfico de barras simples con etiquetas superiores (328, 160, 111).
> * **Pie de figura:** *Figura 2.1: Distribución absoluta de páginas por tipo de documento dentro del corpus normativo.*

---

## 2.2 Métricas de Volumen y Geometría Textual

### 2.2.1 Distribución de Longitud por Página
Se evaluó la cantidad de caracteres por página de manera independiente para cada uno de los tres textos mediante una estimación de densidad de kernel (KDE). El análisis determinó si el corpus era homogéneo en densidad o si existían colas que pudiesen sesgar el *chunking*.

> **[CONFIGURACIÓN DE GRÁFICO 2.2]**
> * **Ubicación en Metricas.docx:** Gráfico "Distribución de longitud de página (corpus)".
> * **Tipo de gráfico:** Tres histogramas de densidad con curvas KDE superpuestas.
> * **Pie de figura:** *Figura 2.2: Distribución de densidad y perfil geométrico de caracteres por página en el corpus bruto.*

**Implicancia en el diseño:** El análisis demostró perfiles geométricos sumamente heterogéneos. Mientras el RRS presenta páginas cortas con picos de densidad bimodal debido a tablas y señales, el *Case Book* exhibe bloques densos de texto de casos. Esto confirmó la hipótesis de que no existe un único tamaño fijo de fragmento (*chunk*) óptimo para el corpus completo si este se procesa en bruto, forzando a segmentar respetando fronteras normativas (regla, *Call*, caso) y no la geometría de la página [6].

### 2.2.2 Validación del Pipeline de Limpieza de Texto
A fin de asegurar que la remoción de ruido no afectara la integridad conceptual del texto, se comparó la extracción cruda (`pypdf` [9]) frente a una extracción refinada con `pdfplumber` [8], aplicando colapso de espacios, normalización de cadenas (`strip`) y remoción de metadatos de citación bibliográfica secundaria.

> **[CONFIGURACIÓN DE GRÁFICO 2.3]**
> * **Ubicación en Metricas.docx:** Gráfico "Caracteres por bloque de ~10 páginas: pypdf vs pdfplumber (limpio)".
> * **Tipo de gráfico:** Tres paneles de barras agrupadas (Azul: Antes, Naranja: Después) en ventanas de 10 páginas.
> * **Pie de figura:** *Figura 2.3: Comparativa de volumen de caracteres en ventanas de diez páginas para la validación del proceso de limpieza.*

**Implicancia en el diseño:** Las barras demostraron un comportamiento paralelo y una reducción marginal y predecible de volumen en todo el espectro del documento. Esto validó que el pipeline de producción reduce el ruido de codificación de manera homogénea sin provocar recortes accidentales en el cuerpo principal de las normas.

---

## 2.3 Análisis Léxico y Barreras Idiomáticas

### 2.3.1 Análisis de Palabras Vacías (Stop Words)
Se cuantificó la proporción de tokens alfabéticos que corresponden a conectores funcionales y palabras vacías utilizando una lista optimizada para el dominio náutico (donde verbos modales críticos como *must* o *may* y sustantivos como *call* fueron preservados). Los resultados arrojaron valores de presencia de *stopwords* situados entre el 44 % y el 49 % (RRS: 47.1 %, Call Book: 44.2 %, Case Book: 49.3 %).

> **[CONFIGURACIÓN DE GRÁFICO 2.4]**
> * **Ubicación en Metricas.docx:** Gráfico "Proporción de stop words por documento (inglés)".
> * **Tipo de gráfico:** Gráfico de barras simples con porcentajes indicados en el tope.
> * **Pie de figura:** *Figura 2.4: Porcentaje de palabras vacías identificadas sobre tokens alfabéticos.*

### 2.3.2 Distribución de Frecuencia de Términos
Excluyendo las palabras vacías, se extrajeron los términos léxicos de mayor ocurrencia en el corpus para identificar el sesgo temático y el ruido normativo.

> **[CONFIGURACIÓN DE GRÁFICO 2.5]**
> * **Ubicación en Metricas.docx:** Gráficos "Top 18 términos por documento".
> * **Tipo de gráfico:** Tres diagramas de barras horizontales independientes ordenados por frecuencia descendente.
> * **Pie de figura:** *Figura 2.5: Análisis comparativo de los 18 términos técnicos más frecuentes por documento normativo.*

**Implicancia en el diseño:** Este análisis reveló el vocabulario dominante de cada libro (v.g. *shall*, *rule*, *boat*, *mark*, *case*) y anticipó de manera temprana la brecha lingüística del sistema: el corpus técnico está completamente redactado en **inglés**, mientras que las consultas empíricas y los relatos de los regatistas se producen en **español** — asimetría relevante para el diseño de recuperación en arquitecturas RAG [5][6].

### 2.3.3 Rareza Léxica del Vocabulario Global
Para verificar el nivel de dispersión y fragmentación de las señales en el índice, se evaluó el vocabulario global compuesto por **4 164 términos distintos** distribuidos en los chunks del índice.

> **[CONFIGURACIÓN DE GRÁFICO 2.6]**
> * **Ubicación en Metricas.docx:** Gráfico "Rareza léxica en el índice (df = nº de chunks que contienen el término)".
> * **Tipo de gráfico:** Barra horizontal segmentada por colores (Rojo: Hapax con df=1 [1557 términos], Amarillo: Raro con df 2-5 [1296 términos], Verde: Frecuente con df>=6 [1311 términos]).
> * **Pie de figura:** *Figura 2.6: Composición y estabilidad del vocabulario global del índice según frecuencia documental.*

**Implicancia en el diseño:** Más del 68 % del vocabulario (hapax y términos raros con frecuencia documental ≤ 5) aparece en muy pocos fragmentos del índice. Esa dispersión indicó que un recuperador basado únicamente en el solapamiento de tokens del cuerpo del texto sería frágil: muchas señales léxicas son únicas y no se repiten entre consulta y fragmento, en particular ante la brecha español–inglés ya señalada en el apartado 2.3.2. No se descartó por ello el enfoque léxico, pero se condicionó su viabilidad al **enriquecimiento de cada fragmento** con identificadores estables y repetibles —número de regla, código TR CALL, sección y reglas referenciadas en cabecera— que concentran términos de mayor frecuencia documental y anclan la búsqueda a unidades normativas explícitas [5][6]. El vocabulario global acotado (~4 164 términos sobre el índice de referencia) mostró además que el corpus era manejable sin embeddings densos; la evaluación sistemática posterior confirmó ese criterio frente al experimento de recuperación híbrida.

---

## 2.4 Métricas de Contexto y Tokenización bajo Arquitectura Qwen
A fin de calibrar el motor de recuperación con los límites del Modelo de Lenguaje de evaluación (`Qwen/Qwen2.5-14B-Instruct` [7]), se analizaron los textos utilizando su tokenizador nativo (excluyendo tokens especiales).

### 2.4.1 Volumen del Corpus en Tokens y Capacidad de Cobertura
El corpus completo se traduce en tokens distribuidos de la siguiente manera: RRS con 58 199 tokens, Call Book con 32 921 tokens y Case Book con 107 973 tokens. Al promediar este volumen sobre una ventana estándar de 512 tokens, se constató que una ventana aislada solo es capaz de abarcar el 0.9 % del RRS, el 1.6 % del Call Book y el 0.5 % del Case Book.

> **[CONFIGURACIÓN DE GRÁFICO 2.7]**
> * **Ubicación en Metricas.docx:** Gráficos correlativos "Tokens totales por documento" y "Porción del documento que cabe en 512 tokens".
> * **Tipo de gráfico:** Gráficos de barras simples.
> * **Pie de figura:** *Figura 2.7: Volumen técnico del corpus en tokens y representatividad de una ventana de contexto de 512 tokens.*

**Implicancia en el diseño:** Esto evidenció de forma matemática que el desafío del RAG no reside en la incapacidad del modelo para procesar páginas aisladas, sino en la necesidad crítica de un índice fragmentado, dado que el volumen total del conocimiento normativo excede por varios órdenes de magnitud los límites de representatividad de una única ventana [5][6].

---

## 2.5 Calidad de la Extracción Técnica y Estructura Escondida
Se auditaron las anomalías de diseño de los PDF y los defectos de layout mediante herramientas estadísticas para verificar que no hubiese pérdida de contenido útil.

### 2.5.1 Distribución Física y Páginas Vacías
Se cruzó la distribución de longitud de caracteres de pdfplumber mediante diagramas de caja junto con el indicador de páginas casi vacías (menos de 50 caracteres), el cual actúa como detector de fallos de OCR o páginas puramente gráficas.

> **[CONFIGURACIÓN DE GRÁFICO 2.8]**
> * **Ubicación en Metricas.docx:** Gráficos combinados "Distribución de longitud por página" y "Páginas casi vacías".
> * **Tipo de gráfico:** Boxplot de caracteres por página al lado de un gráfico de barras.
> * **Pie de figura:** *Figura 2.8: Auditoría de longitud de caracteres físicos y tasa de páginas sin contenido de texto extraíble.*

### 2.5.2 Fragmentación Fina y Artefactos de Impresión
Para caracterizar el ruido de layout, se midió la densidad de palabras partidas al final del renglón (patrones de guión más salto de línea `-\n`) y el porcentaje de líneas muy cortas (menos de 4 caracteres), que indican fragmentación por columnas o encabezados ruidosos.

> **[CONFIGURACIÓN DE GRÁFICO 2.9]**
> * **Ubicación en Metricas.docx:** Gráficos combinados "Cortes palabra–guión–salto de línea" y "Líneas con menos de 4 caracteres".
> * **Tipo de gráfico:** Gráficos de barras simples.
> * **Pie de figura:** *Figura 2.9: Identificación programática de guionación por composición y líneas fragmentadas por layout.*

**Implicancia en el diseño:** Los resultados confirmaron que el texto digitalizado era completamente usable y libre de fallos masivos de fuentes o Unicode. El incremento de páginas con bajo volumen de texto en el *Case Book* (7.32 %) resultó consistente con la presencia legítima de diagramas tácticos e ilustraciones de maniobras que interrumpen la prosa.

---

## 2.6 Diagnóstico de la Fragmentación Basada en Ventanas de Tokens
Para configurar de forma sólida la fragmentación, se simuló un índice sintético basado en una ventana deslizante fija de 512 tokens con un solape de 128 tokens.

### 2.6.1 Comportamiento Geométrico de las Ventanas Fijas
Al graficar la longitud resultante de los fragmentos, se observó que los percentiles p50, p90 y p95 se fijaron exactamente en el techo de **512 tokens**. Los fragmentos se forzaban a completarse artificialmente, sin alineación alguna con las unidades o reglas náuticas [6].

> **[CONFIGURACIÓN DE GRÁFICO 2.10]**
> * **Ubicación en Metricas.docx:** Gráficos combinados "Distribución de longitud de chunks (512 / solape 128)" y "Chunks por documento".
> * **Tipo de gráfico:** Diagrama de cajas horizontales junto con su gráfico de barras de volumen de chunks.
> * **Pie de figura:** *Figura 2.10: Simulación geométrica de la saturación de tokens bajo una estrategia de fragmentación por ventana fija.*

### 2.6.2 Densidad Léxica y Cobertura de Embeddings en Producción
Frente a la ventana fija, se contrastó el comportamiento de los fragmentos reales del pipeline de producción (~1 247 chunks bajo la configuración de 900 caracteres / 120 solape por página), analizando la riqueza léxica y la cantidad de tokens Qwen por fragmento respecto al techo del encoder.

> **[CONFIGURACIÓN DE GRÁFICO 2.11]**
> * **Ubicación en Metricas.docx:** Gráficos combinados "Cobertura léxica por fragmento" y "Proxy de cobertura para embeddings".
> * **Tipo de gráfico:** Dos diagramas de cajas y bigotes con línea de referencia roja en los 512 tokens.
> * **Pie de figura:** *Figura 2.11: Distribución de la densidad de términos léxicos y volumen de tokens reales en los chunks de producción.*

**Implicancia en el diseño:** Los diagramas de caja confirmaron que la gran mayoría de los chunks reales se agrupan de forma compacta (p50 en 193 y p90 en 231 tokens), quedando muy lejos del límite de saturación de embeddings de 512 tokens. Esto demostró matemáticamente que el problema del RAG no radicaba en el truncamiento de vectores, sino en la **granularidad semántica**: recortar basándose en caracteres fijos mezclaba múltiples normas o fragmentos de casos incompletos en un mismo fragmento [6].

---

## 2.7 Síntesis: Decisiones de Arquitectura Derivadas del EDA
El proceso de exploración de datos cumplió un rol fundamental en el modelado del sistema. En lugar de orientar el esfuerzo hacia la búsqueda de hiperparámetros numéricos tradicionales (como el tamaño exacto de la ventana), el EDA redireccionó las decisiones de ingeniería del proyecto hacia la reestructuración del corpus, tal como se sintetiza a continuación:

<table style="width:100%; border-collapse: collapse; margin-top: 10px;">
  <thead>
    <tr style="background-color: #f2f2f2; border-bottom: 2px solid #ddd;">
      <th style="padding: 10px; text-align: left; width: 40%;">Evidencia Hallada en el EDA</th>
      <th style="padding: 10px; text-align: left; width: 60%;">Decisión de Ingeniería Implementada</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid #ddd;">
      <td style="padding: 10px; text-align: left;">La fragmentación por ventanas físicas fijas colapsa en el límite y rompe la continuidad lógica de las reglas y los casos normativos.</td>
      <td style="padding: 10px; text-align: left;">Abandono del procesamiento en PDF plano y migración hacia un formato <strong>JSONL estructurado y tipado</strong> por unidad normativa (~707 registros explícitos) [6].</td>
    </tr>
    <tr style="border-bottom: 1px solid #ddd; background-color: #f9f9f9;">
      <td style="padding: 10px; text-align: left;">Asimetría de volumen crítico: el 55 % del corpus pertenece al <i>Case Book</i>, amenazando con saturar el <i>retrieval</i>.</td>
      <td style="padding: 10px; text-align: left;">Implementación de una estrategia de <strong>cupos fijos por tipo de documento</strong> en el <code>top_k</code> del contexto para balancear la jurisprudencia [5][6].</td>
    </tr>
    <tr style="border-bottom: 1px solid #ddd;">
      <td style="padding: 10px; text-align: left;">La relación de conversión de caracteres a tokens es estable y compacta (~190-230 tokens por chunk de producción), sin riesgo de truncamiento en el encoder.</td>
      <td style="padding: 10px; text-align: left;">Mantenimiento de la configuración de seguridad (900 caracteres / 120 de solapamiento) únicamente como contingencia para textos residuales.</td>
    </tr>
    <tr style="border-bottom: 1px solid #ddd; background-color: #f9f9f9;">
      <td style="padding: 10px; text-align: left;">Asimetría idiomática estructural: consultas empíricas en español frente a un marco regulatorio nativo en inglés.</td>
      <td style="padding: 10px; text-align: left;">Optimización del motor mediante un enfoque de <strong>recuperación léxica avanzada</strong> con enriquecimiento semántico de encabezados estructurados [5][6].</td>
    </tr>
  </tbody>
</table>

En soluciones RAG sobre corpus normativos —heterogéneos en volumen, idioma y estructura, como el de protestas náuticas— el EDA no es un paso accesorio previo al desarrollo, sino una fase que **acota qué conviene optimizar**. Sin este análisis, el esfuerzo técnico habría gravitado hacia hiperparámetros genéricos (tamaño de ventana, embeddings densos, índices híbridos) que el propio corpus demostró secundarios: el cuello de botella no era truncar vectores ni afinar un número mágico de caracteres, sino **alinear cada fragmento con una unidad citable** y **equilibrar qué normas entran al contexto**. El EDA tradujo esas restricciones del dominio en decisiones de ingeniería verificables —corpus estructurado, cupos por tipo de documento, recuperación léxica enriquecida— antes de invertir en corridas costosas de evaluación con LLM. En ese sentido, la exploración de datos y el golden set cumplen roles complementarios: el primero reduce el espacio de búsqueda arquitectónica; el segundo mide si la configuración elegida cumple los objetivos del sistema. Para un dominio especializado, conocer la geometría y el léxico del corpus resulta tan determinante como elegir el modelo de lenguaje.

---

## Referencias bibliográficas

[1] World Sailing. (2024). *The Racing Rules of Sailing 2025–2028*. Federación internacional de vela. https://www.sailing.org/racingrules/

[2] World Sailing. (2025). *The Call Book for Team Racing 2025–2028* (8.ª ed.). https://www.sailing.org/document/2025-2028-call-book-for-team-racing/

[3] World Sailing. (2025). *World Sailing Case Book 2025–2028*. https://www.sailing.org/document/world-sailing-case-book-2025-2028/

[4] World Sailing. (s. f.). *RRS — Introduction* (publicaciones complementarias: Case Book, Call Books, interpretaciones). https://www.racingrulesofsailing.org/rules

[5] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html

[6] Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M., & Wang, H. (2024). Retrieval-augmented generation for large language models: A survey. *arXiv preprint* arXiv:2312.10997. https://arxiv.org/abs/2312.10997

[7] Qwen Team. (2024). Qwen2.5 technical report. *arXiv preprint* arXiv:2412.15115. https://arxiv.org/abs/2412.15115

[8] Vine, J. (s. f.). *pdfplumber* (biblioteca de extracción de texto PDF utilizada en el proyecto). https://github.com/jsvine/pdfplumber

[9] py-pdf. (s. f.). *pypdf* (biblioteca de lectura de PDF utilizada en el proyecto). https://github.com/py-pdf/pypdf