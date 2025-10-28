import json
from app.core.manager import ConnectionManager

class ChatService:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def relay_message(self, sender_id: str, target_id: str, message: str = "Empty"):
        data = {"type": "chat", "from": sender_id, "message": message}
        await self.manager.send_to_device(target_id, json.dumps(data))
        return {"status": "delivered", "to": target_id}
