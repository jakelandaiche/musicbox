"""
Room module
"""
import logging
import json
from sys import stdout
from asyncio import Task, sleep, create_task, CancelledError
from typing import Iterable, Callable, Coroutine

from websockets import broadcast
from websockets.server import WebSocketServerProtocol as Socket
from websockets.exceptions import ConnectionClosed

from .utils import Hub, Sub, send
from .player import Player

class Room:
    """ 
    A Room object. 
    """
    MAX_PLAYERS = 8 
    MIN_TO_START = 3

    dead: bool = False

    def __init__(self, code: str, websocket=None, debug=False):
        
        self.code = code
        self.debug = debug
        # The Host WebSocket tied to this room.
        self.websocket: Socket | None = websocket 
        
        # The centralized message queue for this room.
        self.messages = Hub()

        # Players and their timeouts
        self.players: dict[str, Player] = dict()

        # This holds the timeout task, which is called whenever
        # the room loses the host websocket.
        # It gets cancelled if a new host websocket reconnects to it
        self.destroy_task: Task | None = None

        # The running systems
        self.subsystems: set[Task] = set()

        # Game info
        self.dataset: str = "musicCaps1.csv"
        self.nrounds: int = 5

        # The currently running game
        self.game: Task | None = None

        self.setup_logger()

    def setup_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(stdout))
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)

    @property
    def connections(self) -> Iterable[Socket]:
        return (player.websocket for player in self.players.values() if player.websocket is not None)

    @property
    def nconnected(self) -> int:
        return sum(1 for player in self.players.values() if player.connected)


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
            self.logger.debug(f"{self.code}: Marking self dead in {timeout} seconds")
            await sleep(timeout)

            self.dead = True
            for subsystem in list(self.subsystems):
                subsystem.cancel()
            for connection in list(self.connections):
                await connection.close()
            
        except CancelledError:
            self.logger.debug(f"{self.code}: Self-destruct cancelled")


    async def bind_player(self, websocket: Socket, name: str):
        """
        Registers a WebSocket as the websocket for one 
        of the players.

        A player is either created or rebound as necessary
        """

        # If there are too many players, don't
        if self.nconnected >= Room.MAX_PLAYERS:
            return
        
        # Check if there is already a player with the given name
        if name in self.players:
            self.players[name].websocket = websocket
            await send(websocket, {
                "type": "playerinfo",
                "player": self.players[name].to_obj()
                })
        else:
            self.players[name] = Player(name=name, websocket=websocket)
            self.messages.pub({
                "type": "newplayer",
                "name": name
                })
        
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
        self.players[name].websocket = None
        await self.update_players()
        

    async def update_players(self):
        """
        Sends over all player information to the Host 
        websocket
        """
        players = [player.to_obj() for player in self.players.values() if player.connected]
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
