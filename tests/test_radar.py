"""
Pruebas unitarias de radar.py (ejecutar con: python -m pytest).
"""

import pytest

import radar
import tablero


# ------------------------------------------------------------------
# Auxiliares
# ------------------------------------------------------------------

def flota_ejemplo():
    """
    Objetivo: armar una flota minima de prueba con una nave por tipo.
    Salida: lista de tuplas (letra, puntos, impactos).
    """
    return [
        ("F", [(1, 1, 1)], {(1, 1, 1): 0}),
        ("D", [(1, 2, 1), (1, 2, 2)], {(1, 2, 1): 0, (1, 2, 2): 0}),
        ("S", [(2, 1, 1), (2, 1, 2)], {(2, 1, 1): 0, (2, 1, 2): 0}),
        ("C", [(3, 2, 2), (3, 2, 3), (3, 2, 4)], {(3, 2, 2): 0, (3, 2, 3): 0, (3, 2, 4): 0}),
        ("P", [(6, 4, 4), (6, 4, 5), (6, 4, 6), (6, 4, 7)], {(6, 4, 4): 0, (6, 4, 5): 0, (6, 4, 6): 0, (6, 4, 7): 0}),
        ("E", [(4, 4, 4), (4, 4, 5), (4, 5, 4), (4, 5, 5)], {(4, 4, 4): 0, (4, 4, 5): 0, (4, 5, 4): 0, (4, 5, 5): 0}),
    ]


# ------------------------------------------------------------------
# Busquedas de naves (Lineal, Optimizada y Recursiva)
# ------------------------------------------------------------------

@pytest.mark.parametrize("id_nave,esperadas", [
    ("F", [(1, 1, 1)]),
    ("D", [(1, 2, 1), (1, 2, 2)]),
    ("S", [(2, 1, 1), (2, 1, 2)]),
    ("C", [(3, 2, 2), (3, 2, 3), (3, 2, 4)]),
    ("P", [(6, 4, 4), (6, 4, 5), (6, 4, 6), (6, 4, 7)]),
    ("E", [(4, 4, 4), (4, 4, 5), (4, 5, 4), (4, 5, 5)]),
])
def test_busquedas_encuentran_mismas_coordenadas(id_nave, esperadas):
    flota_j = flota_ejemplo()
    n = 8

    coords_lin, comp_lin = radar.busqueda_lineal_nave(flota_j, id_nave, n)
    coords_opt, comp_opt = radar.busqueda_optimizada(flota_j, id_nave, n)
    coords_rec, comp_rec = radar.busqueda_recursiva_nave(flota_j, id_nave, n)

    assert coords_lin == esperadas
    assert coords_opt == esperadas
    assert coords_rec == esperadas
    assert comp_lin == n * n * n
    assert comp_rec == n * n * n
    assert comp_opt <= comp_lin


def test_busqueda_nave_inexistente():
    flota_j = flota_ejemplo()
    coords, comps = radar.busqueda_lineal_nave(flota_j, "Z", 5)
    assert coords == []
    assert comps == 125

@pytest.mark.parametrize("n", [10, 20])
def test_busqueda_recursiva_y_comparar_cubos_grandes(n):
    flota_j = flota_ejemplo()
    coords, comps = radar.busqueda_recursiva_nave(flota_j, "F", n)
    assert coords == [(1, 1, 1)]
    assert comps == n * n * n

    resumen = radar.comparar_busquedas(flota_j, n=n)
    assert set(resumen.keys()) == {"F", "D", "S", "C", "P", "E"}
    for datos in resumen.values():
        assert datos["recursiva"] == n * n * n
        

# ------------------------------------------------------------------
# Recorridos recursivos del cubo (Entrega 3)
# ------------------------------------------------------------------

@pytest.mark.parametrize("n", [5, 8, 10, 20])
def test_recorrido_recursivo_capas_completo(n):
    recorrido = radar.recorrido_recursivo_capas(n)
    assert len(recorrido) == n * n * n
    assert len(set(recorrido)) == n * n * n
    assert recorrido[0] == (1, 1, 1)
    assert recorrido[-1] == (n, n, n)


@pytest.mark.parametrize("n", [5, 8, 10, 20])
def test_recorrido_recursivo_octantes_completo(n):
    recorrido = radar.recorrido_recursivo_octantes(n)
    assert len(recorrido) == n * n * n
    assert len(set(recorrido)) == n * n * n


# ------------------------------------------------------------------
# Sonar por planos, mapa de probabilidad y comparacion
# ------------------------------------------------------------------

def test_sonar_por_planos():
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (2, 1, 1), tablero.NAVE_OCULTA)
    tablero.escribir_celda(cubo, (2, 3, 4), tablero.DETECTADO)
    tablero.escribir_celda(cubo, (2, 5, 5), tablero.AGUA_MARCADA)

    contactos, puntos = radar.sonar_por_planos(cubo, "z", 2)
    assert contactos == 2
    assert len(puntos) == 25


def test_generar_mapa_de_probabilidad():
    cubo = tablero.crear_cubo(6)
    flota_r = [("D", [(3, 3, 3), (3, 3, 4)], {(3, 3, 3): 1, (3, 3, 4): 0})]
    tablero.escribir_celda(cubo, (3, 3, 3), tablero.IMPACTO)

    mapa = radar.generar_mapa_de_probabilidad(cubo, flota_r, n=6)
    assert len(mapa) == 6 * 6 * 6
    assert mapa[(3, 3, 3)] == 0
    assert mapa[(3, 3, 4)] >= 15


def test_comparar_busquedas():
    flota_j = flota_ejemplo()
    resumen = radar.comparar_busquedas(flota_j, n=8)
    assert set(resumen.keys()) == {"F", "D", "S", "C", "P", "E"}
    for datos in resumen.values():
        assert datos["lineal"] == 512
        assert datos["recursiva"] == 512
        assert datos["ahorro_opt"] == datos["lineal"] - datos["optimizada"]
