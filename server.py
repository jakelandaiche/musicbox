import asyncio
import websockets
import argparse
import json
import logging
import sys

from room import Room
from player import Player
from code import generate_code


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
        self.logger.info(f"Listening on {self.host}:{self.port}")
        async with websockets.serve(self.ws_handler, self.host, self.port):
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
            # Send back code
            await websocket.send(json.dumps({
                "type": "init",
                "code": code
                }))

            # Push messages to room
            async for message in websocket:
                message = json.loads(message)
                message["host"] = True
                room.messages.pub(message)

            # When done, cleanup
            room.stop()
            del self.rooms[code]


        # Player connection
        if info["type"] == "player":

            # Add player to room
            name = info["name"]
            player = Player(name, websocket)
            room.players[name] = player
            await room.update_players()

            await websocket.send(json.dumps({
                "type": "init",
                "code": code
                }))

            # Push messages to room
            async for message in websocket:
                message = json.loads(message)
                message["player"] = player
                room.messages.pub(message)

            # When done, cleanup
            del room.players[name]
            await room.update_players()

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
                self.logger.warn(f"Message was not json: {ex}")
                continue

            # Message must have type
            if "type" not in message:
                continue


            # Case: Message type is "init"
            # (Host connection)
            if message["type"] == "init":
                if "code" in message:
                    # If message contains code, then check if room exists
                    code = message["code"]
                    if code in self.rooms:
                        # Get room if exists
                        room = self.rooms[code]
                    else:
                        # If not, ignore
                        self.logger.warn()
                        continue
                else:
                    # If not, create room 
                    room = Room(websocket, self.debug)
                    new_code = generate_code()
                    self.rooms[new_code] = room

                # Done
                return {
                        "type": "host",
                        "room": new_code
                        }


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
                    if name in room.players:
                        continue
                else:
                    continue

                return {
                        "type": "player",
                        "room": code,
                        "name": name
                        }

        # Can only reach here if connection was closed
        return None


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start())