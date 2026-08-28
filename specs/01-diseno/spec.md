# Spec — Diseño del lenguaje UNO

**Grupo:** A · **Lenguaje de implementación:** Python 
**Estado:** . Todo cambio acá impacta en las specs de las fases siguientes.

---

## 1. Decisiones globales

| # | Decisión | Valor |
|---|---|---|
| D1 | Tipo de datos | Un solo tipo:entero con signo de 32 bits |
| D2 | Rango numerico | −2.147.483.648 a 2.147.483.647 |
| D3 | Declaracion y orden | Obligatoria, pero no se exigen orden previo una variable puede utilizarse antes de ser declarada |
| D4 | Alcance y visibilidad | Ambitos anidados con variables locales dentro de funciones y estructuras de control(if, while). Pueden anidarse una cantidad arbitraria de veces |
| D5 | Sencibilidad a mayúsculas | Sí |
| D6 | Longitud máxima de identificador | 20 caracteres, se trunca con advertencia en el caso de ser mas largo | 
| D7 | Comentarios | De bloque `(/* ... */)`. El léxico los descarta íntegramente. |    
| D8 | Resultado de una comparacion | Valor entero: 0 para falso y -1 para verdadero. Puede asignarse a una variable y operarse aritmeticamente |    
| D9 | División por cero | Error en ejecucion |    
| D10 | Plataforma destino | x86-64, MASM sobre windows |
| D11 | Evaluacion logica | Evaluacion en cortocircuito de and y or |
| D12 | Sentencia de E/S | setencia print para mostrar valores numericos y literales de texto entre comillas dobles |
| D13 | Estructura del programa | Conjunto de funciones. El punto de entrada es una función con el nombre reservado main |

---

## 2. Alfabeto

| Clase | Descripción | Caracteres |
|---|---|---|
| `L` | Letras | `a-z`; `A-Z`;`_` | 
| `D` | Digitos | `0-9` |
| `SIM` | Simbolos| `+`,`-`,`*`,`/`,`(`,`)`,`{`,`}`,`;`,`,`,`=`,<,>`,`!` |
| `BL` | Blanco | Espacio en blanco, tabuladores, saltos de línea | 
| `OTRO` | No reconocido |cualquier otro carácter → error léxico |


---

## 3. Palabras reservadas

`main` · `int` · `if` · `else` · `while` · `and` · `or` · `return` · `print` · `function` ·

Se reconocen como identificadores (L (L | D)*) y se resuelven por búsqueda en tabla, no con estados propios del autómata.


---

## 4. Tabla de tokens

| Código | Token | Lexema |
|---|---|---|

---

## 5. Estructura del programa


---

## 6. Gramática

```
<programa>      ::= 
```

**Notas sobre la gramática**


---

## 7. Semántica

| Regla | Definición |
|---|---|

---

## 8. Responsabilidad de cada error

| Código | Descripción | Fase que lo detecta |
|---|---|---|


---

## 9. Programa de ejemplo

```

```

Salida esperada: 

---

## 10. Fuera de alcance
