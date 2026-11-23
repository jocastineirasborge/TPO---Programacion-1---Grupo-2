"""
Módulo radar.py
Localiza naves en el cubo 3D, ejecuta el sonar por planos, realiza recorridos del tablero
y calcula las métricas de rendimiento.
"""
import tablero
import flota

# -------------------------------------------------------------------------
# Búsqueda de métricas y de nave(Lineal, Optimizada y Recursiva)
# -------------------------------------------------------------------------

def busqueda_lineal_nave(flota_jugador, id_nave, n):
    """
    Objetivo: Localizar las celdas ocupadas por una nave mediante un recorrido
              lineal sobre todas las posiciones (z, x, y) del cubo.
    Parámetros:
        - flota_jugador (list): Lista de tuplas (letra, puntos, impactos) de la flota.
        - id_nave (str): Letra identificadora de la nave ('F', 'D', 'S', 'C', 'P', 'E').
        - n (int): Tamaño de la arista del cubo.
    Devuelve:
        tuple: (coordenadas_encontradas, comparaciones)
    """
    coordenadas_encontradas = []
    comparaciones = 0

    # Puntos ocupados por la nave en la flota del jugador
    puntos_reales = []
    for nave in flota_jugador:
        if nave[0] == id_nave:
            puntos_reales.extend(nave[1])

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                comparaciones += 1
                if (z, x, y) in puntos_reales:
                    coordenadas_encontradas.append((z, x, y))

    return coordenadas_encontradas, comparaciones


def busqueda_optimizada(flota_jugador, id_nave, n):
    """
    Objetivo: Localizar las celdas ocupadas por una nave acotando los límites de
              búsqueda según sus restricciones espaciales y aplicando corte temprano.
    Parámetros:
        - flota_jugador (list): Lista de tuplas (letra, puntos, impactos) de la flota.
        - id_nave (str): Letra identificadora de la nave.
        - n (int): Tamaño de la arista del cubo.
    Devuelve:
        tuple: (coordenadas_encontradas, comparaciones)
    """
    catalogo = flota.obtener_catalogo_naves()
    cant_esperada = catalogo.get(id_nave, {}).get("celdas", 0)

    z_min, z_max = 1, n + 1
    x_min, x_max = 1, n + 1
    y_min, y_max = 1, n + 1

    if id_nave == "S":
        z_max = (n // 2) + 1
    elif id_nave == "P":
        z_min = (n // 2) + 1
    elif id_nave == "C":
        z_min, z_max = 2, n
    elif id_nave == "E":
        z_min, z_max = 2, n
        x_min, x_max = 2, n
        y_min, y_max = 2, n

    puntos_reales = []
    for nave in flota_jugador:
        if nave[0] == id_nave:
            puntos_reales.extend(nave[1])

    coordenadas_encontradas = []
    comparaciones = 0

    for z in range(z_min, z_max):
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                comparaciones += 1
                if (z, x, y) in puntos_reales:
                    coordenadas_encontradas.append((z, x, y))
                    if cant_esperada > 0 and len(coordenadas_encontradas) == cant_esperada:
                        return coordenadas_encontradas, comparaciones

    return coordenadas_encontradas, comparaciones


def busqueda_recursiva_aux(flota_jugador, id_nave, z, x, y, n, comparaciones, coordenadas):
    """
    Objetivo: Recorrer recursivamente las celdas (z, x, y) del cubo para localizar una nave específica. 
    Parámetros:
        - flota_jugador (list): Lista de naves que integran la flota. 
        - id_nave (str): Letra identificadora de la nave a buscar ('F', 'D', 'S', 'C', 'P', 'E').
        - z, x, y (int): Coordenada actual en evaluación dentro del cubo. 
        - n (int): Tamaño de la arista del cubo. - comparaciones (int): Contador acumulado de evaluaciones realizadas. 
        - coordenadas (list): Lista acumulada de posiciones encontradas. 
    Devuelve: 
        tuple: Tupla (coordenadas, comparaciones) con los resultados acumulados al finalizar el recorrido. 
    """
    if z > n:
        return coordenadas, comparaciones
    
    comparaciones += 1
    pt = (z, x, y)
    for nave in flota_jugador:
        if nave[0] == id_nave and pt in nave[1]:
            coordenadas.append(pt)
            break

    #Siguiente coordenada en la secuencia 3D (z, x, y)
    ny = y + 1
    nx = x
    nz = z
    if ny > n:
        ny = 1
        nx += 1
        if nx > n:
            nx = 1
            nz += 1

    return busqueda_recursiva_aux(flota_jugador, id_nave, nz, nx, ny, n, comparaciones, coordenadas)


def busqueda_recursiva_nave(flota_jugador, id_nave, n):
    """
    Objetivo: Localizar las celdas ocupadas por una nave utilizando un recorrido
              recursivo sobre el cubo 3D (Entrega 3).
    Parámetros:
        - flota_jugador (list): Lista de tuplas (letra, puntos, impactos) de la flota.
        - id_nave (str): Letra identificadora de la nave.
        - n (int): Tamaño de la arista del cubo.
    Devuelve:
        tuple: (coordenadas_encontradas, comparaciones)
    """
    comparaciones = 0
    coordenadas = []
    res_coords, res_comps = busqueda_recursiva_aux(flota_jugador, id_nave, 1, 1, 1, n, comparaciones, coordenadas)
    return res_coords, res_comps

# -------------------------------------------------
# Recorridos recursivos alternativos del cubo
# -------------------------------------------------

def recorrido_capas_aux(z, x, y, n, lista):


    if z > n:
        return lista
    lista.append((z, x, y))
    ny = y + 1
    nx = x
    nz = z
    if ny > n:
        ny = 1
        nx += 1
        if nx > n:
            nx = 1
            nz += 1
    return recorrido_capas_aux(nz, nx, ny, n, lista)


def recorrido_recursivo_capas(n=tablero.N_POR_DEFECTO):


    return recorrido_capas_aux(1, 1, 1, n, [])


def recorrido_octantes_aux(cubo, octante_idx, n, lista):

    if octante_idx > tablero.CANTIDAD_OCTANTES:
        return lista
    puntos = tablero.puntos_de_octante(cubo, octante_idx)
    lista.extend(puntos)
    return recorrido_octantes_aux(cubo, octante_idx + 1, n, lista)


def recorrido_recursivo_octantes(n=tablero.N_POR_DEFECTO):


    cubo = tablero.crear_cubo(n)
    return recorrido_octantes_aux(cubo, 1, n, [])

# ---------------------------------------------
# Sonar por planos y Mapa de probabilidad
# ---------------------------------------------

def sonar_por_planos(cubo, eje, valor):
    """
    Objetivo: Inspeccionar y contar la cantidad de contactos de naves en un plano
              determinado del cubo rival sin infringir daño.
    Parámetros:
        - cubo (list): Matriz 3D del tablero rival.
        - eje (str): Eje del plano ('z', 'x' o 'y').
        - valor (int): Número de capa o corte (1 a N).
    Devuelve:
        tuple: (contactos, puntos_del_plano)
    """
    puntos = tablero.puntos_de_plano(cubo, eje, valor)
    contactos = sum(1 for p in puntos if tablero.leer_celda(cubo, p) in (tablero.NAVE_OCULTA, tablero.DETECTADO))
    return contactos, puntos


def generar_mapa_de_probabilidad(cubo_rival, flota_rival, n=tablero.N_POR_DEFECTO):



    mapa = {}
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                mapa[(z, x, y)] = 0


    naves_vivas = []
    for nave in flota_rival:
        letra, puntos, impactos = nave
        if not flota.nave_hundida(puntos, impactos):
            naves_vivas.append(letra)


    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                punto = (z, x, y)
                if tablero.leer_celda(cubo_rival, punto) == tablero.IMPACTO:
                    for vec in tablero.vecinos_ortogonales(cubo_rival, punto):
                        if tablero.leer_celda(cubo_rival, vec) == tablero.SIN_EXPLORAR:
                            mapa[vec] += 15


    catalogo = flota.obtener_catalogo_naves()
    direcciones = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                punto = (z, x, y)
                if tablero.leer_celda(cubo_rival, punto) != tablero.SIN_EXPLORAR:
                    continue

                for letra in naves_vivas:
                    if letra == "S" and z > (n // 2):
                        continue
                    if letra == "P" and z <= (n // 2):
                        continue
                    if letra == "C" and (z == 1 or z == n):
                        continue
                    if letra == "E" and (z == 1 or z == n or x == 1 or x == n or y == 1 or y == n):
                        continue

                    tam = catalogo.get(letra, {}).get("celdas", 1)

                    for dz, dx, dy in direcciones:
                        cabe = True
                        for k in range(1, tam):
                            nz, nx, ny = z + dz*k, x + dx*k + y + dy*k
                            coor_punto = (nz, nx, ny)
                            if not tablero.es_punto_valido(cubo_rival, coor_punto):
                                cabe = False
                                break
                            coor_val = tablero.leer_celda(cubo_rival, coor_punto)
                            if coor_val in (tablero.AGUA_MARCADA, tablero.HUNDIDO):
                                cabe = False
                                break

                    if cabe:
                        mapa[punto] += 1

    return mapa

# --------------------------------
# Comparación de las búsquedas
# --------------------------------

def comparar_busquedas(flota_jugador, n=tablero.N_POR_DEFECTO):
    """
    Objetivo: Calcular y consolidar la comparación de rendimiento de operaciones
              entre la Búsqueda Lineal, Optimizada y Recursiva para toda la flota.
    Parámetros:
        - flota_jugador (list): Lista con el estado de la flota del jugador.
        - n (int): Tamaño del cubo (por defecto 8).
    Devuelve:
        dict: Diccionario estructurado con las métricas por cada nave.
    """
    naves = ["F", "D", "S", "C", "P", "E"]
    resumen = {}

    for nave in naves:
        _, comp_lineal = busqueda_lineal_nave(flota_jugador, nave, n)
        _, comp_optimizada = busqueda_optimizada(flota_jugador, nave, n)
        _, comp_recursiva = busqueda_recursiva_nave(flota_jugador, nave, n)

        resumen[nave] = {
            "lineal": comp_lineal,
            "optimizada": comp_optimizada,
            "recursiva": comp_recursiva,
            "ahorro_opt": comp_lineal - comp_optimizada
        }

    return resumen
