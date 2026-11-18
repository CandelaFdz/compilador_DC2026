# Spec — 07-codigo-assembler
**Grupo:** A · **Lenguaje de implementación:** Python  
**Depende de:** `lista_tercetos` (`tercetos.txt`) y `tabla_simbolos` (`tabla_simbolos.txt`) generados por `sintactico.py`  
**Produce:** Archivo `salida.asm` listo para ensamblar

---

## 1. Objetivo
Traducir de forma secuencial la lista de Tercetos `[operador, operando1, operando2]` y la Tabla de Símbolos a código Assembler ejecutable en Windows mediante MASM32, utilizando variables auxiliares.


---

## 2. Alcance y Reglas de Generación
* Se debe recorrer la `lista_tercetos` desde el inicio al final, uno a uno.
* Cada terceto  tiene exactamente 3 elementos `[op, op1, op2]` y cuando un operando sea una referencia a otro terceto (ej. `"t3"`), se  debe usar una variable temporal (ej. `AUX_3`).
* Se debe identificar previamente a qué números de terceto apuntan los saltos (`BF` o `BI`). Al momento de traducir cada uno de estos tercetos de destino, se debe emitir la etiqueta correspondiente encima (ej. `LABEL_5:`)
* **Plataforma y Ensamblador:** El archivo destino está diseñado para MASM32 en arquitectura x86 (Windows).
* **Estructura del archivo `.asm`:**
  * Sección para la reserva de memoria donde se declara todas las variables `INT` de la Tabla de Símbolos (como enteros de 32 bits `dd 0`), las `CADENA` (`db "...", 0`), los mensajes de error en ejecución (división por cero) y todas las variables temporales `AUX_i dd 0` generadas por las operaciones.
  * Seccion dende se escriben las instrucciones correspondientes (detalladas en un siguiente item) y las subrutinas de funciones, incluyendo librerías de consola de Windows (`msvcrt.lib`) para las salidas.


---

## 3. Traducción de Tercetos a Assembler (Método de la Cátedra)

**Mapeo de Pseudo-Registros a MASM32:** Para mantener la compatibilidad teórica con las diapositivas de la cátedra, la lógica de traducción se documenta utilizando los pseudo-registros `R1` y `R2`. Sin embargo, para cumplir con el requisito de ejecución real, el programa generador de código deberá reemplazar textualmente `R1` por `EAX` (Acumulador principal) y `R2` por `EBX` (Registro base) al momento de escribir el archivo `.asm`.

Implementar el uso de registros para operar

### 3.1 Asignaciones (`=`)
* **Terceto `i`:** `['=', destino, origen]` (Ej. `4 (=, a, t3)`).
* **Acción requerida:**
  1. Cargar el `origen` en el registro `R1`: `MOV R1, AUX_3`.
  2. Guardar el contenido de `R1` en el `destino`: `MOV a_main_b1, R1`.

### 3.2 Expresiones Aritméticas (`+`, `-`, `*`, `/`)
* **Regla general:** Almacenar el resultado en la variable `AUX_i` correspondiente al número del terceto analizado.
  * **Suma (`+`) y Resta (`-`):** 
    1. Cargar `op1` en `R1`: `MOV R1, <op1>`.
    2. Sumar o Restar `op2` ejecutando `ADD R1, <op2>` o `SUB R1, <op2>`.
    3. Almacenar el resultado: `MOV AUX_i, R1`.
  * **Multiplicación (`*`):** Aplicar la misma secuencia usando `IMUL`.
  * **División (`/`) con control de Error por Cero:**
    1. Cargar el divisor (`op2`) en el registro secundario `R2` y validar que no sea cero (`CMP R2, 0`). En caso de ser cero, saltar a la rutina de error.
    2. Si es distinto de cero, cargar el dividendo en `R1` (`MOV R1, <op1>`), dividir por el registro secundario (`IDIV R2`) y almacenar el resultado en `AUX_i`.


### 3.3 Comparadores y Operadores Lógicos (`AND`, `OR`)
Toda comparación debe retornar:`-1` si es verdadero, y `0` si es falso.
* **Comparaciones (Ej. `<`, `>`):**
  1. Iniciar la variable temporal con valor falso: `MOV AUX_i, 0`.
  2. Cargar `op1` en `R1` y comparar: `MOV R1, <op1>` seguido de `CMP R1, <op2>`.
  3. Ejecutar un salto condicional utilizando la condición INVERSA al operador original (ej. `JLE` para `>`, `JGE` para `<`, `JNE` para `==`, `JE` para `!=`, `JL` para `>=`, `JG` para `<=`) hacia la etiqueta local. Esto esquiva la asignación de verdadero si la condición original es falsa.
  4. Si no saltó (porque la condición sí se cumplió), sobrescribir la variable temporal asignando verdadero: `MOV AUX_i, -1`.
  5. Emitir la etiqueta de destino del salto: `_fin_cmp_i:`.
  * **Lógicos (`AND`/`OR`):**
  1. Si se evalúan ambos lados de la condición, cargar `op1` en `R1`, aplicar la instrucción `AND R1, <op2>` u `OR R1, <op2>` sobre los valores devueltos (`0` o `-1`) y almacenar el resultado en `AUX_i`.
  2. Si en cambio actúa el cortocircuito y el salto previo esquiva esa operación, debe asegurarse de que al aterrizar en la etiqueta de salida `AUX_i` reciba directamente el valor definitivo del cortocircuito (`0` para `AND` porque ya era falso, o `-1` para `OR` porque ya era verdadero), evitando así que conserve resultados viejos de vueltas anteriores en un ciclo `while`.

### 3.4 Saltos Condicionales e Incondicionales
Traducir los saltos lógicos a instrucciones condicionales apuntando a Etiquetas (`LABEL`).
* **Bifurcación Incondicional (`BI`):** Saltar obligatoriamente a la etiqueta de destino aplicando `JMP LABEL_<destino>`.
* **Bifurcación por Falso (`BF`):** Evaluar si la condición (el `AUX` correspondiente) es falsa (igual a `0`): `MOV R1, <condicion>` seguido de `CMP R1, 0`. De ser así, saltar a la etiqueta destino ejecutando `JE LABEL_<destino>`.


### 3.5 Sentencias de Salida (`PRINT`)
* **Acción requerida:** Invocar la subrutina del sistema para imprimir por pantalla, transfiriendo la variable de la cadena literal y, si corresponde, el valor entero a mostrar.
  - Si `op1` es distinto de `'--'`, emitir `PRINT_STR <CADENA>`.
  - Si `op2` es distinto de `'--'`, cargar `MOV R1, <op2>` y emitir `PRINT_INT R1`.

### 3.6 Funciones (`FUNC`, `PARAM`, `CALL`, `RET`)
* **Inicio (`FUNC`):** Escribir la etiqueta de inicio del procedimiento (Ej. `main PROC`).
* **Retorno (`RET`):** Cargar el valor a retornar en el registro `R1` y ejecutar `RET` para devolver el control al invocador.
* **Paso de Parámetros (`PARAM`):** Guardar temporalmente cada `<op_param>` en una lista a medida que aparecen sus tercetos.
* **Llamado (`CALL`):** Antes de emitir `CALL <nombre_funcion>`, asignar los parámetros guardados a las variables de esa función (copiándolos en orden con `MOV R1, <param>` y `MOV <var_funcion>, R1`), luego emitir `CALL <nombre_funcion>` y finalmente guardar el retorno en `AUX_i` (`MOV AUX_i, R1`).

---

## 4. Resolución de Nombres y Shadowing 
* Para prevenir la superposición de memoria entre variables con el mismo nombre pero diferente ámbito (Ej. una `a` global y una `a` en un bloque `if`):
* Todo identificador de variable en los tercetos que provenga de `sintactico.py` con formato `nombre@alcance` se traduce a Assembler reemplazando `@` por `_` (ej. `a@main_b1` pasa a ser `a_main_b1` y `a@if_b2` pasa a ser `a_if_b2`).
* Si un operando en un terceto no incluye `@alcance`, se busca en la Tabla de Símbolos la variable cuyo alcance coincida con la función actual activa.

---


## 5. Criterios de Aceptación
* El archivo generado `.asm` ensambla exitosamente y sin errores.
* Las variables temporales (los resultados `tn` de la lista de tercetos) se declaran explícitamente en su seccion como `AUX_i`.
* Al presentarse una división por cero en ejecución, el programa se detiene emitiendo un mensaje de error en pantalla sin colapsar el sistema.
* Todo destino de `BF` y `BI` tiene su correspondiente etiqueta `LABEL_X:` generada en la posición exacta del terceto destino.