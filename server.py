import asyncio
import json
import os
import secrets
import signal
import datetime as dt

import pandas as pd
import websockets
import json

MEMBERS = set()

# code: {connected: connections, history: list[messages], close_time: timestamp to check against before deleting}
ROOMS: dict[str, dict] = {}

dataset = pd.DataFrame()
# Not needed if we are not sending over labels to frontend
# label_data = pd.read_csv("class_labels_indices.csv", on_bad_lines="skip")


async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def broadcast_message(websocket, key):
    async for message in websocket:
        data = json.loads(message)
        print(data)
        ROOMS[key]["history"].append(data)
        match data["type"]:
            case "message":
                websockets.broadcast(ROOMS[key]["connected"], json.dumps(data))
            case _:
                pass


def cleanup(key: str):
    # Write answers stored in history to a database

    del ROOMS[key]


async def open_room(websocket):
    """
    create key for room, and send it back to the client
    """

    connected = {websocket}

    key = secrets.token_urlsafe(12)

    # Room state
    ROOMS[key] = {
        "connected": connected,
        "history": [],
        "timeout": 0,
        "close_time": dt.datetime.max,
        "players": dict(),
    }

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
    # First make sure room is joinable
    try:
        connected = ROOMS[key]["connected"]
        connected.add(websocket)
    except KeyError:
        await error(websocket, "Room not found.")
        return

    # Send any missing info
    # Not needed for game client since host can store score
    # for message in ROOMS[key]["history"]:
    #     await websocket.send(json.dumps(message))

    # Connection accepted, ask for player info
    await websocket.send(
        json.dumps(
            {
                "type": "user_init",
            }
        )
    )

    # Get username back?
    player_info = json.loads(await websocket.recv())
    player = {"score": 0, "id": player_info["id"]}
    ROOMS[key]["players"][player_info["username"]] = player
    print(f"Added player {player_info['username']}")

    # Game is now ready, sit and wait for messages from the server
    # New loop since we know these should be answers about songs?

    try:
        async for answer in websocket:
            data = json.loads(answer)
            print(data)
            assert data["type"] == "answer"
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
            if now > room["close_time"]:
                to_remove.add(key)
        for key in to_remove:
            cleanup(key)
        await asyncio.sleep(60)


def setup_dataset():
    dataset = pd.read_csv(
        "eval_segments.csv",
        sep=", ",
        on_bad_lines="skip",
        skiprows=2,
        quotechar='"',
        engine="python",
    )

    dataset = dataset[dataset["positive_labels"].str.match(".*/m/04rlf.*")]


def get_videos() -> list[dict]:
    videos = []
    for row in dataset.sample(10):
        videos.append({"id": row["$ YTID"], "start_time": row["start_seconds"]})
    return videos


async def main():
    asyncio.create_task(check_closing())
    print("Returned to main")
    async with websockets.serve(room_handler, "", 8080):
        await asyncio.Future()


if __name__ == "__main__":
    setup_dataset()
    asyncio.run(main())
