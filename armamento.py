"""
Módulo armamento.py
Administra el catálogo de armas, la munición disponible y las celdas afectadas por cada disparo. 
"""

# Catálogo de armas: Diccionario de diccionarios que contienen la información necesaria{letra: {nombre, municion, descripcion}}
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

def efecto_torpedo(objetivo, n):
    """
    Objetivo: Calcular celdas afectadas por el torpedo.
    Parámetros:
        - Objetivo(tuple): Coordenada en (z, x, y) del disparo.
        - n(int): Tamaño del cubo para validación.
    Devuelve:
        List: Lista que contiene la coordenada en formato tupla del punto apuntado.
    """
    z, x, y = objetivo
    if 1 <= z <= n and 1 <= x <= n and 1 <= y <= n:
        return [objetivo]

    return []

def efecto_misil_de_racimo(objetivo, n):
    """
    Para la entrega 2.
    """
    pass

def efecto_carga(objetivo, n):
    """
    Para la entrega 2.
    """
    pass

def efecto_barrido(objetivo, n):
    """
    Para la entrega 2.
    """
    pass

def efecto_sonar(objetivo, n):
    """
    Para la entrega 2.
    """
    pass

def efecto_onda(objetivo, n):
    """
    Para la entrega 3.
    """
    pass

def efecto_torpedo_guiado(objetivo, n):
    """
    Para la entrega 3.
    """
    pass

DESPACHO_ARMAS = {
    "T": efecto_torpedo,
    "R": efecto_misil_de_racimo,
    "C": efecto_carga,
    "S": efecto_sonar,
    "L": efecto_barrido,
    "O": efecto_onda,
    "G": efecto_torpedo_guiado
}

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

        celdas = funcion_elegida(objetivo, n)

        return celdas
    return []

