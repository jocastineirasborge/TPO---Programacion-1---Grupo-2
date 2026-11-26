"""
Pruebas unitarias de flota.py (ejecutar con: python -m pytest).
"""

import pytest

import flota
import tablero


# ------------------------------------------------------------------
# Auxiliares
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def limpiar_flota_global():
    flota.inicializar_flota()
    yield
    flota.inicializar_flota()


# ------------------------------------------------------------------
# Catalogo y funciones auxiliares (Entrega 1)
# ------------------------------------------------------------------

def test_obtener_catalogo_naves():
    catalogo = flota.obtener_catalogo_naves()
    assert isinstance(catalogo, dict)
    for clave in ("F", "D", "S", "C", "P", "E"):
        assert clave in catalogo
        assert "nombre" in catalogo[clave]
        assert "celdas" in catalogo[clave]
        assert "cantidad" in catalogo[clave]


def test_obtener_puntos_tramo():
    assert flota.obtener_puntos_tramo((2, 3, 1), (2, 3, 4)) == [
        (2, 3, 1), (2, 3, 2), (2, 3, 3), (2, 3, 4)
    ]
    assert flota.obtener_puntos_tramo((4, 2, 2), (2, 2, 2)) == [
        (4, 2, 2), (3, 2, 2), (2, 2, 2)
    ]
    assert flota.obtener_puntos_tramo((1, 1, 1), (1, 1, 1)) == [(1, 1, 1)]
    # Cambio en más de un eje (diagonal) debe devolver lista vacía
    assert flota.obtener_puntos_tramo((1, 1, 1), (2, 2, 1)) == []


# ------------------------------------------------------------------
# Reglas de ubicacion y distancia segura (Entrega 1)
# ------------------------------------------------------------------

def test_validar_reglas_ubicacion_por_nave():
    n = 8
    # Submarino (S): solo mitad inferior z <= 4
    assert flota.validar_reglas_ubicacion("S", [(1, 1, 1), (1, 1, 2), (1, 1, 3)], n)
    assert not flota.validar_reglas_ubicacion("S", [(5, 1, 1), (5, 1, 2), (5, 1, 3)], n)

    # Crucero (C): no puede ocupar z=1 ni z=n
    assert flota.validar_reglas_ubicacion("C", [(2, 2, 1), (2, 2, 2), (2, 2, 3), (2, 2, 4)], n)
    assert not flota.validar_reglas_ubicacion("C", [(1, 2, 1), (1, 2, 2), (1, 2, 3), (1, 2, 4)], n)
    assert not flota.validar_reglas_ubicacion("C", [(8, 2, 1), (8, 2, 2), (8, 2, 3), (8, 2, 4)], n)

    # Portaaviones (P): solo mitad superior z > 4
    assert flota.validar_reglas_ubicacion("P", [(5, 1, 1), (5, 1, 2), (5, 1, 3), (5, 1, 4), (5, 1, 5)], n)
    assert not flota.validar_reglas_ubicacion("P", [(4, 1, 1), (4, 1, 2), (4, 1, 3), (4, 1, 4), (4, 1, 5)], n)

    # Estacion orbital (E): no puede tocar ninguna cara exterior
    puntos_e_validos = [
        (3, 3, 3), (3, 3, 4), (3, 4, 3), (3, 4, 4),
        (4, 3, 3), (4, 3, 4), (4, 4, 3), (4, 4, 4)
    ]
    assert flota.validar_reglas_ubicacion("E", puntos_e_validos, n)
    assert not flota.validar_reglas_ubicacion("E", [(1, 3, 3)], n)
    assert not flota.validar_reglas_ubicacion("E", [(3, 8, 3)], n)


def test_hay_distancia_segura():
    cubo = tablero.crear_cubo(8)
    flota_j = []
    flota.ubicar_nave(cubo, flota_j, "F", (2, 2, 2), (2, 2, 3), n=8)

    # Celda adyacente en diagonal (3, 3, 4) viola la distancia de seguridad
    assert not flota.hay_distancia_segura(cubo, [(3, 3, 4), (3, 3, 5)], 8)
    # Celda separada por al menos 1 espacio libre es segura
    assert flota.hay_distancia_segura(cubo, [(4, 4, 4), (4, 4, 5)], 8)


# ------------------------------------------------------------------
# Ubicacion manual y automatica (Entrega 1)
# ------------------------------------------------------------------

def test_ubicar_nave_valida_e_invalidas():
    cubo = tablero.crear_cubo(8)
    flota_j = []

    # Ubicacion valida de Fragata y Estacion orbital
    flota.ubicar_nave(cubo, flota_j, "F", (1, 1, 1), (1, 1, 2), n=8)
    assert len(flota_j) == 1
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.NAVE_OCULTA

    flota.ubicar_nave(cubo, flota_j, "E", (4, 4, 4), (5, 5, 5), n=8)
    assert len(flota_j) == 2

    # Nave desconocida
    with pytest.raises(flota.ErrorFlota):
        flota.ubicar_nave(cubo, flota_j, "Z", (7, 7, 1), (7, 7, 2), n=8)

    # Longitud incorrecta
    with pytest.raises(flota.ErrorFlota):
        flota.ubicar_nave(cubo, flota_j, "F", (7, 1, 1), (7, 1, 4), n=8)

    # Estacion orbital que no forma bloque 2x2x2
    with pytest.raises(flota.ErrorFlota):
        flota.ubicar_nave(cubo, flota_j, "E", (4, 4, 4), (4, 5, 5), n=8)

    # Superposicion / falta de distancia segura
    with pytest.raises(flota.ErrorFlota):
        flota.ubicar_nave(cubo, flota_j, "F", (1, 2, 1), (1, 2, 2), n=8)


def test_ubicacion_automatica_completa():
    cubo = tablero.crear_cubo(8)
    flota_auto = flota.ubicacion_automatica(cubo, semilla=42, n=8)

    # 3 F + 2 D + 2 S + 1 C + 1 P + 1 E = 10 naves en total
    assert len(flota_auto) == 10

    total_celdas_ocupadas = 0
    for letra, puntos, impactos in flota_auto:
        assert flota.validar_reglas_ubicacion(letra, puntos, 8)
        total_celdas_ocupadas += len(puntos)

    # 3*2 + 2*3 + 2*3 + 1*4 + 1*5 + 1*8 = 35 celdas
    assert total_celdas_ocupadas == 35
    assert tablero.contar_estado(cubo, tablero.NAVE_OCULTA) == 35


# ------------------------------------------------------------------
# Control de impactos, averias y hundimiento (Entrega 2)
# ------------------------------------------------------------------

def test_registrar_impacto_y_hundimiento():
    flota_j = [
        ("F", [(1, 1, 1), (1, 1, 2)], {(1, 1, 1): 0, (1, 1, 2): 0}),
        ("P", [(6, 2, 2), (6, 2, 3)], {(6, 2, 2): 0, (6, 2, 3): 0}),
    ]

    # Disparo al agua
    valido, letra, estado = flota.registrar_impacto(flota_j, (8, 8, 8))
    assert not valido
    assert letra is None
    assert estado is None

    # Primer impacto a Fragata -> averiada
    valido, letra, estado = flota.registrar_impacto(flota_j, (1, 1, 1))
    assert valido
    assert letra == "F"
    assert estado == "averiada"
    assert not flota.flota_hundida(flota_j)

    # Segundo impacto a Fragata -> hundida
    valido, letra, estado = flota.registrar_impacto(flota_j, (1, 1, 2))
    assert valido
    assert letra == "F"
    assert estado == "hundida"

    # Portaaviones requiere 2 impactos por celda
    _, _, est1 = flota.registrar_impacto(flota_j, (6, 2, 2))
    _, _, est2 = flota.registrar_impacto(flota_j, (6, 2, 3))
    assert est1 == "averiada"
    assert est2 == "averiada"
    assert not flota.flota_hundida(flota_j)

    flota.registrar_impacto(flota_j, (6, 2, 2))
    _, _, est_final = flota.registrar_impacto(flota_j, (6, 2, 3))
    assert est_final == "hundida"
    assert flota.flota_hundida(flota_j)


def test_submarino_inmune_al_laser():
    flota_j = [
        ("S", [(2, 2, 2), (2, 2, 3), (2, 2, 4)], {(2, 2, 2): 0, (2, 2, 3): 0, (2, 2, 4): 0})
    ]

    valido, letra, estado = flota.registrar_impacto(flota_j, (2, 2, 2), arma_usada="L")
    assert not valido
    assert letra == "S"
    assert estado == "inmune"
    assert flota_j[0][2][(2, 2, 2)] == 0


def test_revelar_celda_rival():
    cubo = tablero.crear_cubo(5)
    flota_r = [("F", [(1, 1, 1), (1, 1, 2)], {(1, 1, 1): 0, (1, 1, 2): 0})]

    tablero.escribir_celda(cubo, (1, 1, 1), tablero.IMPACTO)
    tablero.escribir_celda(cubo, (1, 1, 2), tablero.NAVE_OCULTA)

    revelada = flota.revelar_celda_rival(flota_r, cubo)
    assert revelada == (1, 1, 2)

    # Si no quedan celdas ocultas, devuelve None
    tablero.escribir_celda(cubo, (1, 1, 2), tablero.DETECTADO)
    assert flota.revelar_celda_rival(flota_r, cubo) is None


# ------------------------------------------------------------------
# Exportacion, importacion y reposicion de flota (Entrega 3)
# ------------------------------------------------------------------

def test_exportar_e_importar_flota():
    flota_original = [
        ("F", [(1, 1, 1), (1, 1, 2)], {(1, 1, 1): 1, (1, 1, 2): 0}),
        ("D", [(3, 2, 2), (3, 2, 3), (3, 2, 4)], {(3, 2, 2): 0, (3, 2, 3): 0, (3, 2, 4): 0}),
    ]

    serializada = flota.exportar_flota(flota_original)
    assert isinstance(serializada, list)
    assert serializada[0]["letra"] == "F"
    assert serializada[0]["puntos"] == [[1, 1, 1], [1, 1, 2]]
    assert serializada[0]["impactos"] == {"1,1,1": 1, "1,1,2": 0}

    repuesta = flota.importar_flota(serializada, n=8)
    assert repuesta == flota_original


def test_exportar_e_importar_flota_errores():
    with pytest.raises(flota.ErrorFlota):
        flota.exportar_flota("no_es_lista")

    with pytest.raises(flota.ErrorFlota):
        flota.importar_flota("no_es_lista")

    # Nave desconocida
    with pytest.raises(flota.ErrorFlota):
        flota.importar_flota([{"letra": "X", "puntos": [[1, 1, 1]], "impactos": {}}], n=8)

    # Coordenada fuera de rango del cubo
    with pytest.raises(flota.ErrorFlota):
        flota.importar_flota([{"letra": "F", "puntos": [[9, 1, 1]], "impactos": {}}], n=8)


def test_reponer_flota_en_cubo():
    cubo = tablero.crear_cubo(6)
    flota_repuesta = [
        ("F", [(1, 1, 1), (1, 1, 2)], {(1, 1, 1): 1, (1, 1, 2): 1}),  # Hundida
        ("D", [(3, 2, 2), (3, 2, 3), (3, 2, 4)], {(3, 2, 2): 1, (3, 2, 3): 0, (3, 2, 4): 0}),  # Averiada
    ]

    flota.reponer_flota_en_cubo(cubo, flota_repuesta)

    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.HUNDIDO
    assert tablero.leer_celda(cubo, (1, 1, 2)) == tablero.HUNDIDO
    assert tablero.leer_celda(cubo, (3, 2, 2)) == tablero.IMPACTO
    assert tablero.leer_celda(cubo, (3, 2, 3)) == tablero.NAVE_OCULTA
    assert tablero.leer_celda(cubo, (3, 2, 4)) == tablero.NAVE_OCULTA