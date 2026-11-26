
"""
Módulo partida.py

Integrador principal del juego 'Operación Cubo'. Maneja la creación del estado de las partidas, el bucle de turnos,
la interfaz de consola, la validación de entrada, modos de juego (1v1, vs Máquina, Máquina vs Máquina) y menús.
"""

import random
import re
import tablero
import flota
import registro
import armamento
import radar


class ErrorPartida(Exception):
    """Excepción base para errores controlados del módulo partida."""
    pass


class ErrorJugada(ErrorPartida):
    """Se utiliza cuando una jugada no es válida."""
    pass


class ErrorGuardado(ErrorPartida):
    """Se utiliza cuando no se puede guardar o recuperar una partida."""
    pass


DIFICULTADES = ("facil", "dificil")
PATRON_NOMBRE = r"^[A-Za-z0-9_-]{1,30}$"

# -----------------------------------------
# Funciones auxiliares e Inicialización
# -----------------------------------------

def crear_jugador(n):
    """
    Objetivo: Crear y estructurar diccionario con el estado inicial del jugador.
    Parámetros:
        n(int): Tamaño de la dimensión del cubo(N x N x N).
    Devuelve:
        dict: Diccionario con la estructura básica del jugador.
    """
    cubo = tablero.crear_cubo(n)
    if cubo is None:
        raise ErrorPartida("El tamaño del cubo no es válido.")

    return {
        "cubo": cubo,
        "flota": [],
        "disparos": [],
        "arsenal": municion_inicial()
    }


def municion_inicial():
    """ 
    Objetivo: Generar y obtener el diccionario con la cantidad inicial de munición asignada
    a cada arma a partir del catálogo disponible.
    Devuelve: 
        dict: Diccionario {letra_arma: cantidad} con el stock inicial 
        de cada arma (donde None representa munición ilimitada). 
    """
    catalogo = armamento.obtener_catalogo_armas()

    return {letra: datos.get("municion") for letra, datos in catalogo.items()}


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
    partes = []

    for nave in ("F", "D", "S", "C", "P", "E"):
        cantidad = pendientes.count(nave)

        if cantidad > 0:
            partes.append(f"{nave} x{cantidad}")

    return "   ".join(partes)


def colocar_flota_automatica(jugador, n=tablero.N_POR_DEFECTO, semilla=None):
    """
    Objetivo: Delega la colocación aleatoria a flota.py y actualiza la flota del jugador.
    Parámetros:
        - jugador(dict): Información del jugador actual.
        - n(int): Tamaño de la dimensión del cubo(valor por defecto 8).
    Devuelve:
        None: Modifica de forma directa el diccionario.
    """
    jugador["flota"] = flota.ubicacion_automatica(jugador["cubo"], semilla=semilla, n=n)
    if not jugador["flota"]:
        raise ErrorPartida("No se pudo ubicar la flota automáticamente.")

    return jugador


def pedir_tamanio_cubo():
    """
    Objetivo: Solicita al usuario el tamaño del arista del cubo (entre 5 y 20).
    Devuelve:
        int: Tamaño N configurado.
    """
    while True:
        entrada = input(f"Ingrese el tamaño del cubo N (entre 5 y 20, Enter para {tablero.N_POR_DEFECTO} por defecto): ").strip()

        if entrada == "":
            return tablero.N_POR_DEFECTO
        
        if entrada.isdigit():
            n = int(entrada)

        if 5 <= n <= 20:
            return n
        
        print("Tamaño inválido, debe ingresar un entero entre 5 y 20.")



def solicitar_jugada(jugador_dict, cubo_rival, n):
    """
    Objetivo: Solicita e interactúa por consola con el jugador para obtener su jugada.
    Parámetros:
        - jugador_dict(dict): Información del jugador actual.
        - cubo_rival(list): Matriz 3D del rival.
        - n(int): Tamaño del cubo.
    Devuelve:
        dict: Diccionario con la jugada seleccionada.
    """
    arsenal = jugador_dict.get("arsenal", {})

    texto_armas = []
    for letra, cant in arsenal.items():
        cant_str = "Infinito" if cant is None else str(cant)
        texto_armas.append(f"{letra} ({cant_str})")
    print("\nArmas disponibles: ", " | ".join(texto_armas))

    while True:
        arma = input("Seleccione arma (T / R / C / S / L / O / G): ").strip().upper()
        if arma not in arsenal:
            print("Arma inválida. Ingrese una de las opciones disponibles.")
            continue
        
        cant = arsenal[arma]
        if cant is not None and cant <= 0:
            print(f"Munición insuficiente para {arma}. Elija otra.")
            continue

        break

    if arma == "S":
        while True:
            eje = input("Eje para el Sonar (z/x/y): ").strip().lower()
            if eje in ("z", "x", "y"):
                break
            print("Eje inválido. Debe ser 'z', 'x' o 'y'.")

        while True:
            try:
                valor = int(input(f"Valor del plano (1 a {n}): ").strip())
                if 1 <= valor <= n:
                    break
                print(f"El valor debe estar entre 1 y {n}.")
            except ValueError:
                print("Debe ingresar un número entero.")

        return {
            "arma": "S",
            "eje": eje,
            "valor": valor
        }

    elif arma == "L":
        while True:
            objetivo = input("Coordenada de origen (z, x, y): ").strip()
            if tablero.texto_a_punto(objetivo, cubo_rival) is not None:
                break
            print("Coordenada inválida, inténtelo de nuevo.")

        while True:
            eje = input("Eje de barrido (x/y): ").strip().lower()
            if eje in ("x", "y"):
                break
            print("Eje inválido. Para el láser debe elegir 'x' o 'y'.")

        return {
            "arma": "L",
            "objetivo": objetivo,
            "eje": eje
        }

    else:
        while True:
            objetivo = input("Objetivo (z, x, y): ").strip()
            if tablero.texto_a_punto(objetivo, cubo_rival) is not None:
                break
            print("Coordenada inválida, inténtelo de nuevo.")

        return {
            "arma": arma,
            "objetivo": objetivo,
        }


# -------------------------------------------
# Creación e inicialización de Partidas
# -------------------------------------------

def nueva_partida_1v1(configuracion=None):
    """
    Objetivo: Inicializar la estructura de datos que representa una nueva partida en modo 1v1.
    Parámetros:
        - configuración(dict): Diccionario de configuración que contiene la clave 'n'.
    Devuelve:
        dict: Estado inicial de la partida en modo 1v1.
    """
    configuracion = configuracion or {}
    n = configuracion.get("n", tablero.N_POR_DEFECTO)

    return {
        "tipo": "1v1",
        "n": n,
        "jugadores": [crear_jugador(n), crear_jugador(n)],
        "turno": 0,
        "terminada": False,
        "ganador": None,
        "turnos": 0,
    }


def nueva_partida_vs_maquina(configuracion=None, dificultad="facil"):
    """
    Objetivo: Inicializar la estructura de datos que representa una nueva partida en modo 'vs máquina'.
    Parámetros:
        - configuración(dict): Diccionario de configuración que contiene la clave 'n'.
        - dificultad(str): Nivel de dificultad asignado al comportamiento de la computadora.
    Devuelve:
        dict: Estado inicial de la partida en modo 'vs máquina'.
    """
    if dificultad not in DIFICULTADES:
        raise ValueError("La dificultad debe ser facil o dificil.")

    configuracion = configuracion or {}
    n = configuracion.get("n", tablero.N_POR_DEFECTO)

    estado = nueva_partida_1v1({"n": n})
    estado["tipo"] = "vs_maquina"
    estado["dificultad"] = dificultad

    return estado


def nueva_partida_maquina_vs_maquina(configuracion=None, dificultades=("facil", "facil")):
    """
    Objetivo: Inicializa la estructura de datos que representa una nueva partida en
    modo 'máquina vs máquina'.
    Parámetros:
        - configuracion(dict): Diccionario de configuración que contiene el tamaño del cubo n. Si no
        se especifica, utiliza el valor por defecto.
        - dificultades(tuple): Tupla de 2 cadenas que establece el nivel de inteligencia de cada
        máquina. Por defecto se usa 'facil' dos veces.
    Devuelve:
        dict: Estado inicial de la partida en modo 'máquina vs máquina'.
    """
    if len(dificultades) != 2 or any(d not in DIFICULTADES for d in dificultades):
        raise ValueError("Debe indicar dos dificultades válidas ('facil' o 'dificil').")

    configuracion = configuracion or {}
    n = configuracion.get("n", tablero.N_POR_DEFECTO)

    estado = nueva_partida_1v1({"n": n})
    estado["tipo"] = "maquina_vs_maquina"
    estado["dificultades"] = tuple(dificultades)

    return estado

# ----------------------------------------------------
# Lógica principal de juego y ejecución de turnos
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

    jugador_dict = estado["jugadores"][jugador_actual]
    cubo_rival = estado["jugadores"][rival]["cubo"]
    flota_rival = estado["jugadores"][rival]["flota"]
    n = estado["n"]

    # ---------------------------------------------------
    # Verificamos si el arma coincide con el catálogo
    # ---------------------------------------------------
    arma = jugada.get("arma", "").strip().upper()
    arsenal = jugador_dict.get("arsenal", {})

    if arma not in armamento.obtener_catalogo_armas():
        raise ErrorPartida(f"El arma {arma} no es válida.")

    # -----------------------------
    # Descontamos la munición
    # -----------------------------
    if not armamento.descontar_municion(arsenal, arma):
        raise ErrorPartida(f"No queda munición disponible para {arma}.")

    # ------------------------------------
    # Procesamos según el tipo de arma
    # ------------------------------------
    hubo_impacto = False
    texto_registro_objetivo = ""
    naves_hundidas_nombres = []

    # Si el arma es el Sonar
    if arma == "S":
        eje = jugada.get("eje", "z").lower()
        try:
            valor = int(jugada.get("valor", 1))
        except (ValueError, TypeError):
            raise ErrorPartida("El valor del plano debe ser un número entero.")

        texto_registro_objetivo = f"{eje}={valor}"

        contactos, celdas_plano = radar.sonar_por_planos(cubo_rival, eje, valor)

        for punto in celdas_plano:
            if tablero.leer_celda(cubo_rival, punto) == tablero.NAVE_OCULTA:
                tablero.escribir_celda(cubo_rival, punto, tablero.DETECTADO)
            estado_celda = tablero.leer_celda(cubo_rival, punto)

        contactos_str = "contacto detectado" if contactos == 1 else "contactos detectados"

        print(f"\n[RESULTADO SONAR] Escaneo en plano {eje}={valor}: {contactos} {contactos_str}")
        resultado_str = f"{contactos} contactos"

    #Armas ofensivas
    else:
        if arma == "L":
            eje_laser = jugada.get("eje", "x").lower()
            texto_objetivo = jugada.get("objetivo")
            punto_origen = tablero.texto_a_punto(texto_objetivo, cubo_rival)

            if punto_origen is None or eje_laser not in ("x", "y"):
                raise ErrorPartida("Los parámetros para el barrido láser son inválidos.")

            texto_registro_objetivo = f"{texto_objetivo} (eje {eje_laser})"
            celdas_afectadas = armamento.obtener_celdas_afectadas("L", (punto_origen, eje_laser), n, cubo_rival, flota_rival)

        #Torpedo, Racimo y Carga de profundidad
        else:
            if "punto" in jugada:
                punto_objetivo = jugada["punto"]
            else:
                texto_objetivo = jugada.get("objetivo")
                punto_objetivo = tablero.texto_a_punto(texto_objetivo, cubo_rival)
            

            if punto_objetivo is None or not tablero.es_punto_valido(cubo_rival, punto_objetivo):
                raise ErrorPartida("Coordenada de disparo inválida.")

            texto_registro_objetivo = tablero.punto_a_texto(punto_objetivo)
            celdas_afectadas = armamento.obtener_celdas_afectadas(arma, punto_objetivo, n, cubo_rival, flota_rival)

        if not celdas_afectadas:
            raise ErrorJugada("El disparo no afectó celdas válidas.")
        
        #Impactar celdas afectadas
        for punto in celdas_afectadas:
            estado_actual = tablero.leer_celda(cubo_rival, punto)

            if estado_actual in (tablero.NAVE_OCULTA, tablero.DETECTADO, tablero.IMPACTO):
                impacto_valido, letra, estado_impacto = flota.registrar_impacto(flota_rival, punto, arma)

                if estado_impacto == "inmune":
                    continue

                if impacto_valido:
                    hubo_impacto = True
                    tablero.escribir_celda(cubo_rival, punto, tablero.IMPACTO)

                if estado_impacto == "hundida":
                    for nave in flota_rival:
                        if nave[0] == letra and punto in nave[1]:
                            for p in nave[1]:
                                tablero.escribir_celda(cubo_rival, p, tablero.HUNDIDO)
                            break

                    nombre_nave = flota.CATALOGO_NAVES.get(letra, {}).get("nombre", letra)
                    if nombre_nave not in naves_hundidas_nombres:
                        naves_hundidas_nombres.append(nombre_nave)

                    print(f"¡HUNDIDO! Se ha destruido la nave {nombre_nave} rival.")

                    if letra == "E":
                        print("¡Estación Orbital destruida! Se ha otorgado una recompensa al atacante.")

                elif estado_impacto == "averiada":
                    print(f"¡IMPACTO en {tablero.punto_a_texto(punto)}")

                    if letra == "D":
                        celda_revelada = flota.revelar_celda_rival(flota_rival, cubo_rival)

                        if celda_revelada:
                            tablero.escribir_celda(cubo_rival, celda_revelada, tablero.DETECTADO)
                            print(f"¡EFECTO DESTRUCTOR! Se reveló una nave rival en {tablero.punto_a_texto(celda_revelada)}.")

            elif estado_actual == tablero.SIN_EXPLORAR:
                tablero.escribir_celda(cubo_rival, punto, tablero.AGUA_MARCADA)

        if naves_hundidas_nombres:
            resultado_str = f"Hundido ({', '.join(naves_hundidas_nombres)})"
            print(f"\n[RESULTADO FINAL]: HUNDIDO - {', '.join(naves_hundidas_nombres)}")
        elif hubo_impacto:
            resultado_str = "Impacto"
            print(f"\n[RESULTADO FINAL]: IMPACTO")
        else:
            resultado_str = "Agua"
            print(f"\n[RESULTADO FINAL]: AGUA")

    # -------------------------------
    # Registramos en el historial
    # -------------------------------
    num_turno = len(registro.obtener_historial()) + 1
    id_jugador = f"Jugador {jugador_actual + 1}"
    registro.registrar_turno(num_turno, id_jugador, arma, texto_registro_objetivo, resultado_str)

    # ---------------------------------------------------
    # Verificamos si hay ganador y cambiamos de turno
    # ---------------------------------------------------
    estado["turnos"] = estado.get("turnos", 0) + 1
    ganador = hay_ganador(estado)

    if ganador is None:
        estado["turno"] = rival

    return estado


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
        flota_rival = estado["jugadores"][1 - jugador]["flota"]

        if flota_rival and flota.flota_hundida(flota_rival):
            estado["terminada"] = True
            estado["ganador"] = jugador

            return jugador
    return None


# -----------------------------------
# Comportamiento de la máquina 
# -----------------------------------

def objetivos_disponibles(estado, jugador):
    """
    Objetivo: Genera la lista de coordenadas (z, x, y) dentro del cubo que el jugador o la máquina
    aún no han utilizado para disparar.
    Parámetros:
        - estado(dict): Diccionario con el estado actual de la partida.
        - jugador(int): Índice del jugador.
    Devuelve:
        list: Lista de tuplas (z, x, y) con las coordenadas disponibles que permanencen sin explorar
        en el historial de disparos de dicho jugador.
    """
    disparos_hechos = estado["jugadores"][jugador].get("disparos",[])
    cubo_rival = estado["jugadores"][1 - jugador]["cubo"]
    n = estado["n"]
    disponibles = []

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                punto = (z, x, y)
                if punto not in disparos_hechos or tablero.leer_celda(cubo_rival, punto) == tablero.IMPACTO:
                    disponibles.append(punto)

    return disponibles


def elegir_objetivo_dificil(estado, jugador, disponibles):
    """
    Objetivo: Selecciona de forma táctica la coordenada de disparo para la
    máquina en dificultad 'dificil'.
    Parámetros:
        - estado(dict): Diccionario con el estado actual de la partida.
        - jugador(int): Índice del jugador.
        - disponibles(list): Lista de tuplas (z, x, y) con las coordenadas
        sin explorar.
    Devuelve:
        tuple: Coordenada (z, x, y) seleccionada para el disparo.
    """
    rival = estado["jugadores"][1 - jugador]
    n = estado["n"]
    mapa_prob = radar.generar_mapa_de_probabilidad(rival["cubo"], rival["flota"], n)

    mejor_puntaje = -1
    mejores_opciones = []
    for punto in disponibles:
        score = mapa_prob.get(punto, 0)
        if score > mejor_puntaje:
            mejor_puntaje = score
            mejores_opciones = [punto]
        elif score == mejor_puntaje:
            mejores_opciones.append(punto)

    if mejores_opciones:
        return random.choice(mejores_opciones)
    return random.choice(disponibles)


def elegir_jugada_dificil(estado, jugador, objetivo):
    """
    Objetivo: Selecciona el arma disponible más conveniente para
    la máquina en dificultad dificil.
    Parámetros:
        - 
    """
    arsenal = estado["jugadores"][jugador].get("arsenal", {})

    for arma in ("O", "R", "C", "L", "G"):
        if arsenal.get(arma, 0) and arsenal[arma] > 0:
            if arma == "L":
                eje = random.choice(("x", "y"))
                return {
                    "arma": "L",
                    "objetivo": tablero.punto_a_texto(objetivo),
                    "eje": eje
                }
            return {"arma": arma, "punto": objetivo}

    return {"arma": "T", "punto": objetivo}

def turno_maquina(estado):
    """
    Objetivo: Seleccionar una coordenada de disparo de manera aleatoria.
    Parámetros:
        - estado(dict): Diccionario con el estado de la partida.
    Devuelve:
        function: Devuelve la función 'ejecutar_turno' con los parámetros de estado y la jugada
        actualizados para realizar la jugada.
    """
    jugador = estado["turno"]

    if estado["tipo"] == "1v1":
        raise ErrorPartida("Esta partida no tiene jugadores controlados por la máquina.")

    if estado["tipo"] == "vs_maquina" and jugador == 0:
        raise ErrorPartida("Es el turno del jugador humano.")

    dificultad = estado.get("dificultad", "facil")
    if estado["tipo"] == "maquina_vs_maquina":
        dificultad = estado["dificultades"][jugador]

    disponibles = objetivos_disponibles(estado, jugador)
    if not disponibles:
        raise ErrorPartida("No quedan coordenadas disponibles para disparar.")

    if dificultad == "dificil":
        objetivo = elegir_objetivo_dificil(estado, jugador, disponibles)
        jugada = elegir_jugada_dificil(estado, jugador, objetivo)
    else:
        objetivo = random.choice(disponibles)
        jugada = {"arma": "T", "punto": objetivo}

    estado["jugadores"][jugador]["disparos"].append(objetivo)

    return ejecutar_turno(estado, jugada)

# -----------------------------------------------
# Menús, submenús y preparación de flota
# -----------------------------------------------

def ubicacion_manual(jugador, n=tablero.N_POR_DEFECTO):
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


def submenu_ubicacion(jugador, n=tablero.N_POR_DEFECTO):
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


def pedir_dificultad(etiqueta="Máquina"):
    """
    Objetivo: Solicita e interactua por consola con el usuario para pedir el nivel de dificultad.
    Parámetros:
        - etiqueta(str): Etiqueta descriptiva que indentifica a la máquina.
    Devuelve:
        str: Cadena de texto con la opción de dificultad elegida y validada.
    """
    while True:
        print(f"Dificultad de {etiqueta}: 1 - Fácil / 2 - Difícil")
        opcion = input("Opción: ").strip()

        if opcion == "1":
            return "facil"
        elif opcion == "2":
            return "dificil"
        else:
            print("Opción inválida.")


def preparar_partida(tipo):
    """
    Objetivo: Configura y prepara la partida según el modo de juego seleccionado.
    Parámetros:
        - tipo(str): Modalidad de la partida.
    Devuelve:
        dict: Diccionario con el estado completo e inicializado de la partida.
    """
    registro.inicializar_registro()
    n = pedir_tamanio_cubo()

    if tipo == "1v1":
        estado = nueva_partida_1v1({"n": n})
        print("\n--- Flota de Jugador 1 ---")
        submenu_ubicacion(estado["jugadores"][0], n)
        print("\n--- Flota de Jugador 2 ---")
        submenu_ubicacion(estado["jugadores"][1], n)

    elif tipo == "vs_maquina":
        dificultad = pedir_dificultad("Máquina")
        estado = nueva_partida_vs_maquina({"n": n},dificultad)
        print("\n--- Tu flota ---")
        submenu_ubicacion(estado["jugadores"][0], n)
        print("\n--- Flota de la Máquina ---")
        colocar_flota_automatica(estado["jugadores"][1], n)

    else:
        d1 = pedir_dificultad("Máquina 1")
        d2 = pedir_dificultad("Máquina 2")
        estado = nueva_partida_maquina_vs_maquina({"n": n}, (d1, d2))
        colocar_flota_automatica( estado["jugadores"][0], estado["n"], semilla=1)
        colocar_flota_automatica(estado["jugadores"][1], estado["n"], semilla=2)

    return estado


def guardar_partida(estado):
    """
    Objetivo: Solicita al usuario un nombre de archivo válido y gestiona el guardado del
    estado actual de la partida.
    Parámetros:
        - estado(dict): Diccionario con el estado actual de la partida.
    Devuelve:
        bool: True si la partida se guardó exitosamente, False si el proceso fue cancelado
        o se produjo un error.
    """
    while True:
            nombre = input("Nombre de la partida (máx 30 caracteres): ").strip()
            if re.fullmatch(PATRON_NOMBRE, nombre):
                break
    
            print("Nombre inválido. Use letras, números, _ o -.")
    
    try:
        ya_existia = nombre in registro.listar_partidas()
        registro.guardar_partida(estado, nombre)
        if ya_existia:
            print(f"¡'{nombre}' actualizada exitosamente!")
        else:
            print(f"¡Partida {nombre} guardada exitósamente!")
        return True

    except Exception as error:
        print(f"Error al guardar partida: {error}")
        return False


def continuar_partida():
    """
    Objetivo: Lista por consola las partidas guardadas e interactua con el
    usuario para seleccionar, cargar y reanudar una partida previa.
    Devuelve:
        dict o None: Diccionario con el estado recuperado de la partida si
        la carga fue exitosa, None si no existen partidas guardadas o si
        ocurre un error.
    """
    partidas = registro.listar_partidas()
    if not partidas:
        print("No se encontraron partidas guardadas.")
        return None

    print("\nPartidas disponibles: ")
    for idx, nom in enumerate(partidas, 1):
        print(f"{idx} - {nom}")

    sel = input("Seleccione el número o nombre de la partida: ").strip()
    if sel.isdigit() and 1 <= int(sel) <= len(partidas):
        nombre_elegido = partidas[int(sel) - 1]
    else:
        nombre_elegido = sel

    try:
        estado = registro.cargar_partida(nombre_elegido)
        print(f"¡Partida '{nombre_elegido}' cargada exitosamente!")
        return estado
    except Exception as error:
        print(f"No se pudo recuperar la partida: {error}")
        return None


def eliminar_partidas():
    """
    Objetivo: Lista por consola las partidas guardadas e interactúa con el usuario
    para seleccionar y eliminar una partida previa del disco.
    Devuelve:
        bool: True si se eliminó la partida exitosamente, False si no hay partidas
        guardadas, el usuario cancela u ocurre un error.
    """
    partidas = registro.listar_partidas()
    if not partidas:
        print("No se encontraron partidas guardadas.")
        return False

    print("\nPartidas disponibles: ")
    for idx, nom in enumerate(partidas, 1):
        print(f"{idx} - {nom}")

    sel = input("Seleccione el número o nombre de la partida a eliminar (Enter para cancelar): ").strip()
    if not sel:
        print("Eliminación cancelada.")
        return False

    if sel.isdigit() and 1 <= int(sel) <= len(partidas):
        nombre_elegido = partidas[int(sel) - 1]
    else:
        nombre_elegido = sel

    confirmar = input(f"¿Está seguro de que desea eliminar '{nombre_elegido}'? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Eliminación cancelada.")
        return False

    try:
        registro.eliminar_partida(nombre_elegido)
        print(f"¡Partida '{nombre_elegido}' eliminada exitosamente!")
        return True
    except Exception as error:
        print(f"No se pudo eliminar la partida: {error}")
        return False

    
def mostrar_resumen_final():
    """
    Objetivo: Obtiene las estadísticas globales de la partida e imprime por consola
    el resumen consolidado.
    Devuelve:
        None: Imprime directamente por consola el informe final.
    """
    estadisticas = registro.obtener_estadisticas_partida()
    print("\n=============================================================")
    print(f"     RESUMEN FINAL DE LA PARTIDA - TOTAL TURNOS: {estadisticas['total_turnos']}")
    print("\n=============================================================")
    for nombre_jugador, datos in estadisticas["jugadores"].items():
        print(f"\nEstadísticas de {nombre_jugador}: ")
        print(f"- Disparos realizados: {datos['disparos']}")
        print(f"- Impactos: {datos['impactos']} | Agua: {datos['agua']}")
        print(f"- Efectividad del tiro: {datos['efectividad']}")
        print(f"- Desglose de armas usadas: {datos['armas']}")


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
        print("3 - Métricas de radar")
        print("4 - Guardar y salir")

        opcion = input("Opción: ").strip()

        if opcion == "1":
            jugador_dict = estado["jugadores"][jugador]
            cubo_rival = estado["jugadores"][1 - jugador]["cubo"]
            n = estado["n"]

            jugada = solicitar_jugada(jugador_dict, cubo_rival, n)

            try:
                ejecutar_turno(estado, jugada)
                print("Disparo realizado.")

                if estado["terminada"]:
                    print(f"\n ¡TERMINÓ EL JUEGO! GANADOR: JUGADOR {estado['ganador'] + 1}")
                    mostrar_resumen_final()

            except ErrorPartida as error:
                print("Error:", error)

        elif opcion == "2":
            cubo_jugador = estado["jugadores"][jugador]["cubo"]
            print(tablero.dibujar_cubo(cubo_jugador, mostrar_naves=True))

        elif opcion == "3":
            met = radar.comparar_busquedas(estado["jugadores"][1 - jugador]["flota"], estado["n"])
            print("\n=== MÉTRICAS DE BUSQUEDA EN RADAR ===")
            for nave, datos in met.items():
                print(f"Nave {nave} | Lineal {datos['lineal']} ops | Optimizada: {datos['optimizada']} ops | Recursiva: {datos['recursiva']} ops")

        elif opcion == "4":
            if guardar_partida(estado):
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
            print("Turno del Jugador (Usted)")
            print("----------------------------")
            print("1 - Disparar")
            print("2 - Ver el cubo")
            print("3 - Métricas de radar")
            print("4 - Guardar y salir")

            opcion = input("Opción: ").strip()

            if opcion == "1":
                jugador_dict = estado["jugadores"][0]
                cubo_rival = estado["jugadores"][1]["cubo"]
                n = estado["n"]

                jugada = solicitar_jugada(jugador_dict, cubo_rival, n)

                try:
                    ejecutar_turno(estado, jugada)
                except ErrorPartida as error:
                    print(f"Error: en jugada: {error}")

            elif opcion == "2":
                cubo_jugador = estado["jugadores"][0]["cubo"]
                print(tablero.dibujar_cubo(cubo_jugador, mostrar_naves=True))

            elif opcion == "3":
                met = radar.comparar_busquedas(estado["jugadores"][1]["flota"], estado["n"])
                print("\n=== MÉTRICAS DE BUSQUEDA EN RADAR ===")
                for nave, datos in met.items():
                    print(f"Nave {nave} | Lineal {datos['lineal']} ops | Optimizada: {datos['optimizada']} ops | Recursiva: {datos['recursiva']} ops")

            elif opcion == "4":
                if guardar_partida(estado):
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
                print(f"Error en máquina: {error}")

        if estado["terminada"]:
            ganador_str = "JUGADOR 1 (Usted)" if estado["ganador"] == 0 else "JUGADOR 2 (Máquina)"
            print(f"\n¡TERMINÓ EL JUEGO! GANADOR: {ganador_str}")
            mostrar_resumen_final()
            

def partida_maquina_vs_maquina(estado):
    """
    Objetivo: Gestiona el bucle principal de juego en modo
    'máquina vs máquina'.
    Parámetros:
        - estado(dict): Diccionario con el estado actual de la partida.
    Devuelve:
        None: Se ejecuta de manera interactiva por consola hasta
        que se determine un ganador o el usuario decida salir
        al menú principal.
    """
    while not estado["terminada"]:
        jugador = estado["turno"]
        print(f"Turno de Máquina {jugador + 1} ({estado['dificultades'][jugador]}).")
        try:   
            turno_maquina(estado)
        except ErrorPartida as error:
            print(f"Error en simulación: {error}")
            break

        if estado["terminada"]:
            print(f"\n¡TERMINÓ EL JUEGO! GANADOR: MÁQUINA {estado['ganador'] + 1}")
            mostrar_resumen_final()


def menu_principal():
    """
    Objetivo: Desplega el menú principal del juego 'Operación Cubo'
    y dirige el flujo de ejecución del programa según la opción
    seleccionada por el jugador.
    Devuelve:
        None: Ejecuta un bucle interactivo por consola hasta que el
        usuario decida salir.
    """
    while True:
        print("\n==============================")
        print("       OPERACIÓN CUBO")
        print("==============================")
        print("1 - Partida uno contra uno")
        print("2 - Partida uno contra la máquina")
        print("3 - Partida máquina contra máquina")
        print("4 - Continuar una partida guardada")
        print("5 - Eliminar una partida guardada")
        print("6 - Salir")

        opcion = input("Opción: ").strip()

        try:
            if opcion == "1":
                estado = preparar_partida("1v1")
                partida_1v1(estado)

            elif opcion == "2":
                estado = preparar_partida("vs_maquina")
                partida_vs_maquina(estado)

            elif opcion == "3":
                estado = preparar_partida("maquina_vs_maquina")
                partida_maquina_vs_maquina(estado)

            elif opcion == "4":
                estado = continuar_partida()
                if estado is not None:
                    if estado["tipo"] == "1v1":
                        partida_1v1(estado)
                    elif estado["tipo"] == "vs_maquina":
                        partida_vs_maquina(estado)
                    else:
                        partida_maquina_vs_maquina(estado)

            elif opcion == "5":
                eliminar_partidas()

            elif opcion == "6":
                print("Programa finalizado.")
                break

            else:
                print("Opción inválida")

        except ErrorPartida as error:
            print(f"Error en la partida : {error}")
        except Exception as error:
            print(f"Ocurrió un error inesperado: {error}")


if __name__ == "__main__":
    menu_principal()
