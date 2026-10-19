"""
Módulo registro.py
Administra el historial de la partida almacenado en memoria.
"""
#Lista correspondiente al historial de la partida en donde cada elemento será una tupla con toda la información necesaria.
HISTORIAL_PARTIDA = []

def inicializar_registro():
    """
    Objetivo: Vaciar el registro para una partida nueva.
    """

    HISTORIAL_PARTIDA.clear()

def registrar_turno(num_turno, jugador, arma, objetivo, resultado):
    """
    Objetivo: Agregar la información del turno realizado al historial.
    Parámetros:
        -num_turno(int): Número del turno.
        -jugador(str): Identificador del jugador.
        -arma(str): Letra del arma utilizada.
        -objetivo(tuple): Coordenada en (z, y, x) del disparo.
        -resultado(str): Resultado del disparo.
    """

    registro = (num_turno, jugador, arma, objetivo, resultado)
    HISTORIAL_PARTIDA.append(registro)

def obtener_historial():
    """
    Objetivo: Devuelve la lista completa con todos los turnos registrados.
    Devuelve:
        list: Lista de tuplas con el historial.
    """

    return HISTORIAL_PARTIDA

def obtener_ultimo_turno():
    """
    Objetivo: Consultar la última jugada efectuada.
    Devuelve:
        tuple o None: La tupla del último turno, o None si el historial está vacío.
    """

    if not len(HISTORIAL_PARTIDA):
        return None
    return HISTORIAL_PARTIDA[-1]

def obtener_estadisticas_jugador(jugador_num):

    historial = obtener_historial()

    disparos = 0
    impactos = 0
    agua = 0
    armas = {}

    for num_turno, jugador, arma, objetivo, resultado in historial:
        if jugador == jugador_num:
            disparos += 1
            armas[arma] = armas.get(arma, 0) + 1

            if resultado == "Impacto":
                impactos += 1
            elif resultado == "Agua":
                agua += 1

    if disparos > 0:
        efectividad = (impactos / disparos) * 100
        efectividad_str = f"{efectividad:.2f}%"
    else:
        efectividad_str = "0.00%"

    return {
        "jugador": jugador_num,
        "disparos": disparos,
        "impactos": impactos,
        "agua": agua,
        "efectividad": efectividad_str,
        "armas": armas
    }


def obtener_estadisticas_partida():

    historial = obtener_historial()

    return {
        "total_turnos" : len(historial),
        "jugadores": {
            "Jugador 1": obtener_estadisticas_jugador("Jugador 1"),
            "Jugador 2": obtener_estadisticas_jugador("Jugador 2")
        }
    }
