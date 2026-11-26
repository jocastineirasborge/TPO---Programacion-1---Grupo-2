"""
Pruebas unitarias de partida.py (ejecutar con: python -m pytest).
"""

import pytest

import partida
import tablero


# ------------------------------------------------------------------
# Auxiliares
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def limpiar_historial():
    partida.registro.inicializar_registro()
    yield
    partida.registro.inicializar_registro()



def estado_ejemplo(tipo="vs_maquina", turno=1, n=2):
    """
    Objetivo: crear un estado mínimo de partida para probar funciones.
    Salida: diccionario con dos jugadores y los datos básicos del juego.
    """
    return {
        "tipo": tipo,
        "n": n,
        "jugadores": [
            {
                "cubo": tablero.crear_cubo(n),
                "flota": [],
                "disparos": [],
                "arsenal": partida.municion_inicial(),
            },
            {
                "cubo": tablero.crear_cubo(n),
                "flota": [],
                "disparos": [],
                "arsenal": partida.municion_inicial(),
            },
        ],
        "turno": turno,
        "terminada": False,
        "ganador": None,
        "turnos": 0,
        "dificultad": "facil",
        "dificultades": ("facil", "dificil"),
    }


# ------------------------------------------------------------------
# Funciones auxiliares e inicializacion
# ------------------------------------------------------------------

def test_municion_inicial():
    catalogo = partida.armamento.obtener_catalogo_armas()
    municion = partida.municion_inicial()

    assert isinstance(municion, dict)
    assert set(municion) == set(catalogo)
    for arma, datos in catalogo.items():
        assert municion[arma] == datos.get("municion")


def test_crear_jugador():
    jugador = partida.crear_jugador(5)

    assert isinstance(jugador, dict)
    assert set(jugador) == {"cubo", "flota", "disparos", "arsenal"}
    assert jugador["cubo"] is not None
    assert jugador["flota"] == []
    assert jugador["disparos"] == []
    assert isinstance(jugador["arsenal"], dict)


def test_crear_jugador_tamanio_invalido(monkeypatch):
    monkeypatch.setattr(partida.tablero, "crear_cubo", lambda n: None)

    with pytest.raises(partida.ErrorPartida):
        partida.crear_jugador(2)


def test_formatear_pendientes():
    pendientes = ["F", "F", "D", "S", "S", "S", "E"]

    assert partida.formatear_pendientes(pendientes) == "F x2   D x1   S x3   E x1"


def test_formatear_pendientes_lista_vacia():
    assert partida.formatear_pendientes([]) == ""


def test_colocar_flota_automatica(monkeypatch):
