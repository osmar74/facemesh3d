# services/storage_service.py
import json
import os
import numpy as np
from datetime import datetime
from typing import Optional


class StorageService:
    """
    Gestiona el guardado y carga de sesiones de deteccion facial.
    Cada sesion contiene landmarks, geometria y parametros de proyeccion.
    Formato: JSON (legible) + NPY opcional para arrays grandes.
    """

    SESSIONS_DIR = "storage/sessions"

    def __init__(self):
        os.makedirs(self.SESSIONS_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # Guardar
    # ------------------------------------------------------------------

    def save_session(self, session_data: dict,
                     session_name: Optional[str] = None) -> dict: 
        """
        Guarda una sesion completa en disco como JSON.

        Args:
            session_data: dict con landmarks, geometria, proyeccion
            session_name: nombre del archivo (sin extension).
                          Si es None, usa timestamp automatico.

        Returns:
            {
                "success": bool,
                "file_path": str,
                "session_name": str,
                "message": str
            }
        """
        if session_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"session_{timestamp}"

        # Limpiar nombre de archivo
        session_name = session_name.replace(" ", "_").replace("/", "_")

        file_path = os.path.join(self.SESSIONS_DIR,
                                 f"{session_name}.json")

        # Preparar datos serializables
        data_to_save = {
            "session_name": session_name,
            "saved_at": datetime.now().isoformat(),
            "version": "1.0",
            "data": self._make_serializable(session_data)
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "file_path": file_path,
                "session_name": session_name,
                "message": f"Sesion guardada: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "file_path": "",
                "session_name": session_name,
                "message": f"Error al guardar: {str(e)}"
            }

    # ------------------------------------------------------------------
    # Cargar
    # ------------------------------------------------------------------

    def load_session(self, session_name: str) -> dict:
        """
        Carga una sesion desde disco.

        Args:
            session_name: nombre sin extension (ej: "session_20240101_120000")

        Returns:
            {
                "success": bool,
                "session_data": dict o None,
                "message": str
            }
        """
        file_path = os.path.join(self.SESSIONS_DIR,
                                 f"{session_name}.json")

        if not os.path.exists(file_path):
            return {
                "success": False,
                "session_data": None,
                "message": f"Sesion no encontrada: {session_name}"
            }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                saved = json.load(f)

            return {
                "success": True,
                "session_data": saved.get("data", {}),
                "saved_at": saved.get("saved_at", ""),
                "session_name": saved.get("session_name", session_name),
                "message": f"Sesion cargada: {session_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "session_data": None,
                "message": f"Error al cargar: {str(e)}"
            }

    def list_sessions(self) -> dict:
        """
        Lista todas las sesiones guardadas.

        Returns:
            {
                "success": bool,
                "sessions": [{"name": str, "saved_at": str, "size_kb": float}],
                "count": int
            }
        """
        sessions = []
        try:
            for fname in sorted(os.listdir(self.SESSIONS_DIR),
                                reverse=True):
                if fname.endswith(".json"):
                    fpath = os.path.join(self.SESSIONS_DIR, fname)
                    name = fname.replace(".json", "")
                    size_kb = os.path.getsize(fpath) / 1024.0

                    # Leer fecha de guardado
                    saved_at = ""
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            saved_at = meta.get("saved_at", "")
                    except Exception:
                        pass

                    sessions.append({
                        "name": name,
                        "saved_at": saved_at,
                        "size_kb": round(size_kb, 2)
                    })

            return {
                "success": True,
                "sessions": sessions,
                "count": len(sessions)
            }
        except Exception as e:
            return {
                "success": False,
                "sessions": [],
                "count": 0,
                "message": str(e)
            }

    def delete_session(self, session_name: str) -> dict:
        """Elimina una sesion del disco."""
        file_path = os.path.join(self.SESSIONS_DIR,
                                 f"{session_name}.json")
        if not os.path.exists(file_path):
            return {"success": False,
                    "message": f"No existe: {session_name}"}
        try:
            os.remove(file_path)
            return {"success": True,
                    "message": f"Sesion eliminada: {session_name}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------

    def _make_serializable(self, obj):
        """
        Convierte recursivamente objetos numpy a tipos Python nativos
        para que json.dump no falle.
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, dict):
            return {k: self._make_serializable(v)
                    for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._make_serializable(i) for i in obj]
        return obj