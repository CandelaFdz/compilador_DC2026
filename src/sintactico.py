import ply.yacc as yacc
import sys
import os
import logging
from lexico import AnalizadorLexico, NOMBRES_TOKENS

tokens = list(set(NOMBRES_TOKENS.values()))

# DEFINICIÓN DE LA GRAMÁTICA (REGLAS BNF)

def p_programa(p):
    '''programa : lista_funciones'''
    pass

def p_lista_funciones(p):
    '''lista_funciones : lista_funciones funcion
                       | funcion'''
    pass

def p_funcion(p):
    '''funcion : FUNC ID PARENTESIS_I lista_pfunc PARENTESIS_D m_func bloque
               | FUNC ID PARENTESIS_I PARENTESIS_D m_func bloque
               | FUNC MAIN PARENTESIS_I PARENTESIS_D m_func bloque'''
    pass

def p_m_func(p):
    '''m_func :'''
    nombre = p[-4] if p[-3] in ('(', 'PARENTESIS_I') else p[-3]
    generar_terceto('FUNC', nombre, '--')
    abrir_ambito(nombre)

def p_bloque(p):
    '''bloque : LLAVE_I m_abre_bloque sentencias LLAVE_D
              | LLAVE_I m_abre_bloque LLAVE_D'''
    cerrar_ambito()

def p_m_abre_bloque(p):
    '''m_abre_bloque :'''
    # Evita abrir un sub-ámbito extra si el bloque pertenece inmediatamente a la declaración de función
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
    parser.errok()

def p_declaracion(p):
    '''declaracion : INT lista_ids PUNTO_COMA'''
    pass

def p_lista_ids(p):
    '''lista_ids : lista_ids COMA ID
                 | ID'''
    declarar_variable_ts(p[len(p)-1])

def p_asignacion(p):
    '''asignacion : ID ASIG expresion_log PUNTO_COMA'''

def p_seleccion(p):
    '''seleccion : IF PARENTESIS_I expresion_log PARENTESIS_D m_cond_if bloque ELSE m_fin_if bloque
                 | IF PARENTESIS_I expresion_log PARENTESIS_D m_cond_if bloque'''
    if len(p) == 7:
        idx_bf = pila_saltos.pop()
        lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
    else:
        idx_bi = pila_saltos.pop()
        lista_tercetos[idx_bi - 1][2] = len(lista_tercetos) + 1

def p_m_cond_if(p):
    '''m_cond_if :'''
    abrir_ambito("if")
    condicion = pila_operandos.pop()
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)

def p_m_fin_if(p):
    '''m_fin_if :'''
    idx_bi = generar_terceto('BI', '--', '--')
    idx_bf = pila_saltos.pop()
    lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
    pila_saltos.append(idx_bi)
    abrir_ambito("else")

def p_iteracion(p):
    '''iteracion : WHILE PARENTESIS_I expresion_log PARENTESIS_D bloque'''
    pass

def p_salida(p):
    '''salida : PRINT PARENTESIS_I expresion_log PARENTESIS_D PUNTO_COMA
              | PRINT PARENTESIS_I CADENA PARENTESIS_D PUNTO_COMA
              | PRINT PARENTESIS_I CADENA COMA expresion_log PARENTESIS_D PUNTO_COMA'''

def p_retorno(p):
    '''retorno : RET expresion_log PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('RET', resultado_expr, '--')

def p_expresion_log(p):
    '''expresion_log : expresion_log OR m_or term_log
                     | term_log'''
    if len(p) == 5:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        idx = generar_terceto('OR', op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        idx_salto = pila_saltos.pop()
        lista_tercetos[idx_salto - 1][2] = len(lista_tercetos) + 1
        p[0] = ref
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
        idx_bf = pila_saltos.pop()
        lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
        p[0] = ref
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

def p_factor_id_cte(p):
    '''factor : ID
              | CTE_ENTERA
              | PARENTESIS_I expresion_log PARENTESIS_D
              | llamada_funcional'''


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

def p_lista_pfunc(p):
    '''lista_pfunc : INT ID COMA INT ID COMA INT ID
                   | INT ID COMA INT ID
                   | INT ID'''
    declarar_variable_ts(p[2])
    if len(p) > 3: declarar_variable_ts(p[5])
    if len(p) > 6: declarar_variable_ts(p[8])
    pass

def p_error(p):
    if p:
        print(f"Error de sintaxis en el token '{p.value}' (Tipo: {p.type}) en la línea {p.lineno}")
    else:
        print("Error de sintaxis: Fin de archivo inesperado")

# ==========================================
# BLOQUE PRINCIPAL
# ==========================================
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.FileHandler("parser_debug.log", mode="w", encoding="utf-8"), logging.StreamHandler(sys.stdout)],
        format="%(message)s"
    )
    log = logging.getLogger()
    parser = yacc.yacc(debug=True, debuglog=log)

   
    ruta_archivo = os.path.join(os.path.dirname(__file__), "..", "tests", "testIncorrecto03.txt")

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        codigo_fuente = archivo.read()

    lexer_instancia = AnalizadorLexico()
    lexer_instancia.input(codigo_fuente)
    lexer_instancia.c = lexer_instancia._read_char()

    print(f"\n=== INICIANDO PARSER CON ARCHIVO: {os.path.basename(ruta_archivo)} ===")
    parser.parse(codigo_fuente, lexer=lexer_instancia, debug=log)
    verificar_variables_no_declaradas()
    
    print("\n=== ANÁLISIS SINTÁCTICO Y SEMÁNTICO FINALIZADO ===")
    exportar_tercetos("tercetos.txt")
    exportar_tabla_simbolos("tabla_simbolos.txt")