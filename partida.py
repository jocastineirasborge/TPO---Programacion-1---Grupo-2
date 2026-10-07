"""
Módulo partida.py

Integrador principal del juego 'Operación Cubo'.
Maneja la creación del estado de las partidas, el bucle de
turnos, la interfaz de consola, la validación de entrada
y los menús.
"""
import random
import tablero
import flota
from radar import busqueda_lineal_nave
from armamento import obtener_celdas_afectadas, obtener_catalogo_armas
import registro

# --------------------------------------------
# Excepciones y constantes
# --------------------------------------------

class ErrorPartida(Exception):
    pass

TAMANO_CUBO = 8

# --------------------------------------------
# Funciones auxiliares
# --------------------------------------------

def crear_jugador(n):
    """
    Objetivo: Crear y estructurar diccionario con el estado inicial del jugador.
    Parámetros:
        n(int): Tamaño de la dimensión del cubo(N x N x N).
    Devuelve:
        dict: Diccionario con la estructura básica del jugador.
    """
    return {"cubo": tablero.crear_cubo(n),"flota": [],"disparos": []}


def formatear_pendientes(pendientes):
    """
    Objetivo: Convertir la lista de naves pendientes de ubicación a una cadena
    de texto formateada de este tipo.
    (ej. 'F x3 D x2 S x2 C x1 P x1 E x1')
    Parámetros:
        - pendientes(list): Lista con las letras identificadoras de cada nave disponible.
    Devuelve:
        str: Cadena de texto formada con los tipos de naves y cantidades disponibles.
    """
    orden_naves = ["F", "D", "S", "C", "P", "E"]
    partes = []
    for nave in orden_naves:
        cant = pendientes.count(nave)
        if cant > 0:
            partes.append(f"{nave} x{cant}")

    return "   ".join(partes)


def colocar_flota_automatica(jugador, n=8):
    """
    Objetivo: Delega la colocación aleatoria a flota.py y actualiza la flota del jugador.
    Parámetros:
        - jugador(dict): Diccionario del jugador con la clave 'cubo'.
        - n(int): Tamaño de la dimensión del cubo(valor por defecto 8).
    Devuelve:
        None: Modifica de forma directa el diccionario.
    """
    jugador["flota"] = flota.ubicacion_automatica(jugador["cubo"], n=n)

# ---------------------------------------------------
# Funciones públicas obligatorias - Inicialización
# ---------------------------------------------------

def nueva_partida_1v1(configuracion):
    """
    Objetivo: Inicializar la estructura de datos que representa una nueva partida en modo 1v1.
    Parámetros:
        - configuración(dict): Diccionario de configuración que contiene la clave 'n'.
    Devuelve:
        dict:  Estado inicial de la partida.
    """
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
    """
    Objetivo: Inicializar la estructura de datos que representa una nueva partida en modo 'vs máquina'.
    Parámetros:
        - configuración(dict): Diccionario de configuración que contiene la clave 'n'.
        - dificultad(str): Nivel de dificultad asignado al comportamiento de la computadora.
    Devuelve:
        dict: Estado inicial de la partida en modo 'vs máquina'.
    """
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

# ----------------------------------------------------
# Funciones públicas obligatorias - Lógica de juego
# ----------------------------------------------------

def ejecutar_turno(estado, jugada):
    """
    Objetivo: Procesa la jugada de un turno, calculando impacto del arma sobre el cubo,
    actualizando estado de las naves, y registrando el evento en el historial.
    Parámetros:
        - estado(dict): Diccionario con el estado de la partida.
        - jugada(dict): Diccionario con las claves 'arma' y 'objetivo'.
    Devuelve:
        dict: Diccionario del estado de la partida actualizado.
    """
    if estado["terminada"]:
        raise ValueError("La partida ya terminó.")

    jugador_actual = estado["turno"]
    rival = 1 - jugador_actual

    cubo_rival = estado["jugadores"][rival]["cubo"]
    flota_rival = estado["jugadores"][rival]["flota"]
    n = estado["n"]

    arma = jugada.get("arma", "T")
    if not arma:
        arma = "T"
    
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
    """
    Objetivo: Seleccionar una coordenada de disparo de manera aleatoria.
    Parámetros:
        - estado(dict): Diccionario con el estado de la partida.
    Devuelve:
        function: Devuelve la función 'ejecutar_turno' con los parámetros de estado y la jugada
        actualizados para realizar la jugada.
    """
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
    """
    Objetivo: Verificar si alguno de los jugadores logró hundir la totalidad
    de la flota rival.
    Parámetros:
        - estado(dict): Diccionario con el estado de la partida.
    Devuelve:
        int o None: El número del jugador ganador si la partida terminó, 
        o None si la flota del oponente aún conserva celdas.
    """
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
      
# ----------------------------------
# Submenús y preparación de flota
# ----------------------------------

def ubicacion_manual(jugador, n=8):
    """
    Objetivo: Gestiona la interfaz por consola para que el jugador ubique manualmente
    todas las naves de la flota.
    Parámetros:
        - jugador(dict): Diccionario del jugador con la matriz 'cubo' y
        la lista 'flota'.
        - n(int): Dimensión del arista del cubo(por defecto 8).
    Devuelve:
        None: Modifica de forma directa las celdas del cubo y asigna
        las naves del jugador.
    """
    cubo = jugador["cubo"]
    flota_jugador = jugador["flota"]
    pendientes = ["F", "F", "F", "D", "D", "S", "S", "C", "P", "E"]

    while len(pendientes) > 0:
        texto_pendientes = formatear_pendientes(pendientes)
        print(f"\nPendientes: {texto_pendientes}")
        nave = input("Nave (F/D/S/C/P/E): ").strip().upper()

        if nave not in pendientes:
            print("Nave inválida o ya ubicada.")
            continue

        if nave == "E":
            texto = input("Tramo de la estación orbital: ").strip()

        else:
            texto = input("Tramo Desde-Hasta: ").strip()

        tramo = tablero.texto_a_tramo(texto, cubo)
        if tramo is None:
            print("Formato de coordenada o rango inválido.")
            continue

        desde, hasta = tramo
        try:
            flota.ubicar_nave(cubo, flota_jugador, nave, desde, hasta, n)
            pendientes.remove(nave)
            print(f"Nave {nave} ubicada exitosamente.")
        except ValueError as ve:
            print(f"La nave no se puede ubicar ahi: {ve}")


def submenú_ubicacion(jugador, n=8):
    """
    Objetivo: Desplegar un menú interactivo correspondiente a
    la selección de ubicación manual o automática de la flota del jugador.
    Parámetros:
        - jugador(dict): Diccionario que representa la estructura de datos
        del jugador.
        - n(int): Tamaño del arista del cubo(por defecto 8).
    Devuelve:
        None: Invoca a las funciones de ubicación(manual o automática) que
        modifican de forma directa el cubo y la flota del jugador.
    """
    while True:
        print("\n1 - Ubicación manual")
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


def preparar_1v1():
    """
    Objetivo: Inicializa el historial de registro, crea el estado base
    de una partida en modo 1v1 y coordina la fase previa de ubicación de nave
    para ambos jugadores.
    Parámetros:
        Ninguno.
    Devuelve:
        dict: Diccionario con el estado de una partida 1v1 configurada y
        lista para comenzar.
    """
    registro.inicializar_registro()
    estado = nueva_partida_1v1({"n": TAMANO_CUBO})

    print("\n--- Flota de Jugador 1 ---")
    submenú_ubicacion(estado["jugadores"][0])

    print("\n--- Flota de Jugador 2 ---")
    submenú_ubicacion(estado["jugadores"][1])

    return estado


def preparar_vs_maquina():
    """
    Objetivo: Inicializa el registro, crea el estado base de una
    partida en modo 'vs máquina' y coordinar la fase previa de ubicación
    de naves(configurable para el jugador humano y automático para la máquina).
    Parámetros:
        Ninguno.
    Devuelve:
        dict: Diccionario con el estado de una partida 'vs máquina' configurada
        y lista para comenzar.
    """
    registro.inicializar_registro()
    estado = nueva_partida_vs_maquina({"n": TAMANO_CUBO},"normal")
    n = estado["n"]

    print("\n--- Flota del Jugador ---")
    submenú_ubicacion(estado["jugadores"][0], n)

    print("\n--- Flota de la máquina ---")
    colocar_flota_automatica(estado["jugadores"][1], n)
    print("Flota de la máquina ubicada automáticamente.")

    return estado

# -------------------------------------
# Bucle principal de partidas y menú
# -------------------------------------

def partida_1v1(estado):
    """
    Objetivo: Gestiona el bucle principal de juego en modo 1v1.
    Parámetros:
        - estado(dict): Diccionario con el estado de la partida.
    Devuelve:
        None: Se ejecuta de manera interactiva por consola hasta
        que se determine un ganador o el usuario decida salir al
        menú principal.
    """
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
            catalogo = obtener_catalogo_armas()
            while True:
                arma = input("Arma (T): ").strip().upper()
                if not arma:
                    arma = "T"
                if arma in catalogo:
                    break
                print("Arma no válida.")

            cubo_rival = estado["jugadores"][1 - jugador]["cubo"]
            while True:
                objetivo = input("Objetivo: ").strip()
                punto = tablero.texto_a_punto(objetivo, cubo_rival)
                if punto is not None:
                    break
                print("Coordenada inválida, inténtelo de nuevo.")

            try:
                ejecutar_turno(estado, {"arma": arma, "objetivo": objetivo})
                print("Disparo realizado.")
                if estado["terminada"]:
                    print(f"\n¡Ganó el Jugador{estado['ganador'] + 1}!")
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


def partida_vs_maquina(estado):
    """
    Objetivo: Gestiona el bucle principal de juego en modo
    'vs máquina'.
    Parámetros:
        - estado(dict): Diccionario con el estado de la partida.
    Devuelve:
        None: Se ejecuta de manera interactiva por consola hasta
        que se determine un ganador o el usuario decida salir
        al menú principal.
    """
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
                catalogo = obtener_catalogo_armas()
                while True:
                    arma = input("Arma (T): ").strip().upper()
                    if not arma:
                        arma = "T"
                    if arma in catalogo:
                        break
                    print("Arma no válida.")

                cubo_rival = estado["jugadores"][1]["cubo"]
                while True:
                    objetivo = input("Objetivo: ").strip()
                    punto = tablero.texto_a_punto(objetivo, cubo_rival)
                    if punto is not None:
                        break
                    print("Coordenada inválida, inténtelo de nuevo.")

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


def menu_principal():
    """
    Objetivo: Desplega el menú principal del juego 'Operación Cubo'
    y dirige el flujo de ejecución del programa según la opción
    seleccionada por el jugador.
    Parámetros:
        Ninguno.
    Devuelve:
        None: Ejecuta un bucle interactivo por consola hasta que el
        usuario decida salir.
    """
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


#Ejecución de programa principal
<<<<<<< HEAD
menu_principal()
=======
menu_principal()
>>>>>>> 067b722159b9298148bdde26880b456d77a6aa9a
