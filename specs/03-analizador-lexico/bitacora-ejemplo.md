# Bitácora — Analizador léxico de MINI

**Grupo:** A
**Spec de referencia:** `specs/03-analizador-lexico/spec.md`
**Modelos usados:** Gemini Pro

---

## Iteración 1 — declaración de matrices
**Fecha:** 15/09/2026 · Gemini Pro

**Qué pedí:** Le pedí pasar las matrices del spec a Python directamente.

**Qué devolvió:** Las tablas de mi spec ( matriz de estados, unread, tokens y acciones semánticas) pasadas a Python

**Qué cambié y por qué:** 

**Impacto en la spec:** 

## Iteración 1 — Primer intento del reconocedor
**Fecha:** 15/09/2026 · Gemini Pro

**Qué pedí:** Le pedí generar la función `yylex()` en Python. Le aclaré explícitamente que el código debe recorrer el autómata leyendo carácter por carácter y utilizando las matrices como arreglos de diccionarios/listas, ejecutando las funciones `f1` a `f_err` correspondientes. También le pedí que incluya el esqueleto de la Tabla de Símbolos

**Qué devolvió:** La tabla de símbolos, una funcion para cada accion semantica y el bucle principal del lexer.

**Qué cambié y por qué:** 

**Impacto en la spec:** 
