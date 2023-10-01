import asyncio
import json
import os
import secrets
import signal

import websockets

MEMBERS = set()

# set type
ROOMS: dict[str, set] = {}


async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def broadcast_message(websocket, connected):
    async for message in websocket:
        data = json.loads(message)

        websockets.broadcast(connected, json.dumps(data))


async def open_room(websocket):
    """
    create key for room, and send it back to the client
    """

    connected = {websocket}

    key = secrets.token_urlsafe(12)
    ROOMS[key] = connected

    try:
        event = {"type": "init", "user": "system", "join": key}
        await websocket.send(json.dumps(event))
        await broadcast_message(websocket, connected)
    finally:
        del ROOMS[key]


async def join_room(websocket, key):
    """
    assign connection to existing room
    """
    try:
        connected = ROOMS[key]
    except KeyError:
        await error(websocket, "Room not found.")
        return

    connected.add(websocket)

    try:
        await broadcast_message(websocket, connected)
    finally:
        connected.remove(websocket)


async def room_handler(websocket):
    message = await websocket.recv()
    event = json.loads(message)

    assert event["type"] == "init"

    if "join" in event:
        await join_room(websocket, event["join"])
    else:
        await open_room(websocket)


async def handler(websocket):
    async for message in websocket:
        sender = message["user"]
        if sender not in MEMBERS:
            websocket.send({"user": "system", "text": f"{sender} joined"})
            MEMBERS.add(sender)
        websocket.send(message)


async def main():
    async with websockets.serve(handler, "", 8080):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
