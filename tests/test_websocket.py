# tests/test_websocket.py
import asyncio
import websockets
import json


async def test():
    uri = "ws://127.0.0.1:8000/ws/stream"
    async with websockets.connect(uri) as ws:
        msg = json.dumps({
            "alpha": 0.5,
            "beta": 0.3,
            "zoom": 1.0,
            "offset_x": 0.0,
            "offset_y": 0.0
        })
        await ws.send(msg)
        resp = await ws.recv()
        data = json.loads(resp)
        print("WebSocket respuesta success:", data["success"])
        print("Mensaje:", data.get("message", "OK"))


if __name__ == "__main__":
    asyncio.run(test())