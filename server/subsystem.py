from asyncio import CancelledError
from typing import Callable, Coroutine

from .room import Room
from .utils import Sub

callback = Callable[[dict, Room], Coroutine]

class Subsystem:
    """
    This can be bound to a room
    """
    def __init__(self, name="Subsystem"):
        self.typed_callbacks: dict[str, callback] = dict()
        self.all_callbacks: set[callback] = set()
        self.name = name

    def on(self, message_type: str):
        def decorator(func: callback):
            self.typed_callbacks[message_type] = func
            return func
        return decorator

    def all(self, func: callback):
        self.all_callbacks.add(func)
        return func
        
    async def bind(self, room: Room):
        try:
            with Sub(room.messages) as messages:
                async for message in messages:
                    if "type" not in message:
                        continue
                    message_type = message["type"]

                    if message_type in self.typed_callbacks:
                        await self.typed_callbacks[message["type"]](message, room)

                    for func in self.all_callbacks:
                        await func(message, room)

        except CancelledError:
            print(f"{room.code}-{self.name} shutting down")


echo = Subsystem("Echoer")
@echo.all
async def echo_message(message, _):
    print("ECHO!")
    print(message)

