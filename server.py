import asyncio
import json
import os
import secrets
import signal
import datetime as dt
import websockets
import json

from player import Player
from room import ROOMS, Room 

from utils import websocket_pusher

async def ws_handler(websocket):
    print(f"New connection: {websocket.id}, {websocket.remote_address}")

    # wait until init or join message received
    while True:
        message = await websocket.recv()
        message = json.loads(message)
        if message["type"] == "init" or message["type"] == "join":
            break

    # if join, try to find room 
    if message["type"] == "join":
        key = message["key"]
        if key in ROOMS:
            room = ROOMS[key]
            await websocket_pusher(websocket, ROOMS[key].messages)

    # if init, try to create room or find it (reconnect)
    elif message["type"] == "init":
        if "key" in message:
            pass
        key = secrets.token_urlsafe(12)
        ROOMS[key] = Room(websocket, key)
        await websocket_pusher(websocket, ROOMS[key].messages)
        

async def main():
    print("Returned to main")
    async with websockets.serve(ws_handler, "", 8080):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
