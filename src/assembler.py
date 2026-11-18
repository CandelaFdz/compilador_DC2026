import os
import re
import sys


class GeneradorAssembler:
    """
    Traduce secuencialmente la lista de Tercetos [operador, operando1, operando2]
    y la Tabla de Símbolos a código Assembler ejecutable en MASM32 (Windows x86),
    cumpliendo estrictamente con 06-spec_2.md.
    """

    def __init__(self, lista_tercetos, tabla_simbolos):
        self.lista_tercetos = lista_tercetos
        self.tabla_simbolos = tabla_simbolos

        self.variables_int = []         # Variables INT en formato nombre_alcance
        self.constantes_cadena = {}     # literal_cadena -> etiqueta (CADENA_1, ...)
        self.auxiliares = []            # Variables temporales AUX_i
        self.destinos_salto = set()     # Números de terceto destino de BF, BI (y BV)
        self.parametros_pendientes = [] # Cola temporal de operandos de PARAM
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
        Obtiene en orden las variables INT declaradas en el alcance de la función
        para copiar en ellas los parámetros al ejecutar CALL (Sección 3.6).
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
        Aplica las Secciones 2 y 4 de 06-spec_2.md:
        - Referencia 't3' -> 'AUX_3'
        - Constante entera -> literal numérico
        - Variable 'a@main_b1' -> 'a_main_b1'
        - Variable sin '@alcance' -> busca en la Tabla de Símbolos según la función activa
        """
        op_str = str(op).strip()

        if self._es_referencia_terceto(op_str):
            num = op_str[1:]
            return self._registrar_auxiliar(num)

        if self._es_constante_entera(op_str):
            return op_str

        if "@" in op_str:
            var_asm = op_str.replace("@", "_")
            if var_asm not in self.variables_int:
                self.variables_int.append(var_asm)
            return var_asm

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
        Pre-escaneo (Sección 2):
        - Registra variables INT y constantes CADENA de la Tabla de Símbolos.
        - Identifica todos los números de terceto a los que apuntan los saltos BF y BI.
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

        for terceto in self.lista_tercetos:
            op, op1, op2 = terceto[0], terceto[1], terceto[2]
            if op in ("BF", "BI", "BV"):
                destino = str(op2).strip()
                if destino.isdigit():
                    self.destinos_salto.add(int(destino))
            elif op == "PRINT" and op1 != "--":
                self._registrar_cadena(op1)

    # ==========================================
    # 2. TRADUCCIÓN DE TERCETOS (MÉTODO CÁTEDRA)
    # ==========================================
    def generar_assembler(self):
        self._preparar_estructura()
        instrucciones_code = []

        MAPA_ARITMETICO = {
            "+": "ADD", "SUMA": "ADD",
            "-": "SUB", "RESTA": "SUB",
            "*": "IMUL", "MULTIPLICAR": "IMUL",
            "/": "IDIV", "DIVISION": "IDIV"
        }

        # Sección 3.3: Salto condicional usando la condición INVERSA al operador original
        MAPA_COMPARADORES_INVERSO = {
            ">":  "JLE", "MAYOR":    "JLE",
            "<":  "JGE", "MENOR":    "JGE",
            "==": "JNE", "IGUAL":    "JNE",
            "!=": "JE",  "DISTINTO": "JE",
            ">=": "JL",  "MAYOR_E":  "JL",
            "<=": "JG",  "MENOR_E":  "JG"
        }

        for i, (op, op1, op2) in enumerate(self.lista_tercetos, start=1):
            # Emitir etiqueta LABEL_i: si el terceto actual es destino de algún salto
            if i in self.destinos_salto:
                instrucciones_code.append(f"LABEL_{i}:")

            # 3.1 Asignaciones (=)
            if op in ("=", ":=", "ASIG"):
                destino = self._resolver_operando(op1)
                origen = self._resolver_operando(op2)
                instrucciones_code.append(f"    MOV R1, {origen}")
                instrucciones_code.append(f"    MOV {destino}, R1")

            # 3.2 Expresiones Aritméticas (+, -, *, /)
            elif op in MAPA_ARITMETICO:
                inst_asm = MAPA_ARITMETICO[op]
                operando1 = self._resolver_operando(op1)
                operando2 = self._resolver_operando(op2)
                aux_i = self._registrar_auxiliar(i)

                if inst_asm in ("ADD", "SUB", "IMUL"):
                    instrucciones_code.append(f"    MOV R1, {operando1}")
                    instrucciones_code.append(f"    {inst_asm} R1, {operando2}")
                    instrucciones_code.append(f"    MOV {aux_i}, R1")
                elif inst_asm == "IDIV":
                    instrucciones_code.append(f"    MOV R2, {operando2}")
                    instrucciones_code.append(f"    CMP R2, 0")
                    instrucciones_code.append(f"    JE _error_div_cero")
                    instrucciones_code.append(f"    MOV R1, {operando1}")
                    instrucciones_code.append(f"    CDQ")
                    instrucciones_code.append(f"    IDIV R2")
                    instrucciones_code.append(f"    MOV {aux_i}, R1")

            # 3.3 Comparadores (con condición inversa hacia _fin_cmp_i)
            elif op in MAPA_COMPARADORES_INVERSO:
                salto_inverso = MAPA_COMPARADORES_INVERSO[op]
                operando1 = self._resolver_operando(op1)
                operando2 = self._resolver_operando(op2)
                aux_i = self._registrar_auxiliar(i)
                lbl_fin_cmp = f"_fin_cmp_{i}"

                instrucciones_code.append(f"    MOV {aux_i}, 0")
                instrucciones_code.append(f"    MOV R1, {operando1}")
                instrucciones_code.append(f"    CMP R1, {operando2}")
                instrucciones_code.append(f"    {salto_inverso} {lbl_fin_cmp}")
                instrucciones_code.append(f"    MOV {aux_i}, -1")
                instrucciones_code.append(f"{lbl_fin_cmp}:")

            # 3.3 Operadores Lógicos (AND / OR)
            # 3.3 Operadores Lógicos (AND / OR) con soporte de cortocircuito en bucles
            elif op in ("AND", "OR"):
                operando1 = self._resolver_operando(op1)
                operando2 = self._resolver_operando(op2)
                aux_i = self._registrar_auxiliar(i)
                lbl_fin_log = f"_fin_log_{i}"
                sig_terceto = i + 1

                instrucciones_code.append(f"    MOV R1, {operando1}")
                instrucciones_code.append(f"    {op} R1, {operando2}")
                instrucciones_code.append(f"    MOV {aux_i}, R1")

                # Si el salto de cortocircuito (BF en AND, BI en OR) apunta a LABEL_{i+1},
                # fijar en esa etiqueta el valor de cortocircuito (0 para AND, -1 para OR)
                if sig_terceto in self.destinos_salto:
                    valor_corto = "0" if op == "AND" else "-1"
                    instrucciones_code.append(f"    JMP {lbl_fin_log}")
                    instrucciones_code.append(f"LABEL_{sig_terceto}:")
                    instrucciones_code.append(f"    MOV {aux_i}, {valor_corto}")
                    instrucciones_code.append(f"{lbl_fin_log}:")
                    self.destinos_salto.remove(sig_terceto)

            # 3.4 Saltos Condicionales e Incondicionales (BI, BF)
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
                    fin_proc = f"LABEL_{i}:" if i in self.destinos_salto else ""
                    if fin_proc and instrucciones_code[-1] == fin_proc:
                        instrucciones_code.pop()
                        instrucciones_code.append(f"{self.funcion_actual} ENDP\n")
                        instrucciones_code.append(fin_proc)
                    else:
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

        # Si algún salto apunta al final de los tercetos (len + 1), emitir su etiqueta antes de cerrar el PROC
        fin_tercetos = len(self.lista_tercetos) + 1
        if fin_tercetos in self.destinos_salto:
            instrucciones_code.append(f"LABEL_{fin_tercetos}:")

        if self.funcion_actual is not None:
            instrucciones_code.append(f"{self.funcion_actual} ENDP")

        # ==========================================
        # 3. ARMADO DEL ARCHIVO .ASM PARA MASM32
        # ==========================================
        cabecera_masm32 = [
            ".386",
            ".model flat, stdcall",
            "option casemap :none",
            "include \\masm32\\include\\windows.inc",
            "include \\masm32\\include\\kernel32.inc",
            "include \\masm32\\include\\msvcrt.inc",
            "includelib \\masm32\\lib\\kernel32.lib",
            "includelib \\masm32\\lib\\msvcrt.lib",
            "",
            "PRINT_STR MACRO cadena",
            "    invoke crt_printf, addr FMT_STR, addr cadena",
            "ENDM",
            "",
            "PRINT_INT MACRO reg_val",
            "    invoke crt_printf, addr FMT_INT, reg_val",
            "ENDM",
            "",
            ".data",
            '    FMT_STR db "%s", 13, 10, 0',
            '    FMT_INT db "%d", 13, 10, 0'
        ]

        lineas_asm = list(cabecera_masm32)

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

        # Punto de entrada de Windows que invoca a main y rutina de error por división por cero
        lineas_asm.extend([
            "",
            "start:",
            "    CALL main",
            "    invoke ExitProcess, 0",
            "",
            "_error_div_cero:",
            "    PRINT_STR MSG_ERR_DIV_CERO",
            "    invoke ExitProcess, 1",
            "END start"
        ])

        texto_asm = "\n".join(lineas_asm) + "\n"

        # Sección 3 (Mapeo de Pseudo-Registros a MASM32): reemplazar R1 -> EAX y R2 -> EBX
        texto_asm = re.sub(r'\bR1\b', 'EAX', texto_asm)
        texto_asm = re.sub(r'\bR2\b', 'EBX', texto_asm)

        return texto_asm

    def exportar_asm(self, ruta="salida.asm"):
        codigo = self.generar_assembler()
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(codigo)
        return codigo


# ==========================================
# LECTURA DESDE ARCHIVOS .TXT
# ==========================================
def leer_tercetos_txt(ruta="tercetos.txt"):
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
    tabla = {}
    if not os.path.isfile(ruta):
        return tabla
    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    for linea in lineas[2:]:
        linea_strip = linea.strip()
        if not linea_strip:
            continue
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


if __name__ == "__main__":
    import sintactico
    import ply.yacc as yacc
    from lexico import AnalizadorLexico

    ruta_fuente = os.path.join(os.path.dirname(__file__), "..", "tests", "testIncorrecto03.txt")
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
    

    import subprocess
    subprocess.run([r"G:\masm32\bin\ml.exe", "/c", "/Zd", "/coff", "salida.asm"])
    subprocess.run([r"G:\masm32\bin\Link.exe", "/SUBSYSTEM:CONSOLE", "salida.obj"])
    print("\n=== EJECUTANDO PROGRAMA COMPILADO (salida.exe) ===")
    subprocess.run(["salida.exe"])