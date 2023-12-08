import json
import asyncio
import websockets
from bidict import bidict
from utils import Hub, Sub
from game import start_game 

ROOMS = bidict()

class Room:
    """ room """

    def __init__(self, websocket):
        self.websocket = websocket

        self.messages = Hub()
        self.players = bidict()

        self.lock = asyncio.Lock()
        self.task = asyncio.create_task(self.run())
        self.game = None


    async def update_players(self):
        players = [player.to_obj() for player in self.players.values()]
        await self.websocket.send(json.dumps({
            "type": "players",
            "players": players,
            }))

    async def broadcast(self, message):
        s = [player.websocket for player in self.players.values()]
        print(s)
        await self.websocket.send(message)
        websockets.broadcast(s, message)


    async def run(self):
        with Sub(self.messages) as queue:
            while True:
                message = await queue.get()

                if "type" not in message:
                    continue
                T = message["type"]

                if T == "start":
                    print("start")
                    num_players = len(self.players)
                    all_ready = all(player.ready for player in self.players.values())

                    if num_players >= 2 and all_ready:
                        self.game = asyncio.create_task(start_game(self, 5))

                    
                if T == "player_info":
                    player = message["player"]
                    player.color = message["color"]
                    player.ready = message["ready"]
                    await self.update_players()
                    


    def stop(self):
        self.task.cancel()
