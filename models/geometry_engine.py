# models/geometry_engine.py
import numpy as np
from scipy.spatial import Delaunay, Voronoi


class GeometryEngine:
    """
    Aplica Triangulacion de Delaunay y diagrama de Voronoi
    sobre los puntos 2D (x, y) de los landmarks faciales.
    """

    def __init__(self):
        self.triangulation = None
        self.voronoi = None
        self.points_2d = None

    def load_landmarks(self, landmarks: list, image_width: int,
                       image_height: int) -> np.ndarray:
        """
        Convierte landmarks normalizados (0-1) a pixeles reales.

        Args:
            landmarks: lista de {"x", "y", "z"}
            image_width: ancho de la imagen original
            image_height: alto de la imagen original

        Returns:
            np.ndarray shape (N, 2) con coordenadas en pixeles
        """
        points = []
        for lm in landmarks:
            px = lm["x"] * image_width
            py = lm["y"] * image_height
            points.append([px, py])
        self.points_2d = np.array(points, dtype=np.float64)
        return self.points_2d

    def compute_delaunay(self) -> dict:
        """
        Calcula la Triangulacion de Delaunay sobre points_2d.

        Returns:
            {
                "simplices": list de tripletas [i, j, k],
                "num_triangles": int,
                "vertices": list de [x, y]
            }
        """
        if self.points_2d is None or len(self.points_2d) < 3:
            return {"simplices": [], "num_triangles": 0, "vertices": []}

        self.triangulation = Delaunay(self.points_2d)
        simplices = self.triangulation.simplices.tolist()

        return {
            "simplices": simplices,
            "num_triangles": len(simplices),
            "vertices": self.points_2d.tolist()
        }

    def compute_voronoi(self) -> dict:
        """
        Calcula el diagrama de Voronoi sobre points_2d.

        Returns:
            {
                "vertices": lista de vertices del diagrama,
                "ridge_points": pares de puntos que comparten arista,
                "ridge_vertices": indices de vertices de cada arista,
                "num_regions": int
            }
        """
        if self.points_2d is None or len(self.points_2d) < 4:
            return {"vertices": [], "ridge_points": [],
                    "ridge_vertices": [], "num_regions": 0}

        self.voronoi = Voronoi(self.points_2d)

        # Filtrar aristas infinitas (indice -1)
        ridge_vertices_finitas = [
            rv for rv in self.voronoi.ridge_vertices if -1 not in rv
        ]
        ridge_points_filtradas = [
            self.voronoi.ridge_points[i].tolist()
            for i, rv in enumerate(self.voronoi.ridge_vertices)
            if -1 not in rv
        ]

        return {
            "vertices": self.voronoi.vertices.tolist(),
            "ridge_points": ridge_points_filtradas,
            "ridge_vertices": ridge_vertices_finitas,
            "num_regions": len(self.voronoi.regions)
        }

    def compute_all(self, landmarks: list, image_width: int,
                    image_height: int) -> dict:
        """
        Pipeline completo: carga landmarks, calcula Delaunay y Voronoi.

        Returns:
            {
                "points_2d": [[x, y], ...],
                "delaunay": {...},
                "voronoi": {...}
            }
        """
        self.load_landmarks(landmarks, image_width, image_height)
        delaunay_data = self.compute_delaunay()
        voronoi_data = self.compute_voronoi()

        return {
            "points_2d": self.points_2d.tolist(),
            "delaunay": delaunay_data,
            "voronoi": voronoi_data
        }

    def get_triangle_centroids(self) -> list:
        """
        Calcula el centroide de cada triangulo de Delaunay.
        Util para colorear triángulos según profundidad Z.
        """
        if self.triangulation is None or self.points_2d is None:
            return []

        centroids = []
        for simplex in self.triangulation.simplices:
            pts = self.points_2d[simplex]
            centroid = pts.mean(axis=0).tolist()
            centroids.append(centroid)
        return centroids