"""
Módulo registro.py
Administra el historial de la partida almacenado en memoria, calcula estadísticas de rendimiento
y gestiona el guardado/carga de partidas en disco mediante archivos JSON.
"""

import json
import os
import flota

HISTORIAL_PARTIDA = []
CARPETA_PARTIDAS = "datos_partidas"


def inicializar_registro():
    """
    Objetivo: Vaciar el registro de turnos en memoria para comenzar una partida nueva.
    Devuelve: None
    """
    HISTORIAL_PARTIDA.clear()


def registrar_turno(num_turno, jugador, arma, objetivo, resultado):
    """
    Objetivo: Agregar la información de un turno realizado al historial de la partida.
    Parámetros:
        - num_turno (int): Número del turno.
        - jugador (str): Identificador del jugador (ej. 'Jugador 1').
        - arma (str): Letra del arma utilizada.
        - objetivo (str): Coordenada o especificación del objetivo.
        - resultado (str): Resultado del disparo.
    Devuelve: None
    """
    registro = (num_turno, jugador, arma, objetivo, resultado)
    HISTORIAL_PARTIDA.append(registro)


def obtener_historial():
    """
    Objetivo: Devuelve la lista completa con todos los turnos registrados.
    Devuelve: list (lista de tuplas con el historial).
    """
    return HISTORIAL_PARTIDA


def obtener_ultimo_turno():
    """
    Objetivo: Consultar la información del último turno registrado.
    Devuelve: tuple o None
    """
    if not HISTORIAL_PARTIDA:
        return None
    return HISTORIAL_PARTIDA[-1]


def obtener_estadisticas_jugador(jugador_num):
    """
    Objetivo: Calcular y recopilar las métricas individuales de rendimiento de un jugador.
    Parámetros:
        - jugador_num (str o int): Identificador del jugador.
    Devuelve: dict con las estadísticas individuales.
    """
    historial = obtener_historial()
    disparos = 0
    impactos = 0
    agua = 0
    armas = {}

    for _, jugador, arma, _, res in historial:
        if jugador == jugador_num:
            disparos += 1
            armas[arma] = armas.get(arma, 0) + 1
            if res in ("Impacto", "Hundido") or "contactos" in str(res):
                impactos += 1
            elif res == "Agua":
                agua += 1

    efectividad_str = f"{(impactos / disparos) * 100:.2f}%" if disparos > 0 else "0.00%"

    return {
        "jugador": jugador_num,
        "disparos": disparos,
        "impactos": impactos,
        "agua": agua,
        "efectividad": efectividad_str,
        "armas": armas
    }


def obtener_estadisticas_partida():
    """
    Objetivo: Obtener el resumen global de estadísticas de la partida.
    Devuelve: dict con total de turnos y métricas por jugador.
    """
    historial = obtener_historial()
    return {
        "total_turnos": len(historial),
        "jugadores": {
            "Jugador 1": obtener_estadisticas_jugador("Jugador 1"),
            "Jugador 2": obtener_estadisticas_jugador("Jugador 2")
        }
    }


# ------------------------------------------------------------------
# Guardado y Carga de Partidas en disco (Entrega 3)
# ------------------------------------------------------------------

def guardar_partida(estado, nombre_archivo):
    """
    Objetivo: Serializar el estado completo de la partida y guardarlo en disco en formato JSON.
    Parámetros:
        - estado (dict): Diccionario con el estado completo de la partida.
        - nombre_archivo (str): Nombre deseado para el archivo guardado (sin extensión).
    Devuelve: 
        bool (True si se guardó correctamente).
    """
    if not os.path.exists(CARPETA_PARTIDAS):
        os.makedirs(CARPETA_PARTIDAS)

    ruta = os.path.join(CARPETA_PARTIDAS, f"{nombre_archivo}.json")

    datos_guardado = {
        "tipo": estado["tipo"],
        "dificultad": estado.get("dificultad", "normal"),
        "n": estado["n"],
        "turno": estado["turno"],
        "terminada": estado["terminada"],
        "ganador": estado["ganador"],
        "historial": HISTORIAL_PARTIDA,
        "jugadores": [
            {
                "cubo": estado["jugadores"][0]["cubo"],
                "flota": flota.exportar_flota(estado["jugadores"][0]["flota"]),
                "disparos": estado["jugadores"][0].get("disparos", []),
                "arsenal": estado["jugadores"][0]["arsenal"]
            },
            {
                "cubo": estado["jugadores"][1]["cubo"],
                "flota": flota.exportar_flota(estado["jugadores"][1]["flota"]),
                "disparos": estado["jugadores"][1].get("disparos", []),
                "arsenal": estado["jugadores"][1]["arsenal"]
            }
        ]
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos_guardado, f, indent=4)
    return True


def cargar_partida(nombre_archivo):
    """
    Objetivo: Reconstruir y cargar el estado completo de una partida guardada previamente.
    Parámetros:
        - nombre_archivo (str): Nombre del archivo guardado a recuperar.
    Devuelve: 
        dict (estado de la partida cargada).
    """
    ruta = os.path.join(CARPETA_PARTIDAS, f"{nombre_archivo}.json")
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe la partida guardada '{nombre_archivo}'.")

    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    HISTORIAL_PARTIDA.clear()
    for item in datos["historial"]:
        HISTORIAL_PARTIDA.append(tuple(item))

    estado = {
        "tipo": datos["tipo"],
        "dificultad": datos["dificultad"],
        "n": datos["n"],
        "turno": datos["turno"],
        "terminada": datos["terminada"],
        "ganador": datos["ganador"],
        "jugadores": [
            {
                "cubo": datos["jugadores"][0]["cubo"],
                "flota": flota.importar_flota(datos["jugadores"][0]["flota"]),
                "disparos": datos["jugadores"][0]["disparos"],
                "arsenal": datos["jugadores"][0]["arsenal"]
            },
            {
                "cubo": datos["jugadores"][1]["cubo"],
                "flota": flota.importar_flota(datos["jugadores"][1]["flota"]),
                "disparos": datos["jugadores"][1]["disparos"],
                "arsenal": datos["jugadores"][1]["arsenal"]
            }
        ]
    }
    return estado


def listar_partidas():
    """
    Objetivo: Obtener la lista de nombres de partidas guardadas disponibles en la carpeta de guardado.
    Devuelve:
        list (nombres de archivos de partidas disponibles sin extensión).
    """
    if not os.path.exists(CARPETA_PARTIDAS):
        return []
    archivos = os.listdir(CARPETA_PARTIDAS)
    return [a.replace(".json", "") for a in archivos if a.endswith(".json")]

def eliminar_partida(nombre_archivo):
    """
    Objetivo: Eliminar del disco el archivo JSON correspondiente a una partida guardada.
    Parámetros:
        - nombre_archivo(str): Nombre de la partida guardada a eliminar.
    Devuelve:
        bool: True si el archivo fue eliminado correctamente.
    """
    ruta = os.path.join(CARPETA_PARTIDAS, f"{nombre_archivo}.json")
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe la partida guardada '{nombre_archivo}'.")
    os.remove(ruta)
    return True

