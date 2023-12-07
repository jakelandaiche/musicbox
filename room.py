import asyncio
from bidict import bidict

from utils import Hub, Sub

ROOMS = bidict()

class Room:
    """ room """

    def __init__(self, websocket):
        self.websocket = websocket

        self.messages = Hub()
        self.players = bidict()

        asyncio.create_task(self.run())

    async def run(self):
        with Sub(self.messages) as queue:

            pass
