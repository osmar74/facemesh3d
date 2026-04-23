
# FaceMesh3D — Triangulacion Delaunay/Voronoi Facial 3D

Aplicacion web que detecta landmarks faciales y genera una malla 3D
interactiva usando Triangulacion de Delaunay y diagrama de Voronoi.

## Tecnologias

- **Backend**: Python 3.11, FastAPI, WebSocket, face-alignment, SciPy, OpenCV
- **Frontend**: HTML5 Canvas, JavaScript vanilla, tema oscuro
- **Geometria**: Triangulacion Delaunay, Voronoi, proyeccion perspectiva 3D

## Formulas implementadas
Rotacion 3D:
XT = Xcos(a) - Zsin(a)
YT = Ycos(b) - Zcos(a)sin(b) - Xsin(a)sin(b)
ZT = Zcos(a)cos(b) + Xsin(a)cos(b) + Ysin(b)
Proyeccion perspectiva:
XT_proj = D * XT / (D - ZT)
YT_proj = D * YT / (D - ZT)

## Instalacion

```cmd
git clone https://github.com/TU_USUARIO/facemesh3d.git
cd facemesh3d
"D:\Program Files\Python311\python.exe" -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Uso

```cmd
venv\Scripts\activate.bat
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Abrir: http://127.0.0.1:8000

## Paneles

| Panel | Descripcion |
|-------|-------------|
| 01 | Imagen original |
| 02a | Foto con landmarks superpuestos |
| 02b | Solo landmarks sobre fondo negro |
| 03a | Foto con triangulacion Delaunay |
| 03b | Triangulacion Delaunay y Voronoi |
| 04 | Proyeccion 3D interactiva con ejes XYZ |

## Arquitectura

Patron MVC con OOP:
- `models/` — FaceDetector, GeometryEngine, Projection3D, SessionManager
- `services/` — CameraService, MathService, StorageService
- `controllers/` — FaceController
- `app.py` — FastAPI entry point

## Control de versiones

- Rama `dev` — desarrollo
- Rama `master` — produccion estable
- Tag `v1.0` — version inicial completa