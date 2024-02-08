from asyncio import create_task

from ..subsystem import Subsystem
from ..game import game_task 
from ..room import Room

base = Subsystem("Base room functionality")

@base.on("start")
async def start_game(_, room):
    num_players = len(room.players)
    all_ready = all(player.ready for player in room.players.values())

    if (num_players >= Room.MIN_TO_START) and all_ready:
        print("starting!")
        room.game = create_task(game_task(room, 3))


@base.on("dataset")
async def update_dataset(message, room):
    room.dataset = message["dataset"]


@base.on("restart")
async def restart_game(_, room):
    await room.broadcast({
        "type": "state",
        "state": "LOBBY"
        })


@base.on("playercolor")
async def update_player_color(message, room):
    player = room.players[message["name"]]
    player.color = message["color"]
    await room.update_players()


@base.on("playerready")
async def update_player_ready(message, room):
    player = room.players[message["name"]]
    player.ready = message["ready"]
    await room.update_players()
