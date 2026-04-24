
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

---

## Requisitos

- Windows 11
- Python 3.11 (MediaPipe/face-alignment no soporta 3.12+)
- Git
- VSCode + extension GitLens

---

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

---

## Inicio del servidor

Dos formas equivalentes — elige la que prefieras:

### Opcion A — mas corta (desde terminal con venv activo)

```cmd
python app.py
```

### Opcion B — abre navegador automaticamente

```cmd
python run.py
```


## Uso

1. Clic en **+ Subir imagen** o usar **Webcam**
2. Ajustar **Densidad landmarks** (0=68pts, 1=~250pts, 2=~700pts, 3=~2000pts)
3. Activar/desactivar **Voronoi** y **Mostrar puntos**
4. Arrastrar mouse en **Panel 04** para rotar la malla 3D
5. Usar sliders **Alpha / Beta / Zoom / D** para controlar la proyeccion
6. Clic en **Guardar sesion** para guardar los datos
7. Clic en una sesion de la lista para recargarla

---

## Estructura del proyecto
facemesh3d/
├── app.py                        ← FastAPI entry point
├── run.py                        ← Inicio con auto-browser
├── run.bat                       ← Inicio con doble clic Windows
├── requirements.txt
├── README.md
│
├── controllers/
│   └── face_controller.py        ← Orquesta el flujo MVC
│
├── models/
│   ├── face_detector.py          ← Deteccion facial + frente sintetica
│   ├── geometry_engine.py        ← Delaunay + Voronoi (SciPy)
│   ├── projection_3d.py          ← Formulas XT YT ZT + perspectiva
│   └── session_manager.py        ← Manejo de sesiones
│
├── services/
│   ├── camera_service.py         ← Webcam + carga de archivo
│   ├── math_service.py           ← Pipeline matematico completo
│   └── storage_service.py        ← Guardar/cargar sesiones JSON
│
├── static/
│   ├── css/style.css             ← Tema oscuro verde/negro
│   └── js/
│       ├── renderer.js           ← Dibuja en canvas (6 paneles)
│       ├── orbitControls.js      ← Mouse drag + zoom para Panel 04
│       └── wsClient.js           ← WebSocket + fetch upload
│
├── templates/
│   └── index.html                ← UI principal 6 paneles
│
├── storage/
│   └── sessions/                 ← Sesiones guardadas (.json)
│
└── tests/
├── test_geometry.py
├── test_projection.py
├── test_services.py
├── test_face_detector.py
└── test_websocket.py

---

## Arquitectura — Patron MVC + OOP
Usuario
│
├── POST /upload  ──→ FaceController
├── WS  /ws/stream ──→ FaceController.reproject()
└── GET /sessions  ──→ FaceController.list_sessions()
│
├── CameraService    (carga imagen / webcam)
├── MathService      (detecta → geometria → proyecta)
│     ├── FaceDetector    (68 landmarks + frente)
│     ├── GeometryEngine  (Delaunay + Voronoi)
│     └── Projection3D   (XT YT ZT + perspectiva)
└── StorageService   (JSON en disco)

---

## Control de versiones

| Rama | Uso |
|------|-----|
| `dev` | Desarrollo activo |
| `master` | Produccion estable |
| `v1.0` | Version inicial completa |

### Flujo de trabajo Git

```cmd
# Trabajar siempre en dev
git checkout dev

# Commit en momentos clave
git add .
git commit -m "feat: descripcion del cambio"
git push origin dev

# Cuando una fase esta completa → merge a main
git checkout master
git merge dev --no-ff -m "merge: descripcion"
git push origin master

## Problemas conocidos

| Problema | Solucion |
|----------|----------|
| MediaPipe no instala | Usar Python 3.11 exactamente |
| `mp.solutions` no existe | face-alignment reemplaza mediapipe |
| WebSocket desconectado | Se reconecta automaticamente cada 2s |
| Frente no cubierta | Activar `add_forehead=True` (default) |
| Landmarks lentos | Reducir nivel de densidad a 0 o 1 |

---