"""
Módulo radar.py
Localiza naves en el cubo 3D, ejecuta el sonar por planos, realiza recorridos del tablero
y calcula las métricas de rendimiento.
"""

# -----------------------------------
# Búsqueda de métricas y de nave
# -----------------------------------

def busqueda_lineal_nave(cubo, id_nave, n):
    """
    Objetivo: Localizar las celdas ocupadas por una nave en el cubo con un recorrido lineal.
    Parámetros:
        - cubo(list): Lista anidada en 3D correspondiente al tablero(N x N x N)
        - id_nave(str): Letra identificadora de la nave
        - n(int): Tamaño del cubo.
    Devuelve:
        tuple: Una tupla que contiene las coordenadas encontradas y la cantidad de comparaciones.
    """
    coordenadas_encontradas = []
    comparaciones = 0

    for z in range(0, n):
        for x in range(0, n):
            for y in range(0, n):
                comparaciones += 1
                if cubo[z][x][y] == id_nave:
                    coordenadas_encontradas.append((z + 1, x + 1, y + 1))

    return coordenadas_encontradas, comparaciones
