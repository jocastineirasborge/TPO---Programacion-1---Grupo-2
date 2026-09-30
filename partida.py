"""Módulo para la partida"""
import random
from tablero import (
    crear_cubo,
    dibujar_cubo,
    texto_a_punto,
    texto_a_tramo,
    escribir_celda,
    IMPACTO,
    HUNDIDO,
    AGUA_MARCADA
)
from flota import (
    ubicar_nave,
    ubicacion_automatica,
    obtener_catalogo_naves
)
from radar import busqueda_lineal_nave
from armamento import obtener_celdas_afectadas, obtener_catalogo_armas
from registro import inicializar_registro, registrar_turno

# EXCEPCIÓN PROPIA
class ErrorPartida(Exception):
    pass

# CONSTANTES
AGUA = "~"
NAVE = "N"
IMPACTO = "X"
HUNDIDO = "#"
TAMANO_CUBO = 8
NAVES = {
    "F": {"nombre": "Fragata", "celdas": 3, "cantidad": 2},
    "D": {"nombre": "Destructor", "celdas": 2, "cantidad": 2},
    "S": {"nombre": "Submarino", "celdas": 2, "cantidad": 2},
    "C": {"nombre": "Crucero", "celdas": 4, "cantidad": 1},
    "P": {"nombre": "Portaaviones", "celdas": 5, "cantidad": 1},
    "E": {"nombre": "Estacion orbital", "celdas": 8, "cantidad": 1}
    }

def validar_punto(punto, n):
    partes = punto.split(",")
    if len(partes) != 3:
        return False
    try:
        z = int(partes[0])
        x = int(partes[1])
        y = int(partes[2])
    except ValueError:
        return False
    return (1 <= z <= n
        and 1 <= x <= n
        and 1 <= y <= n)

def convertir_punto(punto):
    partes = punto.split(",")
    z = int(partes[0]) - 1
    x = int(partes[1]) - 1
    y = int(partes[2]) - 1
    return z, x, y

# UBICACIÓN DE NAVES
def obtener_celdas(desde, hasta):
    z1, x1, y1 = desde
    z2, x2, y2 = hasta
    celdas = []
    if x1 == x2 and y1 == y2:
        paso = 1 if z2 >= z1 else -1
        for z in range(z1, z2 + paso, paso):
            celdas.append((z, x1, y1))
        return celdas
    if z1 == z2 and y1 == y2:
        paso = 1 if x2 >= x1 else -1
        for x in range(x1, x2 + paso, paso):
            celdas.append((z1, x, y1))
        return celdas
    if z1 == z2 and x1 == x2:
        paso = 1 if y2 >= y1 else -1
        for y in range(y1, y2 + paso, paso):
            celdas.append((z1, x1, y))
        return celdas
    return []

def celdas_ocupadas(flota):
    ocupadas = []
    for nave in flota:
        for celda in nave["celdas"]:
            ocupadas.append(celda)
    return ocupadas

def estan_cerca(celda1, celda2):
    z1, x1, y1 = celda1
    z2, x2, y2 = celda2
    return (abs(z1 - z2) <= 1
        and abs(x1 - x2) <= 1
        and abs(y1 - y2) <= 1)

def validar_distancia(celdas, flota):
    ocupadas = celdas_ocupadas(flota)
    for nueva in celdas:
        for ocupada in ocupadas:
            if estan_cerca(nueva, ocupada):
                return False
    return True

def validar_restriccion(letra, celdas, n):
    for z, x, y in celdas:
        z_real = z + 1
        if letra == "S":
            if z_real > n // 2:
                return False
        elif letra == "C":
            if z_real == 1 or z_real == n:
                return False
        elif letra == "P":
            if z_real <= n // 2:
                return False
    return True

def ubicar_nave(cubo, flota, letra, desde, hasta):
    n = len(cubo)
    if letra not in NAVES:
        raise ErrorPartida("Nave inválida")
    if letra == "E":
        raise ErrorPartida("La estación orbital se ubica aparte")
    if not validar_punto(desde, n):
        raise ErrorPartida("Punto inicial inválido")
    if not validar_punto(hasta, n):
        raise ErrorPartida("Punto final inválido")
    punto1 = convertir_punto(desde)
    punto2 = convertir_punto(hasta)
    celdas = obtener_celdas(punto1, punto2)
    if len(celdas) == 0:
        raise ErrorPartida("La nave debe estar en línea recta")
    if len(celdas) != NAVES[letra]["celdas"]:
        raise ErrorPartida("La longitud de la nave es incorrecta")
    for z, x, y in celdas:
        if cubo[z][x][y] != AGUA:
            raise ErrorPartida("Hay una celda ocupada")
    if not validar_restriccion(letra, celdas, n):
        raise ErrorPartida("La nave no cumple su restricción")
    if not validar_distancia(celdas, flota):
        raise ErrorPartida("Debe quedar al menos una celda libre entre naves")
    for z, x, y in celdas:
        cubo[z][x][y] = NAVE
    flota.append({"letra": letra,"celdas": celdas,"impactos": 0,"hundida": False})
    return True

def ubicar_estacion(cubo, flota, punto):
    n = len(cubo)
    if not validar_punto(punto, n):
        raise ErrorPartida("Punto inválido")
    z, x, y = convertir_punto(punto)
    if z <= 0 or x <= 0 or y <= 0:
        raise ErrorPartida("La estación toca una cara exterior")
    if z + 1 >= n - 1:
        raise ErrorPartida("La estación toca una cara exterior")
    if x + 1 >= n - 1:
        raise ErrorPartida("La estación toca una cara exterior")
    if y + 1 >= n - 1:
        raise ErrorPartida("La estación toca una cara exterior")
    celdas = []
    for dz in range(2):
        for dx in range(2):
            for dy in range(2):
                celda = (z + dz,
                    x + dx,
                    y + dy)
                if cubo[celda[0]][celda[1]][celda[2]] != AGUA:
                    raise ErrorPartida("Hay una celda ocupada")
                celdas.append(celda)
    if not validar_distancia(celdas, flota):
        raise ErrorPartida("Debe quedar al menos una celda libre entre naves")
    for z2, x2, y2 in celdas:
        cubo[z2][x2][y2] = NAVE
    flota.append({"letra": "E",
        "celdas": celdas,
        "impactos": 0,
        "hundida": False})
    return True

# UBICACIÓN AUTOMÁTICA
def ubicacion_automatica(jugador):
    letras = ["F", "F",
        "D", "D",
        "S", "S",
        "C",
        "P"]
    n = len(jugador["cubo"])
    for letra in letras:
        ubicada = False
        while not ubicada:
            z1 = random.randint(1, n)
            x1 = random.randint(1, n)
            y1 = random.randint(1, n)
            eje = random.randint(1, 3)
            largo = NAVES[letra]["celdas"]
            z2 = z1
            x2 = x1
            y2 = y1
            if eje == 1:
                z2 = z1 + largo - 1
            elif eje == 2:
                x2 = x1 + largo - 1
            else:
                y2 = y1 + largo - 1
            if z2 > n or x2 > n or y2 > n:
                continue
            try:
                ubicar_nave(jugador["cubo"],jugador["flota"],letra,str(z1) + "," + str(x1) + "," + str(y1),str(z2) + "," + str(x2) + "," + str(y2))
                ubicada = True
            except ErrorPartida:
                pass
    ubicada = False
    while not ubicada:
        z = random.randint(2, n - 2)
        x = random.randint(2, n - 2)
        y = random.randint(2, n - 2)
        try:
            ubicar_estacion(jugador["cubo"],jugador["flota"],str(z) + "," + str(x) + "," + str(y))
            ubicada = True
        except ErrorPartida:
            pass

# JUGADOR
def crear_jugador(n):
    return {"cubo": crear_cubo(n),"flota": [],"disparos": []}

# FUNCIONES PÚBLICAS OBLIGATORIAS
def nueva_partida_1v1(configuracion):
    n = configuracion.get("n", TAMANO_CUBO)

    return {
        "tipo": "1v1",
        "n": n,
        "jugadores": [crear_jugador(n),crear_jugador(n)],
        "turno": 0,
        "terminada": False,
        "ganador": None
        }

def nueva_partida_vs_maquina(configuracion, dificultad):
    n = configuracion.get("n", TAMANO_CUBO)

    return {
        "tipo": "vs_maquina",
        "dificultad": dificultad,
        "n": n,
        "jugadores": [crear_jugador(n), crear_jugador(n)],
        "turno": 0,
        "terminada": False,
        "ganador": None
        }

def buscar_nave(flota, celda):
    for nave in flota:
        if celda in nave["celdas"]:
            return nave
    return None

def disparar(estado, jugador, objetivo):
    n = estado["n"]

    if not validar_punto(objetivo, n):
        raise ErrorPartida("Objetivo inválido")
    
    celda = convertir_punto(objetivo)

    if celda in estado["jugadores"][jugador]["disparos"]:
        raise ErrorPartida("Ya se disparó a esa celda")
    
    estado["jugadores"][jugador]["disparos"].append(celda)
    rival = 1 - jugador
    nave = buscar_nave(estado["jugadores"][rival]["flota"],celda)

    if nave is None:
        return "Agua."
    
    nave["impactos"] += 1
    z, x, y = celda
    estado["jugadores"][rival]["cubo"][z][x][y] = IMPACTO

    if nave["impactos"] >= len(nave["celdas"]):
        nave["hundida"] = True

        for z2, x2, y2 in nave["celdas"]:
            estado["jugadores"][rival]["cubo"][z2][x2][y2] = HUNDIDO

        return "Hundido"
    
    return "Impacto"

def ejecutar_turno(estado, jugada):
    if estado["terminada"]:
        raise ErrorPartida("La partida ya terminó")
    arma = jugada.get("arma")
    objetivo = jugada.get("objetivo")
    if arma != "T":
        raise ErrorPartida("En la Entrega 1 solamente se utiliza el torpedo")
    jugador = estado["turno"]
    disparar(estado,jugador,objetivo)
    ganador = hay_ganador(estado)
    if ganador is None:
        estado["turno"] = 1 - jugador
    return estado
def turno_maquina(estado):
    if estado["turno"] != 1:
        raise ErrorPartida("No es el turno de la máquina.")
    n = estado["n"]
    disponibles = []
    for z in range(n):
        for x in range(n):
            for y in range(n):
                if (z, x, y) not in estado["jugadores"][1]["disparos"]:disponibles.append((z, x, y))
    objetivo = random.choice(disponibles)
    texto = (str(objetivo[0] + 1)+ ","+ str(objetivo[1] + 1)+ ","+ str(objetivo[2] + 1))
    jugada = {"arma": "T","objetivo": texto}
    return ejecutar_turno(estado, jugada)
def hay_ganador(estado):
    for jugador in range(2):
        rival = 1 - jugador
        if len(estado["jugadores"][rival]["flota"]) == 0:
            continue
        todas_hundidas = True
        for nave in estado["jugadores"][rival]["flota"]:
            if not nave["hundida"]:
                todas_hundidas = False
        if todas_hundidas:
            estado["terminada"] = True
            estado["ganador"] = jugador
            return jugador
    return None

# DIBUJO
def mostrar_capa(cubo, z, ocultar_naves=False):
    n = len(cubo)
    print()
    print("========= CAPA z =", z + 1, "=========")
    print("     ", end="")
    for x in range(n):
        print("x" + str(x + 1), end=" ")
    print()
    for y in range(n):
        print("y" + str(y + 1), end="   ")
        for x in range(n):
            valor = cubo[z][x][y]
            if ocultar_naves and valor == NAVE:
                valor = AGUA
            print(valor, end="  ")
        print()
def mostrar_cubo(jugador, ocultar_naves=False):
    for z in range(len(jugador["cubo"])):
        mostrar_capa(jugador["cubo"],z,ocultar_naves)
      
# SUBMENÚ DE UBICACIÓN
def ubicacion_manual(jugador):
    pendientes = ["F", "F",
        "D", "D",
        "S", "S",
        "C",
        "P",
        "E"]
    while len(pendientes) > 0:
        print()
        print("Pendientes:", pendientes)
        letra = input("Nave (F/D/S/C/P/E): ").upper()
        if letra not in pendientes:
            print("Nave inválida.")
            continue
        try:
            if letra == "E":
                punto = input("Esquina de la estación: ")
                ubicar_estacion(jugador["cubo"],jugador["flota"],punto)
            else:
                tramo = input("Desde-hasta: ")
                partes = tramo.split("-")
                if len(partes) != 2:
                    raise ErrorPartida("Formato incorrecto")
                ubicar_nave(jugador["cubo"],jugador["flota"],letra,partes[0],partes[1])
            pendientes.remove(letra)
            print("Ubicada.")
        except ErrorPartida as error:
            print("No se puede ubicar ahí.")
            print(error)
def submenú_ubicacion(jugador):
    while True:
        print()
        print("1 - Ubicación manual")
        print("2 - Ubicación automática")
        opcion = input("Opción: ")
        if opcion == "1":
            ubicacion_manual(jugador)
            break
        elif opcion == "2":
            ubicacion_automatica(jugador)
            print("Flota ubicada automáticamente")
            break
        else:
            print("Opción inválida")

# PREPARACIÓN DE PARTIDAS
def preparar_1v1():
    estado = nueva_partida_1v1({"n": TAMANO_CUBO})
    print()
    print("--- Flota de Jugador 1 ---")
    submenú_ubicacion(estado["jugadores"][0])
    print()
    print("--- Flota de Jugador 2 ---")
    submenú_ubicacion(estado["jugadores"][1])
    return estado
def preparar_vs_maquina():
    estado = nueva_partida_vs_maquina({"n": TAMANO_CUBO},"normal")
    print()
    print("--- Flota del Jugador ---")
    submenú_ubicacion(estado["jugadores"][0])
    print()
    print("--- Flota de la máquina ---")
    ubicacion_automatica(estado["jugadores"][1])
    print("Flota de la máquina ubicada.")
    return estado

# PARTIDA 1 VS 1
def partida_1v1(estado):
    while not estado["terminada"]:
        jugador = estado["turno"]
        print("----------------------------")
        print("Turno de Jugador", jugador + 1)
        print("----------------------------")
        print("1 - Disparar")
        print("2 - Ver el cubo")
        print("3 - Salir")
        opcion = input("Opción: ")
        if opcion == "1":
            arma = input("Arma (T): ").upper()
            objetivo = input("Objetivo: ")
            try:
                ejecutar_turno(estado,{"arma": arma,"objetivo": objetivo})
                print("Disparo realizado.")
                if estado["terminada"]:
                    print("Ganó el Jugador",
                        estado["ganador"] + 1)
            except ErrorPartida as error:
                print("Error:", error)
        elif opcion == "2":
            mostrar_cubo(estado["jugadores"][jugador])
        elif opcion == "3":
            break
        else:
            print("Opción inválida")

# PARTIDA CONTRA MÁQUINA
def partida_vs_maquina(estado):
    while not estado["terminada"]:
        if estado["turno"] == 0:
            print("----------------------------")
            print("Turno del Jugador")
            print("----------------------------")
            print("1 - Disparar")
            print("2 - Ver el cubo")
            print("3 - Salir")
            opcion = input("Opción: ")
            if opcion == "1":
                arma = input("Arma (T): ").upper()
                objetivo = input("Objetivo: ")
                try:
                    ejecutar_turno(estado,{"arma": arma,"objetivo": objetivo})
                    print("Disparo realizado.")
                except ErrorPartida as error:
                    print("Error:", error)
            elif opcion == "2":
                mostrar_cubo(estado["jugadores"][0])
            elif opcion == "3":
                break
            else:
                print("Opción inválida")
        else:
            print("----------------------------")
            print("Turno de la máquina")
            print("----------------------------")
            try:
                turno_maquina(estado)
                print("La máquina realizó su disparo")
            except ErrorPartida as error:
                print("Error:", error)
        if estado["terminada"]:
            if estado["ganador"] == 0:
                print("Ganaste.")
            else:
                print("Ganó la máquina")

# MENÚ PRINCIPAL
def menu_principal():

    while True:
        print("==============================")
        print("       OPERACION CUBO")
        print("==============================")
        print("1 - Partida uno contra uno")
        print("2 - Partida uno contra la maquina")
        print("3 - Partida maquina contra maquina")
        print("4 - Continuar una partida guardada")
        print("5 - Salir")
        opcion = input("Opción: ")

        if opcion == "1":
            estado = preparar_1v1()
            input("\nPresione ENTER para comenzar...")
            partida_1v1(estado)

        elif opcion == "2":
            estado = preparar_vs_maquina()
            input("\nPresione ENTER para comenzar...")
            partida_vs_maquina(estado)

        elif opcion == "3":
            print("Máquina contra máquina "
                "corresponde a una entrega posterior")
            
        elif opcion == "4":
            print("Continuar partida guardada "
                "corresponde a una entrega posterior")
            
        elif opcion == "5":
            print("Programa finalizado")
            break
        
        else:
            print("Opción inválida")