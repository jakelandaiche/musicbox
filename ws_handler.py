import json

from code import generate_code
from room import ROOMS, Room 
from player import Player

async def get_info(websocket):
    async for message in websocket:
        try:
            message = json.loads(message)
        except:
            continue

        if "type" not in message:
            continue

        if message["type"] == "init":
            if "code" in message:
                code = message["code"]
                if code in ROOMS:
                    room = ROOMS[code]
                else:
                    continue
            else:
                room = Room(websocket)
                ROOMS[generate_code()] = room

            return {
                    "type": "host",
                    "room": room
                    }

        if message["type"] == "join":
            if "code" in message:
                code = message["code"]
                if code in ROOMS:
                    room = ROOMS[code]
                else:
                    continue
            else:
                continue

            if "name" in message:
                name = message["name"]
            else:
                continue

            room.players[websocket] = Player(name)
            players = [player.name for player in room.players.values()]
            await room.websocket.send(json.dumps({
                "type": "players",
                "players": players
                }))

            return {
                    "type": "player",
                    "room": room,
                    "name": name
                    }

    return None



async def ws_handler(websocket):
    print(f"New connection: {websocket.id}, {websocket.remote_address}")

    info = await get_info(websocket)
    if info is None:
        return

    if info["type"] == "host":
        room = info["room"]
        await websocket.send(json.dumps({
            "type": "init",
            "code": ROOMS.inv[room]
            }))
        async for message in websocket:
            room.messages.pub(message)

    if info["type"] == "player":
        room = info["room"]
        async for message in websocket:
            room.messages.pub(message)


        
