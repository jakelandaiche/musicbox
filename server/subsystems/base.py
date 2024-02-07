from asyncio import create_task

from ..subsystem import Subsystem
from ..game import game_task 

base = Subsystem("Base room functionality")

MIN_PLAYERS_TO_START = 0

@base.on("start")
async def start_game(_, room):
    num_players = len(room.players)
    all_ready = all(player.info["ready"] for player in room.players.values())

    if (num_players >= MIN_PLAYERS_TO_START) and all_ready:
        print("starting!")
        room.game = create_task(game_task(room, 3))

@base.on("playercolor")
async def update_player_color(message, room):
    player = room.players[message["name"]]
    player.info["color"] = message["color"]
    print(player.info)
    await room.update_players()


@base.on("playerready")
async def update_player_ready(message, room):
    player = room.players[message["name"]]
    player.info["ready"] = message["ready"]
    print(player.info)
    await room.update_players()
