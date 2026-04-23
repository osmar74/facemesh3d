// static/js/orbitControls.js
'use strict';

const OrbitControls = (() => {

    let _canvas   = null;
    let _onChange = null;

    let _alpha    = 0.0;   // rotacion horizontal (rad)
    let _beta     = 0.0;   // rotacion vertical   (rad)
    let _zoom     = 1.0;
    let _offsetX  = 0.0;
    let _offsetY  = 0.0;

    let _dragging   = false;
    let _lastMouseX = 0;
    let _lastMouseY = 0;
    let _sensitivity = 0.005;

    function init(canvas, onChange) {
        _canvas   = canvas;
        _onChange = onChange;

        canvas.addEventListener('mousedown',  onMouseDown);
        canvas.addEventListener('mousemove',  onMouseMove);
        canvas.addEventListener('mouseup',    onMouseUp);
        canvas.addEventListener('mouseleave', onMouseUp);
        canvas.addEventListener('wheel',      onWheel, { passive: true });
    }

    function onMouseDown(e) {
        _dragging   = true;
        _lastMouseX = e.clientX;
        _lastMouseY = e.clientY;
    }

    function onMouseMove(e) {
        if (!_dragging) return;

        const dx = e.clientX - _lastMouseX;
        const dy = e.clientY - _lastMouseY;

        _alpha += dx * _sensitivity;
        _beta  += dy * _sensitivity;

        // Limitar beta para evitar voltear el modelo
        _beta = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, _beta));

        _lastMouseX = e.clientX;
        _lastMouseY = e.clientY;

        if (_onChange) _onChange(getState());
    }

    function onMouseUp() {
        _dragging = false;
    }

    function onWheel(e) {
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        _zoom = Math.max(0.2, Math.min(5.0, _zoom + delta));
        if (_onChange) _onChange(getState());
    }

    function getState() {
        return {
            alpha:   _alpha,
            beta:    _beta,
            zoom:    _zoom,
            offset_x: _offsetX,
            offset_y: _offsetY
        };
    }

    function setState(alpha, beta, zoom) {
        _alpha = alpha || 0.0;
        _beta  = beta  || 0.0;
        _zoom  = zoom  || 1.0;
    }

    function reset() {
        _alpha   = 0.0;
        _beta    = 0.0;
        _zoom    = 1.0;
        _offsetX = 0.0;
        _offsetY = 0.0;
        if (_onChange) _onChange(getState());
    }

    function setSensitivity(s) { _sensitivity = s; }

    return { init, reset, getState, setState, setSensitivity };

})();