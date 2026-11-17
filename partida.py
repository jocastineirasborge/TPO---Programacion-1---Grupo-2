
"""
Módulo partida.py

Integrador de Operación Cubo. Administra la creación de partidas,
los turnos, los modos de juego y la interfaz por consola.
"""

import random
import re
import tablero
import flota
import registro
from armamento import obtener_catalogo_armas, obtener_celdas_afectadas


class ErrorPartida(Exception):
    """Excepción base para errores controlados del módulo partida."""


class ErrorJugada(ErrorPartida):
    """Se utiliza cuando una jugada no es válida."""


class ErrorGuardado(ErrorPartida):
    """Se utiliza cuando no se puede guardar o recuperar una partida."""


TAMANO_CUBO = 8
DIFICULTADES = ("facil", "dificil")
PATRON_NOMBRE = r"^[A-Za-z0-9_-]{1,30}$"


def crear_jugador(n):
    """Crea el estado inicial de un jugador."""
    cubo = tablero.crear_cubo(n)

    if cubo is None:
        raise ErrorPartida("El tamaño del cubo no es válido.")

    return {
        "cubo": cubo,
        "flota": [],
        "disparos": [],
        "municion": _municion_inicial()
    }


def _municion_inicial():
    """Obtiene la munición inicial de cada arma."""
    catalogo = obtener_catalogo_armas()

    return {
        letra: datos.get("municion")
        for letra, datos in catalogo.items()
    }


def formatear_pendientes(pendientes):
    """Muestra las naves que todavía deben ubicarse."""
    partes = []

    for letra in ("F", "D", "S", "C", "P", "E"):
        cantidad = pendientes.count(letra)

        if cantidad:
            partes.append(f"{letra} x{cantidad}")

    return "   ".join(partes)


def colocar_flota_automatica(jugador, n=8, semilla=None):
    """Coloca automáticamente la flota de un jugador."""
    jugador["flota"] = flota.ubicacion_automatica(
        jugador["cubo"],
        semilla=semilla,
        n=n
    )

    if not jugador["flota"]:
        raise ErrorPartida("No se pudo ubicar la flota automáticamente.")

    return jugador


def nueva_partida_1v1(configuracion=None):
    """Crea una partida entre dos jugadores."""
    configuracion = configuracion or {}
    n = configuracion.get("n", TAMANO_CUBO)

    return {
        "tipo": "1v1",
        "n": n,
        "jugadores": [
            crear_jugador(n),
            crear_jugador(n)
        ],
        "turno": 0,
        "terminada": False,
        "ganador": None,
        "turnos": 0,
        "dificultades": None
    }


def nueva_partida_vs_maquina(configuracion=None, dificultad="facil"):
    """Crea una partida entre una persona y la máquina."""
    if dificultad not in DIFICULTADES:
        raise ValueError("La dificultad debe ser facil o dificil.")

    configuracion = configuracion or {}
    n = configuracion.get("n", TAMANO_CUBO)

    estado = nueva_partida_1v1({"n": n})
    estado["tipo"] = "vs_maquina"
    estado["dificultad"] = dificultad

    return estado


def nueva_partida_maquina_vs_maquina(
    configuracion=None,
    dificultades=("facil", "facil")
):
    """Crea una partida entre dos máquinas."""
    if len(dificultades) != 2:
        raise ValueError("Debe indicar dos dificultades.")

    if any(d not in DIFICULTADES for d in dificultades):
        raise ValueError("Dificultad inválida.")

    configuracion = configuracion or {}
    n = configuracion.get("n", TAMANO_CUBO)

    estado = nueva_partida_1v1({"n": n})
    estado["tipo"] = "maquina_vs_maquina"
    estado["dificultades"] = tuple(dificultades)

    return estado


def _buscar_nave(flota_jugador, punto):
    """Busca qué nave contiene una coordenada."""
    for nave in flota_jugador:
        if punto in nave[1]:
            return nave

    return None


def ejecutar_turno(estado, jugada):
    """Ejecuta una jugada y actualiza el estado de la partida."""
    if estado.get("terminada"):
        raise ErrorJugada("La partida ya terminó.")

    jugador_actual = estado["turno"]
    rival = 1 - jugador_actual

    jugador = estado["jugadores"][jugador_actual]
    objetivo_jugador = estado["jugadores"][rival]
    cubo_rival = objetivo_jugador["cubo"]

    arma = str(jugada.get("arma", "T")).strip().upper()

    if arma not in obtener_catalogo_armas():
        raise ErrorJugada("El arma seleccionada no existe.")

    punto = jugada.get("punto")

    if punto is None:
        punto = tablero.texto_a_punto(
            jugada.get("objetivo", ""),
            cubo_rival
        )

    if not tablero.es_punto_valido(cubo_rival, punto):
        raise ErrorJugada("La coordenada indicada no es válida.")

    municion = jugador.setdefault(
        "municion",
        _municion_inicial()
    )

    disponible = municion.get(arma)

    if disponible is not None and disponible <= 0:
        raise ErrorJugada("No queda munición para esa arma.")

    celdas = obtener_celdas_afectadas(
        arma,
        punto,
        estado["n"]
    )

    if not celdas:
        raise ErrorJugada(
            "El efecto de esta arma todavía no está disponible."
        )

    impacto = False
    resultados = []

    for celda in celdas:
        estado_celda = tablero.leer_celda(
            cubo_rival,
            celda
        )

        if estado_celda == tablero.NAVE_OCULTA:
            impacto = True

            tablero.escribir_celda(
                cubo_rival,
                celda,
                tablero.IMPACTO
            )

            nave = _buscar_nave(
                objetivo_jugador["flota"],
                celda
            )

            if nave is not None and celda not in nave[2]:
                nave[2].append(celda)

                if len(nave[2]) >= len(nave[1]):
                    for punto_nave in nave[1]:
                        tablero.escribir_celda(
                            cubo_rival,
                            punto_nave,
                            tablero.HUNDIDO
                        )

                    resultados.append(
                        f"Nave {nave[0]} hundida"
                    )

        elif estado_celda == tablero.SIN_EXPLORAR:
            tablero.escribir_celda(
                cubo_rival,
                celda,
                tablero.AGUA_MARCADA
            )

    if disponible is not None:
        municion[arma] = disponible - 1

    jugador["disparos"].append(punto)

    estado["turnos"] = estado.get("turnos", 0) + 1

    descripcion = "Impacto" if impacto else "Agua"

    if resultados:
        descripcion += ". " + ", ".join(resultados)

    try:
        registro.registrar_turno(
            estado["turnos"],
            f"Jugador {jugador_actual + 1}",
            arma,
            tablero.punto_a_texto(punto),
            descripcion
        )
    except (AttributeError, TypeError):
        pass

    ganador = hay_ganador(estado)

    if ganador is None:
        estado["turno"] = rival

    return estado


def _objetivos_disponibles(estado, jugador):
    """Obtiene las coordenadas que la máquina todavía no utilizó."""
    disparos = estado["jugadores"][jugador]["disparos"]
    n = estado["n"]

    disponibles = []

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                punto = (z, x, y)

                if punto not in disparos:
                    disponibles.append(punto)

    return disponibles


def _elegir_objetivo_dificil(estado, jugador, disponibles):
    """Busca disparar cerca de impactos anteriores."""
    rival = estado["jugadores"][1 - jugador]
    impactos = []

    for z in range(1, estado["n"] + 1):
        for x in range(1, estado["n"] + 1):
            for y in range(1, estado["n"] + 1):
                punto = (z, x, y)

                if tablero.leer_celda(
                    rival["cubo"],
                    punto
                ) == tablero.IMPACTO:
                    impactos.append(punto)

    candidatos = []

    for impacto in impactos:
        z, x, y = impacto

        vecinos = (
            (z - 1, x, y),
            (z + 1, x, y),
            (z, x - 1, y),
            (z, x + 1, y),
            (z, x, y - 1),
            (z, x, y + 1)
        )

        for vecino in vecinos:
            if vecino in disponibles and vecino not in candidatos:
                candidatos.append(vecino)

    if candidatos:
        return random.choice(candidatos)

    return random.choice(disponibles)


def turno_maquina(estado):
    """Ejecuta el turno de una máquina."""
    jugador = estado["turno"]

    if estado["tipo"] == "1v1":
        raise ErrorPartida(
            "Esta partida no tiene jugadores controlados por la máquina."
        )

    if estado["tipo"] == "vs_maquina" and jugador == 0:
        raise ErrorPartida("Es el turno del jugador.")

    dificultad = estado.get("dificultad", "facil")

    if estado["tipo"] == "maquina_vs_maquina":
        dificultad = estado["dificultades"][jugador]

    disponibles = _objetivos_disponibles(
        estado,
        jugador
    )

    if not disponibles:
        raise ErrorPartida(
            "No quedan coordenadas disponibles para disparar."
        )

    if dificultad == "dificil":
        objetivo = _elegir_objetivo_dificil(
            estado,
            jugador,
            disponibles
        )
    else:
        objetivo = random.choice(disponibles)

    return ejecutar_turno(
        estado,
        {
            "arma": "T",
            "punto": objetivo
        }
    )


def hay_ganador(estado):
    """Comprueba si uno de los jugadores hundió toda la flota rival."""
    for jugador in range(2):
        flota_rival = estado["jugadores"][1 - jugador]["flota"]

        if flota_rival and all(
            len(nave[2]) >= len(nave[1])
            for nave in flota_rival
        ):
            estado["terminada"] = True
            estado["ganador"] = jugador

            return jugador

    return None


def ubicacion_manual(jugador, n=8):
    """Permite ubicar manualmente las naves."""
    pendientes = [
        "F", "F", "F",
        "D", "D",
        "S", "S",
        "C", "P", "E"
    ]

    while pendientes:
        print("\nPendientes:", formatear_pendientes(pendientes))

        nave = input("Nave (F/D/S/C/P/E): ").strip().upper()

        if nave not in pendientes:
            print("Nave inválida o ya ubicada.")
            continue

        texto = input("Tramo (z,x,y-z,x,y): ").strip()

        tramo = tablero.texto_a_tramo(
            texto,
            jugador["cubo"]
        )

        if tramo is None:
            print("Formato o coordenada inválida.")
            continue

        try:
            flota.ubicar_nave(
                jugador["cubo"],
                jugador["flota"],
                nave,
                tramo[0],
                tramo[1],
                n
            )

            pendientes.remove(nave)
            print("Nave ubicada.")

        except ValueError as error:
            print("No se pudo ubicar:", error)


def submenu_ubicacion(jugador, n=8):
    """Permite elegir ubicación manual o automática."""
    while True:
        print("1 - Ubicación manual")
        print("2 - Ubicación automática")

        opcion = input("Opción: ").strip()

        if opcion == "1":
            ubicacion_manual(jugador, n)
            return

        elif opcion == "2":
            colocar_flota_automatica(jugador, n)
            print("Flota ubicada automáticamente.")
            return

        else:
            print("Opción inválida.")


def _pedir_dificultad(etiqueta="Máquina"):
    """Solicita el nivel de dificultad."""
    while True:
        print(
            f"Dificultad de {etiqueta}: "
            "1 - Fácil / 2 - Difícil"
        )

        opcion = input("Opción: ").strip()

        if opcion == "1":
            return "facil"

        elif opcion == "2":
            return "dificil"

        else:
            print("Opción inválida.")


def _preparar_partida(tipo):
    """Prepara las flotas y el registro de la partida."""
    try:
        registro.inicializar_registro()
    except AttributeError:
        pass

    if tipo == "1v1":
        estado = nueva_partida_1v1({
            "n": TAMANO_CUBO
        })

        for indice in range(2):
            print(f"\n--- Flota del Jugador {indice + 1} ---")

            submenu_ubicacion(
                estado["jugadores"][indice]
            )

    elif tipo == "vs_maquina":
        dificultad = _pedir_dificultad()

        estado = nueva_partida_vs_maquina(
            {"n": TAMANO_CUBO},
            dificultad
        )

        print("\n--- Tu flota ---")

        submenu_ubicacion(
            estado["jugadores"][0]
        )

        colocar_flota_automatica(
            estado["jugadores"][1],
            estado["n"],
            semilla=2
        )

    else:
        dificultades = (
            _pedir_dificultad("Máquina 1"),
            _pedir_dificultad("Máquina 2")
        )

        estado = nueva_partida_maquina_vs_maquina(
            {"n": TAMANO_CUBO},
            dificultades
        )

        colocar_flota_automatica(
            estado["jugadores"][0],
            estado["n"],
            semilla=1
        )

        colocar_flota_automatica(
            estado["jugadores"][1],
            estado["n"],
            semilla=2
        )

    return estado


def _guardar_partida(estado):
    """Guarda la partida si registro.py tiene implementada esa función."""
    if not hasattr(registro, "guardar_partida"):
        print(
            "El módulo registro.py todavía no implementa "
            "guardar_partida()."
        )
        return False

    while True:
        nombre = input(
            "Nombre de la partida "
            "(letras, números, _ o -, máximo 30): "
        ).strip()

        if re.fullmatch(PATRON_NOMBRE, nombre):
            break

        print("Nombre inválido.")

    try:
        registro.guardar_partida(estado, nombre)

        print("Partida guardada.")
        return True

    except Exception as error:
        print("No se pudo guardar la partida:", error)
        return False


def _continuar_partida():
    """Carga una partida guardada si registro.py tiene las funciones necesarias."""
    requeridas = (
        "listar_partidas",
        "cargar_partida"
    )

    if not all(
        hasattr(registro, nombre)
        for nombre in requeridas
    ):
        print(
            "El módulo registro.py todavía no implementa "
            "listado y carga JSON."
        )
        return None

    try:
        partidas = registro.listar_partidas()

        if not partidas:
            print("No hay partidas guardadas.")
            return None

        for indice, nombre in enumerate(partidas, 1):
            print(f"{indice} - {nombre}")

        seleccion = input(
            "Partida a continuar: "
        ).strip()

        if (
            not seleccion.isdigit()
            or not 1 <= int(seleccion) <= len(partidas)
        ):
            print("Selección inválida.")
            return None

        return registro.cargar_partida(
            partidas[int(seleccion) - 1]
        )

    except Exception as error:
        print("No se pudo recuperar la partida:", error)
        return None


def _turno_humano(estado):
    """Gestiona el turno de un jugador humano."""
    jugador = estado["turno"]

    while True:
        print(f"\n--- Turno del Jugador {jugador + 1} ---")
        print("1 - Disparar")
        print("2 - Ver mi cubo")
        print("3 - Guardar y salir")

        opcion = input("Opción: ").strip()

        if opcion == "2":
            print(
                tablero.dibujar_cubo(
                    estado["jugadores"][jugador]["cubo"],
                    mostrar_naves=True
                )
            )

            continue

        elif opcion == "3":
            _guardar_partida(estado)
            return False

        elif opcion != "1":
            print("Opción inválida.")
            continue

        catalogo = obtener_catalogo_armas()

        arma = input(
            "Arma (T/R/C/S/L/O/G): "
        ).strip().upper()

        if arma not in catalogo:
            print("Arma inválida.")
            continue

        objetivo = input(
            "Objetivo (z,x,y): "
        ).strip()

        try:
            ejecutar_turno(
                estado,
                {
                    "arma": arma,
                    "objetivo": objetivo
                }
            )

            print("Jugada realizada.")
            return True

        except ErrorPartida as error:
            print("No se pudo realizar la jugada:", error)

        except (ValueError, TypeError) as error:
            print("Entrada inválida:", error)


def partida_1v1(estado):
    """Ejecuta una partida entre dos personas."""
    while not estado["terminada"]:
        if not _turno_humano(estado):
            break

    _mostrar_ganador(estado)


def partida_vs_maquina(estado):
    """Ejecuta una partida entre una persona y la máquina."""
    while not estado["terminada"]:

        if estado["turno"] == 0:
            if not _turno_humano(estado):
                break

        else:
            turno_maquina(estado)
            print("La máquina realizó su disparo.")

    _mostrar_ganador(estado)


def partida_maquina_vs_maquina(estado):
    """Ejecuta una partida entre dos máquinas."""
    while not estado["terminada"]:
        jugador = estado["turno"]

        print(
            f"Turno de Máquina {jugador + 1} "
            f"({estado['dificultades'][jugador]})."
        )

        turno_maquina(estado)

        if hasattr(registro, "obtener_ultimo_turno"):
            print("Disparo:", registro.obtener_ultimo_turno())
        else:
            print("Disparo realizado.")

    _mostrar_ganador(estado)


def _mostrar_ganador(estado):
    """Muestra el ganador de la partida."""
    if estado.get("terminada"):
        print(
            f"\n¡Ganó el Jugador {estado['ganador'] + 1}!"
        )


def menu_principal():
    """Muestra el menú principal del juego."""
    while True:
        print("\n==============================")
        print("       OPERACIÓN CUBO")
        print("==============================")
        print("1 - Partida uno contra uno")
        print("2 - Partida uno contra la máquina")
        print("3 - Partida máquina contra máquina")
        print("4 - Continuar una partida guardada")
        print("5 - Salir")

        opcion = input("Opción: ").strip()

        try:
            if opcion == "1":
                estado = _preparar_partida("1v1")
                partida_1v1(estado)

            elif opcion == "2":
                estado = _preparar_partida("vs_maquina")
                partida_vs_maquina(estado)

            elif opcion == "3":
                estado = _preparar_partida("maquina_vs_maquina")
                partida_maquina_vs_maquina(estado)

            elif opcion == "4":
                estado = _continuar_partida()

                if estado is not None:
                    if estado["tipo"] == "1v1":
                        partida_1v1(estado)

                    elif estado["tipo"] == "vs_maquina":
                        partida_vs_maquina(estado)

                    else:
                        partida_maquina_vs_maquina(estado)

            elif opcion == "5":
                print("Programa finalizado.")
                break

            else:
                print("Opción inválida")
        except ErrorPartida as error:
            print(f"Error en la partida : {error}")
        
#Ejecución de programa principal
menu_principal()
