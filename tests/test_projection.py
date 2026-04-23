# tests/test_projection.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
from models.projection_3d import Projection3D


def _landmarks_sinteticos():
    """Genera landmarks sinteticos normalizados para pruebas."""
    return [
        {"x": 0.3, "y": 0.3, "z": -0.05},
        {"x": 0.5, "y": 0.2, "z": -0.03},
        {"x": 0.7, "y": 0.3, "z": -0.05},
        {"x": 0.4, "y": 0.5, "z":  0.00},
        {"x": 0.6, "y": 0.5, "z":  0.00},
        {"x": 0.5, "y": 0.7, "z":  0.02},
    ]


def test_sin_rotacion():
    """Sin rotacion, los puntos proyectados deben ser consistentes."""
    proj = Projection3D(D=500.0)
    proj.set_rotation(0.0, 0.0)

    resultado = proj.transform(_landmarks_sinteticos(), 640, 480)

    assert len(resultado["projected"]) == 6
    assert len(resultado["rotated"]) == 6
    assert len(resultado["normalized"]) == 6
    print(f"  Puntos proyectados: {len(resultado['projected'])}")
    print(f"  Alpha={resultado['alpha']}, Beta={resultado['beta']}")
    print("  PASS: proyeccion sin rotacion correcta")


def test_con_rotacion():
    """Con rotacion, los puntos deben cambiar respecto a sin rotacion."""
    lm = _landmarks_sinteticos()

    proj_base = Projection3D(D=500.0)
    proj_base.set_rotation(0.0, 0.0)
    res_base = proj_base.transform(lm, 640, 480)

    proj_rot = Projection3D(D=500.0)
    proj_rot.set_rotation(math.radians(30), math.radians(15))
    res_rot = proj_rot.transform(lm, 640, 480)

    # Los puntos deben ser diferentes
    base_x = res_base["projected"][0][0]
    rot_x  = res_rot["projected"][0][0]
    assert abs(base_x - rot_x) > 0.001
    print(f"  Sin rotacion X[0]={base_x:.3f}")
    print(f"  Con rotacion X[0]={rot_x:.3f}")
    print("  PASS: rotacion modifica correctamente los puntos")


def test_zoom():
    """El zoom debe escalar los puntos proyectados."""
    lm = _landmarks_sinteticos()

    proj1 = Projection3D(D=500.0)
    proj1.set_rotation(0.0, 0.0)
    proj1.set_zoom(1.0)
    res1 = proj1.transform(lm, 640, 480)

    proj2 = Projection3D(D=500.0)
    proj2.set_rotation(0.0, 0.0)
    proj2.set_zoom(2.0)
    res2 = proj2.transform(lm, 640, 480)

    val1 = abs(res1["projected"][0][0])
    val2 = abs(res2["projected"][0][0])
    assert val2 > val1
    print(f"  Zoom 1x primer punto X={val1:.3f}")
    print(f"  Zoom 2x primer punto X={val2:.3f}")
    print("  PASS: zoom funciona correctamente")


def test_landmarks_vacios():
    """Lista vacia no debe crashear."""
    proj = Projection3D(D=500.0)
    resultado = proj.transform([], 640, 480)
    assert resultado["projected"] == []
    print("  PASS: landmarks vacios manejados correctamente")


def test_formula_manual():
    """
    Verifica las formulas XT, YT, ZT con un punto conocido.
    Con a=0, b=0: XT=X, YT=Y, ZT=Z (rotacion identidad).
    """
    import numpy as np

    proj = Projection3D(D=500.0)
    proj.set_rotation(0.0, 0.0)

    pts = np.array([[10.0, 20.0, 5.0]])
    rotated = proj.rotate(pts)

    # Con a=0, b=0:
    # XT = X*1 - Z*0 = X = 10
    # YT = Y*1 - Z*1*0 - X*0*0 = Y = 20
    # ZT = Z*1*1 + X*0*1 + Y*0 = Z = 5
    assert abs(rotated[0][0] - 10.0) < 1e-9, f"XT esperado 10, obtenido {rotated[0][0]}"
    assert abs(rotated[0][1] - 20.0) < 1e-9, f"YT esperado 20, obtenido {rotated[0][1]}"
    assert abs(rotated[0][2] -  5.0) < 1e-9, f"ZT esperado  5, obtenido {rotated[0][2]}"
    print(f"  XT={rotated[0][0]:.4f} YT={rotated[0][1]:.4f} ZT={rotated[0][2]:.4f}")
    print("  PASS: formulas XT YT ZT verificadas matematicamente")


if __name__ == "__main__":
    print("=== Probando Projection3D ===\n")
    test_sin_rotacion()
    test_con_rotacion()
    test_zoom()
    test_landmarks_vacios()
    test_formula_manual()
    print("\n=== Todas las pruebas pasaron ===")