# app.py

# app.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
import json
import math
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from controllers.face_controller import FaceController


# ------------------------------------------------------------------
# Instancia global del controller
# ------------------------------------------------------------------
controller = FaceController(D=500.0, device="cpu")


# ------------------------------------------------------------------
# Lifespan (reemplaza on_event deprecated)
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FaceMesh3D iniciado en http://127.0.0.1:8000")
    yield
    controller.close()
    print("FaceMesh3D cerrado.")


# ------------------------------------------------------------------
# App FastAPI
# ------------------------------------------------------------------
app = FastAPI(
    title="FaceMesh3D",
    description="Triangulacion Delaunay/Voronoi facial 3D",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------------------------
# Rutas HTTP
# ------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Sirve la interfaz principal."""
    return templates.TemplateResponse(request,"index.html")


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Recibe imagen subida por el usuario.
    Detecta landmarks, calcula Delaunay/Voronoi y proyeccion 3D.

    Returns:
        JSON con landmarks, geometria y proyeccion inicial.
    """
    image_bytes = await file.read()
    result = controller.process_upload(image_bytes)

    if not result["success"]:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": result["message"]}
        )
    return JSONResponse(content=result)


@app.post("/webcam")
async def capture_webcam():
    """
    Captura frame de la webcam y lo procesa.
    """
    result = controller.process_webcam()
    if not result["success"]:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": result["message"]}
        )
    return JSONResponse(content=result)


@app.get("/sessions")
async def list_sessions():
    """Lista todas las sesiones guardadas."""
    return JSONResponse(content=controller.list_sessions())


@app.post("/session/save")
async def save_session(request: Request):
    """
    Guarda la sesion activa.
    Body JSON: {"session_name": "mi_sesion"} (opcional)
    """
    try:
        body = await request.json()
        name = body.get("session_name", None)
    except Exception:
        name = None

    result = controller.save_session(name)
    return JSONResponse(content=result)


@app.get("/session/load/{session_name}")
async def load_session(session_name: str):
    """Carga una sesion guardada y la activa."""
    result = controller.load_session(session_name)
    if not result["success"]:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(content=result)


@app.delete("/session/{session_name}")
async def delete_session(session_name: str):
    """Elimina una sesion del disco."""
    result = controller.delete_session(session_name)
    return JSONResponse(content=result)


# ------------------------------------------------------------------
# WebSocket — rotacion en tiempo real
# ------------------------------------------------------------------

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket para rotacion interactiva en tiempo real.

    El frontend envia JSON:
        {"alpha": float, "beta": float, "zoom": float,
         "offset_x": float, "offset_y": float}

    El backend responde con JSON:
        {"success": bool, "projection": {...}, "geometry": {...}}
    """
    await websocket.accept()
    print("WebSocket conectado")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({"success": False,
                                "message": "JSON invalido"})
                )
                continue

            alpha    = float(msg.get("alpha",    0.0))
            beta     = float(msg.get("beta",     0.0))
            zoom     = float(msg.get("zoom",     1.0))
            offset_x = float(msg.get("offset_x", 0.0))
            offset_y = float(msg.get("offset_y", 0.0))
            D        = float(msg.get("D",        500.0))

            # Actualizar distancia focal antes de re-proyectar
            controller.math.projection.D = D

            result = controller.reproject(
                alpha=alpha, beta=beta,
                zoom=zoom,
                offset_x=offset_x,
                offset_y=offset_y
            )

            await websocket.send_text(json.dumps(result))

    except WebSocketDisconnect:
        print("WebSocket desconectado")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_text(
                json.dumps({"success": False, "message": str(e)})
            )
        except Exception:
            pass