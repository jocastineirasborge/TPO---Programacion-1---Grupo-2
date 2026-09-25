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

def validacion_de_coordenada(objetivo, n):
    """
    Objetivo: Validar si la coordenada (x, y, z) es válida (x, y, z) dentro del cubo.
    Parámetros:
        - Objetivo(tupla): Coordenada en (x, y, z) del disparo.
        - n(int): Tamaño del cubo para validación.
    Devuelve:
        List: Lista que contiene la coordenada en formato tupla del punto apuntado.
    """
    if len(objetivo) != 3:
        return False

    x, y, z = objetivo
    if type(x) is not int or type(y) is not int or type(z) is not int:
        return False

    if not (1 <= x <= n and 1 <= y <= n and 1 <= z <= n):
        return False

    return True


def efecto_torpedo(objetivo, n):
    """
    Objetivo: Calcular celdas afectadas por el torpedo.
    Parámetros:
        - Objetivo(tupla): Coordenada en (x, y, z) del disparo.
        - n(int): Tamaño del cubo para validación.
    Devuelve:
        List: Lista que contiene la coordenada en formato tupla del punto apuntado.
    """

    if not validacion_de_coordenada(objetivo, n):
        return False

    return objetivo

