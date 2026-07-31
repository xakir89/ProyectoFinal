matrizPaquetes = []

# FUNCIONES RECURSIVAS DE APOYO
def existe_codigo(codigo_buscar, lista_paquetes):
    # Verifica recursivamente si un código de guía ya está registrado en la matriz.
    if lista_paquetes == []:
        return False
    if lista_paquetes[0][0] == codigo_buscar: 
        return True
    return existe_codigo(codigo_buscar, lista_paquetes[1:])

def calcular_peso_total(lista_paquetes):
    if lista_paquetes == []:
        return 0
    return lista_paquetes[0][1] + calcular_peso_total(lista_paquetes[1:])

def contar_paquetes_fragiles(lista_paquetes):
    if lista_paquetes == []:
        return 0
    if lista_paquetes[0][3]:  
        return 1 + contar_paquetes_fragiles(lista_paquetes[1:])
    return contar_paquetes_fragiles(lista_paquetes[1:])

def contar_paquetes_express(lista_paquetes):
    if lista_paquetes == []:
        return 0
    if lista_paquetes[0][4]:  
        return 1 + contar_paquetes_express(lista_paquetes[1:])
    return contar_paquetes_express(lista_paquetes[1:])

def obtener_paquetes_sobrepeso(lista_paquetes, peso_limite):
    if lista_paquetes == []:
        return []
    if lista_paquetes[0][1] > peso_limite:
        return [lista_paquetes[0][0]] + obtener_paquetes_sobrepeso(lista_paquetes[1:], peso_limite)
    return obtener_paquetes_sobrepeso(lista_paquetes[1:], peso_limite)

# VALIDACIÓN Y REGISTRO
def validarPaquete(codigo, pesoTexto, fleteTexto, ciudad):
    # Valida los campos obligatorios, incluyendo los requerimientos de código y flete."""
    if codigo == "" or pesoTexto == "" or fleteTexto == "" or ciudad == "":
        return False, "Debes completar todos los campos, incluyendo la ciudad."
    
    if not (codigo.isdigit() and len(codigo) >= 4):
        return False, "El código de guía debe ser numérico y tener 4 dígitos o más."

    if existe_codigo(codigo, matrizPaquetes):
        return False, f"El código de guía '{codigo}' ya se encuentra registrado en el manifiesto."

    try:
        peso = float(pesoTexto)
    except ValueError:
        return False, "El peso debe ser un número (ej: 12.5)."

    if peso <= 0:
        return False, "El peso debe ser mayor a 0 kg."

    try:
        valorFlete = float(fleteTexto)
    except ValueError:
        return False, "El valor del flete debe ser un número."

    if valorFlete < 11500:
        return False, "El valor del flete mínimo aceptado es de $11,500 en adelante."

    return True, (peso, valorFlete)

def registrarPaquete(codigo, peso, valorFlete, esFragil, esExpress, ciudad):
    # agrega el paquete a la matriz y retorna la fila visual.
    nuevoPaquete = [codigo, peso, valorFlete, esFragil, esExpress, ciudad]
    matrizPaquetes.append(nuevoPaquete)

    tipo = ""
    if esFragil and esExpress:
        tipo = "Frágil + Express"
    elif esFragil:
        tipo = "Frágil"
    elif esExpress:
        tipo = "Express"
    else:
        tipo = "Normal"

    return [codigo, f"{peso:.2f} kg", f"${valorFlete:,.0f}", tipo, ciudad]

# SISTEMA DE CONSOLIDACIÓN CON PRIORIDAD Y ASIGNACIÓN
def separar_paquetes(lista):
    """Separa la matriz en 4 grupos para asegurar el orden exacto de prioridad."""
    if lista == []:
        return [], [], [], []
    
    oversized_pri, pri, oversized_nor, nor = separar_paquetes(lista[1:])
    paquete = lista[0]
    peso = paquete[1]
    esFragil = paquete[3]
    esExpress = paquete[4]
    es_prioritario = esFragil or esExpress
    
    # Regla: Si pasa de 300, se va a su propio camión (clasificado por prioridad)
    if peso > 300:
        if es_prioritario:
            return [paquete] + oversized_pri, pri, oversized_nor, nor
        else:
            return oversized_pri, pri, [paquete] + oversized_nor, nor
    # Regla: Paquetes combinables
    else:
        if es_prioritario:
            return oversized_pri, [paquete] + pri, oversized_nor, nor
        else:
            return oversized_pri, pri, oversized_nor, [paquete] + nor

def armar_carros_oversized(oversized):
    #Convierte cada paquete gigante en un carro independiente.
    if oversized == []:
        return []
    return [[oversized[0]]] + armar_carros_oversized(oversized[1:])

def encontrar_un_carro(paquetes, carga_actual, sobrantes):
    # Busca una combinación exacta (250-300kg) y retorna el carro y los paquetes no usados.
    peso = calcular_peso_total(carga_actual)
    # Si la carga ya está en el rango ideal, se retorna el carro y todos los sobrantes acumulados
    if 250 <= peso <= 300:
        return carga_actual, paquetes + sobrantes
    # Rutas muertas: Nos pasamos de peso o ya no quedan más paquetes
    if peso > 300 or paquetes == []:
        return None, [] 
    # Rama 1: Intentamos empacar este paquete
    carro, resto = encontrar_un_carro(paquetes[1:], carga_actual + [paquetes[0]], sobrantes)
    if carro is not None:
        return carro, resto
    # Rama 2: Si incluirlo no funcionó, lo dejamos como sobrante y probamos con el siguiente
    return encontrar_un_carro(paquetes[1:], carga_actual, sobrantes + [paquetes[0]])

def armar_todos_los_carros(disponibles):
    """Arma todos los carros posibles agotando la lista en orden (Prioridad y luego Normal)."""
    if disponibles == []:
        return [], [] 
    carro, resto_paquetes = encontrar_un_carro(disponibles, [], [])
    if carro is None:
        return [], disponibles # Ya no es posible armar más carros   
    siguientes_carros, sobrantes_finales = armar_todos_los_carros(resto_paquetes)
    return [carro] + siguientes_carros, sobrantes_finales

def consolidar_manifiesto(lista_paquetes):
    """Función principal que orquesta la creación completa de las rutas en el orden solicitado."""
    oversized_pri, pri, oversized_nor, nor = separar_paquetes(lista_paquetes)
    # 1. Los prioritarios pesados van primero
    carros_gigantes_pri = armar_carros_oversized(oversized_pri)
    # 2. Armamos combinaciones dando prioridad a los envíos prioritarios y rellenando con normales
    candidatos = pri + nor
    carros_combinados, sobrantes = armar_todos_los_carros(candidatos)
    # 3. Los normales pesados van después de agotar toda la prioridad posible
    carros_gigantes_nor = armar_carros_oversized(oversized_nor)
    # El orden en el que se suman las listas dicta cómo salen en pantalla
    return carros_gigantes_pri + carros_combinados + carros_gigantes_nor, sobrantes

# FUNCIONES RECURSIVAS DE FORMATO VISUAL
def agrupar_por_ciudades(carga):
    if carga == []:
        return {}
    resto = agrupar_por_ciudades(carga[1:])
    paquete = carga[0]
    ciudad = paquete[5]
    if ciudad not in resto:
        resto[ciudad] = []
    resto[ciudad] = [paquete] + resto[ciudad]
    return resto

def obtener_codigos_recursivo(paquetes):
    if paquetes == []: return ""
    if len(paquetes) == 1: return paquetes[0][0]
    return paquetes[0][0] + ", " + obtener_codigos_recursivo(paquetes[1:])

def formatear_diccionario_ciudades(dic, llaves):
    if llaves == []: return ""
    ciudad = llaves[0]
    paquetes = dic[ciudad]
    return f"  - {ciudad}: {obtener_codigos_recursivo(paquetes)}\n" + formatear_diccionario_ciudades(dic, llaves[1:])

def formatear_salida_carros(carros, num_carro):
    if carros == []: return ""
    carro = carros[0]
    peso_opcion = calcular_peso_total(carro)
    dic_ciudades = agrupar_por_ciudades(carro)
    texto_ciudades = formatear_diccionario_ciudades(dic_ciudades, list(dic_ciudades.keys()))
    
    # Verificación de carro de envío único
    if len(carro) == 1 and peso_opcion > 300:
        encabezado = f"\n[ CARRO {num_carro} (ENVÍO ÚNICO POR SOBREPESO) | Peso: {peso_opcion:.2f} kg ]\n"
    else:
        encabezado = f"\n[ CARRO {num_carro} | Peso: {peso_opcion:.2f} kg ]\n"   
    return encabezado + texto_ciudades + formatear_salida_carros(carros[1:], num_carro + 1)

def formatear_sobrantes(sobrantes):
    if sobrantes == []: return "\n[ ESTADO LOGÍSTICO: Todos los paquetes combinables fueron asignados a un carro. ]\n"
    dic_ciudades = agrupar_por_ciudades(sobrantes)
    texto_ciudades = formatear_diccionario_ciudades(dic_ciudades, list(dic_ciudades.keys()))
    return "\n[ PAQUETES PENDIENTES SIN ASIGNAR (No alcanzan el peso para un carro) ]\n" + texto_ciudades