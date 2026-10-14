# Spec — 02-tabla-simbolos
**Grupo:** A · **Lenguaje de implementación:** Python  
**Depende de:** `specs/01-diseno/spec.md`, `specs/03-lexico/spec.md`  
**Produce:** Estructura `tabla_simbolos` en memoria y archivo de volcado final (`tabla_simbolos.txt`)

---

## Objetivo
Registrar y conservar la información asociada a cada símbolo (identificadores de variables, parámetros, funciones, constantes numéricas y cadenas de texto) que el compilador necesita consultar después del reconocimiento léxico y durante el análisis sintáctico.

Ademas, la tabla debe permitir resolver nombres respetando bloques anidados con ocultamiento (*shadowing*).

---

## Alcance
La tabla registra como mínimo `nombre`, `tipo`, `valor` (para constantes) y `longitud`, sumando el `alcance` para diferenciar variables locales, y se exporta a un archivo de texto al finalizar la compilación.

El único tipo de dato numérico es el entero con signo de 32 bits (`int`), y los identificadores tienen un largo máximo de 20 caracteres. Las palabras reservadas (`main`, `int`, `if`, `else`, `while`, `and`, `or`, `return`, `print`, `function`) no se guardan en esta tabla.

---

## Entradas / Salidas
* **Entradas:**
  * Desde el analizador sintáctico: asignación del tipo `INT` en declaraciones y parámetros, registro de nombres de funciones y control de apertura y cierre de bloques (`{` y `}`).
* **Salidas:**
  * Diccionario `tabla_simbolos` en memoria para consulta entre etapas.
  * Archivo `tabla_simbolos.txt` generado al terminar la ejecución del compilador.

---

## Reglas y decisiones de diseño

### 1. Campos de la tabla
| Campo | Uso en Grupo A |
| ------ | ------ |
| `nombre` | Lexema del `ID` (hasta 20 caracteres, distingue mayúsculas de minúsculas), número o texto |
| `tipo` | `ID`, `CTE_ENTERA` o `CADENA` en el léxico; pasa a `INT` o `FUNC` en el sintáctico |
| `valor` | Número entero de 32 bits en `CTE_ENTERA`; texto en `CADENA`; `None` en variables y funciones |
| `longitud` | Cantidad de caracteres en `ID` y `CADENA`; `None` en `CTE_ENTERA` |
| `alcance` | Bloque al que pertenece el símbolo (`global`, función o bloque interno `if` / `while`) |
| `declarada` | Indica si la variable ya tuvo su sentencia `int` (`True` / `False`) |

### 2. Ámbitos anidados y ocultamiento (*shadowing*)
* cada función y cada bloque `if`, `else` o `while` abre un bloque nuevo al leer `{` y lo cierra al leer `}`.
* Si se declara una variable con el mismo nombre que otra de un bloque externo, se guarda como una entrada separada con su propio `alcance`. Mientras ese bloque interno esté abierto, el programa usa la variable más cercana sin pisar la externa.

### 3. Varaibles usadas antes de su declaracion

---

## Criterios de aceptación
* La estructura conserva sin excepción los campos mínimos (`nombre`, `tipo`, `valor`, `longitud`) junto con la información de alcance para todas las entradas.
* Las palabras reservadas (`int`, `main`, `function`, `return`, `print`, `if`, `else`, `while`, `and`, `or`) son filtradas por `PALABRAS_RESERVADAS` en `f4` y nunca ingresan a la Tabla de Símbolos.
* Soporta el caso de prueba obligatorio de *shadowing*: dos variables llamadas igual en distintos niveles de anidamiento coexisten en la tabla diferenciadas por su ámbito sin sobrescribirse.
* Soporta el caso de prueba obligatorio de declaración tardía: acepta una variable usada antes de su `int` dentro del alcance válido y rechaza al cierre de la función cualquier variable que nunca haya sido declarada.
