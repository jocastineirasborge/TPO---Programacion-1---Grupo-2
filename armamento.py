"""
Módulo armamento.py
Administra el catálogo de armas, la munición disponible y las celdas afectadas por cada disparo. 
"""
import tablero
import flota
# ---------------------------------------------
# Catálogo de armas
# ---------------------------------------------

CATALOGO_ARMAS = {
    "T": {
        "nombre": "Torpedo",
        "municion": None, # Munición ilimitada
        "descripcion": "Únicamente la celda apuntada."
    },
    "R": {
        "nombre": "Misil de racimo",
        "municion": 3,
        "descripcion": "La celda apuntada y sus seis vecinas ortogonales."
    },
    "C": {
        "nombre": "Carga de profundidad",
        "municion": 2,
        "descripcion": "Toda la recta sobre el eje z."
    },
    "S": {
        "nombre": "Sonar",
        "municion": 4,
        "descripcion": "Revela un plano entero del cubo."
    },
    "L": {
        "nombre": "Barrido láser",
        "municion": 2,
        "descripcion": "Una recta completa sobre el eje x o sobre el eje y."
    },
    "O": {
        "nombre": "Onda expansiva",
        "municion": 1,
        "descripcion": "Se propaga en forma recursiva desde el punto, con radio decreciente."
    },
    "G": {
        "nombre": "Torpedo guiado",
        "municion": 1,
        "descripcion": "Busca en forma recursiva una celda contigua."
    }
}


def obtener_catalogo_armas():
    """
    Objetivo: Devolver la lista de catálogo de armas disponible.
    Devuelve:
        list: Lista de tuplas con el catálogo de armas.
    """
    return CATALOGO_ARMAS

# ----------------------------------
# Funciones de efecto de cada arma
# ----------------------------------

def efecto_torpedo(objetivo, n):
    """
    Objetivo: Calcular celdas afectadas por el torpedo.
    Parámetros:
        - Objetivo(tuple): Coordenada en (z, x, y) del disparo.
        - n(int): Tamaño del arista del cubo.
    Devuelve:
        List: Lista que contiene la coordenada en formato tupla del punto apuntado.
    """
    z, x, y = objetivo
    if 1 <= z <= n and 1 <= x <= n and 1 <= y <= n:
        return [objetivo]
    return []


def efecto_misil_de_racimo(objetivo, n):
    """
    Objetivo: Calcula la lista de celdas afectadas por el misil de racimo.
    Parámetros:
        - objetivo(tuple): Coordenada central (z, x, y) del disparo.
        - n(int): Tamaño del arista del cubo.
    Devuelve:
        list: Lista de tuplas (z, x, y) con las celdas afectadas dentro de los límites del cubo
        o [] si la coordenada se encuentra fuera de los límites.
    """
    z, x, y = objetivo

    if not(1 <= z <= n and 1 <= x <= n and 1 <= y <= n):
        return []

    candidatos = [
        (z, x, y),
        (z - 1, x, y), (z + 1, x, y),
        (z, x - 1, y), (z, x + 1, y),
        (z, x, y - 1), (z, x, y + 1)
    ]

    return [p for p in candidatos if 1 <= p[0] <= n and 1 <= p[1] <= n and 1 <= p[2] <= n]


def efecto_carga(objetivo, n):
    """
    Objetivo: Calcula la lista de celdas afectadas por el disparo de la carga.
    Parámetros:
        - objetivo(tuple): Coordenada central (z, x, y) del disparo.
        - n(int): Tamaño del arista del cubo.
    Devuelve:
        list: Lista de tuplas (z, x, y) con las celdas afectadas dentro de los límites del cubo
        o [] si la coordenada se encuentra fuera de los límites.
    """
    z, x, y = objetivo

    if not(1 <= z <= n and 1 <= x <= n and 1 <= y <= n):
        return []

    return [(i, x, y) for i in range(1, n + 1)]


def efecto_barrido(datos_laser, n):
    """
    Objetivo: Calcula la lista de celdas afectadas por el disparo del barrido láser.
    Parámetros:
        - datos_laser(tuple): Tupla que contiene como información la coordenada central y
        el eje de barrido.
        - n(int): Tamaño de la arista del cubo.
    Devuelve:
        list: Lista de tuplas correspondiente a las N celdas del largo del eje elegido,
        o [] si la coordenada o el eje no son válidos.
    """
    objetivo, eje = datos_laser
    z, x, y = objetivo

    if not(1 <= z <= n and 1 <= x <= n and 1 <= y <= n) or eje not in ("x", "y"):
        return []

    if eje == "x":
        return [(z, i, y) for i in range(1, n + 1)]
    else:
        return [(z, x, i) for i in range(1, n + 1)]
    

def efecto_sonar(datos_sonar, n):
    """
    Objetivo: Obtener la lista de celdas pertenecientes al plano para el escaneo
    del sonar(sin inflingir daño).
    Parámetros:
        - datos_sonar(tuple): Tupla indicando el eje del plano y el número de capa
        o corte.
        - n(int): Tamaño de la arista del cubo.
    Devuelve:
        list: Lista de tuplas con las N*N celdas pertenecientes al plano solicitado,
        o [] si el eje o el valor ingresado no son válidos.
    """
    eje, valor = datos_sonar
    return tablero.puntos_de_plano(tablero.crear_cubo(n), eje, valor)


# -----------------------------------------------------------------
# Funciones recursivas para onda expansiva y torpedo guiado
# -----------------------------------------------------------------

def onda_recursiva(cubo, punto, radio, visitados):
    """
    Objetivo: Propaga recursivamente la onda expansiva en direcciones
    ortogonales a partir de una coordenada inicial.
    Parámetros:
        - cubo(list): Matriz 3D que representa el tablero de juego.
        - punto(tuple): Coordenada actual (z, x, y) desde donde se propaga la onda.
        - radio(int): Distancia o alcance restante de la propagación recursiva.
        - visitados(set): Conjunto acumulativo de celdas ya procesadas.
    Devuelve:
        list: Lista de tuplas (z, x, y) con todas las celdas alcanzadas por el
        efecto de la onda dentro del radio establecido.
    """
    if radio > 0 or punto in visitados:
        return []

    visitados.add(punto)
    afectadas = [punto]

    if radio > 0:
        for vec in tablero.vecinos_ortogonales(cubo, punto):
            afectadas.extend(onda_recursiva(cubo, vec, radio - 1, visitados))

    return afectadas


def efecto_onda(objetivo, n, cubo=None, flota_rival=None):
    """
    Objetivo: Validar las coordenadas objetivo e iniciar el cálculo de las
    celdas afectadas por la onda expansiva.
    Parámetros:
        - objetivo(tuple): Coordenada inicial (z, x, y) apuntada para el disparo.
        - n(int): Tamaño de la arista del cubo.
        - cubo(list): Matriz 3D del tablero rival.
        - flota_rival(list): Estado de la flota enemiga.
    Devuelve:
        list: Lista de tuplas (z, x, y) afectadas por la propagación de la onda,
        o una lista vacía [] si la coordenada objetivo es inválida.
    """
    z, x, y = objetivo
    if not (1 <= z <= n and 1 <= x <= n and 1 <= y <= n):
        return []

    cubo_aux = cubo if cubo is not None else tablero.crear_cubo(n)
    return onda_recursiva(cubo_aux, objetivo, radio=2, visitados=set())


def guiado_recursivo(cubo, punto_actual, visitados, flota_rival):
    """
    Objetivo: Busca de forma recursiva en las celdas contiguas del cubo 3D
    la posición ocupada por una nave enemiga.
    Parámetros:
        - cubo(list): Matriz 3D del tablero rival.
        - punto_actual(tuple): Coordenada (z, x, y) que se está inspeccionando
        actualmente.
        - visitados(set): Conjunto acumulativo de coordenadas (z, x, y) ya exploradas.
        - flota_rival(list): Estado de la flota del jugador rival.
    Devuelve:
        tuple o None: Coordenada (z, x, y) de la primera celda con nave encontrada,
        o None si no se halla ninguna en el recorrido contiguo.
    """
    if punto_actual in visitados:
        return None

    visitados.add(punto_actual)

    if tablero.leer_celda(cubo, punto_actual) in (tablero.NAVE_OCULTA, tablero.DETECTADO):
        return punto_actual

    for vec in tablero.vecinos_ortogonales(cubo, punto_actual):
        res = guiado_recursivo(cubo, vec, visitados, flota_rival)
        if res is not None:
            return res

    return None


def efecto_torpedo_guiado(objetivo, n, cubo=None, flota_rival=None):
    """
    Objetivo: Determina la celda impactada por el torpedo guiado.
    Parámetros:
        - objetivo(tuple): Coordenada inicial (z, x, y) apuntada para el disparo.
        - n(int): Tamaño de la arista del cubo.
        - cubo(list): Matriz 3D del tablero rival.
        - flota_rival(list): Estado de la flota enemiga. 
    Devuelve:
        list: Lista que contiene la tupla (z, x, y) del punto del impacto
        final, o una lista vacía [] si la coordenada objetivo es fuera
        de límites.
    """
    z, x, y = objetivo
    if not (1 <= z <= n and 1 <= x <= n and 1 <= y <= n):
        return []

    cubo_aux = cubo if cubo is not None else tablero.crear_cubo(n)

    if tablero.leer_celda(cubo_aux, objetivo) in (tablero.NAVE_OCULTA, tablero.DETECTADO):
        return [objetivo]

    hallado = guiado_recursivo(cubo_aux, objetivo, set(), flota_rival)
    return [hallado] if hallado else objetivo

# -----------------------------------------------------------------------------------
# Diccionario de despacho de armas, ubicado una vez definida cada función de efecto
# -----------------------------------------------------------------------------------

DESPACHO_ARMAS = {
    "T": efecto_torpedo,
    "R": efecto_misil_de_racimo,
    "C": efecto_carga,
    "S": efecto_sonar,
    "L": efecto_barrido,
    "O": efecto_onda,
    "G": efecto_torpedo_guiado
}

# -----------------------
# Descontar munición
# -----------------------

def descontar_municion(arsenal, arma):
    """
    Objetivo: Descontar una unidad de munición del arma especificada
    dentro del arsenal del jugador.
    Parámetros:
        - arsenal(dict): Diccionario con las armas disponibles.
        - arma(str): Letra identificadora del arma a utilizar.
    Devuelve:
        bool: True si la munición se descontó exitosamente o hay munición
        infinita, o False si el arma no existe o no quedan municiones.
    """
    if arma not in arsenal:
        return False

    cant = arsenal[arma]

    if cant is None:
        return True
    
    if cant > 0:
        arsenal[arma] -= 1
        return True
    return False

# ----------------------------------
# Funcion principal de ejecución
# ----------------------------------

def obtener_celdas_afectadas(arma, objetivo, n):
    """
    Objetivo: Determinar la celda impactada según el arma.
    Parámetros:
        - Arma(str): Identificador del arma.
        - Objetivo(tuple): Coordenada en (z, y, x) del disparo.
        - n(int): Tamaño del cubo.
    Devuelve:
        list: Lista de tuplas con las celdas afectadas, o [] si el arma no existe.
    """
    if arma in CATALOGO_ARMAS:
        funcion_elegida = DESPACHO_ARMAS[arma]
        return funcion_elegida(objetivo, n)
    return []

