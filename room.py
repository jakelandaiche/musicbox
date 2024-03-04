import json
import asyncio
import websockets
from utils import Hub, Sub
from game import start_game
import logging
from sys import stdout

MIN_PLAYERS_TO_START = 3

class Room:
    """ room """

    def __init__(self, websocket, debug):
        self.websocket = websocket

        self.messages = Hub()
        self.players = dict()

        self.lock = asyncio.Lock()
        self.task = asyncio.create_task(self.run())
        self.game = None
        self.debug = debug

    def setup_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(stdout))
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)


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
        with Sub(self.messages) as queue:
            try:
                while True:
                    message = await queue.get()
                    self.logger.debug(f"{message}")

                    if "type" not in message:
                        continue
                    T = message["type"]

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
                    


    def stop(self):
        self.task.cancel()
