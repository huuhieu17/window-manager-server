from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.manager import ConnectionManager
from app.services.command_service import CommandService
from app.services.chat_service import ChatService
import json

router = APIRouter()
manager = ConnectionManager()
command_service = CommandService(manager)
chat_service = ChatService(manager)

@router.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await manager.connect(device_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse JSON
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                continue  # Ignore invalid JSON
            
            identity = message.get("client_id") or device_id
            msg_type = message.get("type")
            target_id = message.get("to")
            payload = message.get("payload", {})

            # ----- CONNECT AGENT -----
            if msg_type == "connect_agent":
                if target_id in manager.active_connections:
                    await manager.send_to_device(identity, json.dumps({
                        "type": "connect_success",
                        "message": "Connected to agent successfully.",
                        "agent_id": identity,
                    }))
                    print(f"[+] {identity} connected to: {target_id}")
                    await manager.send_to_device(target_id,json.dumps({
                        "type": "connect_success",
                        "message": "Connected to controller successfully.",
                        "controller_id": identity,
                    }))
                else:
                    await manager.send_to_device(identity, json.dumps({
                        "type": "error",
                        "message": f"Agent {target_id} not connected"
                    }))
                continue

            # ----- COMMAND -----
            elif msg_type == "command":
                await command_service.send_command(target_id, payload.get("cmd_type"), payload)
                continue

            # ----- CHAT -----
            elif msg_type == "chat":
                await chat_service.relay_message(device_id, target_id, payload.get("message"))
                continue

            # ----- FORWARD LIST RUNNING PROCESS -----
            elif msg_type == "forward_list_running_process":
                controller_id = message.get("client_id")
                if controller_id in manager.active_connections:
                    await manager.send_to_device(controller_id, json.dumps({
                        "type": "forward_list_running_process",
                        "data": message.get("data"),
                        "agent_id": message.get("agent_id"),
                        "controller_id": target_id
                    }))
                    print(f"[<] Forwarded forward_list_running_process to controller {controller_id}")
                continue

            # ----- COMMAND RESULT -----
            elif msg_type == "command_result":
                client_id = message.get("client_id")
                if client_id in manager.active_connections:
                    await manager.send_to_device(client_id, json.dumps({
                        "type": "command_result",
                        "data": message.get("output"),
                        "agent_id": message.get("agent_id"),
                    }))
                    print(f"[<] Forwarded command_result to client {client_id}")
                continue

            # ----- PING -----
            elif msg_type == "ping":
                await manager.send_to_device(device_id, json.dumps({"type": "pong"}))
                continue
            else:
                await manager.send_to_device(identity, json.dumps(message))


    except WebSocketDisconnect:
        manager.disconnect(device_id)
        print(f"[-] Device disconnected: {device_id}")
