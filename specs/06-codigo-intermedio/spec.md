# Spec — 06-codigo-intermedio (Tercetos)
**Grupo:** A · **Lenguaje de implementación:** Python (con `ply.yacc`)

---

## 1. Objetivo

Obtener las estructuras que generan los tercetos en `sintactico.py` para agregarla a la traduccion de la gramatica, utilizando una Lista de Tercetos, una Pila Simbólica (Pila de Operandos) y una Pila (Pila de Saltos).

---

## 2. Alcance y Reglas de Generación
- El compilador debe mantener una lista de tercetos.
- Cada terceto generado tendrá el formato: `[operador, operando1, operando2]`, ej: 22(+, b, 0 ).
- El identificador del terceto está dado por su número de orden (ej. 1, 2, 3). Cuando una operación necesita el resultado de un terceto anterior, guardará la referencia a su número (ej. `"t22"`)
- **Pila Simbólica:** Si se lee un operando (`ID` o `CTE_ENTERA`), se apila. Si se reduce un operador, se desapilan los dos últimos elementos, se genera el terceto y se apila.
- **Pila de Saltos:** Las estructuras de control (`if`, `while`, `and`, `or`) generarán tercetos de salto incompletos (`BF` para Bifucacion si Falso, `BI` para Bifurcacionn Incondicional) que apilarán su índice. Al finalizar el bloque, se desapilará el índice y se completará el destino del salto.
  - Las comparaciones devuelven numéricamente `-1` (verdadero) o `0` (falso).
  - La evaluación lógica de `AND` y `OR` debe ser en cortocircuito.

---

## 3. Estructura de Tercetos por Regla Gramatical
Cada accion semantica para cada regla

**Uso de Marcadores:** como `ply.yacc` ejecuta las acciones al finalizar una producción completa, para cualquier estructura que requiera generar saltos tempranos, apilar índices o abortar evaluaciones en el medio de una regla (como el inicio de un `while`  la condición de un `if`), se deberá agregar marcadores o reglas vacías (ej. `m_marcador : empty`) en la gramática donde sea necesario.

### 3.1 Operando simples y Reglas intermedias
- **Operandos (`<factor> ::= ID | CTE_ENTERA`):** No generan tercetos 
**Acción:** Apilar el valor literal (`p[1]`) directamente en la pila simbolica.
- **Reglas intermedias(ej. `<termino> ::= <factor>`, `<expresion_aritmetica> ::= <termino>`):** No generan tercetos ni alteran las pilas. 
**Acción:** Solo suben la referencia en el árbol sintáctico (`p[0] = p[1]`).

-
  - **Acción:** Si es un `ID`, se resuelve primero su ámbito activo mediante `usar_variable_ts(p[1])` obteniendo su clave con alcance (ej. `a@main_b1`) y se apila dicha clave en la pila simbólica (si se desea mantener el nombre plano en `tercetos.txt`, se apila `clave_var` o se registra el alcance). Si es `CTE_ENTERA`, se registra en la Tabla de Símbolos y se apila su valor literal (`p[1]`).

### 3.1 Expresiones Aritméticas y Relacionales
*   **Regla:** `<expr> ::= <expr> OP <term>` (Suma, Resta, Multiplicación, División, Comparadores).
*   **Acción:** Sacar los dos últimos elementos de la pila, Generar el terceto con la operación que le corresponde (convirtiendo el nombre del token léxico a su símbolo). Ejemplo: `3('*', '2', 'b')` y apilar la referencia a este nuevo terceto (ej. `"t3"`).


### 3.2 Asignaciones
*   **Regla:** `<asignacion> ::= ID ASIG <expresion_log> ';'`
*   **Acción:** Luego de resolver el ambito, generar el terceto `['=', p[1], p[3]]` (Ej: `27 (=, a, T26)`), con el id y el ultimo elemento de la pila que seria el resultado de la expresion.

 ### 3.3 Estructura While 
*   **Al iniciar el `while` (antes de evaluar la condición):**
    *   **SE TIENE QUE SABER EL COMIENZO DEL WHILE:** Se debe guardar el paso (el número del próximo terceto a generar, correspondiente a la condición).
    *   Apilar este número de paso en la pila.
*   **Al reducir la condición:**
    *   **Se tiene que saber el fin del while:** Se debe generar y escribir el terceto de Bifurcación si Falso (`BF`), dejándolo incompleto. Ejemplo: `['BF', condicion, '--']`.
    *   Guardar el salto apilando el número de este terceto `BF` en la pila de saltos. 
*   **Al finalizar el bloque `while`:**
    *   **Fin de la condición (desapilar dos veces):** Se deben sacar los dos valores guardados en la pila de saltos.
    *   Una vez para saber **dónde está el salto**: El primer valor desapilado es el número del terceto `BF`. A ese terceto en la lista se le debe agregar el número actual (para que no pase y salte todo si la confirmación es falsa).
    *   Otra vez para saber **dónde está el comienzo**: El segundo valor desapilado es el paso inicial. Se tiene que escribir la Bifurcación Incondicional (`BI`) usando este valor en el espacio correspondiente (para retornar al comienzo y que se quede en el while). : `['BI', '--', valor_inicio]`.

### 3.4 Operadores Lógicos (AND / OR)
-   **Para el operador `OR`:**
    *   **Se tiene que saber si ya es verdadero:** Si el primer operando de un `OR` es verdadero (`-1`), el resto no se evalúa. Se genera un terceto de Bifurcación si Verdadero (`BV`) incompleto hacia el final de la expresión y se apila.
    **Al terminar de reducir la regla `OR` completa:** Se desapilan los operandos simbólicos, se genera `['OR', op1, op2]`, se apila su referencia `"tN"`, y se desapila el indice de la `pila_saltos` para completar el `BV` con su destino, el número del próximo terceto a generar.
-   **Para el operador `AND`:**
    *   **Se tiene que saber si ya es falso:** Si el primer operando es falso (`0`), el resto no se evalúa. Se genera un `BF` incompleto y se apila.
-   **Al terminar de reducir el `AND`:** Se desapilan los operandos simbólicos, se genera `['AND', op1, op2]`, se apila su referencia `"tN"`, y se desapila de `pila_saltos` para completar el `BF`.


### 3.5 Sentencias de Salida y Retorno (PRINT / RET)
-   **Regla `PRINT`:** `<salida> ::= PRINT '(' CADENA ',' <expresion_log> ')' ';'`
    * **Variante 1 (Cadena y Expresión):** `<salida> ::= PRINT '(' CADENA ',' <expresion_log> ')' ';'`
        * **Acción:** Desapilar el último elemento de la pila simbólica (`resultado_expr`) y generar el terceto: `['PRINT', CADENA, resultado_expr]`.
    * **Variante 2 (Solo Cadena):** `<salida> ::= PRINT '(' CADENA ')' ';'`
        * **Acción:** No altera la pila simbólica. Generar directamente el terceto: `['PRINT', CADENA, '--']`.
    * **Variante 3 (Solo Expresión):** `<salida> ::= PRINT '(' <expresion_log> ')' ';'`
        * **Acción:** Desapilar el último elemento de la pila simbólica (`resultado_expr`) y generar el terceto: `['PRINT', '--', resultado_expr]`.
-   **Regla `RET`:** `<retorno> ::= RET <expresion_log> ';'`
    *   **Acción:** Desapilar el resultado a retornar de la pila. Generar el terceto de retorno: `['RET', resultado_expr, '--']`.
    

### 3.6 Estructura If - Else
-   **Al reducir la condición del `if`:**
    *   **Se tiene que saber a dónde saltar si es falso:** Se debe generar y escribir el terceto de Bifurcación si Falso (`BF`), dejándolo incompleto. Ejemplo: `['BF', condicion, '--']`.
    *   Guardar el salto apilando el número de este terceto `BF` en la pila de saltos.
-   **Al finalizar el bloque `if` (y antes de evaluar el `else`):**
    *   **Salto para esquivar el `else`:** Se debe generar un terceto de Bifurcación Incondicional (`BI`) incompleto. Para que si se ejecutó el bloque verdadero, se salte el bloque falso. Ejemplo: `['BI', '--', '--']`.
    *   **Fin de la condición desapilar una vez:** Se debe sacar el valor guardado en la pila (el ultimo `BF` de la condición). A ese terceto se le debe completar el destino con el número del terceto actual, el inicio del bloque `else`.
    *   **Guardar el salto de salida:** Apilar el número del nuevo terceto `BI` en la pila.
-   **Al finalizar el bloque `else`:**
    *   **Fin de toda la estructura (desapilar una vez):** Se debe completar el terceto indicado en el cuerpo del if. Se debe sacar el último valor guardado en la pila (el `BI` generado para esquivar el `else`). A ese terceto se le debe completar el destino agregándole el número actual para que el programa continúe normalmente.
-   **Caso If simple (sin else):**
    *   Al finalizar el bloque `if`, se desapila el índice de la `pila_saltos` y se completa el `BF` original apuntando al próximo terceto a generar.


### 3.7 Declaración y Llamado de Funciones
Las funciones deben generar tercetos para su punto de inicio, envío de parámetros, y llamado a ejecución.
*   **Inicio de funcion(`<funcion>`):** Para comenzar una funcion se define una etiqueta de inicio para que se pueda saltar a ella.
    *   **Acción:** Generar `['FUNC', nombre_funcion, '--']`.
*   **Paso de Parámetros (`<lista_parametros>` en llamada):** Cada parámetro enviado en una llamada a función debe generar un terceto individual que lo prepare para la ejecución.
    *   **Acción:** Desapilar el resultado de la expresión del parámetro y generar `['PARAM', resultado_parametro, '--']`.
*   **Llamado a Función (`<llamada_funcional>`):** Tras preparar todos los parámetros, se debe generar la instrucción que salta a la ejecución de la función.
    *   **Acción:** Generar `['CALL', nombre_funcion, cantidad_parametros]`. El resultado de la función (si devuelve un valor) se debe asociar al identificador del terceto recién creado.

---

## 4. Entradas y Salidas Modificadas
*   **Entradas:** Archivo fuente válido leído por el analizador léxico.
*   **Salidas:** Además de validar la gramática, al finalizar el análisis con éxito, impresión en consola y generación del archivo `tercetos.txt` con la lista numerada de tercetos generados en orden. Ejemplo:
    `22 (>, a, 0)`
    `25 (BF, t22, 31)`
    `27 (=, a, t26)`


## 5. Criterios de Aceptación
-   La generación de código intermedio debe ejecutarse estrictamente a la par de las reducciones sintácticas dictadas por la gramática.
-   La pila de saltos debe gestionarse de forma limpia para soportar cualquier tipo de anidamiento múltiple (`if` dentro de `while`, `while` dentro de `if-else`, etc.) sin sobrescribir ni perder referencias de salto.
-   Bajo ninguna circunstancia pueden quedar tercetos de salto (`BF`, `BI`) con destinos indefinidos o incompletos (ej. `'--'`) tras finalizar el análisis sintáctico de un bloque válido.




