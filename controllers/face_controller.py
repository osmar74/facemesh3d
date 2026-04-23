# controllers/face_controller.py
import numpy as np
from typing import Optional
from services.camera_service import CameraService
from services.math_service import MathService
from services.storage_service import StorageService


class FaceController:
    """
    Orquesta el flujo completo de la aplicacion.
    Coordina CameraService, MathService y StorageService.
    Patron MVC: este es el Controller.
    """

    def __init__(self, D: float = 500.0, device: str = "cpu"):
        self.camera = CameraService()
        self.math = MathService(D=D, device=device)
        self.storage = StorageService()

        # Estado de la sesion activa en memoria
        self._active_landmarks = []
        self._active_width = 640
        self._active_height = 480
        self._active_image_b64 = ""

    # ------------------------------------------------------------------
    # Procesamiento de imagen
    # ------------------------------------------------------------------

    def process_upload(self, image_bytes: bytes,
                       alpha: float = 0.0,
                       beta: float = 0.0,
                       zoom: float = 1.0) -> dict:
        """
        Recibe bytes de imagen subida por el usuario.
        Detecta landmarks, calcula geometria y proyeccion.

        Returns:
            dict con todos los datos para el frontend
        """
        # Cargar imagen
        cam_result = self.camera.load_from_bytes(image_bytes)
        if not cam_result["success"]:
            return {"success": False,
                    "message": cam_result["message"]}

        frame = cam_result["frame"]

        # Guardar imagen como base64 para el panel "foto real"
        self._active_image_b64 = self.camera.frame_to_base64(frame)

        # Pipeline matematico completo
        result = self.math.process_image(
            frame, alpha=alpha, beta=beta, zoom=zoom
        )

        if result["success"]:
            # Guardar estado activo para re-proyeccion por WebSocket
            self._active_landmarks = result["landmarks"]
            self._active_width = result["image_width"]
            self._active_height = result["image_height"]

        result["image_b64"] = self._active_image_b64
        return result

    def process_webcam(self, alpha: float = 0.0,
                       beta: float = 0.0,
                       zoom: float = 1.0) -> dict:
        """
        Captura un frame de la webcam y lo procesa.
        """
        cam_result = self.camera.capture_single()
        if not cam_result["success"]:
            return {"success": False,
                    "message": cam_result["message"]}

        frame = cam_result["frame"]
        self._active_image_b64 = self.camera.frame_to_base64(frame)

        result = self.math.process_image(
            frame, alpha=alpha, beta=beta, zoom=zoom
        )

        if result["success"]:
            self._active_landmarks = result["landmarks"]
            self._active_width = result["image_width"]
            self._active_height = result["image_height"]

        result["image_b64"] = self._active_image_b64
        return result

    # ------------------------------------------------------------------
    # Re-proyeccion (WebSocket — solo rotacion, sin re-detectar)
    # ------------------------------------------------------------------

    def reproject(self, alpha: float, beta: float,
                  zoom: float = 1.0,
                  offset_x: float = 0.0,
                  offset_y: float = 0.0) -> dict:
        """
        Re-proyecta landmarks activos con nuevos angulos.
        Llamado por el WebSocket cuando el usuario rota con el mouse.
        No vuelve a detectar landmarks — usa los guardados en memoria.
        """
        if not self._active_landmarks:
            return {"success": False,
                    "message": "No hay sesion activa. Sube una imagen primero."}

        return self.math.reproject(
            landmarks=self._active_landmarks,
            image_width=self._active_width,
            image_height=self._active_height,
            alpha=alpha,
            beta=beta,
            zoom=zoom,
            offset_x=offset_x,
            offset_y=offset_y
        )

    # ------------------------------------------------------------------
    # Sesiones
    # ------------------------------------------------------------------

    def save_session(self, session_name: Optional[str] = None) -> dict:
        """Guarda la sesion activa en disco."""
        if not self._active_landmarks:
            return {"success": False,
                    "message": "No hay datos activos para guardar."}

        session_data = {
            "landmarks": self._active_landmarks,
            "image_width": self._active_width,
            "image_height": self._active_height,
            "image_b64": self._active_image_b64
        }
        return self.storage.save_session(session_data, session_name)

    def load_session(self, session_name: str) -> dict:
        """
        Carga sesion desde disco y la activa en memoria.
        Luego calcula proyeccion inicial (sin rotacion).
        """
        load_result = self.storage.load_session(session_name)
        if not load_result["success"]:
            return load_result

        data = load_result["session_data"]
        self._active_landmarks = data.get("landmarks", [])
        self._active_width = data.get("image_width", 640)
        self._active_height = data.get("image_height", 480)
        self._active_image_b64 = data.get("image_b64", "")

        # Calcular proyeccion inicial
        proj = self.math.reproject(
            landmarks=self._active_landmarks,
            image_width=self._active_width,
            image_height=self._active_height,
            alpha=0.0, beta=0.0, zoom=1.0
        )

        return {
            "success": True,
            "message": load_result["message"],
            "session_name": session_name,
            "landmarks": self._active_landmarks,
            "image_width": self._active_width,
            "image_height": self._active_height,
            "image_b64": self._active_image_b64,
            "geometry": proj.get("geometry", {}),
            "projection": proj.get("projection", {})
        }

    def list_sessions(self) -> dict:
        """Lista todas las sesiones guardadas."""
        return self.storage.list_sessions()

    def delete_session(self, session_name: str) -> dict:
        """Elimina una sesion del disco."""
        return self.storage.delete_session(session_name)

    def close(self):
        """Libera recursos."""
        self.math.close()