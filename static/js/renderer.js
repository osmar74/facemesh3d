// static/js/renderer.js
'use strict';

const Renderer = (() => {

    const GREEN       = '#00ff41';
    const GREEN_DIM   = '#004d14';
    const GREEN_MID   = '#00aa2a';
    const GREEN_POINT = '#00ff41';
    const BG          = '#000000';

    // ── Utilidades ──────────────────────────────────────────────

    function clearCanvas(canvas) {
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = BG;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    function fitCanvas(canvas) {
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width  = Math.floor(rect.width);
        canvas.height = Math.floor(rect.height - 28); // restar header
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
            const x = (cw - w) / 2;
            const y = (ch - h) / 2;
            ctx.drawImage(img, x, y, w, h);
        };
        img.src = 'data:image/jpeg;base64,' + base64;
    }

    // ── Panel 2: landmarks (puntos) ──────────────────────────────

    function drawLandmarks(canvas, landmarks, imgW, imgH) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!landmarks || landmarks.length === 0) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;
        const scaleX = cw / imgW;
        const scaleY = ch / imgH;
        const scale  = Math.min(scaleX, scaleY);
        const offX   = (cw - imgW * scale) / 2;
        const offY   = (ch - imgH * scale) / 2;

        ctx.fillStyle = GREEN_POINT;
        landmarks.forEach(lm => {
            const px = lm.x * imgW * scale + offX;
            const py = lm.y * imgH * scale + offY;
            ctx.beginPath();
            ctx.arc(px, py, 1.5, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    // ── Panel 3: triangulacion Delaunay ──────────────────────────

    function drawDelaunay(canvas, points2d, simplices, imgW, imgH) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!simplices || simplices.length === 0) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;
        const scale  = Math.min(cw / imgW, ch / imgH);
        const offX   = (cw - imgW * scale) / 2;
        const offY   = (ch - imgH * scale) / 2;

        ctx.strokeStyle = GREEN;
        ctx.lineWidth   = 0.6;

        simplices.forEach(tri => {
            const [i, j, k] = tri;
            const ax = points2d[i][0] * scale + offX;
            const ay = points2d[i][1] * scale + offY;
            const bx = points2d[j][0] * scale + offX;
            const by = points2d[j][1] * scale + offY;
            const cx2 = points2d[k][0] * scale + offX;
            const cy2 = points2d[k][1] * scale + offY;

            ctx.beginPath();
            ctx.moveTo(ax, ay);
            ctx.lineTo(bx, by);
            ctx.lineTo(cx2, cy2);
            ctx.closePath();
            ctx.stroke();
        });

        // Puntos sobre la malla
        ctx.fillStyle = GREEN_MID;
        points2d.forEach(pt => {
            const px = pt[0] * scale + offX;
            const py = pt[1] * scale + offY;
            ctx.beginPath();
            ctx.arc(px, py, 1.2, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    // ── Panel 4: proyeccion 3D (rotacion) ────────────────────────

    function drawProjected(canvas, projected, simplices) {
        fitCanvas(canvas);
        clearCanvas(canvas);
        if (!projected || projected.length === 0) return;

        const ctx = canvas.getContext('2d');
        const cw  = canvas.width;
        const ch  = canvas.height;
        const cx  = cw / 2;
        const cy  = ch / 2;

        // Calcular bounding box para centrar
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

        function toScreen(p) {
            return [
                cx + (p[0] - (minX + maxX) / 2) * scale,
                cy + (p[1] - (minY + maxY) / 2) * scale
            ];
        }

        // Dibujar triangulos si hay simplices
        if (simplices && simplices.length > 0) {
            ctx.strokeStyle = GREEN;
            ctx.lineWidth   = 0.7;

            simplices.forEach(tri => {
                const [i, j, k] = tri;
                if (i >= projected.length || j >= projected.length ||
                    k >= projected.length) return;

                const [ax, ay] = toScreen(projected[i]);
                const [bx, by] = toScreen(projected[j]);
                const [cx2, cy2] = toScreen(projected[k]);

                ctx.beginPath();
                ctx.moveTo(ax, ay);
                ctx.lineTo(bx, by);
                ctx.lineTo(cx2, cy2);
                ctx.closePath();
                ctx.stroke();
            });
        } else {
            // Solo puntos si no hay simplices
            ctx.fillStyle = GREEN;
            projected.forEach(p => {
                const [sx, sy] = toScreen(p);
                ctx.beginPath();
                ctx.arc(sx, sy, 1.5, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Puntos sobre la malla
        ctx.fillStyle = GREEN_MID;
        projected.forEach(p => {
            const [sx, sy] = toScreen(p);
            ctx.beginPath();
            ctx.arc(sx, sy, 1.0, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    // ── API publica ──────────────────────────────────────────────

    return { drawRealImage, drawLandmarks, drawDelaunay, drawProjected, fitCanvas, clearCanvas };

})();