import ply.yacc as yacc
import sys
from lexico import AnalizadorLexico, NOMBRES_TOKENS

# PLY exige la lista de tokens extraída del lexer
tokens = list(set(NOMBRES_TOKENS.values()))

# DEFINICIÓN DE LA GRAMÁTICA (REGLAS BNF)

def p_programa(p):
    '''programa : lista_funciones'''

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

def p_seleccion(p):
    '''seleccion : IF PARENTESIS_I expresion_log PARENTESIS_D bloque ELSE bloque
                 | IF PARENTESIS_I expresion_log PARENTESIS_D bloque'''
    pass

def p_iteracion(p):
    '''iteracion : WHILE PARENTESIS_I expresion_log PARENTESIS_D bloque'''
    pass

def p_salida(p):
    '''salida : PRINT PARENTESIS_I expresion_log PARENTESIS_D PUNTO_COMA
              | PRINT PARENTESIS_I CADENA PARENTESIS_D PUNTO_COMA
              | PRINT PARENTESIS_I CADENA COMA expresion_log PARENTESIS_D PUNTO_COMA'''

def p_retorno(p):
    '''retorno : RET expresion_log PUNTO_COMA'''

def p_expresion_log(p):
    '''expresion_log : expresion_log OR term_log
                     | term_log'''


def p_term_log(p):
    '''term_log : term_log AND factor_log
                | factor_log'''


def p_factor_log(p):
    '''factor_log : expresion_relacional'''


def p_expresion_relacional(p):
    '''expresion_relacional : expresion_aritmetica comparador expresion_aritmetica
                            | expresion_aritmetica'''


def p_comparador(p):
    '''comparador : IGUAL
                  | MAYOR
                  | MENOR
                  | MAYOR_E
                  | MENOR_E
                  | DISTINTO'''


def p_expresion_aritmetica(p):
    '''expresion_aritmetica : expresion_aritmetica SUMA termino
                            | expresion_aritmetica RESTA termino
                            | termino'''


def p_termino(p):
    '''termino : termino MULTIPLICAR factor
               | termino DIVISION factor
               | factor'''


def p_factor(p):
    '''factor : ID
              | CTE_ENTERA
              | PARENTESIS_I expresion_log PARENTESIS_D
              | llamada_funcional'''


def p_llamada_funcional(p):
    '''llamada_funcional : ID PARENTESIS_I lista_parametros PARENTESIS_D
                         | ID PARENTESIS_I PARENTESIS_D'''
    pass

def p_lista_parametros(p):
    '''lista_parametros : expresion_log COMA expresion_log COMA expresion_log
                        | expresion_log COMA expresion_log
                        | expresion_log'''
    pass




