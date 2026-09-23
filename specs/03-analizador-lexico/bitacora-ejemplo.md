# Bitácora — Analizador léxico de MINI

**Grupo:** A
**Spec de referencia:** `specs/03-analizador-lexico/spec.md`
**Modelos usados:** Gemini Pro

---

## Iteración 1 — declaración de matrices
**Fecha:** 15/09/2026 · Gemini Pro

**Qué pedí:** Le pedí pasar las matrices del spec a Python directamente.

**Qué devolvió:** Las tablas de mi spec ( matriz de estados, unread, tokens y acciones semánticas) pasadas a Python
 

## Iteración 2 — Primer intento del reconocedor
**Fecha:** 15/09/2026 · Gemini Pro

**Qué pedí:** Le pedí generar la función `yylex()` en Python. Le aclaré explícitamente que el código debe recorrer el autómata leyendo carácter por carácter y utilizando las matrices como arreglos de diccionarios/listas, ejecutando las funciones `f1` a `f_err` correspondientes. También le pedí que incluya el esqueleto de la Tabla de Símbolos

**Qué devolvió:** La tabla de símbolos, una funcion para cada accion semantica y el bucle principal del lexer.

**Qué cambié y por qué:** No estaba conforme con el bucle principal del lexer y no estaba teniendo en cuanta que se utilizaria en PLY asi que segui iterando para corregirlo.

**Impacto en la spec:** Sirvió para armar el motor básico del autómata y comprobar que la lógica de leer carácter por carácter funcionaba bien con las tablas, además de dejar lista la estructura para guardar las variables.

## Iteración 3 — Adaptando a PLY
**Fecha:** 20/09/2026 · Gemini Pro

**Qué pedí:** Le pedí que modifique el código inicial para que funcione con la herramienta PLY.

**Qué devolvió:** Me devolvió el analizador léxico metido adentro de una clase (orientado a objetos), listo para PLY.

**Qué cambié y por qué:** Cambié lo que devuelve el analizador: en vez de devolver números sueltos, ahora devuelve un objeto (llamado LexToken) con el tipo de palabra y su valor. Esto se hizo porque PLY te obliga a usar este formato para poder conectarlo con el analizador sintáctico.

**Impacto en la spec:** Logramos un codigo que sea compatible con PLY, armando el puente necesario para la siguiente etapa del compilador

## Iteración 4 — Corregir bucle principal
**Fecha:** 20/09/2026 · Gemini Pro

**Qué pedí:** Le pedí que mejore el código del ciclo principal usando un while, y que me explique por qué en el primer intento había usado un continue.

**Qué devolvió:** El lexer que funciona con PLY, encapsulado en una clase.

**Qué cambié y por qué:** Cambié la forma en que da vueltas el ciclo. Antes usaba un bucle infinito que se cortaba de golpe con un `continue` si la palabra no estaba terminada. Lo cambié por un `while token_code == -1`. Ahora el bucle es mientras la matriz indique -1. Cuando se forma el token,la condicion se vuelve falsa, sale del ciclo de forma limpia y lo arma.

**Impacto en la spec:** Dejó el código mucho más fácil de leer y ordenado, evitando saltos bruscos en la ejecución.




