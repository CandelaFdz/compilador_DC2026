# Spec — 02-tabla-simbolos
**Grupo:** A · **Lenguaje de implementación:** Python  
**Depende de:** `specs/01-diseno/spec.md`, `specs/03-lexico/spec.md`  
**Produce:** Estructura `tabla_simbolos` en memoria y archivo final(`tabla_simbolos.txt`)

---

## 1. Objetivo
Registrar y conservar la información asociada a cada símbolo (identificadores de variables, parámetros, funciones, constantes numéricas y cadenas de texto) que el compilador necesita consultar después del reconocimiento léxico y durante el análisis sintáctico.

Ademas, la tabla debe permitir resolver nombres respetando bloques anidados con ocultamiento (*shadowing*).

---

## 2. Alcance
La tabla registra como mínimo `nombre`, `tipo`, `valor` (para constantes) y `longitud`, sumando el `alcance` para diferenciar variables locales, y se exporta a un archivo de texto al finalizar la compilación.

El único tipo de dato numérico es el entero con signo de 32 bits (`int`), y los identificadores tienen un largo máximo de 20 caracteres. Las palabras reservadas (`main`, `int`, `if`, `else`, `while`, `and`, `or`, `return`, `print`, `function`) no se guardan en esta tabla.

---

## 3. Entradas / Salidas
* **Entradas:**
  * Desde el analizador sintáctico: asignación del tipo `INT` en declaraciones y parámetros, registro de nombres de funciones y control de apertura y cierre de bloques (`{` y `}`).
* **Salidas:**
  * Diccionario `tabla_simbolos` en memoria para consulta entre etapas.
  * Archivo `tabla_simbolos.txt` generado al terminar la ejecución del compilador.

---

## 4. Reglas y decisiones de diseño

### 4.1 Campos de la tabla
Para que dos variables con el mismo `nombre` en distinto `alcance` coexistan sin sobrescribirse y ambas aparezcan en `tabla_simbolos.txt`, cada entrada de variable o función se debe almacenar en la tabla bajo la clave única `(nombre, alcance)`

| Campo | Uso en Grupo A |
| ------ | ------ |
| `nombre` | Lexema limpio del `ID` (hasta 20 caracteres), número o literal de texto |
| `tipo` | `ID`, `CTE_ENTERA` o `CADENA` en el léxico; pasa a `INT` o `FUNC` en el sintáctico |
| `valor` | Número entero de 32 bits en `CTE_ENTERA`; texto en `CADENA`; `None` en variables y funciones |
| `longitud` | Cantidad de caracteres en `ID` y `CADENA`; `None` en `CTE_ENTERA` |
| `alcance` | Ámbito al que pertenece (`global`, nombre de función como `main`, o bloque interno como `main_b1`) |
| `declarada` | Indica si la variable ya tuvo su sentencia `int` (`True` / `False`) |

### 4.2 Ámbitos anidados y ocultamiento (*Shadowing*)
Se mantiene una pila global de ámbitos activos `pila_alcances = ["global"]` y un contador de bloques internos `contador_bloques`:
* **Al iniciar una función:**
  * Se registra el identificador de la función con `tipo = 'FUNC'`, `alcance = 'global'` y `declarada = True`.
  * Se apila el nombre de la función en `pila_alcances` (ej. `'main'`).
* **Al abrir un bloque `{` de `if`, `else` o `while`:**
  * Si es la llave de apertura de la función, se tiene que mantener el alcance de la función actual.
  * Si es un bloque anidado interno, se debe incrementar `contador_bloques` y apila un nuevo alcance en `pila_alcances` (ej:`f"{funcion_actual}_b{contador_bloques}"`).
* **Al declarar una variable:**
  * Se debe tomar el tope de `pila_alcances` es decir el alcance actual .
  * Si la variable no existe en `alcance_actual`, aunque ya exista otra con igual nombre en un alcance externo, se creara una nueva entrada separada asociada a `alcance_actual` con `tipo = 'INT'` y `declarada = True`. Mientras este bloque siga activo en `pila_alcances`, cualquier búsqueda desde el tope encontrará primero esta variable interna sin pisar la externa (*shadowing*).
* **Al cerrar un bloque `}` (reducción de `<bloque>`):**
  * Se desapilara el alcance interno de `pila_alcances` (`pila_alcances.pop()`), pero no se borra el registro de la tabla de símbolos, para que quede documentado en `tabla_simbolos.txt` y el alcance activo vuelva a ser el del bloque externo actual.

### 4.3 Variables usadas antes de su declaración (Declaración tardía)
* **Al usar una variable en `<asignacion>` (`ID ASIG ...`) o `<factor>` (`ID`):**
  1. Se recorrera `pila_alcances` desde el tope (ámbito más interno) hacia la base (ámbito de la función).
  2. Si se encuentra una entrada para ese ID en alguno de los alcances activos, se utiliza esa entrada (para que funcione el *shadowing* asi se sabe si está declarada en el bloque interno, o se esta tomando la de la función externa).
  3. Si no existe en ningún alcance activo, significa que se está usando antes de su sentencia `int`. Se debe insertar una entrada provisoria en el alcance actual con `tipo = 'ID'`, `declarada = False` y el número de línea.
* **Al reducirse posteriormente la declaración `INT <lista_ids> ';'`:**
  * Se debe buscar si el ID ya tenía una entrada provisoria (`declarada == False`) en el alcance actual o en el alcance de la función. Si existe, se actualiza esa misma entrada a `tipo = 'INT'` y `declarada = True` en lugar de duplicarla.
* **Verificación obligatoria al cerrar un bloque o función:**
  * Al desapilar un alcance en el cierre de `<bloque>` o `<funcion>`, se recorren las entradas de ese alcance. Si alguna quedó con `declarada == False`, se debe notificar por consola: `"Error Semántico en línea X: La variable 'ID' fue utilizada pero nunca declarada en el alcance 'ALCANCE'"` sin abortar el resto del archivo.
  
---

## 5. Criterios de aceptación
* La estructura conserva sin excepción los campos mínimos (`nombre`, `tipo`, `valor`, `longitud`) junto con la información de alcance para todas las entradas.
* Las palabras reservadas (`int`, `main`, `function`, `return`, `print`, `if`, `else`, `while`, `and`, `or`) son filtradas por `PALABRAS_RESERVADAS` en `f4` y nunca ingresan a la Tabla de Símbolos.
* Soporta el caso de prueba obligatorio de *shadowing*: dos variables llamadas igual en distintos niveles de anidamiento coexisten en la tabla diferenciadas por su ámbito sin sobrescribirse.
* Soporta el caso de prueba obligatorio de declaración tardía: acepta una variable usada antes de su `int` dentro del alcance válido y rechaza al cierre de la función cualquier variable que nunca haya sido declarada.
