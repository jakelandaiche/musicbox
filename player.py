class Player:
    def __init__(self, name):
        self.name = name 
        self.answer = ""
    
    def to_obj(self):
        obj = {
                "name": self.name,
                "answer": self.answer,
                }
        return obj
