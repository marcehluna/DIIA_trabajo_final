# Golden set — revisión de etiquetas esperadas

Fuente: `/Users/marcelo.luna/Library/CloudStorage/OneDrive-Personal/Diplomaturas/01. Inteligencia Artificial Aplicada/Materias/05. Taller de Trabajo Final/Repositorio/DIIA_trabajo_final/docs/Casos de Regatas.xlsx`  
Generado: `2026-05-25T18:44:45.457297+00:00`  
Casos: **15**

| ID | Título | Reglas RRS esperadas | TR CALL | Casos WS | Dictamen | Penaliza |
|----|--------|----------------------|---------|----------|----------|----------|
| 1 | Orzada brusca sin espacio para mantenerse alejado | 16.1 | A3 | — | penalizar | Y |
| 2 | Sobre-rotación del barco de barlovento proa al viento | 11, 13 | B2 | — | penalizar | B |
| 3 | Retraso en la respuesta al solapamiento desde atrás | 11, 15 | B1 | — | penalizar | Y |
| 4 | Derecho a espacio de marca y pérdida por virada | 18.2(a)(2), 12, 18.2(d) | E1 | — | sin_penalizacion | — |
| 5 | Cambio de rumbo táctico en babor-estribor (Anti-Hunt) | 16.2 | D2 | — | penalizar | B |
| 6 | Incapacidad física de dar espacio de marca al solapar | 18.2(a), 18.2(d) | E2 | — | penalizar | Y |
| 7 | Interferencia durante el cumplimiento de una penalización | 21.2 | L2 | — | penalizar | B |
| 8 | Eliminación de la Regla 18.4 en Team Racing | 18.2(a)(1), D1.1, 18.4 | J5 | — | sin_penalizacion | — |
| 9 | Virada completada libre por proa en la zona | 12, 13, 15 | E6 | — | sin_penalizacion | — |
| 10 | Contacto antes de completar la virada tras cruce | 13 | D4 | — | penalizar | B |
| 11 | Táctica de frenado en la marca (The Trap) | 11, 18.2 | J9 | — | penalizar | X |
| 12 | Provocación de contacto deliberado (Antideportivo) | 10, D2.3(f) | L1 | — | mixto | B |
| 13 | Trasluchada para "apagar" la restricción de la Regla 17 | 17 | G3 | — | sin_penalizacion | — |
| 14 | Interferencia de un barco que ya terminó la regata | D1.1(e) | K1 | — | penalizar | Y |
| 15 | Virada en proa obligando a maniobra evitativa inmediata | 13, 15 | D3 | — | penalizar | B |

## Relatos (Input)

### Caso 1: Orzada brusca sin espacio para mantenerse alejado

> B y Y navegan en la misma amura (babor), solapados. Y es el barco de sotavento. Y comienza a orzar lentamente. B responde de inmediato, pero Y continúa orzando hasta que B ya no puede evitar el contacto. Hay contacto leve.

### Caso 2: Sobre-rotación del barco de barlovento proa al viento

> En la pre-salida, Y (sotavento) y B (barlovento) están solapados. Y orza hacia una posición de "proa al viento". B orza en respuesta. B continúa rotando y pasa de la posición de proa al viento, chocando con el costado de Y.

### Caso 3: Retraso en la respuesta al solapamiento desde atrás

> B establece un solapamiento desde atrás a sotavento de Y muy cerca de la línea de salida. Y puede mantenerse alejada acelerando, pero tarda en reaccionar y luego decide orzar, golpeando a B.

### Caso 4: Derecho a espacio de marca y pérdida por virada

> Y y B se acercan a una boya de barlovento que debe dejarse por babor. B llega a la zona libre por proa de Y. B orza para virar (tack) frente a la boya, pero la presencia de Y por su costado le impide completar la virada.

### Caso 5: Cambio de rumbo táctico en babor-estribor (Anti-Hunt)

> B (estribor) y Y (babor) convergen en ceñida. A 3 esloras, Y vira para pasar por popa de B. B entonces también cae (bear away) manteniendo el rumbo de colisión. Y debe volver a caer bruscamente para evitar a B.

### Caso 6: Incapacidad física de dar espacio de marca al solapar

> Y y B se acercan a una marca de barlovento a dejar por estribor. Y entra en la zona libre por popa de B. Y gana un solapamiento por el interior de B y reclama espacio. B no tiene espacio físico para dejar virar a Y sin chocar.

### Caso 7: Interferencia durante el cumplimiento de una penalización

> B está cumpliendo una penalización de una vuelta. Mientras gira, Y (que no está en penalización) tiene que desviarse para evitar chocar con B.

### Caso 8: Eliminación de la Regla 18.4 en Team Racing

> Y y B solapados en babor hacia la boya de sotavento. Y es interior. Y traslucha a estribor en la zona y orza a B para alejarla de la marca. B es obligada a trasluchar.

### Caso 9: Virada completada libre por proa en la zona

> Y vira en la zona de la marca de barlovento por delante de B. Y completa su virada y queda libre por proa, pero B debe caer inmediatamente para evitar chocar con la popa de Y.

### Caso 10: Contacto antes de completar la virada tras cruce

> B (estribor) cruza por delante de Y (babor). Después de cruzar, B orza y vira a babor. Durante la virada, B choca con Y antes de llegar a rumbo de ceñida.

### Caso 11: Táctica de frenado en la marca (The Trap)

> Tres barcos (B, X, Y) se acercan a una boya por babor. X es el barco más a sotavento y líder. Y y B están solapados por fuera. X frena bruscamente para "atrapar" a B y permitir que su compañero Y pase por el interior. B choca con X.

### Caso 12: Provocación de contacto deliberado (Antideportivo)

> Y navega por la amura de babor. B navega por la amura de estribor. Y tiene que virar para evitar a B, pero durante la maniobra el tripulante de B empuja la botavara hacia afuera deliberadamente para tocar a Y.

### Caso 13: Trasluchada para "apagar" la restricción de la Regla 17

> B y Y están en el tramo de popa, solapados en la misma amura. B es sotavento y tiene restricción de rumbo debido (Regla 17). B traslucha a la amura de babor y vuelve a trasluchar a estribor de inmediato para orzar a Y.

### Caso 14: Interferencia de un barco que ya terminó la regata

> Y ha terminado la regata y está navegando de regreso. En su camino, pasa cerca de B que aún está compitiendo, obligando a B a virar para evitarla.

### Caso 15: Virada en proa obligando a maniobra evitativa inmediata

> B (estribor) y Y (babor) en ceñida. B está claramente por delante y Y pasaría por su popa sin problemas. B decide virar justo en la proa de Y, obligando a Y a virar de inmediato para evitar el choque.

## Output ideal (extracto normativo)

| ID | Fragmento Norma + Decisión |
|----|------------------------------|
| 1 | Hechos: B (barlovento) y Y (sotavento) solapados. Y orza y B responde prontamente. Y sigue orzando hasta que B no puede evitarla.  Norma: Regla 16.1 e interpretación TR CALL A3 . Rationale: Aunque Y es el barco con de… |
| 2 | Hechos: Y y B solapados. Y orza a proa al viento y B responde. B sobre-rota y choca con Y . Norma: Reglas 11 o 13 según TR CALL B2 . Rationale: Y dio espacio inicial para que B respondiera. El contacto fue causado por… |
| 3 | Hechos: B gana solapamiento desde atrás. Y puede mantenerse alejada acelerando pero demora su respuesta y luego orza chocando a B . Norma: Regla 11 según TR CALL B1 . Rationale: B cumplió la Regla 15 al dar espacio in… |
| 4 | Hechos: B entra a la zona libre por proa de Y. B quiere virar pero Y se lo impide . Norma: Reglas 18.2(a)(2) y 12 según TR CALL E1 . Rationale: Y debe dar espacio de marca a B. Sin embargo, si B pasa de la posición de… |
| 5 | Hechos: B en estribor, Y en babor. Y intenta pasar por popa de B. B cae hacia Y obligándola a maniobrar de nuevo . Norma: Regla 16.2 según TR CALL D2 . Rationale: En ceñida, un barco de estribor no puede cambiar de ru… |
| 6 | Hechos: Y entra a la zona libre por popa. Y gana solapamiento interior. B no tiene espacio para dejar virar a Y . Norma: Regla 18.2(a) según TR CALL E2 . Rationale: Si el barco exterior (B) es incapaz de dar espacio d… |
| 7 | Hechos: B tomando penalización. Y debe evitarla . Norma: Regla 21.2 según TR CALL L2 o L5 . Rationale: Un barco que está tomando una penalización debe mantenerse alejado de uno que no lo está haciendo . Decisión: Pena… |
| 8 | Hechos: Y interior solapado. Y traslucha a estribor en la zona y orza a B . Norma: Regla 18.2(a)(1) y Apéndice D (D1.1c) según TR CALL J5 . Rationale: En Team Racing, la Regla 18.4 se borra, por lo que el barco con de… |
| 9 | Hechos: Y vira en la zona. B debe caer para evitarla después de que Y completó su virada . Norma: Regla 12 e interpretación TR CALL E6 . Rationale: Si Y completa su virada sin obligar a B a maniobrar durante la misma … |
| 10 | Hechos: B cruza a Y. B vira y choca con Y antes de completar la virada . Norma: Regla 13 según TR CALL D4 . Rationale: B perdió su derecho de paso al virar. Mientras un barco vira, debe mantenerse alejado de los demás… |
| 11 | Hechos: X frena en la marca para atrapar a B. B choca con X . Norma: Regla 11 y 18.2 según TR CALL J9 . Rationale: X es el barco con derecho de paso y espacio de marca. B (barlovento) debe mantenerse alejada de X inde… |
| 12 | Hechos: Y en babor, B en estribor. Y vira para evitar a B. B empuja la botavara para causar contacto . Norma: Regla 10 y D2.3(f) según TR CALL L1 . Rationale: Es un incumplimiento de la deportividad provocar contacto … |
| 13 | Hechos: B traslucha dos veces. B orza a Y tras las trasluchadas . Norma: Regla 17 según TR CALL G3 . Rationale: Si la trasluchada es real (la vela se llena en la nueva amura), el solapamiento original se rompe y con é… |
| 14 | Hechos: Y ha terminado. B sigue compitiendo. Y obliga a B a maniobrar . Norma: Regla D1.1(e) según TR CALL K1 . Rationale: Un barco que ha terminado no debe interferir con un barco que aún está compitiendo . Decisión:… |
| 15 | Hechos: B vira frente a Y. Y debe virar para evitar contacto . Norma: Regla 13 y 15 según TR CALL D3 . Rationale: B al virar adquiere derecho de paso pero debe dar espacio inicialmente a Y para que se mantenga alejada… |
