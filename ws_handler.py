import json

from code import generate_code
from room import ROOMS, Room 
from player import Player

async def ws_handler(websocket):
    """
    WebSocket connection handler, determines what type of connection
    (player or host) and then pushes messages to the correct room
    """
    print(f"New connection: {websocket.remote_address}, {websocket.id}")

    info = await get_info(websocket)
    if info is None:
        return

    # Host connection
    if info["type"] == "host":
        room = info["room"]

        # Send back code
        await websocket.send(json.dumps({
            "type": "init",
            "code": ROOMS.inv[room]
            }))

        # Push messages to room
        async for message in websocket:
            message = json.loads(message)
            message["host"] = True
            room.messages.pub(message)

        # When done, cleanup
        room.stop()
        del ROOMS[ROOMS.inv[room]]


    # Player connection
    if info["type"] == "player":
        room = info["room"]

        # Add player to room
        name = info["name"]
        player = Player(name, websocket)
        room.players[name] = player
        await room.update_players()

        await websocket.send(json.dumps({
            "type": "init",
            "code": ROOMS.inv[room]
            }))

        # Push messages to room
        async for message in websocket:
            message = json.loads(message)
            message["player"] = player
            room.messages.pub(message)

        # When done, cleanup
        del room.players[name]
        await room.update_players()



async def get_info(websocket):
    """
    Consumes websocket messages until either an "init" or a "join"
    message is read. Then it will attempt to find or create the
    corresponding room. It will also check if the player exists
    """

    # Consume websocket messages
    async for message in websocket:

        # Check if message is json
        try:
            message = json.loads(message)
        except:
            continue

        # Message must have type
        if "type" not in message:
            continue


        # Case: Message type is "init"
        # (Host connection)
        if message["type"] == "init":

            if "code" in message:
                # If message contains code, then check if room exists
                code = message["code"]
                if code in ROOMS:
                    # Get room if exists
                    room = ROOMS[code]
                else:
                    # If not, ignore
                    continue
            else:
                # If not, create room 
                room = Room(websocket)
                ROOMS[generate_code()] = room

            # Done
            return {
                    "type": "host",
                    "room": room
                    }


        # Case: Message type is "join"
        # (Player connection)
        if message["type"] == "join":
            # "join" message must have "code"
            if "code" in message:
                code = message["code"]
                if code in ROOMS:
                    # Get room if exists
                    room = ROOMS[code]
                else:
                    # If not, ignore
                    continue
            else:
                continue

            # "join" message must have "name"
            if "name" in message:
                name = message["name"]
            else:
                continue

            return {
                    "type": "player",
                    "room": room,
                    "name": name
                    }

    # Can only reach here if connection was closed
    return None


