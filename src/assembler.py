import os
import re
import sys

class GeneradorAssembler:
    """
    Traduce la lista secuencial de Tercetos [op, op1, op2] y la Tabla de Símbolos
    a código Assembler siguiendo las reglas de spec.md y el método de la cátedra.
    """

    def __init__(self, lista_tercetos, tabla_simbolos):
        self.lista_tercetos = lista_tercetos
        self.tabla_simbolos = tabla_simbolos

        self.variables_int = []        # Variables INT en formato nombre_alcance
        self.constantes_cadena = {}    # literal_cadena -> etiqueta_assembler (ej. CADENA_1)
        self.auxiliares = []           # Variables temporales AUX_i
        self.destinos_salto = set()    # Números de terceto destino de BF, BV, BI
        self.parametros_pendientes = [] # Lista temporal para tercetos PARAM
        self.funcion_actual = None

    # ==========================================
    # 1. RESOLUCIÓN DE NOMBRES Y PRE-ESCANEO
    # ==========================================
    def _es_referencia_terceto(self, op):
        return isinstance(op, str) and bool(re.match(r'^[tT]\d+$', op.strip()))

    def _es_constante_entera(self, op):
        if isinstance(op, int):
            return True
        if isinstance(op, str):
            return bool(re.match(r'^-?\d+$', op.strip()))
        return False

    def _registrar_auxiliar(self, indice):
        nombre_aux = f"AUX_{indice}"
        if nombre_aux not in self.auxiliares:
            self.auxiliares.append(nombre_aux)
        return nombre_aux

    def _registrar_cadena(self, literal):
        texto = str(literal).strip()
        if texto not in self.constantes_cadena:
            idx = len(self.constantes_cadena) + 1
            self.constantes_cadena[texto] = f"CADENA_{idx}"
        return self.constantes_cadena[texto]

    def _obtener_variables_de_funcion(self, nombre_func):
        """
        Retorna en orden de declaración las variables de la Tabla de Símbolos
        cuyo alcance pertenece a la función indicada (ej. 'sumar_b1').
        """
        vars_func = []
        prefijo = f"{nombre_func}_b"
        for clave, datos in self.tabla_simbolos.items():
            if datos.get("tipo") == "INT":
                alcance = datos.get("alcance", "")
                if alcance == nombre_func or alcance.startswith(prefijo):
                    var_asm = f"{datos['nombre']}_{alcance}"
                    if var_asm not in vars_func:
                        vars_func.append(var_asm)
        return vars_func

    def _resolver_operando(self, op):
        """
        Cumple las secciones 2 y 4 de la spec:
        - Referencia 't3' -> 'AUX_3'
        - Constante entera -> valor literal
        - Variable 'a@main_b1' -> 'a_main_b1'
        - Variable sin '@alcance' -> busca en la Tabla de Símbolos dentro de la función activa
        """
        op_str = str(op).strip()

        # 1. Referencia a otro terceto (ej. "t3" -> "AUX_3")
        if self._es_referencia_terceto(op_str):
            num = op_str[1:]
            return self._registrar_auxiliar(num)

        # 2. Constante numérica entera
        if self._es_constante_entera(op_str):
            return op_str

        # 3. Identificador con formato nombre@alcance (Shadowing resuelto desde sintactico.py)
        if "@" in op_str:
            var_asm = op_str.replace("@", "_")
            if var_asm not in self.variables_int:
                self.variables_int.append(var_asm)
            return var_asm

        # 4. Identificador sin '@alcance': buscar coincidencia con la función actual en la TS
        if self.funcion_actual:
            prefijo = f"{self.funcion_actual}_b"
            for clave, datos in self.tabla_simbolos.items():
                if datos.get("tipo") == "INT" and datos.get("nombre") == op_str:
                    alcance = datos.get("alcance", "")
                    if alcance == self.funcion_actual or alcance.startswith(prefijo):
                        var_asm = f"{op_str}_{alcance}"
                        if var_asm not in self.variables_int:
                            self.variables_int.append(var_asm)
                        return var_asm

        # Fallback en caso de variable global o no calificada
        for clave, datos in self.tabla_simbolos.items():
            if datos.get("tipo") == "INT" and datos.get("nombre") == op_str:
                var_asm = f"{op_str}_{datos.get('alcance', 'global')}"
                if var_asm not in self.variables_int:
                    self.variables_int.append(var_asm)
                return var_asm

        if op_str not in self.variables_int:
            self.variables_int.append(op_str)
        return op_str

    def _preparar_estructura(self):
        """
        Recorre previamente la Tabla de Símbolos y la lista_tercetos para:
        - Declarar todas las variables INT (con alcance concatenado) y CADENA.
        - Identificar todos los números de terceto destino de BF, BV y BI.
        """
        for clave, datos in self.tabla_simbolos.items():
            tipo = datos.get("tipo", "")
            nombre = datos.get("nombre", "")
            alcance = datos.get("alcance", "global")

            if tipo == "INT":
                var_asm = f"{nombre}_{alcance}"
                if var_asm not in self.variables_int:
                    self.variables_int.append(var_asm)
            elif tipo == "CADENA":
                self._registrar_cadena(nombre)

        for i, terceto in enumerate(self.lista_tercetos, start=1):
            op, op1, op2 = terceto[0], terceto[1], terceto[2]
            if op in ("BF", "BV", "BI"):
                destino = str(op2).strip()
                if destino.isdigit():
                    self.destinos_salto.add(int(destino))
            elif op == "PRINT" and op1 != "--":
                self._registrar_cadena(op1)

    # ==========================================
    # 2. TRADUCCIÓN DE TERCETOS A ASSEMBLER
    # ==========================================
    def generar_assembler(self):
        self._preparar_estructura()
        instrucciones_code = []

        # Mapeos para soportar tanto nombres de tokens de lexico.py como símbolos de spec.md
        MAPA_ARITMETICO = {
            "+": "ADD", "SUMA": "ADD",
            "-": "SUB", "RESTA": "SUB",
            "*": "MUL", "MULTIPLICAR": "MUL",
            "/": "DIV", "DIVISION": "DIV"
        }

        MAPA_COMPARADORES = {
            "==": "JE",  "IGUAL": "JE",
            "!=": "JNE", "DISTINTO": "JNE",
            ">":  "JG",  "MAYOR": "JG",
            "<":  "JL",  "MENOR": "JL",
            ">=": "JGE", "MAYOR_E": "JGE",
            "<=": "JLE", "MENOR_E": "JLE"
        }

        for i, (op, op1, op2) in enumerate(self.lista_tercetos, start=1):
            # Emitir etiqueta LABEL_X: si este terceto es destino de algún salto
            if i in self.destinos_salto:
                instrucciones_code.append(f"LABEL_{i}:")

            # 3.1 Asignaciones (=)
            if op in ("=", ":=", "ASIG"):
                destino = self._resolver_operando(op1)
                origen = self._resolver_operando(op2)
                instrucciones_code.append(f"    MOV R1, {origen}")
                instrucciones_code.append(f"    MOV {destino}, R1")

            # 3.2 Expresiones Aritméticas (+, -, *, / o SUMA, RESTA, MULTIPLICAR, DIVISION)
            elif op in MAPA_ARITMETICO:
                operacion_asm = MAPA_ARITMETICO[op]
                operando1 = self._resolver_operando(op1)
                operando2 = self._resolver_operando(op2)
                aux_i = self._registrar_auxiliar(i)

                if operacion_asm in ("ADD", "SUB", "MUL"):
                    instrucciones_code.append(f"    MOV R1, {operando1}")
                    instrucciones_code.append(f"    {operacion_asm} R1, {operando2}")
                    instrucciones_code.append(f"    MOV {aux_i}, R1")
                elif operacion_asm == "DIV":
                    # División con control de Error por Cero en R2
                    instrucciones_code.append(f"    MOV R2, {operando2}")
                    instrucciones_code.append(f"    CMP R2, 0")
                    instrucciones_code.append(f"    JE _error_div_cero")
                    instrucciones_code.append(f"    MOV R1, {operando1}")
                    instrucciones_code.append(f"    DIV R2")
                    instrucciones_code.append(f"    MOV {aux_i}, R1")

            # 3.3 Comparadores (<, >, ==, !=, <=, >= o sus tokens equivalentes)
            elif op in MAPA_COMPARADORES:
                salto_cond = MAPA_COMPARADORES[op]
                operando1 = self._resolver_operando(op1)
                operando2 = self._resolver_operando(op2)
                aux_i = self._registrar_auxiliar(i)
                lbl_verdadero = f"_CMP_VERDADERO_{i}"
                lbl_fin = f"_CMP_FIN_{i}"

                instrucciones_code.append(f"    MOV {aux_i}, 0")
                instrucciones_code.append(f"    MOV R1, {operando1}")
                instrucciones_code.append(f"    CMP R1, {operando2}")
                instrucciones_code.append(f"    {salto_cond} {lbl_verdadero}")
                instrucciones_code.append(f"    JMP {lbl_fin}")
                instrucciones_code.append(f"{lbl_verdadero}:")
                instrucciones_code.append(f"    MOV {aux_i}, -1")
                instrucciones_code.append(f"{lbl_fin}:")

            # 3.3 Operadores Lógicos (AND / OR)
            elif op in ("AND", "OR"):
                operando1 = self._resolver_operando(op1)
                operando2 = self._resolver_operando(op2)
                aux_i = self._registrar_auxiliar(i)

                instrucciones_code.append(f"    MOV R1, {operando1}")
                instrucciones_code.append(f"    {op} R1, {operando2}")
                instrucciones_code.append(f"    MOV {aux_i}, R1")

            # 3.4 Saltos Condicionales e Incondicionales (BI, BF, BV)
            elif op == "BI":
                destino = str(op2).strip()
                instrucciones_code.append(f"    JMP LABEL_{destino}")

            elif op == "BF":
                condicion = self._resolver_operando(op1)
                destino = str(op2).strip()
                instrucciones_code.append(f"    MOV R1, {condicion}")
                instrucciones_code.append(f"    CMP R1, 0")
                instrucciones_code.append(f"    JE LABEL_{destino}")

            elif op == "BV":
                condicion = self._resolver_operando(op1)
                destino = str(op2).strip()
                instrucciones_code.append(f"    MOV R1, {condicion}")
                instrucciones_code.append(f"    CMP R1, 0")
                instrucciones_code.append(f"    JNE LABEL_{destino}")

            # 3.5 Sentencias de Salida (PRINT)
            elif op == "PRINT":
                if op1 != "--":
                    etiqueta_cad = self._registrar_cadena(op1)
                    instrucciones_code.append(f"    PRINT_STR {etiqueta_cad}")
                if op2 != "--":
                    valor_mostrar = self._resolver_operando(op2)
                    instrucciones_code.append(f"    MOV R1, {valor_mostrar}")
                    instrucciones_code.append(f"    PRINT_INT R1")

            # 3.6 Funciones (FUNC, PARAM, CALL, RET)
            elif op == "FUNC":
                if self.funcion_actual is not None:
                    instrucciones_code.append(f"{self.funcion_actual} ENDP\n")
                self.funcion_actual = str(op1).strip()
                instrucciones_code.append(f"{self.funcion_actual} PROC")

            elif op == "PARAM":
                param_resuelto = self._resolver_operando(op1)
                self.parametros_pendientes.append(param_resuelto)

            elif op == "CALL":
                nombre_func = str(op1).strip()
                cant_params = int(op2) if str(op2).isdigit() else 0
                vars_funcion = self._obtener_variables_de_funcion(nombre_func)

                # Tomar los parámetros guardados para esta llamada y copiarlos en orden
                params_actuales = self.parametros_pendientes[:cant_params]
                self.parametros_pendientes = self.parametros_pendientes[cant_params:]

                for idx_p, param_val in enumerate(params_actuales):
                    if idx_p < len(vars_funcion):
                        var_formal = vars_funcion[idx_p]
                    else:
                        var_formal = f"param_{idx_p + 1}_{nombre_func}"
                        if var_formal not in self.variables_int:
                            self.variables_int.append(var_formal)
                    instrucciones_code.append(f"    MOV R1, {param_val}")
                    instrucciones_code.append(f"    MOV {var_formal}, R1")

                aux_i = self._registrar_auxiliar(i)
                instrucciones_code.append(f"    CALL {nombre_func}")
                instrucciones_code.append(f"    MOV {aux_i}, R1")

            elif op == "RET":
                valor_retorno = self._resolver_operando(op1)
                instrucciones_code.append(f"    MOV R1, {valor_retorno}")
                instrucciones_code.append(f"    RET")

        # Si algún salto apunta al final de la lista de tercetos (len + 1), emitir su etiqueta
        fin_tercetos = len(self.lista_tercetos) + 1
        if fin_tercetos in self.destinos_salto:
            instrucciones_code.append(f"LABEL_{fin_tercetos}:")

        if self.funcion_actual is not None:
            instrucciones_code.append(f"{self.funcion_actual} ENDP")

        # Construir el archivo .asm final con sección .data y sección .code
        lineas_asm = [".data"]

        for var_int in self.variables_int:
            lineas_asm.append(f"    {var_int} dd 0")

        for literal_texto, nombre_cad in self.constantes_cadena.items():
            texto_limpio = literal_texto.strip('"')
            lineas_asm.append(f'    {nombre_cad} db "{texto_limpio}", 0')

        lineas_asm.append('    MSG_ERR_DIV_CERO db "Error en ejecucion: Division por cero", 0')

        for aux in self.auxiliares:
            lineas_asm.append(f"    {aux} dd 0")

        lineas_asm.append("\n.code")
        lineas_asm.extend(instrucciones_code)

        # Rutina de error de división por cero al pie de la sección de código
        lineas_asm.append("\n_error_div_cero:")
        lineas_asm.append("    PRINT_STR MSG_ERR_DIV_CERO")
        lineas_asm.append("    HLT")

        return "\n".join(lineas_asm) + "\n"

    def exportar_asm(self, ruta="salida.asm"):
        codigo = self.generar_assembler()
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(codigo)
        return codigo


# ==========================================
# FUNCIONES DE LECTURA DESDE ARCHIVOS .TXT
# ==========================================
def leer_tercetos_txt(ruta="tercetos.txt"):
    """Lee tercetos.txt con el formato: 1 (FUNC, main, --)"""
    tercetos = []
    patron = re.compile(r'^\d+\s*\((.+?),\s*(.+?),\s*(.+?)\)$')
    if not os.path.isfile(ruta):
        return tercetos
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            m = patron.match(linea)
            if m:
                tercetos.append([m.group(1).strip(), m.group(2).strip(), m.group(3).strip()])
    return tercetos


def leer_tabla_simbolos_txt(ruta="tabla_simbolos.txt"):
    """Lee tabla_simbolos.txt en caso de ejecutar assembler.py por separado."""
    tabla = {}
    if not os.path.isfile(ruta):
        return tabla
    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    for linea in lineas[2:]:  # Saltar cabecera y guiones
        linea_strip = linea.strip()
        if not linea_strip:
            continue
        # Soportar cadenas con espacios si llegaran a aparecer en la tabla
        if linea_strip.startswith('"'):
            fin_comilla = linea_strip.find('"', 1)
            if fin_comilla != -1:
                nombre = linea_strip[:fin_comilla + 1]
                resto = linea_strip[fin_comilla + 1:].split()
                if len(resto) >= 5:
                    tipo, valor, longitud, alcance, declarada = resto[0], resto[1], resto[2], resto[3], resto[4]
                    tabla[f"{nombre}@{alcance}"] = {
                        "nombre": nombre,
                        "tipo": tipo,
                        "valor": valor,
                        "longitud": longitud,
                        "alcance": alcance,
                        "declarada": (declarada == "True")
                    }
                continue
        partes = linea_strip.split()
        if len(partes) >= 6:
            nombre, tipo, valor, longitud, alcance, declarada = partes[0], partes[1], partes[2], partes[3], partes[4], partes[5]
            tabla[f"{nombre}@{alcance}"] = {
                "nombre": nombre,
                "tipo": tipo,
                "valor": valor,
                "longitud": longitud,
                "alcance": alcance,
                "declarada": (declarada == "True")
            }
    return tabla


# ==========================================
# BLOQUE PRINCIPAL
# ==========================================
if __name__ == "__main__":
    import sintactico
    import ply.yacc as yacc
    from lexico import AnalizadorLexico

    # Si ya existen tercetos.txt y tabla_simbolos.txt y no se pasa código fuente, los usa;
    # de lo contrario, ejecuta el análisis sintáctico sobre el archivo de prueba y genera salida.asm.
    ruta_fuente = os.path.join(os.path.dirname(__file__), "..", "tests", "testCorrecto01.txt")
    if not os.path.isfile(ruta_fuente):
        ruta_fuente = "testCorrecto01.txt"

    if os.path.isfile(ruta_fuente):
        parser = yacc.yacc(module=sintactico)
        with open(ruta_fuente, "r", encoding="utf-8") as f:
            codigo_fuente = f.read()

        lexer_instancia = AnalizadorLexico()
        lexer_instancia.input(codigo_fuente)
        lexer_instancia.c = lexer_instancia._read_char()

        parser.parse(codigo_fuente, lexer=lexer_instancia)
        sintactico.verificar_variables_no_declaradas()
        sintactico.exportar_tercetos("tercetos.txt")
        sintactico.exportar_tabla_simbolos("tabla_simbolos.txt")

        tercetos_entrada = sintactico.lista_tercetos
        ts_entrada = sintactico.tabla_simbolos_final
    else:
        tercetos_entrada = leer_tercetos_txt("tercetos.txt")
        ts_entrada = leer_tabla_simbolos_txt("tabla_simbolos.txt")

    generador = GeneradorAssembler(tercetos_entrada, ts_entrada)
    codigo_asm = generador.exportar_asm("salida.asm")
    print("=== ARCHIVO salida.asm GENERADO EXITOSAMENTE ===")
    print(codigo_asm)