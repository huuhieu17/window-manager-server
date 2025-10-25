from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # key: device_id, value: websocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        print(f"[+] Device {device_id} connected")

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            print(f"[-] Device {device_id} disconnected")

    async def send_to_device(self, device_id: str, message: str):
        ws = self.active_connections.get(device_id)
        if ws:
            await ws.send_text(message)

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            await ws.send_text(message)

    def get_online_devices(self):
        return list(self.active_connections.keys())
