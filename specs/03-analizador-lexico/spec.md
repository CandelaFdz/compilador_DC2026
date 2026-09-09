# Spec — Analizador léxico de UNO

**Grupo:** ejemplo de cátedra · **Lenguaje de implementación:** C
**Depende de:** `specs/01-diseno/spec.md`
**Produce:** `src/lexico/` · escribe en la tabla de símbolos definida en `specs/02-tabla-simbolos/spec.md`

---

## 1. Alcance e interfaz

Función `yylex()` invocada por el analizador sintáctico. Devuelve **un token por
llamada**, como entero asociado al número de token. No es una pasada previa que
produzca la lista completa.

## 2. Decisiones propias de esta fase

| # | Decisión | Valor |
|---|---|---|

---

## 3. Eventos (columnas de las matrices)

`get_evento(c)` mapea el carácter leído a una columna:

| Col | Evento | Caracteres |
|---|---|---|

---

## 4. Estados y Diagrama


| Estado | Token devuelto |
|---|---|
| E1 | ID o palabra reservada |
| E2 | CTE |
| E3 | MAYOR |
| E4 | MAYOR_E |
| E5 | MENOR |
| E6 | MENOR_E |
| E7 | COMA|
| E8 | ASIG |
| E9 | IGUAL
| E10 | DISTINTO |
| E11 | CADENA |
| E12 | MENOS |
| E13 | MAS |
| E14 | MULTIPLICAR |
| E15 | PARENTESIS_I |
| E16 | PARENTESIS_D |
| E17 | LLAVE_I |
| E18 | LLAVE_D |
| E19 | DIV |

# Automata

![Diagrama del Autómata Finito](Automata.jpeg)

---

## 5. Matriz de Nuevos Estados

| Estado actual | L | D | BL | > | < | = | ! | " | / | * | +- | ( ) { } ; , | EOF | No reconocido |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | e1 | e2 | e0 | e3 | e5 | e8 | e10 | e11 | e19 | -1 | -1 | -1 | -1 | ERR | 
| 1 (ID) | e1 | e1 | -1 | -1 | -1 | -1 | -1| -1 | -1 | -1 | -1 | -1 | -1 | -1 |
| 2 (CTE) | -1 | e2 | -1 | -1 | -1 | -1 | -1| -1 | -1 | -1 | -1 | -1 | -1 | -1 |
| 3 (>) | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 |
| 5 (<) | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 |
| 8 (=) | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 |
| 10 (!) | ERR | ERR | ERR | ERR | ERR | -1 | ERR | ERR | ERR | ERR | ERR | ERR | ERR | ERR | 
| 11 (") | e11 | e11 | e11 | e11 | e11 | e11 | e11 | -1 | e11 | e11 | e11 | e11 | ERR | e11 | 
| 19 (/) | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | e20 | -1 | -1 | -1 | -1 |
| 20 (*) | e20  | e20  | e20  | e20  | e20  | e20  | e20  | e20 | e20 | e21 | e20 | e20 | ERR | e20 | 
| 21 (/) | e20 | e20 | e20 | e20 | e20 | e20 | e20 | e20 | e0 | e21 | e20 | e20 | ERR | e20 | 

---

## 6. Acciones semánticas


| Acción | Qué hace|
|---|---|
| f1 | Inicia un string | 
| f2 | Inicia una constante |
| f3 | Incrementa el contador de longitud. Si se excedió el largo máximo termina |
| f4 | Verifica si el string está en la lista de palabras reservadas (ej: int, if, main). Si está devuelve su token. Si no está, lo agrega como ID. |
| f5 | Verifica si la CTE ya esta almacenada, si no esta la guarda | 
| f6 | Calcula el nuevo valor numerico acumulado |
| f7 | Agrega el caracter al string del literal de texto |
| f8 | Cierra el token de un simbolo u operador simple |
| f_err | Reporta un error lexico |
| fn | No hace nada |


---


## 7. Matriz de Transiciones


| Estado actual | L | D | BL | > | < | = | ! | " | / | * | +- | ( ) { } ; , | EOF | No reconocido |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | e1-f1 | e2-f2 | e0-fn | e3-fn | e5-fn | e8-fn | e10-fn | e11-f1 | e19-fn | F-f8 | F-f8 | F-f8 | F-f8 | ERR-ferr | 
| 1 (ID) | e1-f3 | e1-f3 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 | FU-f4 |
| 2 (CTE) | FU-f5 | e2-f6 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | FU-f5 | 
| 3 (>) | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | F-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | 
| 5 (<) | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | F-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 |
| 8 (=) | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | F-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 |
| 10 (!) | ERR-f_err | ERR | ERR | ERR | ERR | F-f8 | ERR | ERR | ERR | ERR | ERR | ERR | ERR | ERR | 
| 11 (") | e11-f7 | e11-f7 | e11-f7 | e11-f7 | e11-f7 | e11-f7 | e11-f7 | F-f8 | e11-f7 | e11-f7 | e11-f7 | e11-f7 | ERR | e11-f7 | 
| 19 (/) | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | FU-f8 | e20-fn | FU-f8 | FU-f8 | FU-f8 | FU-f8 |
| 20 (*) | e20-fn  | e20-fn  | e20-fn  | e20-fn  | e20-fn  | e20-fn  | e20-fn  | e20-fn | e20-fn | e21-fn | e20-fn | e20-fn | ERR | e20-fn | 
| 21 (/) | e20-fn | e20-fn | e20-fn | e20-fn | e20-fn | e20-fn | e20-fn | e20-fn | e0-fn | e21-fn | e20-fn | e20-fn | ERR | e20-fn |  

---

## 8. Tabla de Unreads

| | | | | | | | | | | | | | |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 
| 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

---

## 9. Matriz Tokens

| | | | | | | | | | | | | | |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| -1 | -1 | -1 | -1 | -1 | -1 | 275 | 259 | -1 | 278 | SIM | SIM | - | -1 | 
| -1 | -1 | 256 | 256 | 256 | 256 | 256 | 256 | 256 | 256 | 256 | 256 | 256 | 256 |
| 257 | -1 | 257 | 257 | 257 | 257 | 257 | 257 | 257 | 257 | 257 | 257 | 257 | 257 |
| 271 | 271 | 271 | 271 | 271 | 274 | 271 | 271 | 271 | 271 | 271 | 271 | 271 | 271 |
| 272 | 272 | 272 | 272 | 272 | 272 | 273 | 272 | 272 | 272 | 272 | 272 | 272 | 272 |
| 269 | 269 | 269 | 269 | 269 | 269 | 270 | 269 | 269 | 269 | 269 | 269 | 269 | 269 |
| -1 | -1 | -1 | -1 | -1 | 275 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | 
| -1 | -1 | -1 | -1 | -1 | -1 | -1 | 259 | -1 | -1 | -1 | -1 | -1 | -1 |
| 279 | 279 | 279 | 279 | 279 | 279 | 279 | 279 | 279 | -1 | 279 | 279 | 279 | 279 |
| -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 |
| -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 |

---

## 9. Errores que emite esta fase

| Código | Condición | Mensaje |
|---|---|---|

---

## 10. Traza de verificación

Entrada ``, con el estado inicial 0:

| Estado | Lee | Evento | Acción | Nuevo estado | Unread | Retorna |
|---|---|---|---|---|---|---|


---

## 11. Casos de prueba de esta fase

| Entrada | Salida esperada | Qué verifica |
|---|---|---|
