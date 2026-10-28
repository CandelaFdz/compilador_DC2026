# Spec — 04-analizador-sintactico
**Grupo:** A · **Lenguaje de implementación:** Python (con `ply.yacc`)

---

## 1. Objetivo
Crear el "sintactico.py" donde se traduzca la gramatica de "./diseno/spec.md" y con este que se pueda validar que la secuencia de tokens entregada por el analizador léxico cumpla con la gramática y actualizar la tabla de símbolos.

---

## 2. Alcance
* Detecta errores de sintaxis indicando la línea y se recupera para seguir analizando el archivo.
* La Gramática Independiente del Contexto (GIC) se debe mapear directamente a código traduciendo cada producción a funciones de Python, para que el motor de ply.yacc las interprete. 
* El analizador consumirá los tokens de a uno por vez llamando al método `token()` del analizador léxico manual encapsulado.
* Su responsabilidad abarca la validación estructural de declaraciones, asignaciones, bloques anidados de control (`if`, `while`), llamadas a funciones y operaciones lógicas/aritméticas.
* Se debe evidenciar el proceso de parsing interno (lectura de tokens, operaciones de shift y reduce) activando la herramienta de depuración nativa de PLY (debug=True) y gestionando su salida mediante el módulo logging


---

## 3. Entradas / Salidas
* **Archivos de Entrada:**
  * `lexico.py`: Contiene la clase `AnalizadorLexico` (el cual expone el método `token()`), la clase `LexToken`, la `tabla_simbolos` y la lista de nombres de tokens.
* **Archivos de Salida :**
  * `sintactico.py`: Contendrá el analizador sintáctico, la definición de las reglas gramaticales (prefijo `p_`), la lógica de generación de tercetos y la exportación de la tabla de símbolos.
  * `parser_debug.log`: Archivo generado por el módulo `logging` con la traza shift/reduce de PLY.
  * **Reporte de errores en consola:** Mensajes indicando el token inesperado, tipo y línea exacta (`p.lineno`), o aviso de fin de archivo inesperado (EOF).

---

## 4. Reglas y decisiones de diseño
* **Límite de parámetros:** Las funciones comunes pueden recibir entre 0 y 3 parámetros por valor (`int ID`). Si se pasan más de 3 parámetros, se informa un error.
* **Orden de declaraciones y bloques:** Las sentencias `int` pueden aparecer en cualquier parte del bloque (antes o después de usar la variable), y los bloques `{ ... }` de `if` y `while` pueden anidarse cualquier cantidad de veces.
* **Comparaciones como enteros:** Las comparaciones devuelven `0` (falso) o `-1` (verdadero) y la gramática permite guardarlas en variables o sumarlas/multiplicarlas dentro de expresiones aritméticas.

---

## 5. Estructura de sintactico.py
* Importación: Importación de la clase `AnalizadorLexico` y tokens desde `lexico.py`.
* Traduce exactamente la gramática de ./diseno/spec a funciones `p_[regla](p)` en Python. Los nombres en mayúscula representan los tokens importados de `lexico.py`
 - Como en la gramatica se utilizan los loterales (como +,-,(,)) se deben traducir a su token correspondiente como `SUMA`, `MAYOR_E` para `>=`, etc.
* Trazabilidad (Proceso de Parsing) y main : El proceso de *shift/reduce* debe visualizarse en consola utilizando la herramienta nativa de PLY, habilitando el parámetro `debug=True` al llamar a `parser.parse()` y utilizando el módulo `logging` de Python para que la salida sea legible. Ademas se debe incluir un bloque main que instancie el parser y el `AnalizadorLexico()`, y permita procesar los archivos de casos de prueba
* Manejo de Errores y Panic Mode: Definir `p_error(p)` para imprimir en que linea exacta ocurre.

---

## 6. Generación de Tests 
Se debe generar archivos con nombre `test[correcto/incorrecto][numero].py` (Ejemplo: testCorrecto01) con el objetivo de validar la gramatica el analisis lexico y la recuperacion de errores, se tiene que tener en cuenta los siguientes casos de prueba:
- **3 programas fuente correctos** que ejerciten todas las estructuras de control del lenguaje (if, while, asignaciones, llamadas a funciones) y dos de ellos deben incluir los siguientes casos para reutilizar y verificar en la siguiente etapa, aunque en la etapa del analizador sintactico solo se verifique la gramatica:
  1. Un programa que utilice una variable ANTES de ser declarada (ej. `x = 10; int x;`).
  2. Un programa que declare una variable local en un bloque interno con el mismo nombre que una externa, demostrando el ocultamiento correcto (Shadowing)  
- **3 programas fuente con errores léxicos y sintácticos deliberados**, demostrando que el analizador no aborta en el primer error, sino que aplica el *Panic Mode* y termina de procesar el archivo.

* Ejemplo de programa funcional:

```
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

---

## 7. Criterios de aceptación
* **Integración transparente:** Se conecta con `AnalizadorLexico` consumiendo tokens mediante `token()` sin modificar las matrices ni el ciclo de lectura de `lexico.py`.
* **Reconocimiento de programas válidos:** Analiza y acepta sin errores sintácticos los 3 programas de prueba correctos (incluyendo estructuras `if/else` y `while` anidadas, funciones con 0 a 3 parámetros, variables usadas antes de declararse y *shadowing* en bloques internos).
* **Detección y recuperación de errores:** Ante los 3 programas de prueba incorrectos, el analizador reporta la línea exacta y el token inesperado mediante `p_error`, se recupera en el delimitador (`;` o `}`) sin abortar la ejecución y continúa analizando el resto del archivo.
* **Evidencia del proceso de parsing:** Al ejecutar el analizador con `debug=True` y `logging`, evidenciando la lectura de tokens y las acciones de *shift* y *reduce*.

