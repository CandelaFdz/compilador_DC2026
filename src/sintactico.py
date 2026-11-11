import ply.yacc as yacc
import sys
import os
import logging
from lexico import AnalizadorLexico, NOMBRES_TOKENS

# PLY exige la lista de tokens extraída del lexer
tokens = list(set(NOMBRES_TOKENS.values()))

# ==========================================
# ESTRUCTURAS PARA CÓDIGO INTERMEDIO (TERCETOS)
# ==========================================
lista_tercetos = []   # Lista de Tercetos
pila_operandos = []   # Pila Simbólica (Pila de Operandos)
pila_saltos = []      # Pila (Pila de Saltos)

def generar_terceto(op, op1, op2):
    """Crea un terceto [operador, operando1, operando2], lo añade a la lista y retorna su número (1-based)"""
    lista_tercetos.append([op, op1, op2])
    return len(lista_tercetos)

def exportar_tercetos(ruta_archivo="tercetos.txt"):
    """Imprime en consola y genera el archivo tercetos.txt con el formato: 22 (>, a, 0)"""
    print("\n=== TERCETOS GENERADOS ===")
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        for i, t in enumerate(lista_tercetos):
            linea = f"{i+1} ({t[0]}, {t[1]}, {t[2]})"
            print(linea)
            f.write(linea + "\n")

# ==========================================
# DEFINICIÓN DE LA GRAMÁTICA Y ACCIONES
# ==========================================

def p_programa(p):
    '''programa : lista_funciones'''
    pass

def p_lista_funciones(p):
    '''lista_funciones : lista_funciones funcion
                       | funcion'''
    pass

# 3.7 Declaración de Funciones
def p_funcion(p):
    '''funcion : FUNC ID PARENTESIS_I lista_pfunc PARENTESIS_D m_func bloque
               | FUNC ID PARENTESIS_I PARENTESIS_D m_func bloque
               | FUNC MAIN PARENTESIS_I PARENTESIS_D m_func bloque'''
    pass

def p_m_func(p):
    '''m_func :'''
    # Inicio de función: Generar ['FUNC', nombre_funcion, '--']
    nombre = p[-3] if p[-2] == '(' or p[-2] == 'PARENTESIS_I' else p[-4]
    if p[-3] in ('(', 'PARENTESIS_I'):
        nombre = p[-4]
    else:
        nombre = p[-3]
    generar_terceto('FUNC', nombre, '--')

def p_funcion_error(p):
    '''funcion : FUNC ID PARENTESIS_I error PARENTESIS_D bloque'''
    parser.errok()

def p_lista_pfunc(p):
    '''lista_pfunc : INT ID COMA INT ID COMA INT ID
                   | INT ID COMA INT ID
                   | INT ID'''
    pass

def p_bloque(p):
    '''bloque : LLAVE_I sentencias LLAVE_D
              | LLAVE_I LLAVE_D'''
    pass

def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | sentencia'''
    pass

def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | seleccion
                 | iteracion
                 | salida
                 | retorno
                 | bloque'''
    pass

def p_sentencia_error(p):
    '''sentencia : error PUNTO_COMA
                 | error LLAVE_D'''
    # Panic Mode: Descarta tokens hasta encontrar ';' o '}' para recuperarse
    parser.errok()

def p_declaracion(p):
    '''declaracion : INT lista_ids PUNTO_COMA'''
    pass

def p_lista_ids(p):
    '''lista_ids : lista_ids COMA ID
                 | ID'''
    pass

# 3.2 Asignaciones
def p_asignacion(p):
    '''asignacion : ID ASIG expresion_log PUNTO_COMA'''
    op_resultado = pila_operandos.pop()
    generar_terceto('=', p[1], op_resultado)

# 3.6 Estructura If - Else
def p_seleccion(p):
    '''seleccion : IF PARENTESIS_I expresion_log PARENTESIS_D m_cond_if bloque ELSE m_fin_if bloque
                 | IF PARENTESIS_I expresion_log PARENTESIS_D m_cond_if bloque'''
    if len(p) == 7:  # IF simple sin else
        idx_bf = pila_saltos.pop()
        lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
    else:            # IF con ELSE: completar el BI generado para esquivar el else
        idx_bi = pila_saltos.pop()
        lista_tercetos[idx_bi - 1][2] = len(lista_tercetos) + 1

def p_m_cond_if(p):
    '''m_cond_if :'''
    condicion = pila_operandos.pop()
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)

def p_m_fin_if(p):
    '''m_fin_if :'''
    idx_bi = generar_terceto('BI', '--', '--')
    idx_bf = pila_saltos.pop()
    lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
    pila_saltos.append(idx_bi)

# 3.3 Estructura While (consume 2 entradas en la pila de saltos)
def p_iteracion(p):
    '''iteracion : WHILE m_while PARENTESIS_I expresion_log PARENTESIS_D m_cond_while bloque'''
    idx_bf = pila_saltos.pop()       # 1° desapilar: dónde está el salto (BF)
    valor_inicio = pila_saltos.pop() # 2° desapilar: dónde está el comienzo del while
    generar_terceto('BI', '--', valor_inicio)
    lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1

def p_m_while(p):
    '''m_while :'''
    pila_saltos.append(len(lista_tercetos) + 1)

def p_m_cond_while(p):
    '''m_cond_while :'''
    condicion = pila_operandos.pop()
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)

# 3.5 Sentencias de Salida (PRINT)
def p_salida_ambos(p):
    '''salida : PRINT PARENTESIS_I CADENA COMA expresion_log PARENTESIS_D PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('PRINT', p[3], resultado_expr)

def p_salida_cadena(p):
    '''salida : PRINT PARENTESIS_I CADENA PARENTESIS_D PUNTO_COMA'''
    generar_terceto('PRINT', p[3], '--')

def p_salida_expr(p):
    '''salida : PRINT PARENTESIS_I expresion_log PARENTESIS_D PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('PRINT', '--', resultado_expr)

# 3.5 Sentencia de Retorno (RET)
def p_retorno(p):
    '''retorno : RET expresion_log PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('RET', resultado_expr, '--')

# 3.4 Operadores Lógicos (AND / OR en cortocircuito)
def p_expresion_log(p):
    '''expresion_log : expresion_log OR m_or term_log
                     | term_log'''
    if len(p) == 5:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        idx = generar_terceto('OR', op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        p[0] = ref

        idx_salto = pila_saltos.pop()
        lista_tercetos[idx_salto - 1][2] = len(lista_tercetos) + 1
    else:
        p[0] = p[1]

def p_m_or(p):
    '''m_or :'''
    condicion = pila_operandos[-1]
    idx_bv = generar_terceto('BV', condicion, '--')
    pila_saltos.append(idx_bv)

def p_term_log(p):
    '''term_log : term_log AND m_and factor_log
                | factor_log'''
    if len(p) == 5:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        idx = generar_terceto('AND', op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        p[0] = ref

        idx_bf = pila_saltos.pop()
        lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
    else:
        p[0] = p[1]

def p_m_and(p):
    '''m_and :'''
    condicion = pila_operandos[-1]
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)

def p_factor_log(p):
    '''factor_log : expresion_relacional'''
    p[0] = p[1]

# 3.1 Expresiones Relacionales
def p_expresion_relacional(p):
    '''expresion_relacional : expresion_aritmetica comparador expresion_aritmetica
                            | expresion_aritmetica'''
    if len(p) == 4:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        idx = generar_terceto(p[2], op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        p[0] = ref
    else:
        p[0] = p[1]

def p_comparador(p):
    '''comparador : IGUAL
                  | MAYOR
                  | MENOR
                  | MAYOR_E
                  | MENOR_E
                  | DISTINTO'''
    p[0] = p[1]

# 3.1 Expresiones Aritméticas
def p_expresion_aritmetica(p):
    '''expresion_aritmetica : expresion_aritmetica SUMA termino
                            | expresion_aritmetica RESTA termino
                            | termino'''
    if len(p) == 4:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        idx = generar_terceto(p[2], op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        p[0] = ref
    else:
        p[0] = p[1]

def p_termino(p):
    '''termino : termino MULTIPLICAR factor
               | termino DIVISION factor
               | factor'''
    if len(p) == 4:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        idx = generar_terceto(p[2], op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        p[0] = ref
    else:
        p[0] = p[1]

# 3.1 Operandos simples y Reglas intermedias
def p_factor_id_cte(p):
    '''factor : ID
              | CTE_ENTERA'''
    pila_operandos.append(p[1])
    p[0] = p[1]

def p_factor_par(p):
    '''factor : PARENTESIS_I expresion_log PARENTESIS_D'''
    p[0] = p[2]

def p_factor_llamada(p):
    '''factor : llamada_funcional'''
    p[0] = p[1]

# 3.7 Llamado de Funciones y Paso de Parámetros
def p_llamada_funcional(p):
    '''llamada_funcional : ID PARENTESIS_I lista_parametros PARENTESIS_D
                         | ID PARENTESIS_I PARENTESIS_D'''
    cantidad_parametros = 0 if len(p) == 4 else p[3]
    idx = generar_terceto('CALL', p[1], cantidad_parametros)
    ref = f"t{idx}"
    pila_operandos.append(ref)
    p[0] = ref

def p_lista_parametros(p):
    '''lista_parametros : expresion_log COMA expresion_log COMA expresion_log
                        | expresion_log COMA expresion_log
                        | expresion_log'''
    if len(p) == 6:
        op3 = pila_operandos.pop()
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        generar_terceto('PARAM', op1, '--')
        generar_terceto('PARAM', op2, '--')
        generar_terceto('PARAM', op3, '--')
        p[0] = 3
    elif len(p) == 4:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        generar_terceto('PARAM', op1, '--')
        generar_terceto('PARAM', op2, '--')
        p[0] = 2
    else:
        op1 = pila_operandos.pop()
        generar_terceto('PARAM', op1, '--')
        p[0] = 1

def p_error(p):
    if p:
        print(f"Error de sintaxis en el token '{p.value}' (Tipo: {p.type}) en la línea {p.lineno}")
    else:
        print("Error de sintaxis: Fin de archivo inesperado")

# ==========================================
# BLOQUE DE PRUEBA
# ==========================================
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("parser_debug.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
        format="%(message)s"
    )
    log = logging.getLogger()

    parser = yacc.yacc(debug=True, debuglog=log)

    ruta_archivo = os.path.join(os.path.dirname(__file__), "..", "tests", "testcorrecto03.txt")

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        codigo_fuente = archivo.read()

    lexer_instancia = AnalizadorLexico()
    lexer_instancia.input(codigo_fuente)
    lexer_instancia.c = lexer_instancia._read_char()

    print(f"\n=== INICIANDO PARSER CON ARCHIVO: {os.path.basename(ruta_archivo)} ===")
    parser.parse(codigo_fuente, lexer=lexer_instancia, debug=log)
    print("=== ANÁLISIS SINTÁCTICO FINALIZADO ===")

    exportar_tercetos("tercetos.txt")