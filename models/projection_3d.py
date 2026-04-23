# models/projection_3d.py
import numpy as np
import math


class Projection3D:
    """
    Aplica rotacion 3D y proyeccion perspectiva sobre landmarks faciales.

    Formulas implementadas:
        Rotacion:
            XT = X*cos(a) - Z*sin(a)
            YT = Y*cos(b) - Z*cos(a)*sin(b) - X*sin(a)*sin(b)
            ZT = Z*cos(a)*cos(b) + X*sin(a)*cos(b) + Y*sin(b)

        Proyeccion perspectiva:
            XT_proj = D * XT / (D - ZT)
            YT_proj = D * YT / (D - ZT)
    """

    def __init__(self, D: float = 500.0):
        """
        Args:
            D: distancia focal para proyeccion perspectiva.
               Valor tipico: 300-800. Mayor D = menos distorsion.
        """
        self.D = D
        self.alpha = 0.0    # angulo rotacion eje Y (horizontal)
        self.beta = 0.0     # angulo rotacion eje X (vertical)
        self.zoom = 1.0     # factor de escala
        self.offset_x = 0.0
        self.offset_y = 0.0

    def set_rotation(self, alpha: float, beta: float):
        """
        Establece angulos de rotacion en radianes.

        Args:
            alpha: rotacion horizontal (arrastre mouse X)
            beta:  rotacion vertical   (arrastre mouse Y)
        """
        self.alpha = float(alpha)
        self.beta = float(beta)

    def set_zoom(self, zoom: float):
        """
        Establece factor de zoom. 1.0 = sin zoom.
        """
        self.zoom = max(0.1, float(zoom))

    def set_offset(self, offset_x: float, offset_y: float):
        """
        Establece traslacion del centro de proyeccion.
        """
        self.offset_x = float(offset_x)
        self.offset_y = float(offset_y)

    def normalize_landmarks(self, landmarks: list,
                             image_width: int,
                             image_height: int) -> np.ndarray:
        """
        Convierte landmarks normalizados (0-1) a coordenadas centradas
        en el origen para que la rotacion sea correcta.

        El centro del rostro queda en (0, 0, 0).

        Returns:
            np.ndarray shape (N, 3) con coordenadas centradas
        """
        pts = np.array([
            [lm["x"] * image_width,
             lm["y"] * image_height,
             lm["z"]]
            for lm in landmarks
        ], dtype=np.float64)

        # Centrar en el origen
        center_x = (pts[:, 0].max() + pts[:, 0].min()) / 2.0
        center_y = (pts[:, 1].max() + pts[:, 1].min()) / 2.0

        pts[:, 0] -= center_x
        pts[:, 1] -= center_y

        # Normalizar Z para que este en escala similar a X,Y
        z_range = pts[:, 2].max() - pts[:, 2].min()
        if z_range > 0:
            scale = (image_width + image_height) / 2.0 * 0.3
            pts[:, 2] = pts[:, 2] / z_range * scale

        return pts

    def rotate(self, pts: np.ndarray) -> np.ndarray:
        """
        Aplica rotacion 3D con las formulas exactas requeridas.

        Formulas:
            XT = X*cos(a) - Z*sin(a)
            YT = Y*cos(b) - Z*cos(a)*sin(b) - X*sin(a)*sin(b)
            ZT = Z*cos(a)*cos(b) + X*sin(a)*cos(b) + Y*sin(b)

        Args:
            pts: np.ndarray (N, 3) con columnas [X, Y, Z]

        Returns:
            np.ndarray (N, 3) con columnas [XT, YT, ZT] rotados
        """
        a = self.alpha
        b = self.beta

        cos_a = math.cos(a)
        sin_a = math.sin(a)
        cos_b = math.cos(b)
        sin_b = math.sin(b)

        X = pts[:, 0]
        Y = pts[:, 1]
        Z = pts[:, 2]

        XT = X * cos_a - Z * sin_a
        YT = Y * cos_b - Z * cos_a * sin_b - X * sin_a * sin_b
        ZT = Z * cos_a * cos_b + X * sin_a * cos_b + Y * sin_b

        return np.column_stack([XT, YT, ZT])

    def project(self, pts_rotated: np.ndarray) -> np.ndarray:
        """
        Aplica proyeccion perspectiva.

        Formulas:
            XT_proj = D * XT / (D - ZT)
            YT_proj = D * YT / (D - ZT)

        Args:
            pts_rotated: np.ndarray (N, 3) ya rotado

        Returns:
            np.ndarray (N, 2) con coordenadas 2D proyectadas
        """
        XT = pts_rotated[:, 0]
        YT = pts_rotated[:, 1]
        ZT = pts_rotated[:, 2]

        D = self.D

        # Evitar division por cero
        denominador = D - ZT
        denominador = np.where(np.abs(denominador) < 1e-6,
                               1e-6, denominador)

        XT_proj = D * XT / denominador
        YT_proj = D * YT / denominador

        return np.column_stack([XT_proj, YT_proj])

    def transform(self, landmarks: list,
                  image_width: int,
                  image_height: int) -> dict:
        """
        Pipeline completo: normaliza → rota → proyecta → aplica zoom.

        Args:
            landmarks: lista de {"x", "y", "z"}
            image_width: ancho imagen original
            image_height: alto imagen original

        Returns:
            {
                "projected": [[x, y], ...] coordenadas 2D finales,
                "rotated":   [[x, y, z], ...] puntos 3D rotados,
                "normalized":[[x, y, z], ...] puntos centrados,
                "alpha": float,
                "beta": float,
                "zoom": float,
                "D": float
            }
        """
        if not landmarks:
            return {
                "projected": [],
                "rotated": [],
                "normalized": [],
                "alpha": self.alpha,
                "beta": self.beta,
                "zoom": self.zoom,
                "D": self.D
            }

        # 1. Normalizar y centrar
        pts_norm = self.normalize_landmarks(
            landmarks, image_width, image_height
        )

        # 2. Aplicar zoom antes de rotar
        pts_scaled = pts_norm * self.zoom

        # 3. Rotar con formulas XT, YT, ZT
        pts_rotated = self.rotate(pts_scaled)

        # 4. Proyeccion perspectiva
        pts_projected = self.project(pts_rotated)

        # 5. Aplicar offset de traslacion
        pts_projected[:, 0] += self.offset_x
        pts_projected[:, 1] += self.offset_y

        return {
            "projected": pts_projected.tolist(),
            "rotated": pts_rotated.tolist(),
            "normalized": pts_norm.tolist(),
            "alpha": self.alpha,
            "beta": self.beta,
            "zoom": self.zoom,
            "D": self.D
        }