"""
Módulo flota.py
Administra el catálogo de naves, reglas de ubicación, la colocación manual y automática dentro del cubo, 
el registro de impactos, naves averiadas y hundidas, y los datos de la flota para guardar y reponer la partida .
"""

import random
import tablero

# ------------------------------------
# Excepciones propias
# ------------------------------------

class ErrorFlota(Exception):
    """Excepción base para errores en la ubicación, gestión o reposición de la flota."""
    pass


# ------------------------------------
# Catálogo y estructuras globales
# ------------------------------------

CATALOGO_NAVES = {
    "F": {"nombre": "Fragata", "celdas": 2, "cantidad": 3},
    "D": {"nombre": "Destructor", "celdas": 3, "cantidad": 2},
    "S": {"nombre": "Submarino", "celdas": 3, "cantidad": 2},
    "C": {"nombre": "Crucero", "celdas": 4, "cantidad": 1},
    "P": {"nombre": "Portaaviones", "celdas": 5, "cantidad": 1},
    "E": {"nombre": "Estacion orbital", "celdas": 8, "cantidad": 1}
}

FLOTA_UBICADA = []


# -------------------------------------
# Funciones de consulta y auxiliares
# -------------------------------------

def inicializar_flota():
    """
    Objetivo: Vaciar la lista de flota para una partida nueva.
    Parámetros:
        Ninguno.
    Devuelve:
        None.
    Excepciones:
        Ninguna.
    """
    FLOTA_UBICADA.clear()


def obtener_catalogo_naves():
    """
    Objetivo: Devolver el catálogo de naves disponible.
    Parámetros:
        Ninguno.
    Devuelve:
        dict: Diccionario con el catálogo de naves.
    Excepciones:
        Ninguna.
    """
    return CATALOGO_NAVES


def obtener_puntos_tramo(desde, hasta):
    """
    Objetivo: Generar la lista de puntos entre 'desde' y 'hasta' a lo largo de un solo eje.
    Parámetros:
        - desde (tuple): Coordenada inicial (z, x, y).
        - hasta (tuple): Coordenada final (z, x, y).
    Devuelve:
        list: Lista de tuplas con los puntos intermedios, o [] si cambia en más de un eje.
    Excepciones:
        Ninguna.
    """
    z1, x1, y1 = desde
    z2, x2, y2 = hasta

    # Contar cuántos ejes cambian sin usar abs
    diferentes = 0
    if z1 != z2:
        diferentes += 1
    if x1 != x2:
        diferentes += 1
    if y1 != y2:
        diferentes += 1

    if diferentes > 1:
        return []

    puntos = []
    if z1 != z2:
        paso = 1 if z1 < z2 else -1
        for z in range(z1, z2 + paso, paso):
            puntos.append((z, x1, y1))
    elif x1 != x2:
        paso = 1 if x1 < x2 else -1
        for x in range(x1, x2 + paso, paso):
            puntos.append((z1, x, y1))
    elif y1 != y2:
        paso = 1 if y1 < y2 else -1
        for y in range(y1, y2 + paso, paso):
            puntos.append((z1, x1, y))
    else:
        puntos.append(desde)

    return puntos


# -----------------------------------------
# Reglas de ubicación y distancia segura
# -----------------------------------------

def validar_reglas_ubicacion(nave_letra, puntos, n):
    """
    Objetivo: Validar que los puntos cumplan con las restricciones específicas de cada nave.
    Parámetros:
        - nave_letra (str): Identificador de la nave.
        - puntos (list): Lista de coordenadas (z, x, y).
        - n (int): Tamaño del cubo.
    Devuelve:
        bool: True si cumple las reglas, False en caso contrario.
    Excepciones:
        Ninguna.
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
    Excepciones:
        Ninguna.
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


# -----------------------------------------------
# Colocación manual y automática de las naves
# -----------------------------------------------

def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta, n=8):
    """
    Objetivo: Ubicar una nave en el cubo y actualizar la lista de flota.
    Parámetros:
        - cubo (list): Matriz 3D del tablero.
        - flota (list): Lista con el estado de las naves ubicadas.
        - nave (str): Letra identificadora de la nave.
        - punto_desde (tuple): Coordenada inicial (z, x, y).
        - punto_hasta (tuple): Coordenada final (z, x, y).
        - n (int): Tamaño del cubo.
    Devuelve:
        tuple: (cubo, flota) actualizados.
    Excepciones:
        ErrorFlota: Si alguna regla de ubicación es violada o los datos son inválidos.
    """
    if nave not in CATALOGO_NAVES:
        raise ErrorFlota(f"Tipo de nave no reconocido: {nave}")

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
            raise ErrorFlota("La estación orbital debe formar un bloque de 2x2x2.")
    else:
        puntos = obtener_puntos_tramo(punto_desde, punto_hasta)
        if len(puntos) != celdas_requeridas:
            raise ErrorFlota("La cantidad de celdas no coincide con la longitud de la nave.")

    if not validar_reglas_ubicacion(nave, puntos, n):
        raise ErrorFlota("La nave no cumple con las reglas de posición o límites del cubo.")

    # Validar que las celdas estén libres
    for p in puntos:
        if tablero.leer_celda(cubo, p) != tablero.SIN_EXPLORAR:
            raise ErrorFlota("Hay una celda ocupada por otra nave.")

    if not hay_distancia_segura(cubo, puntos, n):
        raise ErrorFlota("No se respeta la distancia de seguridad (1 celda libre alrededor).")

    for p in puntos:
        tablero.escribir_celda(cubo, p, tablero.NAVE_OCULTA)

    # Registro de impactos por celda
    impactos_iniciales = {}
    for p in puntos:
        impactos_iniciales[p] = 0

    flota.append((nave, puntos, impactos_iniciales))
    return cubo, flota


def ubicacion_automatica(cubo, catalogo=None, semilla=None, n=8):
    """
    Objetivo: Ubicar de forma automática toda la flota respetando todas las reglas.
    Parámetros:
        - cubo (list): Matriz 3D del tablero.
        - catalogo (dict): Catálogo de naves. Por defecto usa CATALOGO_NAVES.
        - semilla (int): Semilla aleatoria opcional para pruebas.
        - n (int): Tamaño del cubo.
    Devuelve:
        list: Lista de la flota ubicada.
    Excepciones:
        Ninguna.
    """
    if catalogo is None:
        catalogo = CATALOGO_NAVES

    if semilla is not None:
        random.seed(semilla)

    flota = []
    for letra, datos in catalogo.items():
        celdas = datos["celdas"]
        cantidad = datos["cantidad"]

        for i in range(cantidad):
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
                except ErrorFlota:
                    pass
    return flota


# Entrega 2
# --------------------------------------------------------
# Control de impactos, averías y hundimiento 
# --------------------------------------------------------

def nave_hundida(nave_letra, puntos, impactos):
    """
    Objetivo: Determinar si todas las celdas de una nave sufrieron el daño suficiente.
    Parámetros:
        - nave_letra (str): Identificador de la nave.
        - puntos (list): Lista de coordenadas (z, x, y) que ocupa la nave.
        - impactos (dict): Mapa del contador de impactos por celda.
    Devuelve:
        bool: True si la nave está hundida, False en caso contrario.
    Excepciones:
        Ninguna.
    """
    # Averiguamos cuántos disparos requiere cada celda
    if nave_letra == "P":
        impactos_necesarios = 2  # Portaaviones necesita 2 por celda
    else:
        impactos_necesarios = 1  # Las demás naves necesitan 1 por celda

    # Revisamos cada punto de la nave uno por uno
    for p in puntos:
        cant_impactos = 0
        if p in impactos:
            cant_impactos = impactos[p]

        # Si alguna celda no alcanza el mínimo de impactos, la nave sigue viva
        if cant_impactos < impactos_necesarios:
            return False

    # Si todas las celdas alcanzaron la cantidad necesaria, está hundida
    return True


def registrar_impacto(flota, punto, arma_usada="T"):
    """
    Objetivo: Registrar el impacto de un disparo sobre una coordenada específica.
    Parámetros:
        - flota (list): Lista de naves de la partida.
        - punto (tuple): Coordenada (z, x, y) a impactar.
        - arma_usada (str): Identificador del arma enviada.
    Devuelve:
        tuple: (impacto_valido, nave_letra, estado)
               estado puede ser "averiada", "hundida", "inmune" o None.
    Excepciones:
        Ninguna.
    """
    for nave in flota:
        letra = nave[0]
        puntos = nave[1]
        impactos = nave[2]

        # Si el punto disparado pertenece a esta nave
        if punto in puntos:

            # Regla del Submarino: El Láser (L) no lo afecta
            if letra == "S" and arma_usada == "L":
                return False, letra, "inmune"

            # Sumamos 1 al contador de impactos de esta celda
            if punto in impactos:
                impactos[punto] = impactos[punto] + 1
            else:
                impactos[punto] = 1

            # Revisamos si con este disparo la nave se hundió
            if nave_hundida(letra, puntos, impactos):
                return True, letra, "hundida"
            else:
                return True, letra, "averiada"

    # Si el punto no tocó ninguna nave
    return False, None, None


def flota_hundida(flota):
    """
    Objetivo: Comprobar si todas las naves de la flota han sido destruidas.
    Parámetros:
        - flota (list): Lista con el estado de las naves de la partida.
    Devuelve:
        bool: True si todas las naves están hundidas, False en caso contrario.
    Excepciones:
        Ninguna.
    """
    if len(flota) == 0:
        return False

    for nave in flota:
        letra = nave[0]
        puntos = nave[1]
        impactos = nave[2]

        if not nave_hundida(letra, puntos, impactos):
            return False

    return True


def revelar_celda_rival(flota, cubo):
    """
    Objetivo: Comportamiento propio del Destructor (D): al ser impactado revela una celda ocupada del rival.
    Parámetros:
        - flota (list): Lista de la flota rival.
        - cubo (list): Matriz 3D del tablero rival.
    Devuelve:
        tuple o None: Coordenada (z, x, y) de la celda revelada, o None si no hay celdas para revelar.
    Excepciones:
        Ninguna.
    """
    celdas_candidatas = []

    for nave in flota:
        puntos = nave[1]
        for p in puntos:
            # Si en el cubo la celda todavía tiene una nave oculta
            if tablero.leer_celda(cubo, p) == tablero.NAVE_OCULTA:
                celdas_candidatas.append(p)

    # Si hay celdas disponibles para revelar, elegimos una al azar
    if len(celdas_candidatas) > 0:
        return random.choice(celdas_candidatas)

    return None


# Entrega 3
# --------------------------------------------------------
# Datos de la flota para guardar y reponer la partida
# --------------------------------------------------------

def exportar_flota(flota):
    """
    Objetivo: Preparar los datos de la flota en diccionarios y listas simples para guardar en JSON.
    Parámetros:
        - flota (list): Lista de naves ubicadas [(letra, puntos, impactos), ...].
    Devuelve:
        list: Lista de diccionarios con los datos de cada nave listos para JSON.
    Excepciones:
        ErrorFlota: Si la estructura de la flota recibida no es válida.
    """
    if type(flota) != list:
        raise ErrorFlota("La flota debe ser una lista.")

    datos_guardados = []
    try:
        for nave in flota:
            letra = nave[0]
            puntos = nave[1]
            impactos = nave[2]

            if letra not in CATALOGO_NAVES:
                raise ErrorFlota(f"Nave no reconocida al exportar: {letra}")

            puntos_simples = []
            impactos_simples = {}

            for p in puntos:
                clave_texto = f"{p[0]},{p[1]},{p[2]}"
                puntos_simples.append([p[0], p[1], p[2]])
                impactos_simples[clave_texto] = impactos.get(p, 0)

            datos_guardados.append({
                "letra": letra,
                "puntos": puntos_simples,
                "impactos": impactos_simples
            })
    except ErrorFlota:
        raise
    except (TypeError, IndexError, AttributeError) as error:
        raise ErrorFlota(f"Error al preparar los datos de la flota para guardar: {error}")
    else:
        return datos_guardados


def importar_flota(datos_guardados, n=8):
    """
    Objetivo: Reconstruir la estructura de la flota a partir de los datos leídos del JSON.
    Parámetros:
        - datos_guardados (list): Lista de diccionarios recuperados del archivo JSON.
        - n (int): Tamaño del cubo para validar los límites de las coordenadas (por defecto 8).
    Devuelve:
        list: Lista de la flota reconstruida en su formato original [(letra, puntos, impactos), ...].
    Excepciones:
        ErrorFlota: Si los datos guardados están corruptos, incompletos o fuera de rango.
    """
    if type(datos_guardados) != list:
        raise ErrorFlota("Los datos de la flota guardada deben ser una lista.")

    flota_repuesta = []
    try:
        for item in datos_guardados:
            letra = item["letra"]
            if letra not in CATALOGO_NAVES:
                raise ErrorFlota(f"Nave no reconocida en partida guardada: {letra}")

            puntos = []
            impactos = {}

            for coords in item["puntos"]:
                if type(coords) != list or len(coords) != 3:
                    raise ErrorFlota("Coordenada inválida en archivo guardado.")

                z, x, y = coords[0], coords[1], coords[2]
                if type(z) != int or type(x) != int or type(y) != int:
                    raise ErrorFlota("Las coordenadas deben ser números enteros.")
                if not (1 <= z <= n and 1 <= x <= n and 1 <= y <= n):
                    raise ErrorFlota("Coordenada fuera de los límites del cubo.")

                punto = (z, x, y)
                puntos.append(punto)

                clave_texto = f"{z},{x},{y}"
                cant = item["impactos"].get(clave_texto, 0)
                if type(cant) != int or cant < 0:
                    raise ErrorFlota("Cantidad de impactos inválida en archivo guardado.")
                impactos[punto] = cant

            flota_repuesta.append((letra, puntos, impactos))
    except ErrorFlota:
        raise
    except (KeyError, TypeError, IndexError, AttributeError) as error:
        raise ErrorFlota(f"Error al reponer los datos de la flota: {error}")
    else:
        return flota_repuesta


def reponer_flota_en_cubo(cubo, flota):
    """
    Objetivo: Sincronizar el estado visual del cubo a partir de una flota repuesta desde archivo.
    Parámetros:
        - cubo (list): Matriz 3D del tablero de juego.
        - flota (list): Lista de la flota reconstruida.
    Devuelve:
        list: El cubo actualizado con los estados correspondientes de cada nave.
    Excepciones:
        ErrorFlota: Si algún punto de la flota no es válido dentro del cubo recibido.
    """
    for nave in flota:
        letra = nave[0]
        puntos = nave[1]
        impactos = nave[2]
        hundida = nave_hundida(letra, puntos, impactos)

        for p in puntos:
            if not tablero.es_punto_valido(cubo, p):
                raise ErrorFlota(f"Punto fuera de rango al reponer el cubo: {p}")

            if hundida:
                tablero.escribir_celda(cubo, p, tablero.HUNDIDO)
            elif impactos.get(p, 0) > 0:
                tablero.escribir_celda(cubo, p, tablero.IMPACTO)
            else:
                tablero.escribir_celda(cubo, p, tablero.NAVE_OCULTA)

    return cubo
