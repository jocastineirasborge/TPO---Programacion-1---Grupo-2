"""
Pruebas unitarias de armamento.py (ejecutar con: python -m pytest).
"""

import pytest

import armamento
import tablero


# ------------------------------------------------------------------
# Catalogo y municion
# ------------------------------------------------------------------

def test_obtener_catalogo_armas():
    catalogo = armamento.obtener_catalogo_armas()
    assert isinstance(catalogo, dict)
    for clave in ("T", "R", "C", "S", "L", "O", "G"):
        assert clave in catalogo
        assert "nombre" in catalogo[clave]
        assert "municion" in catalogo[clave]


def test_descontar_municion_infinita_y_finita():
    arsenal = {"T": None, "R": 2, "O": 0}
    assert armamento.descontar_municion(arsenal, "T")
    assert arsenal["T"] is None

    assert armamento.descontar_municion(arsenal, "R")
    assert arsenal["R"] == 1
    assert armamento.descontar_municion(arsenal, "R")
    assert arsenal["R"] == 0
    assert not armamento.descontar_municion(arsenal, "R")

    assert not armamento.descontar_municion(arsenal, "O")
    assert not armamento.descontar_municion(arsenal, "Z")


# ------------------------------------------------------------------
# Efectos de armas simples y de area (Entrega 2)
# ------------------------------------------------------------------

def test_efecto_torpedo():
    assert armamento.efecto_torpedo((3, 4, 5), 8) == [(3, 4, 5)]
    assert armamento.efecto_torpedo((0, 4, 5), 8) == []
    assert armamento.efecto_torpedo((3, 9, 5), 8) == []


def test_efecto_misil_de_racimo_centro_y_esquina():
    afectadas_centro = armamento.efecto_misil_de_racimo((3, 3, 3), 6)
    assert len(afectadas_centro) == 7
    assert (3, 3, 3) in afectadas_centro

    afectadas_esquina = armamento.efecto_misil_de_racimo((1, 1, 1), 6)
    assert len(afectadas_esquina) == 4
    assert set(afectadas_esquina) == {(1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2)}

    assert armamento.efecto_misil_de_racimo((0, 1, 1), 6) == []


def test_efecto_carga():
    celdas = armamento.efecto_carga((2, 3, 4), 5)
    assert celdas == [(1, 3, 4), (2, 3, 4), (3, 3, 4), (4, 3, 4), (5, 3, 4)]
    assert armamento.efecto_carga((6, 3, 4), 5) == []


@pytest.mark.parametrize("eje", ["x", "y"])
def test_efecto_barrido_valido(eje):
    celdas = armamento.efecto_barrido(((2, 3, 4), eje), 5)
    assert len(celdas) == 5
    for z, x, y in celdas:
        assert z == 2
        if eje == "x":
            assert y == 4
        else:
            assert x == 3


def test_efecto_barrido_invalido():
    assert armamento.efecto_barrido(((2, 3, 4), "z"), 5) == []
    assert armamento.efecto_barrido(((0, 3, 4), "x"), 5) == []


def test_efecto_sonar():
    plano = armamento.efecto_sonar(("z", 2), 5)
    assert len(plano) == 25
    for punto in plano:
        assert punto[0] == 2
    assert armamento.efecto_sonar(("w", 1), 5) == []


# ------------------------------------------------------------------
# Efectos recursivos (Entrega 3)
# ------------------------------------------------------------------

def test_efecto_onda_centro_y_limites():
    celdas = armamento.efecto_onda((4, 4, 4), 8)
    assert (4, 4, 4) in celdas
    assert len(celdas) == 25
    assert len(set(celdas)) == len(celdas)
    assert armamento.efecto_onda((0, 4, 4), 8) == []


def test_efecto_torpedo_guiado_impacta_nave_y_contigua():
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (2, 2, 2), tablero.NAVE_OCULTA)
    assert armamento.efecto_torpedo_guiado((2, 2, 2), 5, cubo=cubo) == [(2, 2, 2)]

    cubo2 = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo2, (2, 2, 3), tablero.NAVE_OCULTA)
    assert armamento.efecto_torpedo_guiado((2, 2, 2), 5, cubo=cubo2) == [(2, 2, 3)]

    assert armamento.efecto_torpedo_guiado((0, 1, 1), 5, cubo=cubo) == []


# ------------------------------------------------------------------
# Despacho general
# ------------------------------------------------------------------

def test_obtener_celdas_afectadas_despacho():
    assert armamento.obtener_celdas_afectadas("T", (1, 1, 1), 5) == [(1, 1, 1)]
    assert len(armamento.obtener_celdas_afectadas("R", (3, 3, 3), 5)) == 7
    assert len(armamento.obtener_celdas_afectadas("C", (2, 2, 2), 5)) == 5
    assert len(armamento.obtener_celdas_afectadas("L", ((2, 2, 2), "x"), 5)) == 5
    assert len(armamento.obtener_celdas_afectadas("S", ("z", 1), 5)) == 25
    assert len(armamento.obtener_celdas_afectadas("O", (3, 3, 3), 5)) == 25
    assert armamento.obtener_celdas_afectadas("X", (1, 1, 1), 5) == []
