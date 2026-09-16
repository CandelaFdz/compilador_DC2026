# Spec — Diseño del lenguaje UNO

**Grupo:** A · **Lenguaje de implementación:** Python 
**Estado:** . Todo cambio acá impacta en las specs de las fases siguientes.

---

## 1. Decisiones globales

| # | Decisión | Valor |
|---|---|---|
| D1 | Tipo de datos | Un solo tipo: entero con signo de 32 bits |
| D2 | Rango numerico | −2.147.483.648 a 2.147.483.647 |
| D3 | Declaracion y orden | Obligatoria, pero no se exige orden previo. Una variable puede utilizarse antes de ser declarada |
| D4 | Alcance y visibilidad | Ambitos anidados con variables locales dentro de funciones y estructuras de control (if, while). Pueden anidarse una cantidad arbitraria de veces |
| D5 | Sensibilidad a mayúsculas | Sí |
| D6 | Longitud máxima de identificador | 20 caracteres, se trunca con advertencia en el caso de ser mas largo | 
| D7 | Comentarios | De bloque `(/* ... */)`. El léxico los descarta íntegramente |    
| D8 | Resultado de una comparacion | Valor entero: 0 para falso y -1 para verdadero. Puede asignarse a una variable y operarse aritmeticamente |    
| D9 | División por cero | Error en ejecucion |    
| D10 | Plataforma destino | x86-64, MASM sobre windows |
| D11 | Evaluacion logica | Evaluacion en cortocircuito de and y or |
| D12 | Sentencia de E/S | sentencia print para mostrar valores numericos y literales de texto entre comillas dobles |
| D13 | Estructura del programa | Conjunto de funciones. El punto de entrada es una función con el nombre reservado main |


---

## 2. Alfabeto

| Clase | Descripción | Caracteres |
|---|---|---|
| `L` | Letras | `a-z`; `A-Z`;`_` | 
| `D` | Digitos | `0-9` |
| `SIM` | Simbolos| `+`,`-`,`*`,`/`,`(`,`)`,`{`,`}`,`;`,`,`,`=`,`<`,`>`,`!`,`"` |
| `BL` | Blanco | Espacio en blanco, tabuladores, saltos de línea | 
| `OTRO` | No reconocido | Cualquier otro carácter → error léxico |



---


## 3. Palabras reservadas

`main` · `int` · `if` · `else` · `while` · `and` · `or` · `return` · `print` · `function` ·

Se reconocen como identificadores (L (L | D)*) y se resuelven por búsqueda en tabla, no con estados propios del autómata.


---

## 4. Tabla de tokens


| Código | Token | Lexema |
|---|---|---|
| 256 | `ID` | `Identificador` | 
| 257 | `CTE` | `entero` | 
| 258 | `INT` | `int` |
| 259 | `CADENA` | `literal de texto` | 
| 260 | `MAIN` | `main` |
| 261 | `FUNC` | `function` |
| 262 | `RET` | `return` |
| 263 | `PRINT` | `print` |
| 264 | `IF` | `if` |
| 265 | `ELSE` | `else` |
| 266 | `WHILE` | `while` |
| 267 | `AND` | `and` |
| 268 | `OR` | `or` |
| 269 | `ASIG` | `=` |
| 270 | `IGUAL` | `==` |
| 271 | `MAYOR` | `>` |
| 272 | `MENOR` | `<` |
| 273 | `MENOR_E` | `<=` |
| 274 | `MAYOR_E` | `>=` |
| 275 | `DISTINTO` | `!=` |
| 276 | `SUMA` | `+` |
| 277 | `RESTA` | `-` |
| 278 | `MULTIPLICAR` | `*` |
| 279 | `DIVISION` | `/` |
| 280 | `PARENTESIS_I` | `(` |
| 281 | `PARENTESIS_D` | `)` |
| 282 | `LLAVE_I` | `{` |
| 283 | `LLAVE_D` | `}` |
| 284 | `PUNTO` | `;` |
| 285 | `COMA` | `,` |


---

## 5. Estructura del programa

La unidad de compilacion es un conjunto de una o mas funciones. La funcion `main` es la funcion que se ejecuta al inicio del programa.

- Cada función declara un nombre, una lista de hasta 3 parámetros por valor (o ninguno), y un bloque de código delimitado por llaves `{` `}` y retornan un valor entero.
- 
- 


---

## 6. Gramática

```
<programa>      ::=  <lista_funciones>

<lista_funciones> ::= <lista_funciones> <funcion> | <funcion>

<funcion>       ::= FUNC ID '(' <lista_pfunc> ')' <bloque> | FUNC ID '(' ')' <bloque> | FUNC MAIN '(' ')' <bloque>

<lista_pfunc> ::= INT ID ',' INT ID ',' INT ID | INT ID ',' INT ID | INT ID

<bloque>   ::= '{' <sentencias> '}' | '{' '}'

<sentencias> ::= <sentencias> <sentencia> | <sentencia>

<sentencia> ::= <declaracion> | <asignacion> | <seleccion> | <iteracion> | <salida> | <retorno> | <bloque>

<declaracion> ::= INT <lista_ids> ';' 

<lista_ids> ::= <lista_ids> ',' ID | ID

<asignacion> ::= ID ASIG <expresion_log> ';'

<seleccion> ::= IF '(' <expresion_log> ')' <bloque> ELSE <bloque> | IF '(' <expresion_log> ')' <bloque>

<iteracion> ::= WHILE '(' <expresion_log> ')' <bloque>

<salida> ::= PRINT '(' <expresion_log> ')' ';' | PRINT '(' CADENA ')' ';' | PRINT '(' CADENA ',' <expresion_log> ')' ';'

<retorno> ::= RET <expresion_log> ';'

<expresion_log> ::= <expresion_log> OR <term_log>  |  <term_log> 

<term_log> ::= <term_log>  AND <factor_log> | <factor_log>

<factor_log> ::= <expresion_relacional> 

<expresion_relacional> ::= <expresion_aritmetica> <comparador> <expresion_aritmetica> | <expresion_aritmetica>

<comparador> ::= IGUAL | MAYOR | MENOR | MAYOR_E | MENOR_E | DISTINTO

<expresion_aritmetica> ::= <expresion_aritmetica> '+' <termino> | <expresion_aritmetica> '-' <termino> | <termino>

<termino> ::= <termino> '*' <factor> | <termino> '/' <factor> | <factor>

<factor> ::= ID | CTE_ENTERA | '(' <expresion_log> ')' | <llamada_funcional>

<llamada_funcional> ::= ID '(' <lista_parametros> ')' | ID '(' ')'

<lista_parametros> ::= <expresion_log> ',' <expresion_log> ',' <expresion_log> | <expresion_log> ',' <expresion_log> | <expresion_log>

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

## 9. Programas de ejemplo

```
PROGRAMA 1
function main() { 
    int i, suma;

    i= 1;
    suma = 0;
    while (i<=5){
        suma = suma + i;
        i = i + 1;
        if(i == 6){
            print("ultima vuelta");
        } 
    }

    print("la suma total es: ", suma);
    
    return 0;
}

```

Salida esperada: ultima vuelta
la suma total es: 15

```
PROGRAMA 2
function main() {
    int x;
    x = 10;

    print("Valor de x en main:", x);

    if (x > 0) {
        int x;      
        x = 99;

        print("Valor de x en el if", x);
    }

    print("Valor de x en main:", x);

    return 0;
}

```

Salida esperada: 
Valor de x en el main 10
Valor de x en el if: 99
Valor de x en el main: 10

---

## 10. Fuera de alcance
