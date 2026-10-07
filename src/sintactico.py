import ply.yacc as yacc
import sys
from lexico import AnalizadorLexico, NOMBRES_TOKENS

# PLY exige la lista de tokens extraída del lexer
tokens = list(set(NOMBRES_TOKENS.values()))

# --- ESTRUCTURAS PARA CÓDIGO INTERMEDIO (TERCETOS) ---
# Memoria global donde se van guardando el historial de operaciones, desdpues contendra todas las instrucciones
lista_tercetos = [] 
#variable temporal para resolver operaciones anidadas
temp_counter = 1

#permite que el resultado de una sub operacion para ser utilizado por una regla de un nivel mayor
def crear_terceto(operador, arg1, arg2):
    """Genera una variable temporal, crea el terceto y lo guarda."""
    global temp_counter
    temp = f"@t{temp_counter}"
    temp_counter += 1
    lista_tercetos.append((operador, arg1, arg2))
    return temp

# DEFINICIÓN DE LA GRAMÁTICA (REGLAS BNF)

def p_programa(p):
    '''programa : lista_funciones'''
    p[0] = p[1]
    print("Sintáctico: Programa compilado correctamente.")

def p_lista_funciones(p):
    '''lista_funciones : lista_funciones funcion
                       | funcion'''
    pass

def p_funcion(p):
    '''funcion : FUNC ID PARENTESIS_I lista_pfunc PARENTESIS_D bloque
               | FUNC ID PARENTESIS_I PARENTESIS_D bloque
               | FUNC MAIN PARENTESIS_I PARENTESIS_D bloque'''
    pass

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

def p_declaracion(p):
    '''declaracion : INT lista_ids PUNTO_COMA'''
    pass

def p_lista_ids(p):
    '''lista_ids : lista_ids COMA ID
                 | ID'''
    pass

def p_asignacion(p):
    '''asignacion : ID ASIG expresion_log PUNTO_COMA'''
    # Terceto de asignación: (=, valor_a_asignar, _, variable_destino)
    lista_tercetos.append(('=', p[3], '_', p[1]))

def p_seleccion(p):
    '''seleccion : IF PARENTESIS_I expresion_log PARENTESIS_D bloque ELSE bloque
                 | IF PARENTESIS_I expresion_log PARENTESIS_D bloque'''
    # Nota: La generación de tercetos de salto condicional (backpatching)
    # se omite en esta fase lineal por complejidad, pero la estructura base ya existe.
    pass

def p_iteracion(p):
    '''iteracion : WHILE PARENTESIS_I expresion_log PARENTESIS_D bloque'''
    pass

def p_salida(p):
    '''salida : PRINT PARENTESIS_I expresion_log PARENTESIS_D PUNTO_COMA
              | PRINT PARENTESIS_I CADENA PARENTESIS_D PUNTO_COMA
              | PRINT PARENTESIS_I CADENA COMA expresion_log PARENTESIS_D PUNTO_COMA'''
    if len(p) == 6:
        lista_tercetos.append(('PRINT', p[3], '_', '_'))
    else:
        lista_tercetos.append(('PRINT', p[3], p[5], '_'))

def p_retorno(p):
    '''retorno : RET expresion_log PUNTO_COMA'''
    lista_tercetos.append(('RET', p[2], '_', '_'))

def p_expresion_log(p):
    '''expresion_log : expresion_log OR term_log
                     | term_log'''
    if len(p) == 4:
        p[0] = crear_terceto('OR', p[1], p[3])
    else:
        p[0] = p[1]

def p_term_log(p):
    '''term_log : term_log AND factor_log
                | factor_log'''
    if len(p) == 4:
        p[0] = crear_terceto('AND', p[1], p[3])
    else:
        p[0] = p[1]

def p_factor_log(p):
    '''factor_log : expresion_relacional'''
    p[0] = p[1]

def p_expresion_relacional(p):
    '''expresion_relacional : expresion_aritmetica comparador expresion_aritmetica
                            | expresion_aritmetica'''
    if len(p) == 4:
        p[0] = crear_terceto(p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_comparador(p):
    '''comparador : IGUAL
                  | MAYOR
                  | MENOR
                  | MAYOR_E
                  | MENOR_E
                  | DISTINTO'''
    p[0] = p[1] # Retorna el operador literal para que exp_relacional lo use

def p_expresion_aritmetica(p):
    '''expresion_aritmetica : expresion_aritmetica SUMA termino
                            | expresion_aritmetica RESTA termino
                            | termino'''
    if len(p) == 4:
        p[0] = crear_terceto(p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_termino(p):
    '''termino : termino MULTIPLICAR factor
               | termino DIVISION factor
               | factor'''
    if len(p) == 4:
        p[0] = crear_terceto(p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_factor(p):
    '''factor : ID
              | CTE_ENTERA
              | PARENTESIS_I expresion_log PARENTESIS_D
              | llamada_funcional'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2] # Resuelve los paréntesis devolviendo la expresión interior

def p_llamada_funcional(p):
    '''llamada_funcional : ID PARENTESIS_I lista_parametros PARENTESIS_D
                         | ID PARENTESIS_I PARENTESIS_D'''
    pass

def p_lista_parametros(p):
    '''lista_parametros : expresion_log COMA expresion_log COMA expresion_log
                        | expresion_log COMA expresion_log
                        | expresion_log'''
    pass


# RUTINA DE ERRORES (OBLIGATORIO DE PLY)

def p_error(p):
    if p:
        print(f"Error Sintáctico (Línea {p.lineno}): Token inesperado '{p.value}' de tipo {p.type}")
    else:
        print("Error Sintáctico: Fin de archivo inesperado (EOF)")


# BUCLE DE EJECUCIÓN DEL PARSER

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python sintactico.py <archivo_fuente.txt>")
        sys.exit(1)
        
    # Inicializar Autómata Manual
    lexer_manual = AnalizadorLexico()
    
    # Inicializar PLY YACC
    parser = yacc.yacc()
    
    with open(sys.argv[1], 'r') as f:
        codigo_fuente = f.read()
        
    print("=== INICIANDO ANÁLISIS SINTÁCTICO ===")
    
    # Conectamos el Lexer al Parser
    lexer_manual.input(codigo_fuente)
    resultado = parser.parse(codigo_fuente, lexer=lexer_manual)
    
    print("\n=== TERCETOS GENERADOS ===")
    for idx, terceto in enumerate(lista_tercetos):
        print(f"[{idx}] {terceto}")