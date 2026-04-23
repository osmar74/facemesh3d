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
        
    def enrich_landmarks(self, landmarks: list,
                         image_width: int,
                         image_height: int,
                         levels: int = 1) -> list:
        """
        Enriquece los landmarks agregando puntos interpolados
        entre pares de landmarks existentes.

        Args:
            landmarks:    lista original de {"x","y","z"}
            image_width:  ancho imagen
            image_height: alto imagen
            levels:       niveles de subdivision (1=~3x, 2=~5x, 3=~9x puntos)

        Returns:
            lista ampliada de landmarks con el mismo formato
        """
        import numpy as np
        from scipy.spatial import Delaunay

        if not landmarks or levels == 0:
            return landmarks

        pts = np.array([[lm["x"], lm["y"], lm["z"]]
                        for lm in landmarks], dtype=np.float64)

        for _ in range(levels):
            pts2d = pts[:, :2]
            try:
                tri = Delaunay(pts2d)
            except Exception:
                break

            new_pts = list(pts)
            seen = set()

            for simplex in tri.simplices:
                for i in range(3):
                    a = simplex[i]
                    b = simplex[(i + 1) % 3]
                    key = (min(a, b), max(a, b))
                    if key in seen:
                        continue
                    seen.add(key)
                    mid = (pts[a] + pts[b]) / 2.0
                    new_pts.append(mid)

            pts = np.array(new_pts, dtype=np.float64)

        return [{"x": float(p[0]),
                 "y": float(p[1]),
                 "z": float(p[2])} for p in pts]

    def close(self):
        """Libera recursos."""
        pass