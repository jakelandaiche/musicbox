"""
Room module
"""

import json
from asyncio import Task, sleep, create_task, CancelledError, current_task
from typing import Iterable

from websockets import broadcast
from websockets.server import WebSocketServerProtocol as Socket
from websockets.exceptions import ConnectionClosed

from bidict import bidict
from utils import Hub, Sub, send
from game import start_game 
from player import Player

# Global rooms object
ROOMS: bidict[str, "Room"] = bidict()

MIN_PLAYERS_TO_START = 0

class HostDisconnectedException(Exception):
    pass
class HasHostSocketException(Exception):
    pass

class Room:
    """ 
    A Room object. 

    This holds 
    - A WebSocket, for messages to/from the host machine
    - A collection of Player objects
    - Corresponding task variables that hold timeout tasks
    """
    def __init__(self, websocket=None):
        # The Host WebSocket tied to this room.
        self.websocket: Socket | None = websocket 
        
        # The centralized message queue for this room.
        self.messages = Hub()

        # Players and their timeouts
        self.players: bidict[str, Player] = bidict()
        self.player_timeout_tasks: bidict[str, Task] = bidict()

        # This holds the timeout task, which is called whenever
        # the room loses the host websocket.
        # It gets cancelled if a new host websocket reconnects to it
        self.destroy_task: Task | None = None

        # The running systems
        self.subsystems: set[Task] = set()

        # The currently running game
        self.game: Task | None = None


    @property
    def code(self) -> str:
        return ROOMS.inv[self]

    @property
    def connections(self) -> Iterable[Socket]:
        return (player.websocket for player in self.players.values() if player.websocket is not None)


    async def bind_host(self, websocket: Socket):
        """
        Registers a WebSocket as the room's host websocket,
        and consumes messages from it until its closure
        """

        # Check if room already has a host socket
        if self.websocket is not None:
            raise HasHostSocketException

        # Cancel destroy task if one is alive
        if self.destroy_task is not None:
            self.destroy_task.cancel("Host socket reestablished")
            self.destroy_task = None

        # Set websocket and return init message
        self.websocket = websocket
        await send(websocket, {
            "type": "init",
            "code": self.code
            })
        
        self.messages.pub({ "type": "hostbind" })
        # Push messages to queue
        async for message in websocket:
            message = json.loads(message)
            message["host"] = True
            self.messages.pub(message)
        self.messages.pub({ "type": "hostleave" })
        
        # Remove websocket
        # Note code can only reach here if connection was closed
        self.websocket = None
        self.destroy_task = create_task(self.destroy_timeout())
    

    async def destroy_timeout(self, timeout=600):
        try:
            print(f"{self.code}: Deleting self in {timeout} seconds")
            await sleep(timeout)

            del ROOMS[self.code]
            for subsystem in self.subsystems:
                subsystem.cancel()
            await self.broadcast(json.dumps({
                "type": "room_close",
                }))
        except CancelledError:
            print(f"{self.code}: Self-destruct cancelled")
            


    async def player_timeout(self, name, timeout=30):
        try: 
            print(f"{self.code}: Removing {name} in {timeout} seconds")
            await sleep(timeout)
            del self.players[name]
            await self.update_players()
            print(f"{self.code}: Removed {name}")
        except CancelledError:
            print(f"{self.code}: Timeout to remove {name} cancelled")
            


    async def bind_player(self, websocket: Socket, name: str):
        # Check if there is already a player with the given name
        if name in self.players:
            self.players[name].websocket = websocket
        else:
            self.players[name] = Player(name, websocket=websocket)

        # Cancel timeout if there
        if name in self.player_timeout_tasks:
            self.player_timeout_tasks[name].cancel("Player rejoined")
            del self.player_timeout_tasks[name]
        
        # Send init message
        await send(websocket, {
            "type": "init",
            "code": self.code
            })

        await self.update_players()
        async for message in websocket:
            message = json.loads(message)
            message["player"] = True
            self.messages.pub(message)

        # Remove websocket
        # Note code can only reach here if connection was closed
        self.players[name].websocket = None
        await self.update_players()
        self.player_timeout_tasks[name] = create_task(self.player_timeout(name))


    async def update_players(self):
        if self.websocket is not None:
            players = [player.to_obj() for player in self.players.values()]
            try:
                await send(self.websocket, {
                    "type": "players",
                    "players": players,
                    })
            except ConnectionClosed:
                pass


    async def broadcast(self, message, with_host=True):
        broadcast(self.connections, message)

        if with_host:
            if self.websocket is not None:
                try:
                    await send(self.websocket, message)
                except ConnectionClosed:
                    return


    async def run(self):
        with Sub(self.messages) as messages:
            async for message in messages:
                if "type" not in message:
                    continue
                T = message["type"]

                if T == "start":
                    num_players = len(self.players)
                    all_ready = all(player.ready for player in self.players.values())

                    if num_players >= MIN_PLAYERS_TO_START and all_ready:
                        self.game = create_task(start_game(self, 5))

                if T == "exit":
                    pass
                    
                if T == "player_info":
                    player = message["player"]
                    player.color = message["color"]
                    player.ready = message["ready"]
                    await self.update_players()
