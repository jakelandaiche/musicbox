import asyncio
import argparse
import json
import logging
import sys
import websockets
import ssl

from asyncio import create_task

from server.room import Room
from server.player import Player
from server.utils import generate_code
from server.subsystems.base import base


class Server:

    rooms: dict[str, Room] = dict()

    def __init__(self):
        self.parse_args()
        self.setup_logger()

    def parse_args(self):
        parser = argparse.ArgumentParser(
            prog="MusicBox",
        )
        parser.add_argument("--host", default="localhost")
        parser.add_argument("--port", default=8080)
        parser.add_argument("--file", default="filtered.csv")
        parser.add_argument("--debug", action="store_true", default=False)
        args = parser.parse_args()
        self.host = args.host
        self.port = args.port
        self.debug = args.debug

    def setup_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)

    async def start(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_cert = "./fullchain1.pem"
        ssl_key = "./privkey1.pem"
        ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)

        self.logger.info(f"Listening on {self.host}:{self.port}")
        async with websockets.serve(
            self.ws_handler, self.host, self.port, ssl=ssl_context
        ):
            await asyncio.Future()

    async def ws_handler(self, websocket: websockets):
        """
        WebSocket connection handler, determines what type of connection
        (player or host) and then pushes messages to the correct room
        """
        self.logger.info(f"New connection: {websocket.remote_address}, {websocket.id}")

        info = await self.get_info(websocket)
        if info is None:
            return

        code: str = info["room"]
        room: Room = self.rooms[code]

        # Host connection
        if info["type"] == "host":
            await room.bind_host(websocket)

        # Player connection
        if info["type"] == "player":
            name = info["name"]
            await room.bind_player(websocket, name)

        self.logger.debug(f"{websocket.remote_address}: Handler terminated")

    async def get_info(self, websocket):
        """
        Consumes websocket messages until either an "init" or a "join"
        message is read. Then it will attempt to find or create the
        corresponding room. It will also check if the player exists
        """

        # Consume websocket messages
        async for message in websocket:

            # Check if message is json
            try:
                message = json.loads(message)
            except Exception as ex:
                self.logger.error(f"Message was not json: {ex}")
                continue

            # Message must have type
            if "type" not in message:
                continue

            # Case: Message type is "init"
            # (Host connection)
            if message["type"] == "init":
                new_code = generate_code()
                code = message.get("code", new_code)
                if code in self.rooms:
                    # Get room if exists
                    room = self.rooms[code]
                else:
                    room = Room(new_code, None, self.debug)
                    room.subsystems.add(create_task(base.bind(room)))

                    self.rooms[code] = room

                # clean out dead rooms
                for key, room in self.rooms.items():
                    if room.dead:
                        del self.rooms[key]

                return {"type": "host", "room": code}

            # Case: Message type is "join"
            # (Player connection)
            if message["type"] == "join":
                # "join" message must have "code"
                if "code" in message:
                    code = message["code"]
                    if code in self.rooms:
                        # Get room if exists
                        room = self.rooms[code]
                    else:
                        # If not, ignore
                        continue
                else:
                    continue

                # "join" message must have "name"
                if "name" in message:
                    name = message["name"]
                else:
                    continue

                return {"type": "player", "room": code, "name": name}

        # Can only reach here if connection was closed
        return None


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start())
