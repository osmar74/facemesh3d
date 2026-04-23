# tests/test_services.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import cv2
from services.camera_service import CameraService
from services.storage_service import StorageService


def test_camera_bytes_invalidos():
    """CameraService maneja bytes invalidos correctamente."""
    cam = CameraService()
    result = cam.load_from_bytes(b"no es imagen")
    assert result["success"] == False
    print(f"  {result['message']}")
    print("  PASS: bytes invalidos manejados")


def test_camera_load_bytes_validos():
    """CameraService decodifica correctamente imagen en bytes."""
    cam = CameraService()
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img)
    result = cam.load_from_bytes(buf.tobytes())
    assert result["success"] == True
    assert result["frame"] is not None
    print(f"  Frame shape: {result['frame'].shape}")
    print("  PASS: bytes validos decodificados")


def test_camera_frame_to_base64():
    """Conversion de frame a base64 funciona."""
    cam = CameraService()
    frame = np.zeros((50, 50, 3), dtype=np.uint8)
    b64 = cam.frame_to_base64(frame)
    assert isinstance(b64, str)
    assert len(b64) > 0
    print(f"  Base64 length: {len(b64)}")
    print("  PASS: frame a base64 correcto")


def test_storage_guardar_y_cargar():
    """StorageService guarda y recarga sesion correctamente."""
    storage = StorageService()

    data = {
        "landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0}],
        "image_width": 640,
        "image_height": 480,
        "projection": {"alpha": 0.1, "beta": 0.2, "zoom": 1.0}
    }

    save_result = storage.save_session(data, "test_session_temp")
    assert save_result["success"] == True
    print(f"  Guardado en: {save_result['file_path']}")

    load_result = storage.load_session("test_session_temp")
    assert load_result["success"] == True
    assert load_result["session_data"]["image_width"] == 640
    print(f"  Cargado: image_width={load_result['session_data']['image_width']}")
    print("  PASS: guardar y cargar sesion correcto")

    # Limpiar archivo de prueba
    storage.delete_session("test_session_temp")


def test_storage_listar():
    """StorageService lista sesiones correctamente."""
    storage = StorageService()
    storage.save_session({"test": 1}, "list_test_a")
    storage.save_session({"test": 2}, "list_test_b")

    result = storage.list_sessions()
    assert result["success"] == True
    assert result["count"] >= 2
    print(f"  Sesiones encontradas: {result['count']}")
    for s in result["sessions"]:
        print(f"    - {s['name']} ({s['size_kb']} KB)")
    print("  PASS: listado de sesiones correcto")

    storage.delete_session("list_test_a")
    storage.delete_session("list_test_b")


def test_storage_sesion_inexistente():
    """Cargar sesion inexistente no crashea."""
    storage = StorageService()
    result = storage.load_session("sesion_que_no_existe")
    assert result["success"] == False
    print(f"  Mensaje: {result['message']}")
    print("  PASS: sesion inexistente manejada correctamente")


if __name__ == "__main__":
    print("=== Probando Servicios ===\n")
    test_camera_bytes_invalidos()
    test_camera_load_bytes_validos()
    test_camera_frame_to_base64()
    test_storage_guardar_y_cargar()
    test_storage_listar()
    test_storage_sesion_inexistente()
    print("\n=== Todas las pruebas pasaron ===")