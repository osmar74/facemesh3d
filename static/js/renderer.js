// static/js/renderer.js
'use strict';

const Renderer = (() => {

    const GREEN       = '#00ff41';
    const GREEN_DIM   = '#004d14';
    const GREEN_MID   = '#00aa2a';
    const GREEN_POINT = '#00ff41';
    const VORONOI_COL = '#005518';
    const BG          = '#000000';

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

    // ── Panel 1: imagen real ─────────────────────────────────────

    function drawRealImage(canvas, base64) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!base64) return;
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.onload = () => {
            const cw = canvas.width, ch = canvas.height;
            const scale = Math.min(cw / img.width, ch / img.height);
            const w = img.width  * scale;
            const h = img.height * scale;
            ctx.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
        };
        img.src = 'data:image/jpeg;base64,' + base64;
    }

    // ── Panel 2a: foto + landmarks superpuestos ──────────────────

    function drawLandmarksOnImage(canvas, base64, landmarks, imgW, imgH) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!base64) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;
        const img = new Image();

        img.onload = () => {
            const scale = Math.min(cw / img.width, ch / img.height);
            const dw    = img.width  * scale;
            const dh    = img.height * scale;
            const offX  = (cw - dw) / 2;
            const offY  = (ch - dh) / 2;

            // Dibujar imagen con opacidad reducida
            ctx.globalAlpha = 0.55;
            ctx.drawImage(img, offX, offY, dw, dh);
            ctx.globalAlpha = 1.0;

            // Dibujar puntos encima
            if (!landmarks || landmarks.length === 0) return;
            ctx.fillStyle = GREEN_POINT;
            landmarks.forEach(lm => {
                const px = lm.x * imgW * scale + offX;
                const py = lm.y * imgH * scale + offY;
                ctx.beginPath();
                ctx.arc(px, py, 2.0, 0, Math.PI * 2);
                ctx.fill();
            });

            // Anillo verde sutil alrededor de cada punto
            ctx.strokeStyle = GREEN_DIM;
            ctx.lineWidth   = 0.5;
            landmarks.forEach(lm => {
                const px = lm.x * imgW * scale + offX;
                const py = lm.y * imgH * scale + offY;
                ctx.beginPath();
                ctx.arc(px, py, 3.5, 0, Math.PI * 2);
                ctx.stroke();
            });
        };

        img.src = 'data:image/jpeg;base64,' + base64;
    }

    // ── Panel 2b: solo landmarks (puntos) ────────────────────────

    function drawLandmarks(canvas, landmarks, imgW, imgH) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!landmarks || landmarks.length === 0) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;
        const scale = Math.min(cw / imgW, ch / imgH);
        const offX  = (cw - imgW * scale) / 2;
        const offY  = (ch - imgH * scale) / 2;

        // Puntos principales
        ctx.fillStyle = GREEN_POINT;
        landmarks.forEach(lm => {
            const px = lm.x * imgW * scale + offX;
            const py = lm.y * imgH * scale + offY;
            ctx.beginPath();
            ctx.arc(px, py, 1.8, 0, Math.PI * 2);
            ctx.fill();
        });

        // Lineas conectoras sutiles entre puntos consecutivos
        ctx.strokeStyle = GREEN_DIM;
        ctx.lineWidth   = 0.3;
        ctx.beginPath();
        landmarks.forEach((lm, i) => {
            const px = lm.x * imgW * scale + offX;
            const py = lm.y * imgH * scale + offY;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        });
        ctx.stroke();
    }

    // ── Panel 3: Delaunay + Voronoi opcional ─────────────────────

    function drawDelaunay(canvas, points2d, simplices, imgW, imgH,
                          voronoiData, showVoronoi) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!points2d || points2d.length === 0) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;
        const scale = Math.min(cw / imgW, ch / imgH);
        const offX  = (cw - imgW * scale) / 2;
        const offY  = (ch - imgH * scale) / 2;

        // Voronoi debajo (si esta habilitado)
        if (showVoronoi && voronoiData && voronoiData.vertices &&
            voronoiData.ridge_vertices) {
            ctx.strokeStyle = VORONOI_COL;
            ctx.lineWidth   = 0.8;

            voronoiData.ridge_vertices.forEach(rv => {
                if (rv[0] < 0 || rv[1] < 0) return;
                const v0 = voronoiData.vertices[rv[0]];
                const v1 = voronoiData.vertices[rv[1]];
                if (!v0 || !v1) return;

                const ax = v0[0] * scale + offX;
                const ay = v0[1] * scale + offY;
                const bx = v1[0] * scale + offX;
                const by = v1[1] * scale + offY;

                // Solo dibujar si esta dentro del canvas
                if (ax < 0 || ay < 0 || bx < 0 || by < 0) return;
                if (ax > cw || ay > ch || bx > cw || by > ch) return;

                ctx.beginPath();
                ctx.moveTo(ax, ay);
                ctx.lineTo(bx, by);
                ctx.stroke();
            });
        }

        // Triangulacion Delaunay encima
        if (simplices && simplices.length > 0) {
            ctx.strokeStyle = GREEN;
            ctx.lineWidth   = 0.6;

            simplices.forEach(tri => {
                const [i, j, k] = tri;
                const ax  = points2d[i][0] * scale + offX;
                const ay  = points2d[i][1] * scale + offY;
                const bx  = points2d[j][0] * scale + offX;
                const by  = points2d[j][1] * scale + offY;
                const cx2 = points2d[k][0] * scale + offX;
                const cy2 = points2d[k][1] * scale + offY;
                ctx.beginPath();
                ctx.moveTo(ax, ay);
                ctx.lineTo(bx, by);
                ctx.lineTo(cx2, cy2);
                ctx.closePath();
                ctx.stroke();
            });
        }

        // Puntos
        if (document.getElementById('chk-points') &&
            document.getElementById('chk-points').checked) {
            ctx.fillStyle = GREEN_MID;
            points2d.forEach(pt => {
                const px = pt[0] * scale + offX;
                const py = pt[1] * scale + offY;
                ctx.beginPath();
                ctx.arc(px, py, 1.2, 0, Math.PI * 2);
                ctx.fill();
            });
        }
    }

    // ── Panel 4: proyeccion 3D ───────────────────────────────────

    function drawProjected(canvas, projected, simplices) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!projected || projected.length === 0) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;

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
        const cx = cw / 2;
        const cy = ch / 2;
        const midX = (minX + maxX) / 2;
        const midY = (minY + maxY) / 2;

        function toScreen(p) {
            return [
                cx + (p[0] - midX) * scale,
                cy + (p[1] - midY) * scale
            ];
        }

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

        ctx.fillStyle = GREEN_MID;
        projected.forEach(p => {
            const [sx, sy] = toScreen(p);
            ctx.beginPath();
            ctx.arc(sx, sy, 1.0, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    return {
        drawRealImage, drawLandmarksOnImage, drawLandmarks,
        drawDelaunay, drawProjected, fitCanvas, clearCanvas
    };

})();