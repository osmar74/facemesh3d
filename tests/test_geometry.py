# tests/test_geometry.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.geometry_engine import GeometryEngine
import numpy as np


def test_delaunay_basico():
    """Prueba Delaunay con puntos sinteticos."""
    engine = GeometryEngine()

    # Simular landmarks normalizados
    landmarks = [
        {"x": 0.3, "y": 0.3, "z": -0.01},
        {"x": 0.5, "y": 0.2, "z": -0.02},
        {"x": 0.7, "y": 0.3, "z": -0.01},
        {"x": 0.4, "y": 0.5, "z": 0.0},
        {"x": 0.6, "y": 0.5, "z": 0.0},
        {"x": 0.5, "y": 0.7, "z": 0.01},
    ]

    resultado = engine.compute_all(landmarks, image_width=640, image_height=480)

    print(f"Puntos 2D: {len(resultado['points_2d'])}")
    print(f"Triangulos Delaunay: {resultado['delaunay']['num_triangles']}")
    print(f"Regiones Voronoi: {resultado['voronoi']['num_regions']}")
    print(f"Vertices Voronoi: {len(resultado['voronoi']['vertices'])}")

    assert len(resultado["points_2d"]) == 6
    assert resultado["delaunay"]["num_triangles"] > 0
    assert len(resultado["delaunay"]["simplices"]) > 0
    print("PASS: Delaunay calculado correctamente")


def test_centroids():
    """Prueba que los centroides se calculan."""
    engine = GeometryEngine()
    landmarks = [
        {"x": 0.2, "y": 0.2, "z": 0.0},
        {"x": 0.5, "y": 0.1, "z": 0.0},
        {"x": 0.8, "y": 0.2, "z": 0.0},
        {"x": 0.5, "y": 0.5, "z": 0.0},
    ]
    engine.compute_all(landmarks, 640, 480)
    centroids = engine.get_triangle_centroids()
    print(f"Centroides calculados: {len(centroids)}")
    assert len(centroids) > 0
    print("PASS: centroides correctos")


def test_sin_puntos():
    """Verifica que falla limpiamente sin puntos."""
    engine = GeometryEngine()
    resultado = engine.compute_all([], 640, 480)
    assert resultado["delaunay"]["num_triangles"] == 0
    print("PASS: manejo de landmarks vacios correcto")


if __name__ == "__main__":
    print("=== Probando GeometryEngine ===")
    test_delaunay_basico()
    test_centroids()
    test_sin_puntos()
    print("\n=== Todas las pruebas pasaron ===")