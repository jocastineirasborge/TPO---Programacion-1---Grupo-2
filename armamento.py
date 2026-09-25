"""
Módulo armamento.py
Administra el catálogo de armas, la munición disponible y las celdas afectadas por cada disparo. 
"""

# Catálogo de armas: Lista de tuplas que contienen la información necesaria(letra, nombre, munición_inicial)
CATALOGO_ARMAS = [
    ("T", "Torpedo", None),
    ("R", "Misil de racimo", 3),
    ("C", "Carga de profundidad", 2),
    ("S", "Sonar", 4),
    ("L", "Barrido láser", 2),
    ("O", "Onda expansiva", 1),
    ("G", "Torpedo guiado", 1)
    ]

#Utilizamos lista de tuplas temporalmente dado que todavía no hemos visto diccionarios.


def obtener_catalogo_armas():
    """
    Objetivo: Devolver la lista de catálogo de armas disponible.
    Devuelve:
        list: Lista de tuplas con el catálogo de armas.
    """
    
    return CATALOGO_ARMAS


def validacion_de_coordenada(objetivo, n):
    """
    Objetivo: Validar si la coordenada (z, y, x) es válida (z, y, x) dentro del cubo.
    Parámetros:
        - Objetivo(tuple): Coordenada en (x, y, z) del disparo.
        - n(int): Tamaño del cubo para validación.
    Devuelve:
        bool: True si la coordenada es válida, False en caso contrario.
    """

    if len(objetivo) != 3:
        return False

    z, y, x = objetivo

    if type(z) is not int or type(y) is not int or type(x) is not int:
        return False

    if not (1 <= x <= n and 1 <= y <= n and 1 <= z <= n):
        return False

    return True


def efecto_torpedo(objetivo, n):
    """
    Objetivo: Calcular celdas afectadas por el torpedo.
    Parámetros:
        - Objetivo(tuple): Coordenada en (z, y, x) del disparo.
        - n(int): Tamaño del cubo para validación.
    Devuelve:
        List: Lista que contiene la coordenada en formato tupla del punto apuntado.
    """

    if not validacion_de_coordenada(objetivo, n):
        return False

    return [objetivo]

DESPACHO_ARMAS = [
    ("T", efecto_torpedo)
]

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

    for letra, funcion_disparo in DESPACHO_ARMAS:
        if letra == arma:
            return funcion_disparo(objetivo, n)

    return []

