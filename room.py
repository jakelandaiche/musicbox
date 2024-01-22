import json
import asyncio
import websockets
from bidict import bidict
from utils import Hub, Sub
from game import start_game 

ROOMS = bidict()

MIN_PLAYERS_TO_START = 0

class Room:
    """ A Room object """

    def __init__(self, websocket):
        self.websocket = websocket

        self.messages = Hub()
        self.players = bidict()
        self.chat = []

        self.lock = asyncio.Lock()
        self.task = asyncio.create_task(self.run())
        self.alive = True
        self.game = None


    async def update_players(self):
        players = [player.to_obj() for player in self.players.values()]
        await self.websocket.send(json.dumps({
            "type": "players",
            "players": players,
            }))


    async def broadcast(self, message):
        s = [player.websocket for player in self.players.values()]
        await self.websocket.send(message)
        websockets.broadcast(s, message)


    async def run(self):
        try:
            with Sub(self.messages) as queue:
                while True:
                    message = await queue.get()
                    if "type" not in message:
                        continue
                    T = message["type"]
                    
                    if T == "ack":
                        print(message)

                    if T == "start":
                        num_players = len(self.players)
                        all_ready = all(player.ready for player in self.players.values())

                        if num_players >= MIN_PLAYERS_TO_START and all_ready:
                            self.game = asyncio.create_task(start_game(self, 5))
                        
                    if T == "player_info":
                        player = message["player"]
                        player.color = message["color"]
                        player.ready = message["ready"]
                        await self.update_players()

        except asyncio.CancelledError:
            raise

        except Exception as e:
            print("Room error")
            print(e)

        finally:
            pass


    def stop(self):
        self.alive = False
        self.task.cancel()
