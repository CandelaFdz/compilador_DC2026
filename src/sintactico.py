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

def abrir_ambito(prefijo):
    global contador_bloques
    contador_bloques += 1
    nuevo_ambito = f"{prefijo}_b{contador_bloques}"
    pila_alcances.append(nuevo_ambito)

def cerrar_ambito():
    if len(pila_alcances) > 1:
        pila_alcances.pop()

def declarar_variable_ts(nombre_var):
    ambito_actual = pila_alcances[-1]
    clave = f"{nombre_var}@{ambito_actual}"
    
    if clave in tabla_simbolos_final:
        # Si ya existe, comprobamos si fue por uso anticipado
        if not tabla_simbolos_final[clave]["declarada"]:
            tabla_simbolos_final[clave]["declarada"] = True
        else:
            print(f"Error semántico: Variable '{nombre_var}' ya declarada en este ámbito.")
    else:
        tabla_simbolos_final[clave] = {
            "nombre": nombre_var,
            "tipo": "INT",
            "alcance": ambito_actual,
            "declarada": True
        }

def usar_variable_ts(nombre_var):
    # Buscar desde el ámbito más interno al más externo (Shadowing)
    for ambito in reversed(pila_alcances):
        clave = f"{nombre_var}@{ambito}"
        if clave in tabla_simbolos_final:
            return clave
            
    # Uso anticipado (Lazy declaration)
    ambito_actual = pila_alcances[-1]
    clave_nueva = f"{nombre_var}@{ambito_actual}"
    tabla_simbolos_final[clave_nueva] = {
        "nombre": nombre_var,
        "tipo": "INT",
        "alcance": ambito_actual,
        "declarada": False
    }
    return clave_nueva

def verificar_variables_no_declaradas():
    for clave, datos in tabla_simbolos_final.items():
        if not datos["declarada"]:
            print(f"Error semántico: Variable '{datos['nombre']}' usada pero nunca declarada en el ámbito {datos['alcance']}.")


def exportar_tabla_simbolos(ruta="tabla_simbolos.txt"):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"{'NOMBRE':<10}{'TIPO':<8}{'VALOR':<8}{'LONGITUD':<10}{'ALCANCE':<12}{'DECLARADA'}\n")
        f.write("-" * 57 + "\n")
        for clave, datos in tabla_simbolos_final.items():
            valor = datos.get("valor", "None")
            longitud = datos.get("longitud", len(datos["nombre"]))
            f.write(f"{datos['nombre']:<10}{datos['tipo']:<8}{str(valor):<8}{str(longitud):<10}{datos['alcance']:<12}{str(datos['declarada'])}\n")


def registrar_constante_ts(nombre, tipo, valor):
    clave = f"{nombre}@global"
    if clave not in tabla_simbolos_final:
        tabla_simbolos_final[clave] = {
            "nombre": nombre,
            "tipo": tipo,
            "valor": valor,
            "longitud": len(str(nombre)) if tipo == "CADENA" else "None",
            "alcance": "global",
            "declarada": True
        }

# ==========================================
# REGLAS SINTÁCTICAS Y SEMÁNTICAS
# ==========================================

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
    clave_var = usar_variable_ts(p[1])
    op_resultado = pila_operandos.pop()
    generar_terceto('=', clave_var, op_resultado)

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
    '''iteracion : WHILE m_while PARENTESIS_I expresion_log PARENTESIS_D m_cond_while bloque'''
    idx_bf = pila_saltos.pop()
    valor_inicio = pila_saltos.pop()
    generar_terceto('BI', '--', valor_inicio)
    lista_tercetos[idx_bf - 1][2] = len(lista_tercetos) + 1

def p_m_while(p):
    '''m_while :'''
    pila_saltos.append(len(lista_tercetos) + 1)
    abrir_ambito("while")

def p_m_cond_while(p):
    '''m_cond_while :'''
    condicion = pila_operandos.pop()
    idx_bf = generar_terceto('BF', condicion, '--')
    pila_saltos.append(idx_bf)

def p_salida_ambos(p):
    '''salida : PRINT PARENTESIS_I CADENA COMA expresion_log PARENTESIS_D PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('PRINT', p[3], resultado_expr)
    registrar_constante_ts(p[3], "CADENA", p[3])

def p_salida_cadena(p):
    '''salida : PRINT PARENTESIS_I CADENA PARENTESIS_D PUNTO_COMA'''
    generar_terceto('PRINT', p[3], '--')
    registrar_constante_ts(p[3], "CADENA", p[3])

def p_salida_expr(p):
    '''salida : PRINT PARENTESIS_I expresion_log PARENTESIS_D PUNTO_COMA'''
    resultado_expr = pila_operandos.pop()
    generar_terceto('PRINT', '--', resultado_expr)

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
              | CTE_ENTERA'''
    if str(p[1]).isalpha() or '_' in str(p[1]): 
        simbolo = usar_variable_ts(p[1])
    else:
        registrar_constante_ts(str(p[1]), "CTE_ENTERA", int(p[1]))
        simbolo = p[1]
    pila_operandos.append(simbolo)
    p[0] = simbolo

def p_factor_par(p):
    '''factor : PARENTESIS_I expresion_log PARENTESIS_D'''
    p[0] = p[2]

def p_factor_llamada(p):
    '''factor : llamada_funcional'''
    p[0] = p[1]

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

    ruta_archivo = os.path.join(os.path.dirname(__file__), "..", "tests", "testCorrecto02.txt")
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