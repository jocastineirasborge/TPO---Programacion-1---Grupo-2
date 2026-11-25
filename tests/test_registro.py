"""
Pruebas unitarias de registro.py (ejecutar con: python -m pytest).
"""

import pytest

import registro
import tablero


# ------------------------------------------------------------------
# Auxiliares
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def limpiar_historial():
    registro.inicializar_registro()
    yield
    registro.inicializar_registro()


# ------------------------------------------------------------------
# Historial en memoria y estadisticas
# ------------------------------------------------------------------

def test_inicializar_y_registrar_turnos():
    assert registro.obtener_historial() == []
    assert registro.obtener_ultimo_turno() is None

    registro.registrar_turno(1, "Jugador 1", "T", "1,1,1", "Agua")
    registro.registrar_turno(2, "Jugador 2", "R", "2,2,2", "Impacto")

    historial = registro.obtener_historial()
    assert len(historial) == 2
    assert registro.obtener_ultimo_turno() == (2, "Jugador 2", "R", "2,2,2", "Impacto")

    registro.inicializar_registro()
    assert registro.obtener_historial() == []


def test_estadisticas_jugador_y_partida():
    registro.registrar_turno(1, "Jugador 1", "T", "1,1,1", "Impacto")
    registro.registrar_turno(2, "Jugador 2", "T", "2,2,2", "Agua")
    registro.registrar_turno(3, "Jugador 1", "S", "z=1", "2 contactos")
    registro.registrar_turno(4, "Jugador 1", "T", "1,1,2", "Agua")

    est_j1 = registro.obtener_estadisticas_jugador("Jugador 1")
    assert est_j1["disparos"] == 3
    assert est_j1["impactos"] == 2
    assert est_j1["agua"] == 1
    assert est_j1["armas"] == {"T": 2, "S": 1}
    assert est_j1["efectividad"] == "66.67%"

    est_j3 = registro.obtener_estadisticas_jugador("Jugador 3")
    assert est_j3["disparos"] == 0
    assert est_j3["efectividad"] == "0.00%"

    resumen = registro.obtener_estadisticas_partida()
    assert resumen["total_turnos"] == 4
    assert "Jugador 1" in resumen["jugadores"]
    assert "Jugador 2" in resumen["jugadores"]


# ------------------------------------------------------------------
# Guardado y carga en disco (Entrega 3)
# ------------------------------------------------------------------

def test_guardar_cargar_y_listar_partidas(tmp_path, monkeypatch):
    monkeypatch.setattr(registro, "CARPETA_PARTIDAS", str(tmp_path))

    assert registro.listar_partidas() == []

    cubo1 = tablero.crear_cubo(5)
    cubo2 = tablero.crear_cubo(5)
    flota1 = [("F", [(1, 1, 1)], {(1, 1, 1): 0})]
    flota2 = [("F", [(5, 5, 5)], {(5, 5, 5): 0})]

    estado = {
        "tipo": "1v1",
        "dificultad": "normal",
        "n": 5,
        "turno": 1,
        "terminada": False,
        "ganador": None,
        "jugadores": [
            {"cubo": cubo1, "flota": flota1, "disparos": [], "arsenal": {"T": None}},
            {"cubo": cubo2, "flota": flota2, "disparos": [(1, 1, 1)], "arsenal": {"T": None}},
        ],
    }

    registro.registrar_turno(1, "Jugador 1", "T", "1,1,1", "Agua")
    assert registro.guardar_partida(estado, "partida_prueba")
    assert registro.listar_partidas() == ["partida_prueba"]

    registro.inicializar_registro()
    cargada = registro.cargar_partida("partida_prueba")

    assert cargada["tipo"] == "1v1"
    assert cargada["n"] == 5
    assert cargada["turno"] == 1
    assert cargada["jugadores"][0]["flota"] == flota1
    assert registro.obtener_historial() == [(1, "Jugador 1", "T", "1,1,1", "Agua")]


def test_cargar_partida_inexistente(tmp_path, monkeypatch):
    monkeypatch.setattr(registro, "CARPETA_PARTIDAS", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        registro.cargar_partida("no_existe")
