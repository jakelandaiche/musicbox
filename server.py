import asyncio
import json
import secrets
import websockets
import logging
import json

from code import code
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
            await websocket_pusher(websocket, room.messages)

    # if init, try to create room or find it (reconnect)
    elif message["type"] == "init":
        if "key" in message:
            pass
        key = code()
        ROOMS[key] = Room(websocket, key)
        await websocket_pusher(websocket, ROOMS[key].messages)
        

async def main(host, port):
    async with websockets.serve(ws_handler, host, port):
        await asyncio.Future()


import argparse
parser = argparse.ArgumentParser(
        prog="MusicBox",
        )
parser.add_argument("--host", default="localhost")
parser.add_argument("--port", default=8080)

if __name__ == "__main__":
    args = parser.parse_args()
    print(f"Listening on {args.host}:{args.port}")

    asyncio.run(main(args.host, args.port))
