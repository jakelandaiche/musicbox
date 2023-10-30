import asyncio
import json
import os
import secrets
import signal
import datetime as dt

import websockets
import json

MEMBERS = set()

# code: {connected: connections, history: list[messages], timeout: somehow track time}
ROOMS: dict[str, dict] = {}


async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def broadcast_message(websocket, key):
    async for message in websocket:
        data = json.loads(message)
        ROOMS[key]["history"].append(data)
        websockets.broadcast(ROOMS[key]["connected"], json.dumps(data))

def cleanup(key:str):

    # Write answers stored in history to a database

    del ROOMS[key]

async def open_room(websocket):
    """
    create key for room, and send it back to the client
    """

    connected = {websocket}

    key = secrets.token_urlsafe(12)
    ROOMS[key] = {"connected": connected, "history": [], "timeout": 0, "close_time": dt.datetime.max}

    try:
        event = {"type": "init", "user": "system", "join": key}
        await websocket.send(json.dumps(event))
        await broadcast_message(websocket, key)
    finally:
        connected.remove(websocket)
        if len(connected) == 0:
            ROOMS[key]["close_time"] = dt.datetime.now() + dt.timedelta(minutes=5)


async def join_room(websocket, key):
    """
    assign connection to existing room
    """
    try:
        connected = ROOMS[key]["connected"]
    except KeyError:
        await error(websocket, "Room not found.")
        return

    connected.add(websocket)

    for message in ROOMS[key]["history"]:
        await websocket.send(json.dumps(message))

    try:
        await broadcast_message(websocket, key)
    finally:
        connected.remove(websocket)
        if len(connected) == 0:
            ROOMS[key]["close_time"] = dt.datetime.now() + dt.timedelta(minutes=5)


async def room_handler(websocket):
    message = await websocket.recv()
    event = json.loads(message)

    assert event["type"] == "init"

    if "join" in event:
        await join_room(websocket, event["join"])
    else:
        await open_room(websocket)

async def check_closing():
    while True:
        to_remove = set()
        now = dt.datetime.now()
        for key, room in ROOMS.items():
            print(f"Room closing at {dt.datetime.strftime(room['close_time'], '%Y-%m-%d @ %H:%M:%S')}")
            if now > room["close_time"]:
                to_remove.add(key)
        for key in to_remove:
            cleanup(key)
        await asyncio.sleep(60)


async def main():
    asyncio.create_task(check_closing())
    print("Returned to main")
    async with websockets.serve(room_handler, "", 8080):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
