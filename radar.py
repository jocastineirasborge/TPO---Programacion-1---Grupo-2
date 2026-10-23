"""
Módulo radar.py
Localiza naves en el cubo 3D, ejecuta el sonar por planos, realiza recorridos del tablero
y calcula las métricas de rendimiento.
"""
import tablero
import flota

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

def busqueda_optimizada(cubo, id_nave, n):
    """
    Objetivo: Localizar las celdas ocupadas por una nave optimizando el recorrido
    mediante el acotamiento de límites según reglas de ubicación y aplicando un corte
    temprano al hallar todas las celdas.
    Parámetros:
        - cubo(list): Matriz anidada 3D del tablero de juego.
        - id_nave(str): Letra identificadora de la nave.
        - n(int): Tamaño de la arista del cubo.
    Devuelve:
        tuple: Devuelve una tupla que consiste de la lista de tuplas con las
        coordenadas válidas y la cantidad de evaluaciones realizadas.
    """
    catalogo = flota.obtener_catalogo_naves()
    cant_esperada = catalogo.get(id_nave, {}).get("celdas", 0)

    z_min, z_max = 0 ,n
    x_min, x_max = 0, n
    y_min, y_max = 0, n

    if id_nave == "S":
        z_max = n // 2

    elif id_nave == "P":
        z_min = n // 2

    elif id_nave == "E":
        z_min, z_max = 1, n - 1
        x_min, x_max = 1, n - 1
        y_min, y_max = 1, n - 1

    coordenadas_encontradas = []
    comparaciones = 0

    for z in range(z_min, z_max):
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                comparaciones += 1
                if cubo[z][x][y] == id_nave:
                    coordenadas_encontradas.append((z + 1, x + 1, y + 1))

                    if cant_esperada > 0 and len(coordenadas_encontradas) == cant_esperada:
                        return coordenadas_encontradas, comparaciones

    return coordenadas_encontradas, comparaciones

# --------------------------------
# Comparación de las búsquedas
# --------------------------------
def comparar_busquedas(cubo, n=8):
    """
    Objetivo: Comparar la eficiencia y el resultado de los dos métodos
    de búsqueda.
    Parámetros:
        - cubo(list): Matriz anidada 3D del tablero de juego.
        - n(int): 
    """

    naves = ["F", "D", "S", "C", "P", "E"]

    print("\n=== COMPARATIVA DE EFICIENCIA EN EL RADAR ===")
    print("Nave | Lineal | Optimizada | Ahorro obtenido")
    print("-------------------------------------------------")

    total_lineal = 0
    total_optimizada = 0

    for nave in naves:
        coor_lineal, comp_lineal = busqueda_lineal_nave(cubo, nave, n)
        coor_optimizada, comp_optimizada = busqueda_optimizada(cubo, nave, n)

        total_lineal += comp_lineal
        total_optimizada += comp_optimizada

        diferencia = comp_lineal - comp_optimizada

        print(f"{nave} | {comp_lineal:3d} | {comp_optimizada:3d} | {diferencia} comparaciones menos")

        ahorro_total = total_lineal - total_optimizada
        porcentaje_ahorro = (ahorro_total / total_lineal) * 100

        print("-------------------------------------------------")
        print(f"TOTAL: Lineal = {total_lineal} ops | Optimizada = {total_optimizada} ops")
        print(f"¡La búsqueda optimizada redujo un {porcentaje_ahorro:.1f}% las operaciones!\n")

# --------------------------------
# Demostración de la comparación
# --------------------------------

def demostracion_comparacion():
    """
    Objetivo: Crear un cubo con naves de forma auxiliar para demostrar la comparación de
    ambos métodos de búsqueda con comparar_busquedas().
    Parámetros:
        Ninguno
    Devuelve:
        None: No devuelve nada porque es una función hecha para llamar otras funciones.
    """
    c = tablero.crear_cubo(8)
    f = flota.ubicacion_automatica(c, n=8)

    comparar_busquedas(c, 8)

def sonar_por_planos(cubo, eje, valor):
    """
    Objetivo: Recorrer e inspeccionar un plano del cubo oponente para
    detectar y contar la cantidad de contactos de naves.
    Parámetros:
        - cubo(list): Matriz anidada del tablero de juego.
        - eje(str): Identificador del eje de plano.
        - valor(int): Número de capa o corte del plano.
    """
    puntos = tablero.puntos_de_plano(cubo, eje, valor)
    contactos = 0

    for p in puntos:
        estado_celda = tablero.leer_celda(cubo, p)
        if estado_celda in (tablero.NAVE_OCULTA, tablero.DETECTADO):
            contactos += 1

    return contactos, puntos


# Ejecutar si desea ver las
#demostracion_comparacion()