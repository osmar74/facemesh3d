# models/face_detector.py
import numpy as np
import cv2
import face_alignment


class FaceDetector:
    """
    Detecta landmarks faciales usando face-alignment (PyTorch).
    Funciona en Windows sin dependencias de MediaPipe.
    Retorna 68 puntos (x, y, z).
    """

    def __init__(self, device: str = "cpu"):
        """
        Args:
            device: 'cpu' o 'cuda' si tienes GPU NVIDIA
        """
        self.device = device
        self.fa = face_alignment.FaceAlignment(
            face_alignment.LandmarksType.THREE_D,
            device=self.device,
            flip_input=False
        )

    def detect_from_image(self, image_bgr: np.ndarray) -> dict:
        """
        Recibe imagen BGR (OpenCV), retorna landmarks.

        Returns:
            {
                "success": bool,
                "landmarks": list de {"x", "y", "z"},
                "image_width": int,
                "image_height": int,
                "message": str
            }
        """
        if image_bgr is None or image_bgr.size == 0:
            return {"success": False, "landmarks": [],
                    "message": "Imagen vacia"}

        height, width = image_bgr.shape[:2]
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        try:
            predictions = self.fa.get_landmarks(image_rgb)
        except Exception as e:
            return {
                "success": False,
                "landmarks": [],
                "image_width": width,
                "image_height": height,
                "message": f"Error en deteccion: {str(e)}"
            }

        if predictions is None or len(predictions) == 0:
            return {
                "success": False,
                "landmarks": [],
                "image_width": width,
                "image_height": height,
                "message": "No se detecto ningun rostro"
            }

        # Tomar el primer rostro — shape (68, 3)
        face_pts = predictions[0]

        # Normalizar x,y a rango 0-1 para consistencia
        landmarks = []
        for pt in face_pts:
            landmarks.append({
                "x": float(pt[0]) / width,
                "y": float(pt[1]) / height,
                "z": float(pt[2])
            })

        return {
            "success": True,
            "landmarks": landmarks,
            "image_width": width,
            "image_height": height,
            "message": f"Detectados {len(landmarks)} landmarks"
        }

    def detect_from_file(self, file_path: str) -> dict:
        """Carga imagen desde ruta de archivo y detecta landmarks."""
        image = cv2.imread(file_path)
        if image is None:
            return {"success": False, "landmarks": [],
                    "message": f"No se pudo cargar: {file_path}"}
        return self.detect_from_image(image)

    def detect_from_bytes(self, image_bytes: bytes) -> dict:
        """Recibe bytes de imagen (desde upload HTTP) y detecta landmarks."""
        np_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if image is None:
            return {"success": False, "landmarks": [],
                    "message": "No se pudo decodificar la imagen"}
        return self.detect_from_image(image)

    def get_landmark_array(self, landmarks: list) -> np.ndarray:
        """Convierte lista de dicts a numpy array (N, 3)."""
        if not landmarks:
            return np.array([])
        return np.array([[lm["x"], lm["y"], lm["z"]]
                         for lm in landmarks])

    def close(self):
        """Libera recursos."""
        pass