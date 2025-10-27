from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.manager import ConnectionManager
from app.services.command_service import CommandService
from app.services.chat_service import ChatService
import json

router = APIRouter()
manager = ConnectionManager()
command_service = CommandService(manager)
chat_service = ChatService(manager)
# Lưu kết nối theo loại và ID
connected_agents = {}
connected_clients = {}

@router.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await manager.connect(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()

            # Data dạng: JSON string {"type": "...", "to": "...", "payload": {...}}
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                continue

            identity = message.get("client_id")
            connected_clients[identity] = websocket
            print(f"[+] Mobile client registered: {identity}")

            msg_type = message.get("type")
            target_id = message.get("to")
            payload = message.get("payload", {})

            if msg_type == "command":
                await command_service.send_command(target_id, payload.get("cmd_type"), payload)
            elif msg_type == "chat":
                await chat_service.relay_message(device_id, target_id, payload.get("message"))
            elif msg_type == "get_list_running_process":
                agent_id = message.get("agent_id")
                if agent_id in connected_agents:
                    await connected_agents[agent_id].send(json.dumps({
                        "type": "get_list_running_process",
                        "data": message.get("data"),
                        "controller_id": identity,
                    }))
                    print(f"[<] Forwarded get_list_running_process to client {identity}")
    
            elif msg_type == "forward_list_running_process":
                controller_id = message.get("controller_id")
                if controller_id in connected_clients:
                    await connected_clients[controller_id].send(json.dumps({
                        "type": "forward_list_running_process",
                        "data": message.get("data"),
                        "agent_id": message.get("agent_id"),
                    }))
                    print(f"[<] Forwarded forward_list_running_process to client {controller_id}")
                    
            elif msg_type == "ping":
                await websocket.send_text("pong")
            elif msg_type == "command_result":
                client_id = message.get("client_id")
                if client_id in connected_clients:
                    await connected_clients[client_id].send(json.dumps({
                        "type": "command_result",
                        "data": message.get("data"),
                        "agent_id": message.get("agent_id"),
                    }))
                    print(f"[<] Forwarded command_result to client {client_id}")

    except WebSocketDisconnect:
        manager.disconnect(device_id)
