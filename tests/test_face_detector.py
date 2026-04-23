# tests/test_face_detector.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.face_detector import FaceDetector
import cv2
import numpy as np


def test_detector_con_imagen_sintetica():
    """Prueba con imagen generada (sin foto real)."""
    detector = FaceDetector()

    # Imagen negra 480x640 — no detectara rostro, pero verifica que no falla
    imagen_negra = np.zeros((480, 640, 3), dtype=np.uint8)
    resultado = detector.detect_from_image(imagen_negra)

    print(f"Resultado imagen negra: {resultado['message']}")
    assert resultado["success"] == False
    assert "landmarks" in resultado
    print("PASS: imagen sin rostro manejada correctamente")

    detector.close()


def test_detector_bytes():
    """Prueba que detect_from_bytes funciona con bytes validos."""
    detector = FaceDetector()

    # Crear imagen en memoria y convertir a bytes
    imagen = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', imagen)
    image_bytes = buffer.tobytes()

    resultado = detector.detect_from_bytes(image_bytes)
    print(f"Resultado bytes: {resultado['message']}")
    assert "landmarks" in resultado
    print("PASS: detect_from_bytes funciona")

    detector.close()


if __name__ == "__main__":
    print("=== Probando FaceDetector ===")
    test_detector_con_imagen_sintetica()
    test_detector_bytes()
    print("\n=== Todas las pruebas pasaron ===")
    