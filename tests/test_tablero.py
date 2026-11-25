"""
Pruebas unitarias de tablero.py (ejecutar con: python -m pytest).
"""

import pytest

import tablero


# ------------------------------------------------------------------
# Auxiliares
# ------------------------------------------------------------------

def todos_los_puntos(n):
    """
    Objetivo: armar el conjunto de todos los puntos de un cubo de n x n x n.
    Parametros: n (int).
    Salida: conjunto de tuplas (z, x, y).
    """
    puntos = set()
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                puntos.add((z, x, y))
    return puntos


# ------------------------------------------------------------------
# Cubo y validacion de puntos (Entrega 1)
# ------------------------------------------------------------------

def test_crear_cubo_tamanio_y_estado_inicial():
    cubo = tablero.crear_cubo(6)
    assert tablero.tamanio_cubo(cubo) == 6
    assert tablero.contar_estado(cubo, tablero.SIN_EXPLORAR) == 6 * 6 * 6


def test_crear_cubo_sin_aliasing():
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.IMPACTO)
    assert tablero.contar_estado(cubo, tablero.IMPACTO) == 1


@pytest.mark.parametrize("n", [4, 21, "8", 8.0])
def test_crear_cubo_invalido(n):
    assert tablero.crear_cubo(n) is None


def test_es_punto_valido():
    cubo = tablero.crear_cubo(8)
    assert tablero.es_punto_valido(cubo, (1, 1, 1))
    assert tablero.es_punto_valido(cubo, (8, 8, 8))
    assert not tablero.es_punto_valido(cubo, (0, 1, 1))
    assert not tablero.es_punto_valido(cubo, (1, 9, 1))
    assert not tablero.es_punto_valido(cubo, (1, 1))
    assert not tablero.es_punto_valido(cubo, [1, 1, 1])


def test_texto_a_punto_y_tramo():
    cubo = tablero.crear_cubo(8)
    assert tablero.texto_a_punto("3,5,4", cubo) == (3, 5, 4)
    assert tablero.texto_a_punto(" 3 , 5 , 4 ", cubo) == (3, 5, 4)
    assert tablero.texto_a_punto("3,5", cubo) is None
    assert tablero.texto_a_punto("3,5,9", cubo) is None
    assert tablero.texto_a_punto("a,b,c", cubo) is None
    assert tablero.texto_a_tramo("3,4,2-3,4,7", cubo) == ((3, 4, 2), (3, 4, 7))
    assert tablero.texto_a_tramo("3,4,2", cubo) is None


def test_punto_a_texto():
    assert tablero.punto_a_texto((6, 3, 1)) == "6,3,1"


def test_leer_y_escribir_celda():
    cubo = tablero.crear_cubo(5)
    assert tablero.escribir_celda(cubo, (2, 3, 4), tablero.NAVE_OCULTA)
    assert tablero.leer_celda(cubo, (2, 3, 4)) == tablero.NAVE_OCULTA
    assert tablero.leer_celda(cubo, (6, 1, 1)) is None
    assert not tablero.escribir_celda(cubo, (6, 1, 1), tablero.IMPACTO)
    assert not tablero.escribir_celda(cubo, (1, 1, 1), 99)


# ------------------------------------------------------------------
# Planos, rectas y vecinos (Entrega 2)
# ------------------------------------------------------------------

def test_obtener_planos():
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (2, 3, 4), tablero.IMPACTO)
    assert tablero.obtener_plano(cubo, "z", 2)[3 - 1][4 - 1] == tablero.IMPACTO
    assert tablero.obtener_plano(cubo, "x", 3)[2 - 1][4 - 1] == tablero.IMPACTO
    assert tablero.obtener_plano(cubo, "y", 4)[2 - 1][3 - 1] == tablero.IMPACTO
    assert tablero.obtener_plano(cubo, "w", 1) is None
    assert tablero.obtener_plano(cubo, "z", 6) is None


def test_puntos_de_plano_y_recta():
    cubo = tablero.crear_cubo(5)
    plano = tablero.puntos_de_plano(cubo, "x", 2)
    assert len(plano) == 25
    for punto in plano:
        assert punto[1] == 2
    recta = tablero.puntos_de_recta(cubo, (3, 2, 1), "z")
    assert recta == [(1, 2, 1), (2, 2, 1), (3, 2, 1), (4, 2, 1), (5, 2, 1)]
    assert tablero.puntos_de_plano(cubo, "w", 1) == []
    assert tablero.puntos_de_recta(cubo, (9, 9, 9), "z") == []


def test_vecinos():
    cubo = tablero.crear_cubo(5)
    assert len(tablero.vecinos_ortogonales(cubo, (3, 3, 3))) == 6
    assert len(tablero.vecinos_ortogonales(cubo, (1, 1, 1))) == 3
    assert len(tablero.vecinos(cubo, (3, 3, 3))) == 26
    assert len(tablero.vecinos(cubo, (1, 1, 1))) == 7
    assert tablero.vecinos(cubo, (0, 0, 0)) == []


def test_vista_rival_oculta_naves():
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (1, 1, 1), tablero.NAVE_OCULTA)
    vista = tablero.vista_rival(cubo)
    assert tablero.leer_celda(vista, (1, 1, 1)) == tablero.SIN_EXPLORAR
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.NAVE_OCULTA


# ------------------------------------------------------------------
# Recorridos alternativos (Entrega 3)
# ------------------------------------------------------------------

@pytest.mark.parametrize("n", [5, 6, 8])
@pytest.mark.parametrize("nombre", list(tablero.RECORRIDOS))
def test_recorridos_visitan_cada_celda_una_vez(nombre, n):
    cubo = tablero.crear_cubo(n)
    recorrido = tablero.recorrer(cubo, nombre)
    assert len(recorrido) == n * n * n
    assert set(recorrido) == todos_los_puntos(n)


@pytest.mark.parametrize("nombre", list(tablero.RECORRIDOS))
def test_recorridos_no_modifican_el_cubo(nombre):
    cubo = tablero.crear_cubo(5)
    tablero.escribir_celda(cubo, (2, 2, 2), tablero.NAVE_OCULTA)
    copia = tablero.copiar_cubo(cubo)
    tablero.recorrer(cubo, nombre)
    assert cubo == copia


def test_recorrido_por_capas_orden():
    cubo = tablero.crear_cubo(5)
    por_z = tablero.recorrido_por_capas(cubo, "z")
    assert por_z[:3] == [(1, 1, 1), (1, 1, 2), (1, 1, 3)]
    assert por_z[24] == (1, 5, 5)
    assert por_z[25] == (2, 1, 1)
    por_x = tablero.recorrido_por_capas(cubo, "x")
    for i in range(0, 25):
        assert por_x[i][1] == 1
    por_y = tablero.recorrido_por_capas(cubo, "y")
    for i in range(0, 25):
        assert por_y[i][2] == 1
    assert tablero.recorrido_por_capas(cubo, "w") == []


@pytest.mark.parametrize("n", [5, 8])
def test_recorrido_serpiente_es_contiguo(n):
    cubo = tablero.crear_cubo(n)
    recorrido = tablero.recorrido_serpiente(cubo)
    for i in range(1, len(recorrido)):
        assert recorrido[i] in tablero.vecinos_ortogonales(cubo, recorrido[i - 1])


def test_rango_en_sentido():
    assert tablero.rango_en_sentido(4, True) == [1, 2, 3, 4]
    assert tablero.rango_en_sentido(4, False) == [4, 3, 2, 1]


def test_espiral_de_capa_orden():
    cubo = tablero.crear_cubo(5)
    espiral = tablero.espiral_de_capa(cubo, 1)
    sin_z = []
    for punto in espiral:
        sin_z.append((punto[1], punto[2]))
    # Borde exterior completo y luego hacia el centro
    assert sin_z[:9] == [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
                         (2, 5), (3, 5), (4, 5), (5, 5)]
    assert sin_z[-1] == (3, 3)
    assert tablero.espiral_de_capa(cubo, 0) == []
    assert tablero.espiral_de_capa(cubo, 6) == []


@pytest.mark.parametrize("n", [5, 6])
def test_espiral_de_capa_es_contigua(n):
    cubo = tablero.crear_cubo(n)
    espiral = tablero.espiral_de_capa(cubo, 2)
    assert len(espiral) == n * n
    for i in range(1, len(espiral)):
        assert espiral[i] in tablero.vecinos_ortogonales(cubo, espiral[i - 1])


def test_mitades_de_eje():
    assert tablero.mitades_de_eje(8) == [(1, 4), (5, 8)]
    assert tablero.mitades_de_eje(5) == [(1, 2), (3, 5)]


def test_octante_de():
    cubo = tablero.crear_cubo(8)
    assert tablero.octante_de(cubo, (1, 1, 1)) == 1
    assert tablero.octante_de(cubo, (8, 8, 8)) == 8
    assert tablero.octante_de(cubo, (1, 1, 8)) == 2
    assert tablero.octante_de(cubo, (8, 1, 1)) == 5
    assert tablero.octante_de(cubo, (0, 1, 1)) is None


@pytest.mark.parametrize("n", [5, 8])
def test_puntos_de_octante_coinciden_con_octante_de(n):
    cubo = tablero.crear_cubo(n)
    for numero in range(1, tablero.CANTIDAD_OCTANTES + 1):
        for punto in tablero.puntos_de_octante(cubo, numero):
            assert tablero.octante_de(cubo, punto) == numero


def test_puntos_de_octante_invalido():
    cubo = tablero.crear_cubo(8)
    assert tablero.puntos_de_octante(cubo, 0) == []
    assert tablero.puntos_de_octante(cubo, 9) == []
    assert len(tablero.puntos_de_octante(cubo, 1)) == 4 * 4 * 4


# ------------------------------------------------------------------
# Despacho de recorridos y dibujo del orden (Entrega 3)
# ------------------------------------------------------------------

def test_listar_recorridos():
    opciones = tablero.listar_recorridos()
    assert len(opciones) == len(tablero.RECORRIDOS)
    for clave, nombre in opciones:
        assert clave in tablero.RECORRIDOS
        assert nombre == tablero.NOMBRES_RECORRIDOS[clave]


def test_recorrer_nombre_invalido():
    cubo = tablero.crear_cubo(5)
    assert tablero.recorrer(cubo, "inexistente") == []


def test_dibujar_orden_recorrido():
    cubo = tablero.crear_cubo(5)
    recorrido = tablero.recorrer(cubo, "capas_z")
    dibujo = tablero.dibujar_orden_recorrido(cubo, recorrido, 1)
    lineas = dibujo.split("\n")
    assert "CAPA z = 1" in lineas[0]
    assert lineas[1].split() == ["x1", "x2", "x3", "x4", "x5"]
    # Capa z: filas y, columnas x. La celda (1, x=2, y=1) es la sexta visitada.
    assert lineas[2].split() == ["y1", "1", "6", "11", "16", "21"]
    assert len(lineas) == 2 + 5


def test_dibujar_orden_recorrido_parcial_e_invalido():
    cubo = tablero.crear_cubo(5)
    dibujo = tablero.dibujar_orden_recorrido(cubo, [(1, 1, 1)], 1)
    assert dibujo.split("\n")[2].split() == ["y1", "1", ".", ".", ".", "."]
    assert tablero.dibujar_orden_recorrido(cubo, [], 0) is None
