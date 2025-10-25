from app.core.manager import ConnectionManager
from app.models.command_model import CommandFactory
import json

class CommandService:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def send_command(self, target_device_id: str, cmd_type: str, payload: dict):
        # Tạo đối tượng command
        command = CommandFactory.create_command(cmd_type, payload)
        command_data = command.to_dict()

        # Gói theo format thống nhất để client dễ parse
        message = {
            "event": "command",
            "data": command_data
        }

        await self.manager.send_to_device(target_device_id, json.dumps(message))

        return {
            "status": "sent",
            "to": target_device_id,
            "command": command_data["type"]
        }
