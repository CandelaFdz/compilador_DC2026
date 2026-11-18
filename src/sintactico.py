import ply.yacc as yacc
import sys
import os
import logging
from lexico import AnalizadorLexico, NOMBRES_TOKENS

tokens = list(set(NOMBRES_TOKENS.values()))

# ==========================================
# ESTRUCTURAS DE CÓDIGO INTERMEDIO
# ==========================================
lista_tercetos = []
pila_operandos = []
pila_saltos = []

MAPA_SIMBOLOS_OP = {
    "SUMA": "+", "+": "+",
    "RESTA": "-", "-": "-",
    "MULTIPLICAR": "*", "*": "*",
    "DIVISION": "/", "/": "/",
    "IGUAL": "==", "==": "==",
    "DISTINTO": "!=", "!=": "!=",
    "MAYOR": ">", ">": ">",
    "MENOR": "<", "<": "<",
    "MAYOR_E": ">=", ">=": ">=",
    "MENOR_E": "<=", "<=": "<="
}

def generar_terceto(op, op1, op2):
    lista_tercetos.append([op, op1, op2])
    return len(lista_tercetos)

def exportar_tercetos(ruta="tercetos.txt"):
    with open(ruta, "w", encoding="utf-8") as f:
        for i, t in enumerate(lista_tercetos):
            f.write(f"{i+1} ({t[0]}, {t[1]}, {t[2]})\n")

# ==========================================
# ESTRUCTURAS DE TABLA DE SÍMBOLOS
# ==========================================
tabla_simbolos_final = {}
pila_alcances = ["global"]
contador_bloques = 0
funcion_actual = "global"
es_bloque_funcion = False

def iniciar_ambito_funcion(nombre_func, linea):
    global funcion_actual, es_bloque_funcion
    funcion_actual = nombre_func
    es_bloque_funcion = True
    clave_func = f"{nombre_func}@global"
    tabla_simbolos_final[clave_func] = {
        "nombre": nombre_func,
        "tipo": "FUNC",
        "valor": None,
        "longitud": len(str(nombre_func)),
        "alcance": "global",
        "declarada": True,
        "parametros": 0,
        "linea": linea
    }
    pila_alcances.append(nombre_func)

def abrir_ambito_bloque():
    global contador_bloques, es_bloque_funcion
    # Si es la llave de apertura de la función, mantiene el alcance de la función actual (4.2)
    if es_bloque_funcion:
        es_bloque_funcion = False
        return
    contador_bloques += 1
    nuevo_ambito = f"{funcion_actual}_b{contador_bloques}"
    pila_alcances.append(nuevo_ambito)

def cerrar_ambito():
    if len(pila_alcances) > 1:
        ambito_cerrado = pila_alcances.pop()
        for clave, datos in list(tabla_simbolos_final.items()):
            if datos.get("alcance") == ambito_cerrado and not datos.get("declarada", True):
                print(f"Error Semántico (Línea {datos.get('linea', 0)}): La variable '{datos['nombre']}' fue utilizada pero nunca declarada en el alcance '{ambito_cerrado}'")
                datos["verificada"] = True

def declarar_variable_ts(nombre_var, linea=0):
    ambito_actual = pila_alcances[-1]
    clave = f"{nombre_var}@{ambito_actual}"

    if clave in tabla_simbolos_final:
        if not tabla_simbolos_final[clave]["declarada"]:
            tabla_simbolos_final[clave]["tipo"] = "INT"
            tabla_simbolos_final[clave]["declarada"] = True
        else:
            print(f"Error Semántico (Línea {linea}): La variable '{nombre_var}' ya fue declarada en el alcance '{ambito_actual}'")
    else:
        tabla_simbolos_final[clave] = {
            "nombre": nombre_var,
            "tipo": "INT",
            "valor": None,
            "longitud": len(str(nombre_var)),
            "alcance": ambito_actual,
            "declarada": True,
            "linea": linea
        }

def usar_variable_ts(nombre_var, linea=0):
    # Buscar desde el tope (ámbito más interno) hacia la base (Shadowing - 4.3)
    for ambito in reversed(pila_alcances):
        clave = f"{nombre_var}@{ambito}"
        if clave in tabla_simbolos_final and tabla_simbolos_final[clave].get("tipo") == "INT":
            return clave

    # Entrada provisoria por declaración tardía (4.3)
    ambito_actual = pila_alcances[-1]
    clave_nueva = f"{nombre_var}@{ambito_actual}"
    tabla_simbolos_final[clave_nueva] = {
        "nombre": nombre_var,
        "tipo": "INT",
        "valor": None,
        "longitud": len(str(nombre_var)),
        "alcance": ambito_actual,
        "declarada": False,
        "linea": linea
    }
    return clave_nueva

def verificar_variables_no_declaradas():
    for clave, datos in tabla_simbolos_final.items():
        if not datos.get("declarada", True) and not datos.get("verificada", False):
            print(f"Error Semántico (Línea {datos.get('linea', 0)}): La variable '{datos['nombre']}' fue utilizada pero nunca declarada en el alcance '{datos['alcance']}'")

def registrar_constante_ts(nombre, tipo, valor, linea=0):
    clave = f"{nombre}@global"
    if clave not in tabla_simbolos_final:
        tabla_simbolos_final[clave] = {
            "nombre": str(nombre),
            "tipo": tipo,
            "valor": valor,
            "longitud": len(str(nombre)) if tipo == "CADENA" else None,
            "alcance": "global",
            "declarada": True,
            "linea": linea
        }

def exportar_tabla_simbolos(ruta="tabla_simbolos.txt"):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"{'NOMBRE':<12}{'TIPO':<12}{'VALOR':<10}{'LONGITUD':<10}{'ALCANCE':<12}{'DECLARADA':<10}{'LINEA'}\n")
        f.write("-" * 72 + "\n")
        for clave, datos in tabla_simbolos_final.items():
            valor = datos.get("valor", None)
            longitud = datos.get("longitud", None)
            linea = datos.get("linea", 0)
            f.write(f"{str(datos['nombre']):<12}{str(datos['tipo']):<12}{str(valor):<10}{str(longitud):<10}{str(datos['alcance']):<12}{str(datos['declarada']):<10}{str(linea)}\n")

# ==========================================
# REGLAS SINTÁCTICAS Y GENERACIÓN DE TERCETOS
# ==========================================

def p_programa(p):
    '''programa : lista_funciones'''
    pass

def p_lista_funciones(p):
    '''lista_funciones : lista_funciones funcion
                       | funcion'''
    pass

def p_funcion(p):
    '''funcion : FUNC ID PARENTESIS_I m_func_con_params lista_pfunc PARENTESIS_D bloque
               | FUNC ID PARENTESIS_I PARENTESIS_D m_func_sin_params bloque
               | FUNC MAIN PARENTESIS_I PARENTESIS_D m_func_sin_params bloque'''
    pass

def p_m_func_con_params(p):
    '''m_func_con_params :'''
    nombre = "main" if p[-2] == "MAIN" else p[-2]
    linea_actual = getattr(p.lexer, "linea", 0)
    generar_terceto('FUNC', nombre, '--')
    iniciar_ambito_funcion(nombre, linea_actual)

def p_m_func_sin_params(p):
    '''m_func_sin_params :'''
    nombre = "main" if p[-3] == "MAIN" else p[-3]
    linea_actual = getattr(p.lexer, "linea", 0)
    generar_terceto('FUNC', nombre, '--')
    iniciar_ambito_funcion(nombre, linea_actual)

def p_lista_pfunc(p):
    '''lista_pfunc : INT ID COMA INT ID COMA INT ID
                   | INT ID COMA INT ID
                   | INT ID'''
    declarar_variable_ts(p[2], p.lineno(2))
    cant = 1
    if len(p) > 3:
        declarar_variable_ts(p[5], p.lineno(5))
        cant = 2
    if len(p) > 6:
        declarar_variable_ts(p[8], p.lineno(8))
        cant = 3
    clave_func = f"{funcion_actual}@global"
    if clave_func in tabla_simbolos_final:
        tabla_simbolos_final[clave_func]["parametros"] = cant

def p_bloque(p):
    '''bloque : LLAVE_I m_abre_bloque sentencias LLAVE_D
              | LLAVE_I m_abre_bloque LLAVE_D'''
    cerrar_ambito()

def p_m_abre_bloque(p):
    '''m_abre_bloque :'''
    abrir_ambito_bloque()

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
    p.parser.errok()

def p_declaracion(p):
    '''declaracion : INT lista_ids PUNTO_COMA'''
    pass

def p_lista_ids(p):
    '''lista_ids : lista_ids COMA ID
                 | ID'''
    idx_id = len(p) - 1
    declarar_variable_ts(p[idx_id], p.lineno(idx_id))

# 3.3 Asignaciones
def p_asignacion(p):
    '''asignacion : ID ASIG expresion_log PUNTO_COMA'''
    clave_var = usar_variable_ts(p[1], p.lineno(1))
    op_resultado = pila_operandos.pop()
    generar_terceto('=', clave_var, op_resultado)

# 3.7 Estructura If - Else
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
    condicion = pila_operandos.pop()
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)

def p_m_fin_if(p):
    '''m_fin_if :'''
    idx_bi = generar_terceto('BI', '--', '--')
    idx_bf = pila_saltos.pop()
    lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
    pila_saltos.append(idx_bi)

# 3.4 Estructura While
def p_iteracion(p):
    '''iteracion : WHILE PARENTESIS_I m_while expresion_log PARENTESIS_D m_cond_while bloque
                 | WHILE error bloque'''
    if len(p) > 4:
        idx_bf = pila_saltos.pop()
        valor_inicio = pila_saltos.pop()
        generar_terceto('BI', '--', valor_inicio)
        lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1
    else:
        p.parser.errok()

def p_m_while(p):
    '''m_while :'''
    pila_saltos.append(len(lista_tercetos) + 1)

def p_m_cond_while(p):
    '''m_cond_while :'''
    condicion = pila_operandos.pop()
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)

# 3.6 Sentencias de Salida y Retorno (PRINT / RET)
def p_salida_ambos(p):
    '''salida : PRINT PARENTESIS_I CADENA COMA expresion_log PARENTESIS_D PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('PRINT', p[3], resultado_expr)
    registrar_constante_ts(p[3], "CADENA", p[3], p.lineno(3))

def p_salida_cadena(p):
    '''salida : PRINT PARENTESIS_I CADENA PARENTESIS_D PUNTO_COMA'''
    generar_terceto('PRINT', p[3], '--')
    registrar_constante_ts(p[3], "CADENA", p[3], p.lineno(3))

def p_salida_expr(p):
    '''salida : PRINT PARENTESIS_I expresion_log PARENTESIS_D PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('PRINT', '--', resultado_expr)

def p_retorno(p):
    '''retorno : RET expresion_log PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('RET', resultado_expr, '--')

# 3.5 Operadores Lógicos (OR con BF y BI, sin BV, y AND con BF)
def p_expresion_log(p):
    '''expresion_log : expresion_log OR m_or term_log
                     | term_log'''
    if len(p) == 5:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        idx = generar_terceto('OR', op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        idx_bi = pila_saltos.pop()
        lista_tercetos[idx_bi - 1][2] = len(lista_tercetos) + 1
        p[0] = ref
    else:
        p[0] = p[1]

def p_m_or(p):
    '''m_or :'''
    condicion = pila_operandos[-1]
    # 1. BF para saltar a evaluar el segundo operando si el primero es falso
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)
    # 2. BI para saltar al final (cortocircuito) si el primero fue verdadero
    idx_bi = generar_terceto('BI', '--', '--')
    # Al iniciar la evaluación del segundo operando: desapilar BF y completar con terceto actual
    idx_bf_extraido = pila_saltos.pop()
    lista_tercetos[idx_bf_extraido - 1][2] = len(lista_tercetos) + 1
    # Dejar apilado el BI para completarlo al terminar de reducir el OR
    pila_saltos.append(idx_bi)

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

# 3.2 Expresiones Aritméticas y Relacionales
def p_expresion_relacional(p):
    '''expresion_relacional : expresion_aritmetica comparador expresion_aritmetica
                            | expresion_aritmetica'''
    if len(p) == 4:
        op2 = pila_operandos.pop()
        op1 = pila_operandos.pop()
        simbolo_op = MAPA_SIMBOLOS_OP.get(p[2], p[2])
        idx = generar_terceto(simbolo_op, op1, op2)
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
        simbolo_op = MAPA_SIMBOLOS_OP.get(p[2], p[2])
        idx = generar_terceto(simbolo_op, op1, op2)
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
        simbolo_op = MAPA_SIMBOLOS_OP.get(p[2], p[2])
        idx = generar_terceto(simbolo_op, op1, op2)
        ref = f"t{idx}"
        pila_operandos.append(ref)
        p[0] = ref
    else:
        p[0] = p[1]

# 3.1 Operandos simples y Números negativos
def p_factor_id_cte(p):
    '''factor : ID
              | CTE_ENTERA'''
    if str(p[1]).isalpha() or '_' in str(p[1]):
        simbolo = usar_variable_ts(p[1], p.lineno(1))
    else:
        registrar_constante_ts(str(p[1]), "CTE_ENTERA", int(p[1]), p.lineno(1))
        simbolo = str(p[1])
    pila_operandos.append(simbolo)
    p[0] = simbolo

def p_factor_cte_negativa(p):
    '''factor : RESTA CTE_ENTERA'''
    cte_neg = f"-{p[2]}"
    registrar_constante_ts(cte_neg, "CTE_ENTERA", int(cte_neg), p.lineno(2))
    pila_operandos.append(cte_neg)
    p[0] = cte_neg

def p_factor_par(p):
    '''factor : PARENTESIS_I expresion_log PARENTESIS_D'''
    p[0] = p[2]

def p_factor_llamada(p):
    '''factor : llamada_funcional'''
    p[0] = p[1]

# 3.8 Declaración y Llamado de Funciones
def p_llamada_funcional(p):
    '''llamada_funcional : ID PARENTESIS_I lista_parametros PARENTESIS_D
                         | ID PARENTESIS_I PARENTESIS_D'''
    cantidad_parametros = 0 if len(p) == 4 else p[3]
    clave_func = f"{p[1]}@global"
    if clave_func not in tabla_simbolos_final or tabla_simbolos_final[clave_func].get("tipo") != "FUNC" or tabla_simbolos_final[clave_func].get("parametros") != cantidad_parametros:
        print(f"Error Semántico (Línea {p.lineno(1)}): Función '{p[1]}' no declarada o cantidad de parámetros incorrecta")
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
    if not os.path.isfile(ruta_archivo):
        ruta_archivo = "testCorrecto01.txt"

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