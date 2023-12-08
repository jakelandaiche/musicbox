class Player:
    def __init__(self, name, websocket):
        self.name = name 
        self.websocket = websocket
        self.color = "#000000"
        self.ready = False

    def to_obj(self):
        return {
                "name": self.name,
                "color": self.color,
                "ready": self.ready,
                }
