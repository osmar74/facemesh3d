# services/math_service.py
import numpy as np
from models.face_detector import FaceDetector
from models.geometry_engine import GeometryEngine
from models.projection_3d import Projection3D


class MathService:
    """
    Orquesta el pipeline matematico completo:
        imagen → landmarks → geometria → proyeccion 3D

    Es el nucleo de procesamiento del sistema.
    """

    def __init__(self, D: float = 500.0, device: str = "cpu"):
        self.detector = FaceDetector(device=device)
        self.geometry = GeometryEngine()
        self.projection = Projection3D(D=D)

    def process_image(self, image_bgr: np.ndarray,
                      alpha: float = 0.0,
                      beta: float = 0.0,
                      zoom: float = 1.0,
                      offset_x: float = 0.0,
                      offset_y: float = 0.0) -> dict:
        """
        Pipeline completo sobre una imagen BGR.

        Args:
            image_bgr: imagen OpenCV BGR
            alpha: angulo rotacion horizontal (radianes)
            beta:  angulo rotacion vertical   (radianes)
            zoom:  factor de escala
            offset_x, offset_y: traslacion del canvas

        Returns:
            {
                "success": bool,
                "message": str,
                "landmarks": [...],
                "image_width": int,
                "image_height": int,
                "geometry": {
                    "points_2d": [...],
                    "delaunay": {"simplices": [...], "num_triangles": int},
                    "voronoi": {...}
                },
                "projection": {
                    "projected": [[x,y], ...],
                    "rotated":   [[x,y,z], ...],
                    "alpha": float,
                    "beta": float,
                    "zoom": float,
                    "D": float
                }
            }
        """
        # 1. Detectar landmarks
        detection = self.detector.detect_from_image(image_bgr)
        if not detection["success"]:
            return {
                "success": False,
                "message": detection["message"],
                "landmarks": [],
                "geometry": {},
                "projection": {}
            }

        landmarks = detection["landmarks"]
        w = detection["image_width"]
        h = detection["image_height"]

        # 2. Calcular geometria (Delaunay + Voronoi)
        geo_data = self.geometry.compute_all(landmarks, w, h)

        # 3. Configurar y aplicar proyeccion 3D
        self.projection.set_rotation(alpha, beta)
        self.projection.set_zoom(zoom)
        self.projection.set_offset(offset_x, offset_y)

        proj_data = self.projection.transform(landmarks, w, h)

        return {
            "success": True,
            "message": detection["message"],
            "landmarks": landmarks,
            "image_width": w,
            "image_height": h,
            "geometry": geo_data,
            "projection": proj_data
        }

    def process_bytes(self, image_bytes: bytes,
                      alpha: float = 0.0,
                      beta: float = 0.0,
                      zoom: float = 1.0,
                      offset_x: float = 0.0,
                      offset_y: float = 0.0) -> dict:
        """
        Pipeline completo desde bytes de imagen (upload HTTP).
        """
        import cv2
        np_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if image is None:
            return {"success": False, "message": "No se pudo decodificar",
                    "landmarks": [], "geometry": {}, "projection": {}}
        return self.process_image(image, alpha, beta, zoom,
                                  offset_x, offset_y)

    def reproject(self, landmarks: list,
                  image_width: int,
                  image_height: int,
                  alpha: float,
                  beta: float,
                  zoom: float = 1.0,
                  offset_x: float = 0.0,
                  offset_y: float = 0.0) -> dict:
        """
        Re-proyecta landmarks ya detectados con nuevos angulos.
        Usado por el WebSocket cuando el usuario rota con el mouse.
        No re-detecta — usa los landmarks guardados en sesion.
        """
        self.projection.set_rotation(alpha, beta)
        self.projection.set_zoom(zoom)
        self.projection.set_offset(offset_x, offset_y)

        proj_data = self.projection.transform(
            landmarks, image_width, image_height
        )

        # Recalcular geometria con puntos 2D actualizados
        geo_data = self.geometry.compute_all(
            landmarks, image_width, image_height
        )

        return {
            "success": True,
            "projection": proj_data,
            "geometry": geo_data
        }

    def close(self):
        """Libera recursos del detector."""
        self.detector.close()