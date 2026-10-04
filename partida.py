"""Módulo para la partida"""
import random
import tablero
import flota
from radar import busqueda_lineal_nave
from armamento import obtener_celdas_afectadas, obtener_catalogo_armas
import registro

# EXCEPCIÓN PROPIA
class ErrorPartida(Exception):
    pass

TAMANO_CUBO = 8

# UBICACIÓN AUTOMÁTICA

def colocar_flota_automatica(jugador, n=8):
    """
    Delega la colocación aleatoria a flota.py y actualiza la flota del jugador.
    """
    jugador["flota"] = flota.ubicacion_automatica(jugador["cubo"], n=n)

# JUGADOR
def crear_jugador(n):
    return {"cubo": tablero.crear_cubo(n),"flota": [],"disparos": []}

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

    punto_objetivo = tablero.texto_a_punto(texto_objetivo, cubo_rival)
    if punto_objetivo is None:
        raise ValueError("Coordenada de disparo inválido.")

    celdas_afectadas = obtener_celdas_afectadas(arma, punto_objetivo, n)

    hubo_impacto = False
    for punto in celdas_afectadas:
        estado_actual = tablero.leer_celda(cubo_rival, punto)

        if estado_actual == tablero.NAVE_OCULTA:
            hubo_impacto = True
            tablero.escribir_celda(cubo_rival, punto, tablero.IMPACTO)
            
            for nave in flota_rival:
                letra, puntos, impactos = nave
                if punto in puntos:
                    if punto not in impactos:
                        impactos.append(punto)
                    if len(impactos) >= len(puntos):
                        for p in puntos:
                            tablero.escribir_celda(cubo_rival, p, tablero.HUNDIDO)
                    break
        elif estado_actual == tablero.SIN_EXPLORAR:
            tablero.escribir_celda(cubo_rival, punto, tablero.AGUA_MARCADA)

    #Guardar en el historial
    num_turno = len(registro.obtener_historial()) + 1
    jugador = f"Jugador {estado['turno'] + 1}"
    resultado = "Impacto" if hubo_impacto else "Agua"

    registro.registrar_turno(num_turno, jugador, arma, texto_objetivo, resultado)

    ganador = hay_ganador(estado)
    if ganador is None:
        estado["turno"] = rival

    return estado

def turno_maquina(estado):

    if estado["turno"] != 1:
        raise ErrorPartida("No es el turno de la máquina.")
    
    n = estado["n"]
    disparos_hechos = estado["jugadores"][1]["disparos"]
    disponibles = []

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                pt = (z, x, y)

                if pt not in disparos_hechos:
                    disponibles.append(pt)

    if not disponibles:
        raise ErrorPartida("No quedan celdas disponibles para disparar.")

    objetivo = random.choice(disponibles)
    disparos_hechos.append(objetivo)
    texto = tablero.punto_a_texto(objetivo)
    jugada = {"arma": "T", "objetivo": texto}

    return ejecutar_turno(estado, jugada)

def hay_ganador(estado):
    for jugador in range(2):
        rival = 1 - jugador
        flota_rival = estado["jugadores"][rival]["flota"]

        if len(flota_rival) == 0:
            continue

        todas_hundidas = True
        for nave in flota_rival:
            letra, puntos, impactos = nave
            if len(impactos) < len(puntos):
                todas_hundidas = False
                break
            
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
    flota_jugador = jugador["flota"]
    pendientes = ["F", "F", "D", "D", "S", "S", "C", "P", "E"]

    while len(pendientes) > 0:
        print(f"\nPendientes: {pendientes}")
        nave = input("Nave (F/D/S/C/P/E): ").strip().upper()

        if nave not in pendientes:
            print("Nave inválida o ya ubicada.")
            continue

        if nave == "E":
            punto = input("Esquina de la estación: ").strip()

        else:
            punto = input("Tramo de la estación orbital(ej. 2,2,2-3,3,3): ").strip()

        tramo = tablero.texto_a_tramo(punto, cubo)
        if tramo is None:
            print("Formato de coordenada o rango inválido.")
            continue

        desde, hasta = tramo
        try:
            flota.ubicar_nave(cubo, flota, nave, desde, hasta, n)
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
    registro.inicializar_registro()
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
def partida_1v1(estado):
    while not estado["terminada"]:
        jugador = estado["turno"]
        print("----------------------------")
        print("Turno de Jugador", jugador + 1)
        print("----------------------------")
        print("1 - Disparar")
        print("2 - Ver el cubo")
        print("3 - Salir")

        opcion = input("Opción: ").strip()

        if opcion == "1":
            arma = input("Arma (T): ").strip().upper()
            objetivo = input("Objetivo: ").strip()
            try:
                ejecutar_turno(estado, {"arma": arma, "objetivo": objetivo})
                print("Disparo realizado.")
                if estado["terminada"]:
                    print(f"\n¡Ganó el Jugador{estado["ganador"] + 1}!")
            except ErrorPartida as error:
                print("Error:", error)

        elif opcion == "2":
            cubo_jugador = estado["jugadores"][jugador]["cubo"]
            print(tablero.dibujar_cubo(cubo_jugador, mostrar_naves=True))

        elif opcion == "3":
            print("Saliendo de la partida...")
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
                print(tablero.dibujar_cubo(cubo_jugador, mostrar_naves=True))

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