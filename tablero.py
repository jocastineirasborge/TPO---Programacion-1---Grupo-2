"""
tablero.py - Modulo del cubo de juego (Operacion Cubo).

Responsabilidad (Entrega 1): crear el cubo, validar puntos, leer y escribir
celdas, operaciones de matrices y dibujo de una capa de z.
Responsabilidad (Entrega 2): planos (cortes) fijando x y fijando y, puntos de
un plano o de una recta, y vecinos de una celda.
Este modulo NO usa print ni input: recibe datos y devuelve datos.

Convenciones del cubo (contrato con el resto de los modulos):
- El cubo es una lista de listas de listas de N x N x N.
- Un punto es una tupla (z, x, y) con valores de 1 a N.
- La celda del punto (z, x, y) se guarda en cubo[z - 1][x - 1][y - 1].
- Cada celda contiene uno de los estados definidos abajo (nunca un numero suelto).
"""

import re

# ------------------------------------------------------------------
# Estados de celda: cada estado tiene nombre propio
# ------------------------------------------------------------------

SIN_EXPLORAR = 0
NAVE_OCULTA = 1
AGUA_MARCADA = 2
IMPACTO = 3
HUNDIDO = 4
DETECTADO = 5

ESTADOS = (SIN_EXPLORAR, NAVE_OCULTA, AGUA_MARCADA, IMPACTO, HUNDIDO, DETECTADO)

SIMBOLOS = {
    SIN_EXPLORAR: "~",
    NAVE_OCULTA: "N",
    AGUA_MARCADA: "o",
    IMPACTO: "X",
    HUNDIDO: "#",
    DETECTADO: "?",
}

DESCRIPCIONES = {
    SIN_EXPLORAR: "sin explorar",
    NAVE_OCULTA: "nave propia",
    AGUA_MARCADA: "agua",
    IMPACTO: "impacto",
    HUNDIDO: "hundido",
    DETECTADO: "detectado",
}

# ------------------------------------------------------------------
# Tamaño del cubo
# ------------------------------------------------------------------

N_POR_DEFECTO = 8
N_MINIMO = 5    # el portaaviones ocupa 5 celdas en linea recta
N_MAXIMO = 20   # limite para que el dibujo por consola siga siendo legible

# Punto tipeado: tres numeros separados por comas (se toleran espacios)
PATRON_PUNTO = r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$"

# ------------------------------------------------------------------
# Ejes y direcciones
# ------------------------------------------------------------------

# Orden de los ejes dentro de un punto (z, x, y)
EJES = ("z", "x", "y")

# Las seis direcciones ortogonales (una celda hacia cada cara)
DIRECCIONES_ORTOGONALES = (
    (-1, 0, 0), (1, 0, 0),
    (0, -1, 0), (0, 1, 0),
    (0, 0, -1), (0, 0, 1),
)

# ------------------------------------------------------------------
# Cubo y validacion de puntos
# ------------------------------------------------------------------

def crear_cubo(n = N_POR_DEFECTO):
    """
    Objetivo: crear un cubo de n x n x n con todas las celdas sin explorar.
    Parametros: n (int) tamanio de cada eje, entre N_MINIMO y N_MAXIMO.
    Salida: el cubo (lista de listas de listas) o None si n no es valido.
    Excepciones: ninguna.
    """
    if type(n) != int or n < N_MINIMO or n > N_MAXIMO:
        return None
    cubo = []
    for z in range(0, n):
        capa = []
        for x in range(0, n):
            fila = []
            for y in range(0, n):
                fila.append(SIN_EXPLORAR)
            capa.append(fila)  # cada fila es una lista NUEVA: no hay aliasing
        cubo.append(capa)

    return cubo


def tamanio_cubo(cubo):
    """
    Objetivo: informar el tamaño N del cubo.
    Parametros: cubo.
    Salida: N (int).
    Excepciones: ninguna.
    """
    return len(cubo)


def es_punto_valido(cubo, punto):
    """
    Objetivo: verificar que un punto exista dentro del cubo.
    Parámetros: cubo y punto (tupla z, x, y).
    Salida: True si es una tupla de 3 enteros entre 1 y N; False si no.
    Excepciones: ninguna.
    """
    if type(punto) != tuple or len(punto) != 3:
        return False
    n = len(cubo)
    
    for i in range(0, len(punto)):
        valor = punto[i]
        if type(valor) != int:
            return False
        if valor < 1 or valor > n:
            return False
        
    return True


def texto_a_punto(texto, cubo):
    """
    Objetivo: convertir un punto tipeado ("3,5,4") en una tupla validada.
    Parametros: texto (str) en el orden z,x,y y el cubo donde debe existir.
    Salida: tupla (z, x, y) o None si el formato o el rango no son validos.
    Excepciones: ninguna.
    """
    if type(texto) != str:
        return None
    
    coincidencia = re.match(PATRON_PUNTO, texto)
    if coincidencia is None:
        return None
    z = int(coincidencia.group(1))
    x = int(coincidencia.group(2))
    y = int(coincidencia.group(3))
    punto = (z, x, y)
    if not es_punto_valido(cubo, punto):
        return None
    
    return punto


def texto_a_tramo(texto, cubo):
    """
    Objetivo: convertir un tramo tipeado ("3,4,2-3,4,7") en dos puntos.
    Parametros: texto (str) con dos puntos unidos por un guion, y el cubo.
    Salida: tupla (desde, hasta) con dos puntos validos, o None.
    No controla que el tramo sea recto: esa regla pertenece a flota.py.
    Excepciones: ninguna.
    """
    if type(texto) != str:
        return None
    partes = texto.split("-")
    if len(partes) != 2:
        return None
    desde = texto_a_punto(partes[0], cubo)
    hasta = texto_a_punto(partes[1], cubo)
    if desde is None or hasta is None:
        return None
    return desde, hasta


def punto_a_texto(punto):
    """
    Objetivo: escribir un punto en el formato del juego.
    Parametros: punto (tupla z, x, y).
    Salida: cadena "z,x,y", por ejemplo "6,3,1".
    Excepciones: ninguna.
    """
    partes = []
    for i in range(0, len(punto)):
        partes.append(str(punto[i]))
    return ",".join(partes)


def leer_celda(cubo, punto):
    """
    Objetivo: obtener el estado de una celda.
    Parametros: cubo y punto (tupla z, x, y).
    Salida: el estado de la celda, o None si el punto no es valido.
    Excepciones: ninguna.
    """
    if not es_punto_valido(cubo, punto):
        return None
    z, x, y = punto
    return cubo[z - 1][x - 1][y - 1]


def escribir_celda(cubo, punto, estado):
    """
    Objetivo: cambiar el estado de una celda (modifica el cubo recibido).
    Parametros: cubo, punto (tupla z, x, y) y estado (uno de ESTADOS).
    Salida: True si se escribio; False si el punto o el estado no son validos.
    Excepciones: ninguna.
    """
    if not es_punto_valido(cubo, punto):
        return False
    if estado not in ESTADOS:
        return False
    z, x, y = punto
    cubo[z - 1][x - 1][y - 1] = estado
    return True


# ------------------------------------------------------------------
# Operaciones de matrices
# ------------------------------------------------------------------

def obtener_capa(cubo, z):
    """
    Objetivo: obtener una copia de la capa z del cubo.
    Parametros: cubo y z (int entre 1 y N).
    Salida: matriz de N x N indexada [x][y], o None si z no es valido.
    Excepciones: ninguna.
    """
    if type(z) != int or z < 1 or z > len(cubo):
        return None
    capa = []
    for x in range(0, len(cubo[z - 1])):
        fila = []
        for y in range(0, len(cubo[z - 1][x])):
            fila.append(cubo[z - 1][x][y])
        capa.append(fila)
    return capa


def obtener_plano_x(cubo, x):
    """
    Objetivo: obtener una copia del plano (corte) que fija el valor de x.
    Parametros: cubo y x (int entre 1 y N).
    Salida: matriz de N x N indexada [z][y], o None si x no es valido.
    Excepciones: ninguna.
    """
    if type(x) != int or x < 1 or x > len(cubo):
        return None
    plano = []
    for z in range(0, len(cubo)):
        fila = []
        for y in range(0, len(cubo[z][x - 1])):
            fila.append(cubo[z][x - 1][y])
        plano.append(fila)
    return plano


def obtener_plano_y(cubo, y):
    """
    Objetivo: obtener una copia del plano (corte) que fija el valor de y.
    Parametros: cubo e y (int entre 1 y N).
    Salida: matriz de N x N indexada [z][x], o None si y no es valido.
    Excepciones: ninguna.
    """
    if type(y) != int or y < 1 or y > len(cubo):
        return None
    plano = []
    for z in range(0, len(cubo)):
        fila = []
        for x in range(0, len(cubo[z])):
            fila.append(cubo[z][x][y - 1])
        plano.append(fila)
    return plano


# Despacho por eje: cada eje sabe como obtener su plano
OBTENER_PLANO = {
    "z": obtener_capa,
    "x": obtener_plano_x,
    "y": obtener_plano_y,
}


def obtener_plano(cubo, eje, valor):
    """
    Objetivo: obtener una copia del plano que fija un eje en un valor.
    Parametros: cubo, eje ("z", "x" o "y") y valor (int entre 1 y N).
    Salida: matriz de N x N, o None si el eje o el valor no son validos.
        - eje "z": indexada [x][y]
        - eje "x": indexada [z][y]
        - eje "y": indexada [z][x]
    Excepciones: ninguna.
    """
    if eje not in OBTENER_PLANO:
        return None
    return OBTENER_PLANO[eje](cubo, valor)


def armar_punto(eje, valor, a, b):
    """
    Objetivo: armar un punto (z, x, y) a partir de un eje fijo y los otros dos valores.
    Parametros: eje fijo ("z", "x" o "y"), su valor, y los valores a y b de los
        otros dos ejes en el orden en que aparecen en EJES.
    Salida: tupla (z, x, y). Ej: armar_punto("x", 2, 5, 7) -> (5, 2, 7).
    Excepciones: ninguna (el eje debe ser valido).
    """
    valores = [a, b]
    valores.insert(EJES.index(eje), valor)
    return tuple(valores)


def puntos_de_plano(cubo, eje, valor):
    """
    Objetivo: listar todos los puntos de un plano del cubo (util para el sonar).
    Parametros: cubo, eje ("z", "x" o "y") y valor (int entre 1 y N).
    Salida: lista de N * N tuplas (z, x, y), o lista vacia si eje o valor no son validos.
    Excepciones: ninguna.
    """
    n = len(cubo)
    if eje not in EJES or type(valor) != int or valor < 1 or valor > n:
        return []
    puntos = []
    for a in range(1, n + 1):
        for b in range(1, n + 1):
            puntos.append(armar_punto(eje, valor, a, b))
    return puntos


def puntos_de_recta(cubo, punto, eje):
    """
    Objetivo: listar los puntos de la recta que pasa por un punto, sobre un eje
        (util para la carga de profundidad y el barrido laser).
    Parametros: cubo, punto (tupla z, x, y) y eje ("z", "x" o "y") sobre el que varia la recta.
    Salida: lista de N tuplas (z, x, y) ordenadas de 1 a N sobre ese eje,
        o lista vacia si el punto o el eje no son validos.
    Excepciones: ninguna.
    """
    if eje not in EJES or not es_punto_valido(cubo, punto):
        return []
    posicion = EJES.index(eje)
    puntos = []
    for valor in range(1, len(cubo) + 1):
        nuevo = list(punto)
        nuevo[posicion] = valor
        puntos.append(tuple(nuevo))
    return puntos


# ------------------------------------------------------------------
# Vecinos de una celda
# ------------------------------------------------------------------

def desplazar(punto, direccion):
    """
    Objetivo: sumar un desplazamiento a un punto.
    Parametros: punto (tupla z, x, y) y direccion (tupla dz, dx, dy).
    Salida: tupla (z + dz, x + dx, y + dy); puede quedar fuera del cubo.
    Excepciones: ninguna.
    """
    z, x, y = punto
    dz, dx, dy = direccion
    return (z + dz, x + dx, y + dy)


def vecinos_ortogonales(cubo, punto):
    """
    Objetivo: obtener las celdas que comparten una cara con el punto.
    Parametros: cubo y punto (tupla z, x, y).
    Salida: lista de hasta 6 puntos dentro del cubo (menos en bordes y esquinas),
        o lista vacia si el punto no es valido.
    Excepciones: ninguna.
    """
    if not es_punto_valido(cubo, punto):
        return []
    vecinos = []
    for i in range(0, len(DIRECCIONES_ORTOGONALES)):
        candidato = desplazar(punto, DIRECCIONES_ORTOGONALES[i])
        if es_punto_valido(cubo, candidato):
            vecinos.append(candidato)
    return vecinos


def vecinos(cubo, punto):
    """
    Objetivo: obtener todas las celdas que rodean al punto, incluidas las diagonales
        (util para la regla de separacion entre naves).
    Parametros: cubo y punto (tupla z, x, y).
    Salida: lista de hasta 26 puntos dentro del cubo (sin incluir al propio punto),
        o lista vacia si el punto no es valido.
    Excepciones: ninguna.
    """
    if not es_punto_valido(cubo, punto):
        return []
    resultado = []
    for dz in range(-1, 2):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dz != 0 or dx != 0 or dy != 0:
                    candidato = desplazar(punto, (dz, dx, dy))
                    if es_punto_valido(cubo, candidato):
                        resultado.append(candidato)
    return resultado


def contar_vecinos_con_estado(cubo, punto, estado, solo_ortogonales=False):
    """
    Objetivo: contar cuantas celdas vecinas de un punto tienen un estado.
    Parametros: cubo, punto (tupla z, x, y), estado y solo_ortogonales (bool):
        si es True cuenta solo las 6 vecinas por cara; si no, las 26.
    Salida: cantidad (int); 0 si el punto no es valido.
    Excepciones: ninguna.
    """
    if solo_ortogonales:
        lista = vecinos_ortogonales(cubo, punto)
    else:
        lista = vecinos(cubo, punto)
    cantidad = 0
    for i in range(0, len(lista)):
        if leer_celda(cubo, lista[i]) == estado:
            cantidad = cantidad + 1
    return cantidad


def trasponer(matriz):
    """
    Objetivo: intercambiar filas por columnas.
    Parametros: matriz de m x n.
    Salida: matriz nueva de n x m (T[j][i] = A[i][j]).
    Excepciones: ninguna.
    """
    if len(matriz) == 0:
        return []
    filas = len(matriz)
    columnas = len(matriz[0])
    resultado = []
    for j in range(0, columnas):
        nueva_fila = []
        for i in range(0, filas):
            nueva_fila.append(matriz[i][j])
        resultado.append(nueva_fila)
    return resultado


def copiar_cubo(cubo):
    """
    Objetivo: crear una copia profunda e independiente del cubo.
    Parametros: cubo.
    Salida: cubo nuevo; modificarlo no afecta al original.
    Excepciones: ninguna.
    """
    copia = []
    for z in range(0, len(cubo)):
        capa = []
        for x in range(0, len(cubo[z])):
            fila = []
            for y in range(0, len(cubo[z][x])):
                fila.append(cubo[z][x][y])
            capa.append(fila)
        copia.append(capa)
    return copia


def contar_en_matriz(matriz, estado):
    """
    Objetivo: contar cuantas celdas de una matriz tienen un estado.
    Parametros: matriz y estado.
    Salida: cantidad (int).
    Excepciones: ninguna.
    """
    cantidad = 0
    for fila in range(0, len(matriz)):
        for columna in range(0, len(matriz[fila])):
            if matriz[fila][columna] == estado:
                cantidad = cantidad + 1
    return cantidad


def contar_estado(cubo, estado):
    """
    Objetivo: contar cuantas celdas de todo el cubo tienen un estado.
    Parametros: cubo y estado.
    Salida: cantidad (int).
    Excepciones: ninguna.
    """
    total = 0
    for z in range(0, len(cubo)):
        total = total + contar_en_matriz(cubo[z], estado)
    return total


def vista_rival(cubo):
    """
    Objetivo: obtener el cubo tal como lo ve el rival (sin naves ocultas).
    Parametros: cubo.
    Salida: cubo nuevo donde NAVE_OCULTA se reemplaza por SIN_EXPLORAR.
    Sirve para que la maquina decida sin "espiar" la flota.
    Excepciones: ninguna.
    """
    vista = copiar_cubo(cubo)
    for z in range(0, len(vista)):
        for x in range(0, len(vista[z])):
            for y in range(0, len(vista[z][x])):
                if vista[z][x][y] == NAVE_OCULTA:
                    vista[z][x][y] = SIN_EXPLORAR
    return vista


# ------------------------------------------------------------------
# Dibujo
# ------------------------------------------------------------------

def completar(texto, ancho):
    """
    Objetivo: agregar espacios a la derecha hasta llegar a un ancho.
    Parametros: texto (str) y ancho (int).
    Salida: cadena de al menos ese ancho.
    Excepciones: ninguna.
    """
    faltan = ancho - len(texto)
    if faltan > 0:
        return texto + " " * faltan
    return texto


def simbolo_de(estado, mostrar_naves):
    """
    Objetivo: obtener el simbolo con el que se dibuja un estado.
    Parametros: estado y mostrar_naves (bool); si es False la nave se ve como agua.
    Salida: simbolo (str de un caracter).
    Excepciones: ninguna.
    """
    if estado == NAVE_OCULTA and not mostrar_naves:
        return SIMBOLOS[SIN_EXPLORAR]
    return SIMBOLOS[estado]


def texto_referencias(mostrar_naves):
    """
    Objetivo: armar la linea de referencias de simbolos.
    Parametros: mostrar_naves (bool); si es False no se incluye la nave propia.
    Salida: cadena con las referencias.
    Excepciones: ninguna.
    """
    partes = []
    for i in range(0, len(ESTADOS)):
        estado = ESTADOS[i]
        if estado != NAVE_OCULTA or mostrar_naves:
            partes.append(SIMBOLOS[estado] + " " + DESCRIPCIONES[estado])
    return "Referencias: " + "   ".join(partes)


# Como se dibuja cada plano: titulo, eje de las filas, eje de las columnas y si
# la matriz que devuelve obtener_plano hay que trasponerla para dibujarla.
# - Capa z:  obtener_plano da [x][y]; se traspone para ver filas y, columnas x.
# - Corte x: obtener_plano da [z][y]; filas z, columnas y.
# - Corte y: obtener_plano da [z][x]; filas z, columnas x.
FORMATO_PLANOS = {
    "z": {"titulo": "CAPA", "filas": "y", "columnas": "x", "trasponer": True},
    "x": {"titulo": "CORTE", "filas": "z", "columnas": "y", "trasponer": False},
    "y": {"titulo": "CORTE", "filas": "z", "columnas": "x", "trasponer": False},
}


def dibujar_plano(cubo, eje, valor, mostrar_naves=True, con_referencias=True):
    """
    Objetivo: armar el dibujo de un plano del cubo que fija un eje en un valor.
    Parametros: cubo, eje ("z", "x" o "y"), valor (int), mostrar_naves (bool)
        y con_referencias (bool).
    Salida: cadena lista para imprimir, o None si el eje o el valor no son validos.
    Excepciones: ninguna.
    """
    if eje not in FORMATO_PLANOS:
        return None
    plano = obtener_plano(cubo, eje, valor)
    if plano is None:
        return None
    formato = FORMATO_PLANOS[eje]
    if formato["trasponer"]:
        plano = trasponer(plano)
    n = len(plano)
    ancho = len(formato["filas"] + str(n)) + 1

    lineas = []
    lineas.append(f"========= {formato['titulo']} {eje} = {valor} =========")
    encabezado = completar("", ancho)

    for columna in range(0, n):
        encabezado = encabezado + completar(formato["columnas"] + str(columna + 1), ancho)
    lineas.append(encabezado.rstrip())

    for fila in range(0, n):
        linea = completar(formato["filas"] + str(fila + 1), ancho)
        for columna in range(0, n):
            linea = linea + completar(simbolo_de(plano[fila][columna], mostrar_naves), ancho)
        lineas.append(linea.rstrip())

    if con_referencias:
        lineas.append(texto_referencias(mostrar_naves))
    return "\n".join(lineas)


def dibujar_capa(cubo, z, mostrar_naves=True, con_referencias=True):
    """
    Objetivo: armar el dibujo de la capa z (filas y, columnas x).
    Parametros: cubo, z (int), mostrar_naves (bool) y con_referencias (bool).
    Salida: cadena lista para imprimir, o None si z no es valido.
    Excepciones: ninguna.
    """
    return dibujar_plano(cubo, "z", z, mostrar_naves, con_referencias)


def dibujar_corte_x(cubo, x, mostrar_naves=True, con_referencias=True):
    """
    Objetivo: armar el dibujo del corte que fija x (filas z, columnas y).
    Parametros: cubo, x (int), mostrar_naves (bool) y con_referencias (bool).
    Salida: cadena lista para imprimir, o None si x no es valido.
    Excepciones: ninguna.
    """
    return dibujar_plano(cubo, "x", x, mostrar_naves, con_referencias)


def dibujar_corte_y(cubo, y, mostrar_naves=True, con_referencias=True):
    """
    Objetivo: armar el dibujo del corte que fija y (filas z, columnas x).
    Parametros: cubo, y (int), mostrar_naves (bool) y con_referencias (bool).
    Salida: cadena lista para imprimir, o None si y no es valido.
    Excepciones: ninguna.
    """
    return dibujar_plano(cubo, "y", y, mostrar_naves, con_referencias)


def dibujar_cubo(cubo, mostrar_naves=True):
    """
    Objetivo: armar el dibujo de todas las capas de z, una debajo de otra.
    Parametros: cubo y mostrar_naves (bool).
    Salida: cadena lista para imprimir, con las referencias al final.
    Excepciones: ninguna.
    """
    bloques = []
    for z in range(1, len(cubo) + 1):
        bloques.append(dibujar_capa(cubo, z, mostrar_naves, False))
    bloques.append(texto_referencias(mostrar_naves))
    return "\n\n".join(bloques)