from websockets.server import WebSocketServerProtocol as Socket
class Player:
    def __init__(self, name, websocket=None):
        self.name: str = name 
        self.websocket: Socket | None = websocket

        self.info = {
                "color": "#000000",
                "ready": False,
                }

    @property
    def connected(self):
        return self.websocket is not None

    def to_obj(self):
        return {
                "name": self.name,
                "connected": self.connected,
                **self.info,
                }

class PlayerManager:
    def __init__(self):
        pass
