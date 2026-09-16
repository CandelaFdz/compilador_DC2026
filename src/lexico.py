import sys

tabla_simbolos = {}
palabras_reservadas = {
    "main": 259, "int": 258, "if": 263, "else": 264, 
    "while": 265, "and": 266, "or": 267, "return": 262, 
    "print": 263, "function": 260
}

buffer_lexema = ""
longitud_id = 0

# --- 2. ACCIONES SEMÁNTICAS ---
def f1(char):
    global buffer_lexema, longitud_id
    buffer_lexema = char
    longitud_id = 1

def f2(char):
    global buffer_lexema
    buffer_lexema = char

def f3(char):
    global buffer_lexema, longitud_id
    longitud_id += 1
    if longitud_id > 20:
        print("Warning: Identificador excede 20 caracteres.") # Regla D6
    buffer_lexema += char

def f4(char):
    # Verifica si es palabra reservada o ID y la inserta en tabla si es necesario
    token = palabras_reservadas.get(buffer_lexema, 256)
    if token == 256 and buffer_lexema not in tabla_simbolos:
        tabla_simbolos[buffer_lexema] = {"tipo": "ID", "valor": None}
    return token

def f5(char):
    # Guarda CTE en la tabla de símbolos con su valor real
    valor_real = int(buffer_lexema)
    if buffer_lexema not in tabla_simbolos:
        tabla_simbolos[buffer_lexema] = {"tipo": "CTE", "valor": valor_real}

def f6(char):
    # Calcula el valor numérico (lo tenías en tu diseño)
    global buffer_lexema
    buffer_lexema += char

def f7(char):
    # Agrega a la cadena
    global buffer_lexema
    buffer_lexema += char

def fn(char):
    pass # No hace nada

def f_err(char):
    print(f"Error Léxico: Carácter no reconocido '{char}'")
    sys.exit(1)

# --- 1. INICIALIZACIÓN DE MATRICES Y TABLA DE SÍMBOLOS ---
matriz_estados = [
    [  1,   2,   0,   3,   5,   8,  10,  11,  19,  14,  13,  12,  15,  16,  17,  18,  22,   7,  -1, f_err], # 0 (Inicio)
    [  1,   1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 1 (ID)
    [ -1,   2,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 2 (CTE)
    [ -1,  -1,  -1,  -1,  -1,   4,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 3 (>)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 4 (>=)
    [ -1,  -1,  -1,  -1,  -1,   6,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 5 (<)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 6 (<=)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 7 (,)
    [ -1,  -1,  -1,  -1,  -1,   9,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 8 (=)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 9 (==)
    [f_err, f_err, f_err, f_err, f_err,  -1, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err], # 10 (!)
    [ 11,  11,  11,  11,  11,  11,  11,  -1,  11,  11,  11,  11,  11,  11,  11,  11,  11,  11, f_err,  11], # 11 (")
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 12 (-)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 13 (+)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 14 (*)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 15 (()
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 16 ())
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 17 ({)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 18 (})
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  20,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 19 (/)
    [ 20,  20,  20,  20,  20,  20,  20,  20,  20,  21,  20,  20,  20,  20,  20,  20,  20,  20, f_err,  20], # 20 (*)
    [ 20,  20,  20,  20,  20,  20,  20,  20,   0,  21,  20,  20,  20,  20,  20,  20,  20,  20, f_err,  20], # 21 (/)
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 22 (;)
]

# --- 2. MATRIZ DE UNREADS ---
matriz_unreads = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 0
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 1
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 2
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 3
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 4
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 5
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 6
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 7
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 8
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 9
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 11
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 12
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 13
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 14
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 15
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 16
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 17
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 18
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 19
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 20
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 21
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 22
]

# --- 3. MATRIZ DE TOKENS ---
matriz_tokens = [
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 0
    [ -1,  -1, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256], # 1
    [257,  -1, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257], # 2
    [271, 271, 271, 271, 271, 274, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271], # 3
    [274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274], # 4
    [272, 272, 272, 272, 272, 273, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272], # 5
    [273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273], # 6
    [285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285], # 7
    [269, 269, 269, 269, 269, 270, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269], # 8
    [270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270], # 9
    [ -1,  -1,  -1,  -1,  -1, 275,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 10
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1, 259,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 11
    [277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277], # 12
    [276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276], # 13
    [278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278], # 14
    [280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280], # 15
    [281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281], # 16
    [282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282], # 17
    [283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283], # 18
    [279, 279, 279, 279, 279, 279, 279, 279, 279,  -1, 279, 279, 279, 279, 279, 279, 279, 279, 279, 279], # 19
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 20
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 21
    [284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284], # 22
]

# --- 4. MATRIZ DE ACCIONES SEMÁNTICAS ---
matriz_acciones = [
    [f1, f2, fn, fn, fn, fn, fn, f1, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, f_err], # 0
    [f3, f3, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4],    # 1
    [f5, f6, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5],    # 2
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 3
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 4
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 5
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 6
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 7
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 8
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 9
    [f_err, f_err, f_err, f_err, f_err, fn, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err], # 10
    [f7, f7, f7, f7, f7, f7, f7, fn, f7, f7, f7, f7, f7, f7, f7, f7, f7, f7, f_err, f7], # 11
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 12
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 13
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 14
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 15
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 16
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 17
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 18
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 19
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, f_err, fn], # 20
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, f_err, fn], # 21
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    # 22
]


# --- 3. BUCLE PRINCIPAL YYLEX ---
def get_columna(char):
    # Retorna el índice de la columna (0 a 20) según el carácter leído
    if char.isalpha(): return 0
    if char.isdigit(): return 1
    if char in [' ', '\t', '\n']: return 2
    # ... Completar mapeo para >, <, =, !, ", /, *, +, -, (, ), {, }, ;, ,, EOF
    return 20 # No reconocido

def yylex(archivo):
    global buffer_lexema
    estado_actual = 0
    
    while True:
        char = archivo.read(1)
        if not char:
            char = "EOF"
            
        col = get_columna(char)
        
        # 1. Ejecutar Acción Semántica
        accion = matriz_acciones[estado_actual][col]
        resultado_accion = accion(char)
        
        # 2. Verificar Unread (Retroceso)
        if matriz_unreads[estado_actual][col] == 1:
            archivo.seek(archivo.tell() - 1)
            
        # 3. Verificar si se emite un Token
        token = matriz_tokens[estado_actual][col]
        
        # 4. Actualizar el Estado
        nuevo_estado = matriz_estados[estado_actual][col]
        estado_actual = nuevo_estado
        
        # 5. Retornar Token al parser si corresponde
        if token != -1:
            # Si f4 devolvió un token específico (ej. INT o WHILE), pisamos el de la matriz
            if resultado_accion is not None:
                token = resultado_accion
            return token