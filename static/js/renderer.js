// static/js/renderer.js
'use strict';

const Renderer = (() => {

    const GREEN       = '#00ff41';
    const GREEN_DIM   = '#004d14';
    const GREEN_MID   = '#00aa2a';
    const GREEN_POINT = '#00ff41';
    const VORONOI_COL = '#005518';
    const BG          = '#000000';

    // Colores ejes XYZ (distinguibles en fondo negro)
    const AXIS_X = '#ff4444';   // rojo
    const AXIS_Y = '#44ff44';   // verde claro
    const AXIS_Z = '#4488ff';   // azul

    function clearCanvas(canvas) {
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = BG;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    function fitCanvas(canvas) {
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width  = Math.floor(rect.width);
        canvas.height = Math.floor(rect.height - 28);
    }

    // ── Rotacion de un vector 3D con las formulas del proyecto ────

    function rotateVec(x, y, z, alpha, beta) {
        const ca = Math.cos(alpha), sa = Math.sin(alpha);
        const cb = Math.cos(beta),  sb = Math.sin(beta);
        const XT =  x * ca - z * sa;
        const YT =  y * cb - z * ca * sb - x * sa * sb;
        // ZT no se usa en proyeccion 2D de los ejes
        return [XT, YT];
    }

    // ── Panel 1: imagen real ──────────────────────────────────────

    function drawRealImage(canvas, base64) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!base64) return;
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.onload = () => {
            const cw = canvas.width, ch = canvas.height;
            const sc = Math.min(cw / img.width, ch / img.height);
            const w  = img.width * sc, h = img.height * sc;
            ctx.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
        };
        img.src = 'data:image/jpeg;base64,' + base64;
    }

    // ── Panel 2a: foto + landmarks superpuestos ───────────────────

    function drawLandmarksOnImage(canvas, base64, landmarks,
                                   imgW, imgH, showPoints) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!base64) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width, ch = canvas.height;
        const img = new Image();

        img.onload = () => {
            const sc   = Math.min(cw / img.width, ch / img.height);
            const dw   = img.width * sc,  dh = img.height * sc;
            const offX = (cw - dw) / 2,   offY = (ch - dh) / 2;

            // Foto con opacidad reducida
            ctx.globalAlpha = 0.55;
            ctx.drawImage(img, offX, offY, dw, dh);
            ctx.globalAlpha = 1.0;

            if (!showPoints || !landmarks || landmarks.length === 0) return;

            // Puntos verdes
            ctx.fillStyle = GREEN_POINT;
            landmarks.forEach(lm => {
                const px = lm.x * imgW * sc + offX;
                const py = lm.y * imgH * sc + offY;
                ctx.beginPath();
                ctx.arc(px, py, 2.0, 0, Math.PI * 2);
                ctx.fill();
            });

            // Anillo sutil
            ctx.strokeStyle = GREEN_DIM;
            ctx.lineWidth   = 0.5;
            landmarks.forEach(lm => {
                const px = lm.x * imgW * sc + offX;
                const py = lm.y * imgH * sc + offY;
                ctx.beginPath();
                ctx.arc(px, py, 3.5, 0, Math.PI * 2);
                ctx.stroke();
            });
        };

        img.src = 'data:image/jpeg;base64,' + base64;
    }

    // ── Panel 2b: solo landmarks (puntos) ─────────────────────────

    function drawLandmarks(canvas, landmarks, imgW, imgH, showPoints) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!landmarks || landmarks.length === 0) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width, ch = canvas.height;
        const sc  = Math.min(cw / imgW, ch / imgH);
        const offX = (cw - imgW * sc) / 2;
        const offY = (ch - imgH * sc) / 2;

        // Lineas conectoras sutiles siempre visibles
        ctx.strokeStyle = GREEN_DIM;
        ctx.lineWidth   = 0.3;
        ctx.beginPath();
        landmarks.forEach((lm, i) => {
            const px = lm.x * imgW * sc + offX;
            const py = lm.y * imgH * sc + offY;
            i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
        });
        ctx.stroke();

        // Puntos solo si showPoints
        if (!showPoints) return;
        ctx.fillStyle = GREEN_POINT;
        landmarks.forEach(lm => {
            const px = lm.x * imgW * sc + offX;
            const py = lm.y * imgH * sc + offY;
            ctx.beginPath();
            ctx.arc(px, py, 1.8, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    // ── Panel 3a: foto + triangulacion superpuesta ────────────────

    function drawDelaunayOnImage(canvas, base64, points2d, simplices,
                                  imgW, imgH, voronoiData, showVoronoi,
                                  showPoints) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!base64) return;

        const ctx  = canvas.getContext('2d');
        const cw   = canvas.width, ch = canvas.height;
        const img  = new Image();

        img.onload = () => {
            const sc   = Math.min(cw / img.width, ch / img.height);
            const dw   = img.width * sc,  dh = img.height * sc;
            const offX = (cw - dw) / 2,   offY = (ch - dh) / 2;

            // Foto con opacidad reducida
            ctx.globalAlpha = 0.45;
            ctx.drawImage(img, offX, offY, dw, dh);
            ctx.globalAlpha = 1.0;

            if (!points2d || points2d.length === 0) return;

            // Voronoi primero (debajo)
            if (showVoronoi && voronoiData && voronoiData.ridge_vertices) {
                ctx.strokeStyle = VORONOI_COL;
                ctx.lineWidth   = 0.8;
                voronoiData.ridge_vertices.forEach(rv => {
                    if (rv[0] < 0 || rv[1] < 0) return;
                    const v0 = voronoiData.vertices[rv[0]];
                    const v1 = voronoiData.vertices[rv[1]];
                    if (!v0 || !v1) return;
                    const ax = v0[0] * sc + offX, ay = v0[1] * sc + offY;
                    const bx = v1[0] * sc + offX, by = v1[1] * sc + offY;
                    if (ax < 0 || ay < 0 || bx < 0 || by < 0) return;
                    if (ax > cw || ay > ch || bx > cw || by > ch) return;
                    ctx.beginPath();
                    ctx.moveTo(ax, ay);
                    ctx.lineTo(bx, by);
                    ctx.stroke();
                });
            }

            // Delaunay encima
            if (simplices && simplices.length > 0) {
                ctx.strokeStyle = GREEN;
                ctx.lineWidth   = 0.7;
                simplices.forEach(tri => {
                    const [i, j, k] = tri;
                    const ax  = points2d[i][0] * sc + offX;
                    const ay  = points2d[i][1] * sc + offY;
                    const bx  = points2d[j][0] * sc + offX;
                    const by  = points2d[j][1] * sc + offY;
                    const cx2 = points2d[k][0] * sc + offX;
                    const cy2 = points2d[k][1] * sc + offY;
                    ctx.beginPath();
                    ctx.moveTo(ax, ay);
                    ctx.lineTo(bx, by);
                    ctx.lineTo(cx2, cy2);
                    ctx.closePath();
                    ctx.stroke();
                });
            }

            // Puntos
            if (showPoints) {
                ctx.fillStyle = GREEN_MID;
                points2d.forEach(pt => {
                    const px = pt[0] * sc + offX;
                    const py = pt[1] * sc + offY;
                    ctx.beginPath();
                    ctx.arc(px, py, 1.2, 0, Math.PI * 2);
                    ctx.fill();
                });
            }
        };

        img.src = 'data:image/jpeg;base64,' + base64;
    }

    // ── Panel 3b: solo triangulacion / Voronoi ────────────────────

    function drawDelaunay(canvas, points2d, simplices, imgW, imgH,
                          voronoiData, showVoronoi, showPoints) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!points2d || points2d.length === 0) return;

        const ctx  = canvas.getContext('2d');
        const cw   = canvas.width, ch = canvas.height;
        const sc   = Math.min(cw / imgW, ch / imgH);
        const offX = (cw - imgW * sc) / 2;
        const offY = (ch - imgH * sc) / 2;

        // Voronoi
        if (showVoronoi && voronoiData && voronoiData.ridge_vertices) {
            ctx.strokeStyle = VORONOI_COL;
            ctx.lineWidth   = 0.8;
            voronoiData.ridge_vertices.forEach(rv => {
                if (rv[0] < 0 || rv[1] < 0) return;
                const v0 = voronoiData.vertices[rv[0]];
                const v1 = voronoiData.vertices[rv[1]];
                if (!v0 || !v1) return;
                const ax = v0[0] * sc + offX, ay = v0[1] * sc + offY;
                const bx = v1[0] * sc + offX, by = v1[1] * sc + offY;
                if (ax < 0 || ay < 0 || bx < 0 || by < 0) return;
                if (ax > cw || ay > ch || bx > cw || by > ch) return;
                ctx.beginPath();
                ctx.moveTo(ax, ay);
                ctx.lineTo(bx, by);
                ctx.stroke();
            });
        }

        // Delaunay
        if (simplices && simplices.length > 0) {
            ctx.strokeStyle = GREEN;
            ctx.lineWidth   = 0.6;
            simplices.forEach(tri => {
                const [i, j, k] = tri;
                const ax  = points2d[i][0] * sc + offX;
                const ay  = points2d[i][1] * sc + offY;
                const bx  = points2d[j][0] * sc + offX;
                const by  = points2d[j][1] * sc + offY;
                const cx2 = points2d[k][0] * sc + offX;
                const cy2 = points2d[k][1] * sc + offY;
                ctx.beginPath();
                ctx.moveTo(ax, ay);
                ctx.lineTo(bx, by);
                ctx.lineTo(cx2, cy2);
                ctx.closePath();
                ctx.stroke();
            });
        }

        // Puntos
        if (showPoints) {
            ctx.fillStyle = GREEN_MID;
            points2d.forEach(pt => {
                const px = pt[0] * sc + offX;
                const py = pt[1] * sc + offY;
                ctx.beginPath();
                ctx.arc(px, py, 1.2, 0, Math.PI * 2);
                ctx.fill();
            });
        }
    }

    // ── Panel 4: proyeccion 3D + ejes XYZ ────────────────────────

    function drawProjected(canvas, projected, simplices, alpha, beta) {
        fitCanvas(canvas);
        clearCanvas(canvas);

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;

        if (projected && projected.length > 0) {
            const xs = projected.map(p => p[0]);
            const ys = projected.map(p => p[1]);
            const minX = Math.min(...xs), maxX = Math.max(...xs);
            const minY = Math.min(...ys), maxY = Math.max(...ys);
            const rangeX = maxX - minX || 1;
            const rangeY = maxY - minY || 1;
            const margin = 30;
            const scale  = Math.min(
                (cw - margin * 2) / rangeX,
                (ch - margin * 2) / rangeY
            );
            const midX = (minX + maxX) / 2;
            const midY = (minY + maxY) / 2;

            function toScreen(p) {
                return [
                    cw / 2 + (p[0] - midX) * scale,
                    ch / 2 + (p[1] - midY) * scale
                ];
            }

            // Triangulos
            if (simplices && simplices.length > 0) {
                ctx.strokeStyle = GREEN;
                ctx.lineWidth   = 0.7;
                simplices.forEach(tri => {
                    const [i, j, k] = tri;
                    if (i >= projected.length || j >= projected.length ||
                        k >= projected.length) return;
                    const [ax, ay]   = toScreen(projected[i]);
                    const [bx, by]   = toScreen(projected[j]);
                    const [cx2, cy2] = toScreen(projected[k]);
                    ctx.beginPath();
                    ctx.moveTo(ax, ay);
                    ctx.lineTo(bx, by);
                    ctx.lineTo(cx2, cy2);
                    ctx.closePath();
                    ctx.stroke();
                });
            } else {
                ctx.fillStyle = GREEN;
                projected.forEach(p => {
                    const [sx, sy] = toScreen(p);
                    ctx.beginPath();
                    ctx.arc(sx, sy, 1.5, 0, Math.PI * 2);
                    ctx.fill();
                });
            }

            // Puntos
            ctx.fillStyle = GREEN_MID;
            projected.forEach(p => {
                const [sx, sy] = toScreen(p);
                ctx.beginPath();
                ctx.arc(sx, sy, 1.0, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // ── Ejes XYZ en esquina inferior izquierda ──────────────
        _drawAxes(ctx, cw, ch, alpha || 0, beta || 0);
    }

    function _drawAxes(ctx, cw, ch, alpha, beta) {
        const ox  = 54;           // origen X desde izquierda
        const oy  = ch - 54;      // origen Y desde abajo
        const len = 36;           // longitud de cada eje en px

        // Fondo semitransparente detrás de los ejes
        ctx.fillStyle = 'rgba(0,0,0,0.55)';
        ctx.beginPath();
        ctx.arc(ox, oy, 50, 0, Math.PI * 2);
        ctx.fill();

        // Circulo borde
        ctx.strokeStyle = '#1a1a1a';
        ctx.lineWidth   = 1;
        ctx.beginPath();
        ctx.arc(ox, oy, 50, 0, Math.PI * 2);
        ctx.stroke();

        // Vectores unitarios rotados con las mismas formulas del backend
        const axes = [
            { vec: [1, 0, 0], col: AXIS_X, label: 'X' },
            { vec: [0, 1, 0], col: AXIS_Y, label: 'Y' },
            { vec: [0, 0, 1], col: AXIS_Z, label: 'Z' }
        ];

        // Ordenar por profundidad ZT para dibujar el mas lejano primero
        const ca = Math.cos(alpha), sa = Math.sin(alpha);
        const cb = Math.cos(beta),  sb = Math.sin(beta);

        function rotFull(x, y, z) {
            const XT =  x * ca - z * sa;
            const YT =  y * cb - z * ca * sb - x * sa * sb;
            const ZT =  z * ca * cb + x * sa * cb + y * sb;
            return [XT, YT, ZT];
        }

        const rendered = axes.map(ax => {
            const [x, y, z] = ax.vec;
            const [XT, YT, ZT] = rotFull(x, y, z);
            return { ...ax, XT, YT, ZT };
        }).sort((a, b) => a.ZT - b.ZT);  // primero los mas lejanos

        rendered.forEach(ax => {
            const ex = ox + ax.XT * len;
            const ey = oy - ax.YT * len;   // Y invertido en canvas

            // Linea del eje
            ctx.strokeStyle = ax.col;
            ctx.lineWidth   = 2;
            ctx.beginPath();
            ctx.moveTo(ox, oy);
            ctx.lineTo(ex, ey);
            ctx.stroke();

            // Punta de flecha
            const angle = Math.atan2(ey - oy, ex - ox);
            ctx.fillStyle = ax.col;
            ctx.beginPath();
            ctx.moveTo(ex, ey);
            ctx.lineTo(ex - 7 * Math.cos(angle - 0.4),
                       ey - 7 * Math.sin(angle - 0.4));
            ctx.lineTo(ex - 7 * Math.cos(angle + 0.4),
                       ey - 7 * Math.sin(angle + 0.4));
            ctx.closePath();
            ctx.fill();

            // Etiqueta
            ctx.fillStyle   = ax.col;
            ctx.font        = 'bold 11px Courier New';
            ctx.textAlign   = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(ax.label,
                         ox + ax.XT * (len + 12),
                         oy - ax.YT * (len + 12));
        });

        // Punto de origen
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(ox, oy, 2.5, 0, Math.PI * 2);
        ctx.fill();
    }

    return {
        drawRealImage,
        drawLandmarksOnImage,
        drawLandmarks,
        drawDelaunayOnImage,
        drawDelaunay,
        drawProjected,
        fitCanvas,
        clearCanvas
    };

})();