# Spec — 04-analizador-sintactico
**Grupo:** A · **Lenguaje de implementación:** Python (con `ply.yacc`)

---

## 1. Objetivo
Validar que la secuencia de tokens entregada por el analizador léxico cumpla con la gramática, actualizar la tabla de símbolos.

---

## 2. Alcance
* Detecta errores de sintaxis indicando la línea y se recupera para seguir analizando el archivo.
* El analizador consumirá los tokens de a uno por vez llamando al método `token()` del analizador léxico manual encapsulado.
* Su responsabilidad abarca la validación estructural de declaraciones, asignaciones, bloques anidados de control (`if`, `while`), llamadas a funciones y operaciones lógicas/aritméticas.



---

## 3. Entradas / Salidas
* **Entradas:**
  * Objetos `LexToken(type, value, lineno, lexpos)` emitidos por `lexico.py`.
  * Lista de nombres de tokens (`NOMBRES_TOKENS`) y la `tabla_simbolos` generada.
* **Salidas:**
  * **Reporte de errores:** Mensajes indicando la línea exacta donde ocurrió una violación a las reglas gramaticales.

---

## 4. Reglas y decisiones de diseño
* **Límite de parámetros:** Las funciones comunes pueden recibir entre 0 y 3 parámetros por valor (`int ID`). Si se pasan más de 3 parámetros, se informa un error.
* **Orden de declaraciones y bloques:** Las sentencias `int` pueden aparecer en cualquier parte del bloque (antes o después de usar la variable), y los bloques `{ ... }` de `if` y `while` pueden anidarse cualquier cantidad de veces.
* **Comparaciones como enteros:** Las comparaciones devuelven `0` (falso) o `-1` (verdadero) y la gramática permite guardarlas en variables o sumarlas/multiplicarlas dentro de expresiones aritméticas.

---

## 5. Estructura de sintactico.py
El archivo se organiza en tres bloques lógicos principales:
* Importación: Importación de la clase AnalizadorLexico.
* Reglas de la Gramática (BNF): Funciones decoradas con docstrings que representan las producciones del lenguaje, integrando los puntos de enganche para la creación de Tercetos.


## 6. Criterios de aceptación
* Se conecta con `AnalizadorLexico` sin modificar las matrices ni el ciclo de lectura de `lexico.py`.
* Analiza y acepta sin errores los programas de prueba válidos (incluyendo funciones con hasta 3 parámetros, variables usadas antes de declararse y *shadowing* en bloques internos).

## 7. Programas ejemplo
* Debe aceptar sin errores un programa como este

```
// PROGRAMA 1 //
 function main() {
    int x, y;
    x = 10;
    y = 0;

    print("Valor de x en main:", x);

    while (y < 3) {
      y = y + 1;
      print("Iteracion numero:", y);
    }

    if (x > 0) {
      int x;      
      x = 99;

      print("Valor de x en el if", x);
    }

    print("Valor de x en main:", x);

    return 0;
  }

```
* Debe remarcar el error en un programa como este

```
// PROGRAMA 2 //
  function calcularPromedio(int a, int b, int c, int d) {
    int suma;
    suma = a + b + c + d;
    return suma / 4;
  }
```
