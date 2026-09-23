import sys

PALABRAS_RESERVADAS = {
    "int": "INT", "main": "MAIN", "function": "FUNC", 
    "return": "RET", "print": "PRINT", "if": "IF", 
    "else": "ELSE", "while": "WHILE", "and": "AND", "or": "OR"
}

# Mapeo de códigos numéricos a los nombres de tokens exigidos por PLY
NOMBRES_TOKENS = {
    256: "ID", 257: "CTE_ENTERA", 258: "INT", 259: "CADENA",
    260: "MAIN", 261: "FUNC", 262: "RET", 263: "PRINT",
    264: "IF", 265: "ELSE", 266: "WHILE", 267: "AND",
    268: "OR", 269: "ASIG", 270: "IGUAL", 271: "MAYOR",
    272: "MENOR", 273: "MENOR_E", 274: "MAYOR_E", 275: "DISTINTO",
    276: "SUMA", 277: "RESTA", 278: "MULTIPLICAR", 279: "DIVISION",
    280: "PARENTESIS_I", 281: "PARENTESIS_D", 282: "LLAVE_I", 283: "LLAVE_D",
    284: "PUNTO_COMA", 285: "COMA"
}

# --- 2. ACCIONES SEMÁNTICAS ---
def f1(char, lexer):
    lexer.buffer = char
    lexer.longitud_id = 1

def f2(char, lexer):
    lexer.buffer = char

def f3(char, lexer):
    lexer.longitud_id += 1
    if lexer.longitud_id > 20:
        print(f"Warning Léxico (Línea {lexer.linea}): Identificador excede 20 caracteres.")
    lexer.buffer += char

def f4(char, lexer):
    # Verifica si el buffer es una palabra reservada o un ID normal
    nombre_token = PALABRAS_RESERVADAS.get(lexer.buffer, "ID")
    
    # Si es ID normal, se inserta en la Tabla de Símbolos si no existe
    if nombre_token == "ID" and lexer.buffer not in lexer.tabla_simbolos:
        lexer.tabla_simbolos[lexer.buffer] = {"tipo": "ID", "valor": None, "longitud": len(lexer.buffer)}
        
    return nombre_token # Retorna el String (ej. "INT" o "ID")

def f5(char, lexer):
    valor_real = int(lexer.buffer)
    # Límite estricto de 32 bits para el Grupo A
    if valor_real > 2147483648:
        print(f"Error Léxico (Línea {lexer.linea}): La constante {valor_real} excede el límite de 32 bits.")
        sys.exit(1)
        
    if lexer.buffer not in lexer.tabla_simbolos:
        lexer.tabla_simbolos[lexer.buffer] = {"tipo": "CTE_ENTERA", "valor": valor_real, "longitud": None}

def f6(char, lexer):
    lexer.buffer += char

def f7(char, lexer):
    lexer.buffer += char

def fn(char, lexer):
    pass # Transición sin acción

def f_err(char, lexer):
    if char == "EOF":
        print(f"Error Léxico (Línea {lexer.linea}): Fin de archivo inesperado.")
    else:
        print(f"Error Léxico (Línea {lexer.linea}): Carácter no reconocido '{char}'")
    sys.exit(1)

# --- 1. INICIALIZACIÓN DE MATRICES Y TABLA DE SÍMBOLOS ---
MATRIZ_ESTADOS = [
    [  1,   2,   0,   3,   5,   8,  10,  11,  19,  14,  13,  12,  15,  16,  17,  18,  22,   7,  -1, f_err], # 0
    [  1,   1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 1 
    [ -1,   2,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 2 
    [ -1,  -1,  -1,  -1,  -1,   4,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 3 
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 4 
    [ -1,  -1,  -1,  -1,  -1,   6,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 5 
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 6 
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 7 
    [ -1,  -1,  -1,  -1,  -1,   9,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 8 
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 9 
    [f_err, f_err, f_err, f_err, f_err,  -1, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err], # 10
    [ 11,  11,  11,  11,  11,  11,  11,  -1,  11,  11,  11,  11,  11,  11,  11,  11,  11,  11, f_err,  11], # 11
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 12
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 13
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 14
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 15
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 16
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 17
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 18
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  20,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 19
    [ 20,  20,  20,  20,  20,  20,  20,  20,  20,  21,  20,  20,  20,  20,  20,  20,  20,  20, f_err,  20], # 20
    [ 20,  20,  20,  20,  20,  20,  20,  20,   0,  21,  20,  20,  20,  20,  20,  20,  20,  20, f_err,  20], # 21
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], # 22
]

# --- 2. MATRIZ DE UNREADS ---
MATRIZ_UNREADS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
]

# --- 3. MATRIZ DE TOKENS ---
MATRIZ_TOKENS = [
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,   0,  -1], 
    [ -1,  -1, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256], 
    [257,  -1, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257, 257], 
    [271, 271, 271, 271, 271, 274, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271, 271], 
    [274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274, 274], 
    [272, 272, 272, 272, 272, 273, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272, 272], 
    [273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273, 273], 
    [285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285, 285], 
    [269, 269, 269, 269, 269, 270, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269, 269], 
    [270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270, 270], 
    [ -1,  -1,  -1,  -1,  -1, 275,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], 
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1, 259,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], 
    [277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277, 277], 
    [276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276, 276], 
    [278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278, 278], 
    [280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280, 280], 
    [281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281, 281], 
    [282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282, 282], 
    [283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283], 
    [279, 279, 279, 279, 279, 279, 279, 279, 279,  -1, 279, 279, 279, 279, 279, 279, 279, 279, 279, 279], 
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], 
    [ -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1], 
    [284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284, 284], 
]

# --- 4. MATRIZ DE ACCIONES SEMÁNTICAS ---
MATRIZ_ACCIONES = [
    [f1, f2, fn, fn, fn, fn, fn, f1, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, f_err], 
    [f3, f3, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4, f4],    
    [f5, f6, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5, f5],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [f_err, f_err, f_err, f_err, f_err, fn, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err, f_err], 
    [f7, f7, f7, f7, f7, f7, f7, fn, f7, f7, f7, f7, f7, f7, f7, f7, f7, f7, f_err, f7], 
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, f_err, fn], 
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, f_err, fn], 
    [fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn, fn],    
]

# --- ESTRUCTURAS PLY ---

class LexToken:
    """Clase obligatoria requerida por el motor interno de PLY."""
    def __init__(self, type, value, lineno, lexpos):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.lexpos = lexpos
        
    def __str__(self):
        return f"LexToken({self.type}, {self.value!r}, {self.lineno}, {self.lexpos})"

    def __repr__(self):
        return str(self)

class AnalizadorLexico:
    """Clase wrapper para acoplar el analizador léxico manual tabular a PLY."""
    def __init__(self):
        self.source = ""
        self.pos = 0
        self.linea = 1
        self.buffer = ""
        self.longitud_id = 0
        self.tabla_simbolos = {}

    def input(self, s):
        self.source = s
        self.pos = 0
        self.linea = 1
        self.tabla_simbolos.clear()

    def _read_char(self):
        if self.pos >= len(self.source):
            self.pos += 1
            return "EOF"
        char = self.source[self.pos]
        self.pos += 1
        return char

    def _unread_char(self):
        if self.pos > 0:
            self.pos -= 1

    def _get_columna(self, char):
        if char == "EOF": return 18
        if char.isalpha() or char == '_': return 0
        if char.isdigit(): return 1
        if char in [' ', '\t', '\n', '\r']: return 2
        if char == '>': return 3
        if char == '<': return 4
        if char == '=': return 5
        if char == '!': return 6
        if char == '"': return 7
        if char == '/': return 8
        if char == '*': return 9
        if char == '+': return 10
        if char == '-': return 11
        if char == '(': return 12
        if char == ')': return 13
        if char == '{': return 14
        if char == '}': return 15
        if char == ';': return 16
        if char == ',': return 17
        return 19

    def token(self):
        estado = 0
        self.buffer = ""
        self.longitud_id = 0
        token_code = -1 
        resultado_accion = None
        
        # El bucle itera mientras el autómata no haya formado un token completo
        while token_code == -1:
            char = self._read_char()
            col = self._get_columna(char)
            
            # Control de línea para los reportes de error de Yacc
            if char == '\n':
                self.linea += 1
            
            # 1. Ejecutar Acción Semántica
            accion = MATRIZ_ACCIONES[estado][col]
            resultado_parcial = accion(char, self)
            
            # Capturamos el resultado por si f4 determinó que es una palabra reservada
            if resultado_parcial is not None:
                resultado_accion = resultado_parcial
            
            # 2. Verificar Unread (Retroceso en la cinta de caracteres)
            if MATRIZ_UNREADS[estado][col] == 1 and char != "EOF":
                self._unread_char()
                
            # 3. Obtener Token. Si da distinto de -1, el while se rompe.
            token_code = MATRIZ_TOKENS[estado][col]
            
            # 4. Transición al Nuevo Estado
            nuevo_estado = MATRIZ_ESTADOS[estado][col]
            if callable(nuevo_estado):
                nuevo_estado(char, self) # Se llama a f_err
            else:
                estado = nuevo_estado
                
        # --- FIN DEL BUCLE WHILE ---
        
        # Si la matriz devolvió 0, es la señal de Fin de Archivo para detener a PLY
        if token_code == 0: 
            return None
            
        # Priorizar la palabra reservada si la acción f4 encontró una
        if resultado_accion is not None:
            token_code = resultado_accion
            
        # Convertir el código numérico (ej. 256) al String ("ID") requerido por PLY
        tipo = NOMBRES_TOKENS.get(token_code, str(token_code))
        
        # El valor del LexToken retiene el lexema exacto solo si tiene contenido útil
        if token_code in [256, 257, 259]: # ID, CTE_ENTERA, CADENA
            valor = self.buffer
        else:
            valor = tipo
            
        token_final = LexToken(tipo, valor, self.linea, self.pos)
        
        self.buffer = ""
        self.longitud_id = 0
        
        return token_final

# ==========================================
# 3. TEST DE EJECUCIÓN 
# ==========================================

if __name__ == "__main__":
    lexer = AnalizadorLexico()
    
    # Programa de prueba (Caso de Shadowing del Grupo A)
    codigo_prueba = """
    function main() { 
        int a;
        a = 10;
        if (a > 0) {
            int a;
            a = 99;
            print("Variable interna: ", a);
        }
        print("Variable externa: ", a);
        return 0;
    }
    """
    
    lexer.input(codigo_prueba)
    
    print("=== INICIANDO ANÁLISIS LÉXICO ===")
    while True:
        tok = lexer.token()
        if not tok:
            print("FIN DE ARCHIVO (EOF)")
            break
        print(tok)
        
    print("\n=== TABLA DE SÍMBOLOS GENERADA ===")
    for key, val in lexer.tabla_simbolos.items():
        print(f"{key}: {val}")