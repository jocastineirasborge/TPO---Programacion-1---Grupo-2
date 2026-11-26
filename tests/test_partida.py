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


def estado_ejemplo(tipo="vs_maquina", turno=1, n=5):
    """
    Objetivo: crear un estado minimo de partida para probar funciones.
    Salida: diccionario con dos jugadores y los datos basicos del juego.
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


def agregar_fragata_prueba(jugador_dict, punto=(1, 1, 1)):
    """
    Objetivo: colocar una fragata minima en el cubo y flota de un jugador.
    """
    tablero.escribir_celda(jugador_dict["cubo"], punto, tablero.NAVE_OCULTA)
    jugador_dict["flota"].append(("F", [punto], {punto: 0}))


# ------------------------------------------------------------------
# Funciones auxiliares e inicializacion de jugadores
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
    assert tablero.tamanio_cubo(jugador["cubo"]) == 5
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
    assert partida.formatear_pendientes([]) == ""


def test_colocar_flota_automatica(monkeypatch):
    jugador = partida.crear_jugador(5)
    flota_falsa = [("F", [(1, 1, 1)], {(1, 1, 1): 0})]
    monkeypatch.setattr(partida.flota, "ubicacion_automatica", lambda cubo, semilla=None, n=8: flota_falsa)

    resultado = partida.colocar_flota_automatica(jugador, n=5, semilla=1)
    assert resultado["flota"] == flota_falsa

    monkeypatch.setattr(partida.flota, "ubicacion_automatica", lambda cubo, semilla=None, n=8: [])
    with pytest.raises(partida.ErrorPartida):
        partida.colocar_flota_automatica(jugador, n=5)


# ------------------------------------------------------------------
# Inicializacion de partidas
# ------------------------------------------------------------------

def test_nueva_partida_1v1():
    estado = partida.nueva_partida_1v1({"n": 6})

    assert estado["tipo"] == "1v1"
    assert estado["n"] == 6
    assert len(estado["jugadores"]) == 2
    assert estado["turno"] == 0
    assert not estado["terminada"]
    assert estado["ganador"] is None
    assert estado["turnos"] == 0


@pytest.mark.parametrize("dificultad", ["facil", "dificil"])
def test_nueva_partida_vs_maquina_valida(dificultad):
    estado = partida.nueva_partida_vs_maquina({"n": 5}, dificultad=dificultad)

    assert estado["tipo"] == "vs_maquina"
    assert estado["dificultad"] == dificultad
    assert estado["n"] == 5


def test_nueva_partida_dificultades_invalidas():
    with pytest.raises(ValueError):
        partida.nueva_partida_vs_maquina(dificultad="imposible")

    with pytest.raises(ValueError):
        partida.nueva_partida_maquina_vs_maquina(dificultades=("facil",))

    with pytest.raises(ValueError):
        partida.nueva_partida_maquina_vs_maquina(dificultades=("facil", "media"))


# ------------------------------------------------------------------
# Ejecucion de turnos y ganador
# ------------------------------------------------------------------

def test_ejecutar_turno_agua_cambia_de_turno():
    estado = estado_ejemplo(tipo="1v1", turno=0, n=5)
    agregar_fragata_prueba(estado["jugadores"][1], (5, 5, 5))

    partida.ejecutar_turno(estado, {"arma": "T", "punto": (1, 1, 1)})

    assert tablero.leer_celda(estado["jugadores"][1]["cubo"], (1, 1, 1)) == tablero.AGUA_MARCADA
    assert estado["turno"] == 1
    assert estado["turnos"] == 1
    assert not estado["terminada"]
    assert partida.registro.obtener_ultimo_turno()[-1] == "Agua"


def test_ejecutar_turno_hunde_flota_y_define_ganador():
    estado = estado_ejemplo(tipo="1v1", turno=0, n=5)
    agregar_fragata_prueba(estado["jugadores"][1], (2, 2, 2))

    partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})

    assert tablero.leer_celda(estado["jugadores"][1]["cubo"], (2, 2, 2)) == tablero.HUNDIDO
    assert estado["terminada"]
    assert estado["ganador"] == 0
    assert partida.hay_ganador(estado) == 0


def test_ejecutar_turno_sin_municion_y_partida_terminada():
    estado = estado_ejemplo(tipo="1v1", turno=0, n=5)
    estado["jugadores"][0]["arsenal"]["O"] = 0

    with pytest.raises(partida.ErrorJugada):
        partida.ejecutar_turno(estado, {"arma": "O", "punto": (1, 1, 1)})

    estado["terminada"] = True
    with pytest.raises(partida.ErrorPartida):
        partida.ejecutar_turno(estado, {"arma": "T", "punto": (1, 1, 1)})


# ------------------------------------------------------------------
# Comportamiento de la maquina
# ------------------------------------------------------------------

def test_objetivos_disponibles():
    estado = estado_ejemplo(tipo="vs_maquina", turno=1, n=5)
    estado["jugadores"][1]["disparos"].append((1, 1, 1))

    disponibles = partida.objetivos_disponibles(estado, 1)

    assert (1, 1, 1) not in disponibles
    assert len(disponibles) >= (5 * 5 * 5) - 1


def test_turno_maquina_errores_de_estado():
    estado_1v1 = estado_ejemplo(tipo="1v1", turno=0, n=5)
    with pytest.raises(partida.ErrorPartida):
        partida.turno_maquina(estado_1v1)

    estado_humano = estado_ejemplo(tipo="vs_maquina", turno=0, n=5)
    with pytest.raises(partida.ErrorPartida):
        partida.turno_maquina(estado_humano)


@pytest.mark.parametrize("dificultad", ["facil", "dificil"])
def test_turno_maquina_facil_y_dificil(dificultad):
    estado = estado_ejemplo(tipo="vs_maquina", turno=1, n=5)
    estado["dificultad"] = dificultad
    agregar_fragata_prueba(estado["jugadores"][0], (3, 3, 3))

    partida.turno_maquina(estado)

    assert len(estado["jugadores"][1]["disparos"]) == 1
    assert estado["turnos"] == 1
