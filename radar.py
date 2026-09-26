"""
Módulo radar.py
Localiza naves en el cubo 3D, ejecuta el sonar por planos, realiza recorridos del tablero
y calcula las métricas de rendimiento.
"""
coordenadas_encontradas = []
comparaciones = 0

def busqueda_lineal_nave(cubo, identificador_nave, n):

    for z in range(0, n):
        for x in range(0, n):
            for y in range(0, n):
                comparaciones += 1
                if cubo[z][x][y] == identificador_nave:
                    coordenadas_encontradas.append(z + 1, x + 1, y + 1)
