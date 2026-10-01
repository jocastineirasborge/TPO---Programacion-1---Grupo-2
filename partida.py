"""Módulo para la partida"""
import random
from tablero import (
    crear_cubo,
    dibujar_cubo,
    es_punto_valido,
    texto_a_punto,
    texto_a_tramo,
    leer_celda,
    escribir_celda,
    dibujar_cubo,
    NAVE_OCULTA,
    SIN_EXPLORAR,
    IMPACTO,
    HUNDIDO,
    AGUA_MARCADA
)
from flota import (
    ubicar_nave,
    CATALOGO_NAVES,
    ubicacion_automatica,
    hay_distancia_segura,
    obtener_puntos_tramo,
    validar_reglas_ubicacion,
    obtener_catalogo_naves
)
from radar import busqueda_lineal_nave
from armamento import obtener_celdas_afectadas, obtener_catalogo_armas
from registro import inicializar_registro, registrar_turno

# CONSTANTES
AGUA = "~"
NAVE = "N"
IMPACTO = "X"
HUNDIDO = "#"
TAMANO_CUBO = 8

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

def ubicar_nave(cubo, flota, letra, desde, hasta):
    n = len(cubo)

    if letra not in CATALOGO_NAVES:
        raise ErrorPartida("Nave inválida")
    
    if letra == "E":
        raise ErrorPartida("La estación orbital se ubica aparte")
    
    if not es_punto_valido(desde, n):
        raise ErrorPartida("Punto inicial inválido")
    
    if not es_punto_valido(cubo, desde):
        raise ErrorPartida("Punto final inválido")
    
    punto_1 = texto_a_punto(cubo, desde)
    punto_2 = texto_a_punto(cubo, hasta)
    celdas = obtener_puntos_tramo(punto_1, punto_2)

    if len(celdas) == 0:
        raise ErrorPartida("La nave debe estar en línea recta")
    
    if len(celdas) != CATALOGO_NAVES[letra]["celdas"]:
        raise ErrorPartida("La longitud de la nave es incorrecta")
    
    for z, x, y in celdas:
        if cubo[z][x][y] != AGUA:
            raise ErrorPartida("Hay una celda ocupada")
        
    if not validar_reglas_ubicacion(letra, celdas, n):
        raise ErrorPartida("La nave no cumple su restricción")
    
    if not validar_distancia(celdas, flota):
        raise ErrorPartida("Debe quedar al menos una celda libre entre naves")
    
    for z, x, y in celdas:
        cubo[z][x][y] = NAVE
    flota.append({"letra": letra,"celdas": celdas,"impactos": 0,"hundida": False})
    return True

def ubicar_estacion(cubo, flota, punto):
    n = len(cubo)
    if not es_punto_valido(punto, n):
        raise ErrorPartida("Punto inválido")
    z, x, y = texto_a_punto(punto)
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
                celda = (
                    z + dz,
                    x + dx,
                    y + dy)
                
                if cubo[celda[0]][celda[1]][celda[2]] != AGUA:
                    raise ErrorPartida("Hay una celda ocupada")
                celdas.append(celda)
                
    if not validar_distancia(celdas, flota):
        raise ErrorPartida("Debe quedar al menos una celda libre entre naves")
    for z2, x2, y2 in celdas:
        cubo[z2][x2][y2] = NAVE
    flota.append(
        {"letra": "E",
        "celdas": celdas,
        "impactos": 0,
        "hundida": False}
        )
    
    return True

# UBICACIÓN AUTOMÁTICA

def colocar_flota_automatica(jugador, n=8):
    """
    Delega la colocación aleatoria a flota.py y actualiza la flota del jugador.
    """
    jugador["flota"] = ubicacion_automatica(jugador["cubo"], n=n)

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




def ejecutar_turno(estado, jugada):
    """
    Objetivo: 
    Parámetros: 
    Devuelve:
    """
    if estado["terminada"]:
        raise ValueError("La partida ya terminó.")

    jugador_actual = estado["turno"]
    rival = 1 - jugador_actual

    cubo_rival = estado["jugadores"][rival]["cubo"]
    flota_rival = estado["jugadores"][rival]["flota"]
    n = estado["n"]

    arma = jugada.get("arma", "T")
    texto_objetivo = jugada.get("objetivo")

    punto_objetivo = texto_a_punto(texto_objetivo, cubo_rival)
    if punto_objetivo is None:
        raise ValueError("Coordenada de disparo inválido.")

    celdas_afectadas = obtener_celdas_afectadas(arma, punto_objetivo, n)

    for punto in celdas_afectadas:
        estado_actual = leer_celda(cubo_rival, punto)
        if estado_actual == NAVE_OCULTA:
            escribir_celda(cubo_rival, punto, IMPACTO)
            for nave in flota_rival:
                letra, puntos, impactos = nave
                if punto in puntos:
                    if punto not in impactos:
                        impactos.append(punto)
                    if len(impactos) >= len(puntos):
                        for p in puntos:
                            escribir_celda(cubo_rival, p, HUNDIDO)
                    break
        elif estado_actual == SIN_EXPLORAR:
            escribir_celda(cubo_rival, punto, AGUA_MARCADA)

    try:
        registrar_turno(estado, jugada, celdas_afectadas)
    except NameError:
        pass #Para la entrega 2

    ganador = hay_ganador(estado)
    if ganador is None:
        estado["turno"] = rival

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
      
# SUBMENÚ DE UBICACIÓN
def ubicacion_manual(jugador, n=8):
    """
    Submenú interactivo para que el usuario ubique sus naves por consola.
    """
    cubo = jugador["cubo"]
    flota = jugador["flota"]

    pendientes = ["F", "F", "D", "D", "S", "S", "C", "P", "E"]
    while len(pendientes) > 0:
        print(f"\nPendientes: {pendientes}")
        nave = input("Nave (F/D/S/C/P/E): ").strip().upper()

        if nave not in pendientes:
            print("Nave inválida o ya ubicada.")
            continue

        if nave == "E":
            punto = input("Esquina de la estación: ").strip

        else:
            tramo = input("Tramo de la estación orbital(ej. 2,2,2-3,3,3): ").strip()

        tramo = texto_a_tramo(punto, cubo)
        if tramo is None:
            print("Formato de coordenada o rango inválido.")
            continue

        desde, hasta = tramo
        try:
            ubicar_nave(cubo, flota, nave, desde, hasta, n)
            pendientes.remove(nave)
            print(f"Nave {nave} ubicada exitosamente.")
        except ValueError as ve:
            print(f"La nave no se puede ubicar ahi: {ve}")

def submenú_ubicacion(jugador, n=8):
    while True:
        print()
        print("1 - Ubicación manual")
        print("2 - Ubicación automática")
        opcion = input("Opción: ")

        if opcion == "1":
            ubicacion_manual(jugador, n)
            break

        elif opcion == "2":
            colocar_flota_automatica(jugador, n)
            print("Flota ubicada automáticamente.")
            break

        else:
            print("Opción inválida")

# PREPARACIÓN DE PARTIDAS

def preparar_1v1():
    estado = nueva_partida_1v1({"n": TAMANO_CUBO})

    print("\n--- Flota de Jugador 1 ---")
    submenú_ubicacion(estado["jugadores"][0])

    print("\n--- Flota de Jugador 2 ---")
    submenú_ubicacion(estado["jugadores"][1])

    return estado

def preparar_vs_maquina():
    estado = nueva_partida_vs_maquina({"n": TAMANO_CUBO},"normal")
    n = estado["n"]

    print("\n--- Flota del Jugador ---")
    submenú_ubicacion(estado["jugadores"][0])

    print("\n--- Flota de la máquina ---")
    colocar_flota_automatica(estado["jugadores"][1], n)
    print("Flota de la máquina ubicada automáticamente.")

    return estado

# PARTIDA 1 VS 1
def partida_1v1(estado, cubo):
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
            cubo_jugador = estado["jugadores"][jugador]["cubo"]
            print(dibujar_cubo(cubo_jugador, mostrar_naves=True))

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
                cubo_jugador = estado["jugadores"][0]["cubo"]
                print(dibujar_cubo(cubo_jugador, mostrar_naves=True))

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

menu_principal()