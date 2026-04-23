// static/js/wsClient.js
'use strict';

const WsClient = (() => {

    let _ws        = null;
    let _onData    = null;
    let _onStatus  = null;
    let _connected = false;
    let _throttle  = null;
    const THROTTLE_MS = 40;  // max 25 fps al WebSocket

    function connect(onData, onStatus) {
        _onData   = onData;
        _onStatus = onStatus;

        const proto = location.protocol === 'https:' ? 'wss' : 'ws';
        const url   = `${proto}://${location.host}/ws/stream`;

        _ws = new WebSocket(url);

        _ws.onopen = () => {
            _connected = true;
            if (_onStatus) _onStatus('ws-conectado', true);
        };

        _ws.onmessage = (evt) => {
            try {
                const data = JSON.parse(evt.data);
                if (_onData) _onData(data);
            } catch (e) {
                console.error('WS parse error:', e);
            }
        };

        _ws.onerror = (e) => {
            console.error('WS error:', e);
            if (_onStatus) _onStatus('ws-error', false);
        };

        _ws.onclose = () => {
            _connected = false;
            if (_onStatus) _onStatus('ws-desconectado', false);
            // Reconectar en 2s
            setTimeout(() => connect(_onData, _onStatus), 2000);
        };
    }

    function send(payload) {
        if (!_connected || !_ws) return;
        // Throttle para no saturar el WebSocket
        if (_throttle) return;
        _throttle = setTimeout(() => { _throttle = null; }, THROTTLE_MS);
        _ws.send(JSON.stringify(payload));
    }

    function disconnect() {
        if (_ws) { _ws.onclose = null; _ws.close(); }
        _connected = false;
    }

    function isConnected() { return _connected; }

    // ── Upload de imagen via fetch ────────────────────────────────

    async function uploadImage(file, levels) {
        const formData = new FormData();
        formData.append('file', file);

        const lvl = (levels !== undefined) ? levels : 1;
        const url = `/upload?levels=${lvl}`;

        const resp = await fetch(url, {
            method: 'POST',
            body: formData
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.message || `HTTP ${resp.status}`);
        }
        return await resp.json();
    }

    // ── Sesiones ─────────────────────────────────────────────────

    async function saveSesion(name) {
        const resp = await fetch('/session/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_name: name || null })
        });
        return await resp.json();
    }

    async function loadSesion(name) {
        const resp = await fetch(`/session/load/${encodeURIComponent(name)}`);
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.message || `HTTP ${resp.status}`);
        }
        return await resp.json();
    }

    async function listSesiones() {
        const resp = await fetch('/sessions');
        return await resp.json();
    }

    async function deleteSesion(name) {
        const resp = await fetch(`/session/${encodeURIComponent(name)}`,
                                 { method: 'DELETE' });
        return await resp.json();
    }

    return {
        connect, send, disconnect, isConnected,
        uploadImage, saveSesion, loadSesion, listSesiones, deleteSesion
    };

})();