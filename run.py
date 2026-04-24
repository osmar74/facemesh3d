# run.py
import subprocess
import sys
import os
import webbrowser
import time
import threading


def open_browser():
    """Abre el navegador 2 segundos despues de iniciar."""
    time.sleep(2.5)
    webbrowser.open("http://127.0.0.1:8000")


def main():
    host = "127.0.0.1"
    port = 8000

    print("=" * 45)
    print("  FaceMesh3D — Triangulacion Delaunay/Voronoi")
    print("=" * 45)
    print(f"  URL : http://{host}:{port}")
    print(f"  Modo: desarrollo (--reload activo)")
    print("  Para detener: Ctrl+C")
    print("=" * 45)

    # Abrir navegador automaticamente
    threading.Thread(target=open_browser, daemon=True).start()

    # Iniciar servidor
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app:app",
        "--host", host,
        "--port", str(port),
        "--reload"
    ])


if __name__ == "__main__":
    main()