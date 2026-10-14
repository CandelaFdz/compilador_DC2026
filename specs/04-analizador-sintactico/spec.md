# Spec — 04-analizador-sintactico
**Grupo:** A · **Lenguaje de implementación:** Python (con `ply.yacc`)

---

## Objetivo
Validar que la secuencia de tokens entregada por el analizador léxico cumpla con la gramática, actualizar la tabla de símbolos, y generar el código intermedio en forma de Tercetos.

---

## Alcance
detecta errores de sintaxis indicando la línea y se recupera para seguir analizando el archivo.

---

## Entradas / Salidas
* **Entradas:**
  * Objetos `LexToken(type, value, lineno, lexpos)` emitidos por `lexico.py`.
  * Lista de nombres de tokens (`NOMBRES_TOKENS`) y la `tabla_simbolos` generada.
* **Salidas:**
  * 

---

## Reglas y decisiones de diseño
* **Límite de parámetros:** Las funciones comunes pueden recibir entre 0 y 3 parámetros por valor (`int ID`). Si se pasan más de 3 parámetros, se informa un error.
* **Orden de declaraciones y bloques:** Las sentencias `int` pueden aparecer en cualquier parte del bloque (antes o después de usar la variable), y los bloques `{ ... }` de `if` y `while` pueden anidarse cualquier cantidad de veces.
* **Comparaciones como enteros:** Las comparaciones devuelven `0` (falso) o `-1` (verdadero) y la gramática permite guardarlas en variables o sumarlas/multiplicarlas dentro de expresiones aritméticas.

---

## Criterios de aceptación
* Se conecta con `AnalizadorLexico` sin modificar las matrices ni el ciclo de lectura de `lexico.py`.
* Analiza y acepta sin errores los programas de prueba válidos (incluyendo funciones con hasta 3 parámetros, variables usadas antes de declararse y *shadowing* en bloques internos).