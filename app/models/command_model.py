from abc import ABC, abstractmethod

# --- Command Interface ---
class Command(ABC):
    @abstractmethod
    def to_dict(self):
        pass


# --- Concrete Commands ---
class ShutdownCommand(Command):
    def to_dict(self):
        return {"type": "shutdown"}


class RestartCommand(Command):
    def to_dict(self):
        return {"type": "restart"}


class KillAppCommand(Command):
    def __init__(self, process_id: str):
        self.process_id = process_id

    def to_dict(self):
        return {"type": "kill_app", "target": self.process_id}

class LockScreenCommand(Command):
    """Khoá thiết bị"""
    def to_dict(self):
        return {"type": "lock"}

class EnableBluetoohCommand(Command):
    """Mở bluetooh thiết bị"""
    def to_dict(self):
        return {"type": "enable_bluetooh"}
    
class DisableBluetoohCommand(Command):
    """Tắt bluetooh thiết bị"""
    def to_dict(self):
        return {"type": "disabled_bluetooh"}
    
class EnableWifiCommand(Command):
    """Mở wifi thiết bị"""
    def to_dict(self):
        return {"type": "enable_wifi"}
    
class DisableWifiCommand(Command):
    """Tắt wifi thiết bị"""
    def to_dict(self):
        return {"type": "disabled_wifi"}

class ChatCommand(Command):
    """Gửi tin nhắn tới Agent (để hiển thị popup hoặc qua UI chat)."""
    def __init__(self, message: str, sender: str = "controller"):
        self.message = message
        self.sender = sender

    def to_dict(self):
        return {"type": "chat", "from": self.sender, "message": self.message}

class ScreenshotCommand(Command):
    """Yêu cầu Agent chụp màn hình và gửi lại."""
    def __init__(self, reply_to: str = None):
        # reply_to có thể là telegram chat id hoặc ws id
        self.reply_to = reply_to

    def to_dict(self):
        return {"type": "screenshot", "reply_to": self.reply_to}

class ShellCommand(Command):
    def __init__(self, command: str):
        self.command = command

    def to_dict(self):
        return {"type": "shell", "command": self.command}
    
class RequestListProcess(Command):
    def __init__(self, controller_id: str = None):
        self.controller_id = controller_id
    def to_dict(self):
        return {"type": "get_list_process", "controller_id": self.controller_id}

class ResponseListProcess(Command):
    def __init__(self, target_id: str = None):
        self.target_id = target_id
    def to_dict(self):
        return {"type": "list_process", "target_id": self.target_id}
    
# --- Factory ---
class CommandFactory:
    @staticmethod
    def create_command(cmd_type: str, payload: dict):
        if cmd_type == "shutdown":
            return ShutdownCommand()
        elif cmd_type == "restart":
            return RestartCommand()
        elif cmd_type == "kill_app":
            return KillAppCommand(payload.get("app_name", ""))
        elif cmd_type == "chat":
            return ChatCommand(payload.get("message", ""), payload.get("sender", "controller"))
        elif cmd_type == "screenshot":
            return ScreenshotCommand(payload.get("reply_to"))
        elif cmd_type == "shell":
            return ShellCommand(payload.get("command", ""))
        elif cmd_type == "lock":
            return LockScreenCommand()
        elif cmd_type == "enable_bluetooh":
            return EnableBluetoohCommand()
        elif cmd_type == "disable_bluetooh":
            return DisableBluetoohCommand()
        elif cmd_type == "enable_wifi":
            return EnableWifiCommand()
        elif cmd_type == "disable_wifi":
            return DisableWifiCommand()
        elif cmd_type == "get_list_process":
            return RequestListProcess(payload.get('controller_id'))
        elif cmd_type == "list_process":
            return ResponseListProcess(payload.get('target_id'))
        else:
            raise ValueError(f"Unknown command type: {cmd_type}")
