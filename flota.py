"""
Módulo flota.py - Operación Cubo
Administra el catálogo de naves, reglas de ubicación y la colocación manual y automática dentro del cubo.
"""

import random

# Catálogo oficial de naves: (letra, nombre, celdas_ocupadas, cantidad_disponible)
CATALOGO_NAVES = [
    ("F", "Fragata", 2, 3),
    ("D", "Destructor", 3, 2),
    ("S", "Submarino", 3, 2),
    ("C", "Crucero", 4, 1),
    ("P", "Portaaviones", 5, 1),
    ("E", "Estación orbital", 8, 1)
]


def inicializar_flota():
    """
    Objetivo: Crear y devolver una lista vacía para la flota de un jugador.
    """
    return []


def obtener_catalogo_naves():
    """
    Objetivo: Devolver la lista del catálogo de naves disponible.
    """
    return CATALOGO_NAVES


def obtener_datos_nave(letra):
    """
    Objetivo: Buscar la información del catálogo para una nave según su letra.
    """
    for nave in CATALOGO_NAVES:
        if nave[0] == letra:
            return nave
    return None


def obtener_puntos(nave_letra, desde, hasta):
    """
    Objetivo: Generar la lista de puntos ocupados según el tipo de nave.
    Parámetros: desde y hasta son tuplas (z, x, y).
    """
    z1, x1, y1 = desde
    z2, x2, y2 = hasta

    if z2 >= z1:
        dz = z2 - z1
    else:
        dz = z1 - z2

    if x2 >= x1:
        dx = x2 - x1
    else:
        dx = x1 - x2

    if y2 >= y1:
        dy = y2 - y1
    else:
        dy = y1 - y2

    # Caso Estación Orbital (bloque 2x2x2)
    if nave_letra == "E":
        if dz != 1 or dx != 1 or dy != 1:
            return []
        puntos = []
        for z in range(min(z1, z2), max(z1, z2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    puntos.append((z, x, y))
        return puntos

    # Caso Naves en línea recta (solo puede cambiar un eje)
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
    paso_z = 1 if z2 >= z1 else -1
    paso_x = 1 if x2 >= x1 else -1
    paso_y = 1 if y2 >= y1 else -1

    if dz > 0:
        for z in range(z1, z2 + paso_z, paso_z):
            puntos.append((z, x1, y1))
    elif dx > 0:
        for x in range(x1, x2 + paso_x, paso_x):
            puntos.append((z1, x, y1))
    elif dy > 0:
        for y in range(y1, y2 + paso_y, paso_y):
            puntos.append((z1, x1, y))
    else:
        puntos.append(desde)

    return puntos


def validar_reglas_ubicacion(nave_letra, puntos, cubo):
    """
    Objetivo: Validar que los puntos cumplan con las restricciones geográficas de cada nave.
    """
    if len(puntos) == 0:
        return False

    n = tablero.tamanio_cubo(cubo)

    for p in puntos:
        if not tablero.es_punto_valido(cubo, p):
            return False

    # Submarino: Solo en la mitad inferior de z
    if nave_letra == "S":
        for z, x, y in puntos:
            if z > (n // 2):
                return False

    # Crucero: No puede ocupar z = 1 ni z = n
    elif nave_letra == "C":
        for z, x, y in puntos:
            if z == 1 or z == n:
                return False

    # Portaaviones: Solo en la mitad superior de z
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


def hay_distancia_segura(cubo, puntos):
    """
    Objetivo: Verificar que se respete al menos una celda libre alrededor de la nave.
    """
    for z, x, y in puntos:
        for dz in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    vecino = (z + dz, x + dx, y + dy)
                    if tablero.es_punto_valido(cubo, vecino):
                        if vecino not in puntos:
                            # Si alguna celda de alrededor tiene una nave, no hay distancia segura
                            celda = tablero.leer_celda(cubo, vecino)
                            if celda == tablero.NAVE_OCULTA:
                                return False
    return True


def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta):
    """
    Objetivo: Ubicar una nave en el cubo y registrarla en la flota.
    Parámetros: punto_desde y punto_hasta deben ser tuplas (z, x, y).
    Devuelve: True si la ubicó con éxito, False si violó alguna regla.
    """
    if punto_desde is None or punto_hasta is None:
        return False

    datos_nave = obtener_datos_nave(nave)
    if datos_nave is None:
        return False

    celdas_requeridas = datos_nave[2]

    puntos = obtener_puntos(nave, punto_desde, punto_hasta)

    if len(puntos) != celdas_requeridas:
        return False

    if not validar_reglas_ubicacion(nave, puntos, cubo):
        return False

    # Validar que las celdas estén libres (sin naves)
    for p in puntos:
        if tablero.leer_celda(cubo, p) == tablero.NAVE_OCULTA:
            return False

    if not hay_distancia_segura(cubo, puntos):
        return False

    # Actualizar estado de las celdas en el tablero
    for p in puntos:
        tablero.escribir_celda(cubo, p, tablero.NAVE_OCULTA)

    # Registrar objeto nave dentro de la flota
    registro_nave = {
        "letra": nave,
        "celdas": puntos,
        "impactos": 0,
        "hundida": False
    }
    flota.append(registro_nave)

    return True


def ubicacion_automatica(cubo, catalogo=None, semilla=None):
    """
    Objetivo: Ubicar de forma automática toda la flota respetando todas las reglas.
    """
    if catalogo is None:
        catalogo = CATALOGO_NAVES

    n = tablero.tamanio_cubo(cubo)
    flota = inicializar_flota()

    for letra, nombre, celdas, cantidad in catalogo:
        for i in range(cantidad):
            colocada = False
            intentos = 0
            while not colocada and intentos < 3000:
                intentos += 1
                if letra == "E":
                    z = random.randint(2, n - 1)
                    x = random.randint(2, n - 1)
                    y = random.randint(2, n - 1)
                    desde = (z, x, y)
                    hasta = (z + 1, x + 1, y + 1)
                else:
                    eje = random.choice(["z", "x", "y"])
                    z = random.randint(1, n)
                    x = random.randint(1, n)
                    y = random.randint(1, n)

                    if eje == "z":
                        desde = (z, x, y)
                        hasta = (z + celdas - 1, x, y)
                    elif eje == "x":
                        desde = (z, x, y)
                        hasta = (z, x + celdas - 1, y)
                    else:
                        desde = (z, x, y)
                        hasta = (z, x, y + celdas - 1)

                exito = ubicar_nave(cubo, flota, letra, desde, hasta)
                if exito:
                    colocada = True

    return flota
