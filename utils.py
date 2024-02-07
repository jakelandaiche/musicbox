import asyncio

class Hub:
    def __init__(self):
        self.subscriptions = set()

    def pub(self, message):
        for queue in self.subscriptions:
            queue.put_nowait(message)

class Sub:
    def __init__(self, hub):
        self.hub = hub
        self.queue = asyncio.Queue()

    def __enter__(self):
        self.hub.subscriptions.add(self.queue)
        return self

    def __exit__(self, type, value, traceback):
        self.hub.subscriptions.remove(self.queue)

    def __aiter__(self):
        return self

    async def __anext__(self):
        message = await self.queue.get()
        return message

from typing import Callable
from functools import wraps

class Listener:
    """
    """
    def __init__(self):
        self.callbacks: dict[str, Callable] = dict()

    async def bind(self, hub: Hub):
        with Sub(hub) as messages:
            async for message in messages:
                if "type" not in message:
                    continue
                if message["type"] in self.callbacks:
                    self.callbacks[message["type"]](message)


    def on(self, message_type: str) -> Callable:
        def decorator(func):
            self.callbacks[message_type] = func
            return func
        return decorator


test = Listener()
@test.on("hehe")
def what(message):
    pass

seed = 68648
i = 0

def generate_code():
    """Basic linear congruential generator"""
    global i 
    n = seed + 41055 * i 
    i += 1 
    g = [7, 5, 15, 19]
    d = []
    for _ in range(4):
        d.append(int(n % 26))
        n //= 26 
    return ''.join(chr(((g[i]*d[i]) % 26) + 65) for i in range(4))


import json
from websockets.server import WebSocketServerProtocol as Socket
async def send(websocket: Socket, message: dict):
    await websocket.send(json.dumps(message))

def statechange(state):
    return json.dumps({
        "type": "state",
        "state": state
        })
