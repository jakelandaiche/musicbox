"""
Room module
"""

import json
from asyncio import Task, sleep, create_task, CancelledError
from typing import Iterable, Callable, Coroutine
from bidict import bidict

from websockets import broadcast
from websockets.server import WebSocketServerProtocol as Socket
from websockets.exceptions import ConnectionClosed

from .utils import Hub, Sub, send
from .player import Player

# Global rooms object
ROOMS: bidict[str, "Room"] = bidict()

class Room:
    """ 
    A Room object. 
    """
    MAX_PLAYERS = 8 
    MIN_TO_START = 0

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

        # Game info
        self.dataset = "musicCaps1.csv"
        self.nrounds = 5

        # The currently running game
        self.game: Task | None = None

    @property
    def code(self) -> str:
        try:
            return ROOMS.inv[self]
        except:
            return ""

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
            return

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
        
        # Push messages to queue
        async for message in websocket:
            message = json.loads(message)
            self.messages.pub(message)
        
        # Remove websocket
        # Note code can only reach here if connection was closed
        self.websocket = None
        self.destroy_task = create_task(self.destroy_timeout())
    

    async def destroy_timeout(self, timeout=10):
        """
        A Task that waits timeout seconds, then removes self
        from the ROOMS global dictionary
        """
        try:
            print(f"{self.code}: Deleting self in {timeout} seconds")
            await sleep(timeout)

            del ROOMS[self.code]
            for subsystem in list(self.subsystems):
                subsystem.cancel()
            for connection in list(self.connections):
                await connection.close()
            
        except CancelledError:
            print(f"{self.code}: Self-destruct cancelled")


    async def bind_player(self, websocket: Socket, name: str):
        """
        Registers a WebSocket as the websocket for one 
        of the players.

        A player is either created or rebound as necessary
        """

        # If there are too many players, don't
        if len(self.players) >= Room.MAX_PLAYERS:
            return
        
        # Check if there is already a player with the given name
        if name in self.players:
            self.players[name].websocket = websocket
        else:
            self.players[name] = Player(name=name, websocket=websocket)
            self.messages.pub({
                "type": "newplayer",
                "name": name
                })

        # Cancel timeout if there is one
        if name in self.player_timeout_tasks:
            self.player_timeout_tasks[name].cancel("Player rejoined")
            del self.player_timeout_tasks[name]
        
        # Send init message
        await send(websocket, {
            "type": "init",
            "code": self.code
            })
        await self.update_players()

        # Push messages
        async for message in websocket:
            message = json.loads(message)
            self.messages.pub(message)

        # Remove websocket
        # Note code can only reach here if connection was closed
        if self.game is None:
            # If no game running, just remove player
            del self.players[name]
            await self.update_players()
        else:
            # If game is running, set a timeout so player can reconnect
            self.players[name].websocket = None
            await self.update_players()
            self.player_timeout_tasks[name] = create_task(self.player_timeout(name))


    async def player_timeout(self, name, timeout=30):
        """
        A Task that waits timeout seconds, then removes 
        a playem from self.players
        """
        try: 
            print(f"{self.code}: Removing {name} in {timeout} seconds")
            await sleep(timeout)
            del self.players[name]
            await self.update_players()
            print(f"{self.code}: Removed {name}")
        except CancelledError:
            print(f"{self.code}: Timeout to remove {name} cancelled")


    async def update_players(self):
        """
        Sends over all player information to the Host 
        websocket
        """
        players = [player.to_obj() for player in self.players.values()]
        await self.send({"type":"players", "players":players})


    async def send(self, message: dict):
        """Send a message to the Host websocket"""
        if self.websocket is not None:
            try:
                await send(self.websocket, message)
            except ConnectionClosed:
                pass


    async def broadcast(self, message, with_host=True):
        """
        Sends a message to all websockets, with the option
        to also send to the host WebSocket (true by default)
        """
        broadcast(self.connections, json.dumps(message))

        if with_host:
            if self.websocket is not None:
                try:
                    await send(self.websocket, message)
                except ConnectionClosed:
                    return


    def listen(self, message_type: str):
        """
        """
        def decorator(func: Callable[[dict, Room], Coroutine]):
            async def task():
                try:
                    with Sub(self.messages) as queue:
                        while True:
                            message = await queue.get()
                            if "type" not in message:
                                continue
                            if message["type"] == message_type:
                                await func(message, self)
                except CancelledError:
                    pass
            return create_task(task())
        return decorator
