# Bitácora — Analizador sintactico

**Grupo:** A
**Spec de referencia:** `specs/04-analizador-sintactico/spec.md`
**Modelos usados:** Gemini Pro

---

## Iteración 1 — Esqueleto de la gramática en PLY
**Fecha:** 7/10/2026 · Gemini Pro
 
**Qué pedí:** Le pedí traducir únicamente la gramática de mi `Spec 01` a código entendible por PLY (`yacc`), dejando solo la estructura pura de las reglas para probar el reconocimiento sintáctico.

**Qué devolvió:** La gramática completa pasada a funciones de Python (`p_programa`, `p_funcion`, `p_sentencia`, etc.) usando los nombres de tokens definidos en `lexico.py` y la función básica `p_error` para detectar fallos de sintaxis.

**Impacto en la spec:** Dejó armada la base del archivo `sintactico.py` cumpliendo con la integración con YACC/PLY, permitiendo verificar primero que las oraciones del lenguaje sean válidas.
