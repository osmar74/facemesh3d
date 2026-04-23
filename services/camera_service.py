# services/camera_service.py
import cv2
import numpy as np


class CameraService:
    """
    Gestiona la captura de imagenes desde webcam o archivo.
    Proporciona frames en formato BGR (OpenCV estandar).
    """

    def __init__(self, camera_index: int = 0,
                 width: int = 640, height: int = 480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self._cap = None

    # ------------------------------------------------------------------
    # Camara en vivo
    # ------------------------------------------------------------------

    def open_camera(self) -> bool:
        """
        Abre la camara del sistema.

        Returns:
            True si se abrio correctamente, False si fallo.
        """
        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            return False
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return True

    def capture_frame(self) -> dict:
        """
        Captura un frame de la camara abierta.

        Returns:
            {
                "success": bool,
                "frame": np.ndarray BGR o None,
                "message": str
            }
        """
        if self._cap is None or not self._cap.isOpened():
            return {"success": False, "frame": None,
                    "message": "Camara no abierta"}

        ret, frame = self._cap.read()
        if not ret or frame is None:
            return {"success": False, "frame": None,
                    "message": "No se pudo capturar frame"}

        return {"success": True, "frame": frame,
                "message": "Frame capturado"}

    def capture_single(self) -> dict:
        """
        Abre camara, captura un frame y la cierra.
        Util para captura puntual sin mantener la camara abierta.
        """
        opened = self.open_camera()
        if not opened:
            return {"success": False, "frame": None,
                    "message": f"No se pudo abrir camara {self.camera_index}"}

        result = self.capture_frame()
        self.close_camera()
        return result

    def close_camera(self):
        """Libera la camara."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    # ------------------------------------------------------------------
    # Desde archivo
    # ------------------------------------------------------------------

    def load_from_file(self, file_path: str) -> dict:
        """
        Carga imagen desde ruta de archivo.

        Returns:
            {
                "success": bool,
                "frame": np.ndarray BGR o None,
                "message": str
            }
        """
        frame = cv2.imread(file_path)
        if frame is None:
            return {"success": False, "frame": None,
                    "message": f"No se pudo cargar: {file_path}"}
        return {"success": True, "frame": frame,
                "message": f"Imagen cargada: {file_path}"}

    def load_from_bytes(self, image_bytes: bytes) -> dict:
        """
        Decodifica imagen desde bytes (upload HTTP multipart).

        Returns:
            {
                "success": bool,
                "frame": np.ndarray BGR o None,
                "message": str
            }
        """
        if not image_bytes:
            return {"success": False, "frame": None,
                    "message": "Bytes vacios"}

        np_array = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if frame is None:
            return {"success": False, "frame": None,
                    "message": "No se pudo decodificar la imagen"}

        return {"success": True, "frame": frame,
                "message": f"Imagen decodificada: {frame.shape}"}

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def frame_to_bytes(self, frame: np.ndarray,
                       ext: str = ".jpg") -> bytes:
        """
        Convierte frame BGR a bytes JPEG o PNG.
        Util para enviar la imagen al frontend via JSON base64.
        """
        _, buffer = cv2.imencode(ext, frame)
        return buffer.tobytes()

    def frame_to_base64(self, frame: np.ndarray,
                        ext: str = ".jpg") -> str:
        """
        Convierte frame BGR a string base64.
        """
        import base64
        img_bytes = self.frame_to_bytes(frame, ext)
        return base64.b64encode(img_bytes).decode("utf-8")

    def resize_frame(self, frame: np.ndarray,
                     width: int, height: int) -> np.ndarray:
        """Redimensiona frame manteniendo proporciones."""
        return cv2.resize(frame, (width, height),
                          interpolation=cv2.INTER_AREA)