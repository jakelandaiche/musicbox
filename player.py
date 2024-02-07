from websockets.server import WebSocketServerProtocol as Socket
class Player:
    def __init__(self, name, websocket=None):
        self.name: str = name 
        self.websocket: Socket | None = websocket
        self.color = "#000000"
        self.ready = False

        self.info = {
                "name": name,
                "color": "#000000",
                "ready": False,
                }

        self.db_id = None 
        self.answer = None
        self.total = 0
        self.score = 0

    @property
    def connected(self):
        return self.websocket is not None

    def clear(self):
        self.answer = None
        self.score = 0

    def to_obj(self):
        return {
                "connected": self.connected,
                "info": self.info,
                "name": self.name,
                "color": self.color,
                "ready": self.ready,
                "answer": self.answer,
                "total": self.total,
                "score": self.score,
                }

class PlayerManager:
    def __init__(self):
        pass
