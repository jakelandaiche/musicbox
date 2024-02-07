from ..subsystem import Subsystem

playercolor = Subsystem("Player colors")

@playercolor.on("playercolor")
async def update_player_color(message, room):
    player = room.players[message["name"]]
    player.info.color = message["color"]
    print(player)

    await room.update_players()
