"""
Módulo flota.py
Administra el catálogo de naves, reglas de ubicación y la colocación manual y automática dentro del cubo.
"""

import random
import tablero

# Catálogo de naves: Diccionario de diccionarios
CATALOGO_NAVES = {
    "F": {"nombre": "Fragata", "celdas": 2, "cantidad": 3},
    "D": {"nombre": "Destructor", "celdas": 3, "cantidad": 2},
    "S": {"nombre": "Submarino", "celdas": 3, "cantidad": 2},
    "C": {"nombre": "Crucero", "celdas": 4, "cantidad": 1},
    "P": {"nombre": "Portaaviones", "celdas": 5, "cantidad": 1},
    "E": {"nombre": "Estacion orbital", "celdas": 8, "cantidad": 1}
    }

# Lista global de la flota ubicada en la partida
FLOTA_UBICADA = []

def inicializar_flota():
    """
    Objetivo: Vaciar la lista de flota para una partida nueva.
    """
    FLOTA_UBICADA.clear()
    

def obtener_catalogo_naves():
    """
    Objetivo: Devolver la lista del catálogo de naves disponible.
    Devuelve:
        list: Lista de tuplas con el catálogo de naves.
    """
    return CATALOGO_NAVES


def obtener_puntos_tramo(desde, hasta):
    """
    Objetivo: Generar la lista de puntos entre 'desde' y 'hasta' a lo largo de un solo eje.
    Parámetros:
        - desde (tuple): Coordenada inicial (z, y, x).
        - hasta (tuple): Coordenada final (z, y, x).
    Devuelve:
        list: Lista de tuplas con los puntos intermedios, o [] si cambia en más de un eje.
    """
    z1, x1, y1 = desde
    z2, x2, y2 = hasta

    dz = abs(z2 - z1)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # Contar en cuántos ejes hay movimiento
    ejes_cambiados = 0
    if dz > 0:
        ejes_cambiados += 1
    if dx > 0:
        ejes_cambiados += 1
    if dy > 0:
        ejes_cambiados += 1

    if ejes_cambiados > 1:
        return []

    puntos = []
    if dz > 0:
        paso = 1 if z2 >= z1 else -1
        for z in range(z1, z2 + paso, paso):
            puntos.append((z, x1, y1))
    elif dx > 0:
        paso = 1 if x2 >= x1 else -1
        for x in range(x1, x2 + paso, paso):
            puntos.append((z1, x, y1))
    elif dy > 0:
        paso = 1 if y2 >= y1 else -1
        for y in range(y1, y2 + paso, paso):
            puntos.append((z1, x1, y))
    else:
        puntos.append(desde)

    return puntos


def validar_reglas_ubicacion(nave_letra, puntos, n):
    """
    Objetivo: Validar que los puntos cumplan con las restricciones específicas de cada nave.
    Parámetros:
        - nave_letra (str): Identificador de la nave.
        - puntos (list): Lista de coordenadas (z, y, x).
        - n (int): Tamaño del cubo.
    Devuelve:
        bool: True si cumple las reglas, False en caso contrario.
    """
    if not puntos:
        return False

    for z, x, y in puntos:
        if not (1 <= z <= n and 1 <= x <= n and 1 <= y <= n):
            return False

    # Submarino: Solo en la mitad inferior de z (z <= n // 2)
    if nave_letra == "S":
        for z, x, y in puntos:
            if z > (n // 2):
                return False

    # Crucero: No puede ocupar z=1 ni z=n
    elif nave_letra == "C":
        for z, x, y in puntos:
            if z == 1 or z == n:
                return False

    # Portaaviones: Solo en la mitad superior de z (z > n // 2)
    elif nave_letra == "P":
        for z, x, y in puntos:
            if z <= (n // 2):
                return False

    # Estación orbital: No puede tocar ninguna cara exterior del cubo
    elif nave_letra == "E":
        for z, x, y in puntos:
            if z == 1 or z == n or x == 1 or x == n or y == 1 or y == n:
                return False

    return True


def hay_distancia_segura(cubo, puntos, n):
    """
    Objetivo: Verificar que quede al menos una celda libre alrededor en cualquier dirección (incluidas diagonales).
    Parámetros:
        - cubo (list): Matriz 3D del tablero.
        - puntos (list): Lista de coordenadas a evaluar.
        - n (int): Tamaño del cubo.
    Devuelve:
        bool: True si hay distancia segura, False si hay una nave colindante.
    """
    for z, x, y in puntos:
        for dz in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nz, nx, ny = z + dz, x + dx, y + dy
                    if 1 <= nz <= n and 1 <= nx <= n and 1 <= ny <= n:
                        if tablero.leer_celda(cubo, (nz, nx, ny)) == tablero.NAVE_OCULTA:
                            if (nz, nx, ny) not in puntos:
                                return False
    return True


def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta, n=8):
    """
    Objetivo: Ubicar una nave en el cubo y actualizar la lista de flota.
    Parámetros:
        - cubo (list): Matriz 3D del tablero.
        - flota (list): Lista con el estado de las naves ubicadas.
        - nave (str): Letra identificadora de la nave.
        - punto_desde (tuple): Coordenada inicial (z, y, x).
        - punto_hasta (tuple): Coordenada final (z, y, x).
        - n (int): Tamaño del cubo.
    Devuelve:
        tuple: (cubo, flota) actualizados.
    Excepciones:
        Lanza ValueError si alguna regla de ubicación es violada.
    """
    if nave not in CATALOGO_NAVES:
        raise ValueError(f"Tipo de nave no reconocido: {nave}")

    celdas_requeridas = CATALOGO_NAVES[nave]["celdas"]

    if nave == "E":
        z1, x1, y1 = punto_desde
        z2, x2, y2 = punto_hasta
        puntos = []
        for z in range(min(z1, z2), max(z1, z2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    puntos.append((z, x, y))

        if len(puntos) != 8:
            raise ValueError("La estación orbital debe formar un bloque de 2x2x2.")
    else:
        puntos = obtener_puntos_tramo(punto_desde, punto_hasta)
        if len(puntos) != celdas_requeridas:
            raise ValueError("La cantidad de celdas no coincide con la longitud de la nave.")

    if not validar_reglas_ubicacion(nave, puntos, n):
        raise ValueError("La nave no cumple con las reglas de posición o límites del cubo.")

    # Validar que las celdas estén libres
    for p in puntos:
        if tablero.leer_celda(cubo, p) != tablero.SIN_EXPLORAR:
            raise ValueError("Hay una celda ocupada por otra nave.")

    if not hay_distancia_segura(cubo, puntos, n):
        raise ValueError("No se respeta la distancia de seguridad (1 celda libre alrededor).")

    for p in puntos:
        tablero.escribir_celda(cubo, p, tablero.NAVE_OCULTA)

    flota.append((nave, puntos, []))
    return cubo, flota


def ubicacion_automatica(cubo, catalogo=None, semilla=None, n=8):
    """
    Objetivo: Ubicar de forma automática toda la flota respetando todas las reglas.
    Parámetros:
        - cubo (list): Matriz 3D del tablero.
        - catalogo (list): Lista de tuplas con las naves. Por defecto usa CATALOGO_NAVES.
        - semilla (int): Semilla aleatoria opcional para pruebas.
        - n (int): Tamaño del cubo.
    Devuelve:
        list: Lista de la flota ubicada.
    """
    if catalogo is None:
        catalogo = CATALOGO_NAVES

    if semilla is not None:
        random.seed(semilla)

    flota = []
    for letra, datos in catalogo.items():
        celdas = datos["celdas"]
        cantidad = datos["cantidad"]

        for i in range(0, cantidad):
            colocada = False
            intentos = 0
            while not colocada and intentos < 2000:
                intentos += 1
                if letra == "E":
                    z = random.randint(2, n - 2)
                    x = random.randint(2, n - 2)
                    y = random.randint(2, n - 2)
                    desde = (z, x, y)
                    hasta = (z + 1, x + 1, y + 1)
                else:
                    eje = random.choice(["z", "x", "y"])
                    z = random.randint(1, n)
                    x = random.randint(1, n)
                    y = random.randint(1, n)

                    desde = (z, x, y)
                    if eje == "z":
                        hasta = (z + celdas - 1, x, y)
                    elif eje == "x":
                        hasta = (z, x + celdas - 1, y)
                    else:
                        hasta = (z, x, y + celdas - 1)

                try:
                    ubicar_nave(cubo, flota, letra, desde, hasta, n)
                    colocada = True
                except ValueError:
                    pass
    return flota