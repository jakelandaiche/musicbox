import asyncio
from asyncio import CancelledError

from data import get_videos
from database import Database

from .utils import Sub 
from .room import Room

async def game_task(room: Room, N=5):
    db = Database()
    game_id = db.create_game()

    videos = get_videos(N=N)

    try:
        # Init 
        for player in room.players.values():
            player.answer = None
            player.db_id = ""
            player.total = 0
            player.score = 0
        await room.update_players()

        # Game Start
        await room.broadcast({
            "type": "state",
            "state": "GAMESTART"
            })
        await asyncio.sleep(1)

        for n in range(1, N+1):
            # Reset scores
            for player in room.players.values():
                player.answer = None
                player.score = 0
            await room.update_players()

            # Update round number
            await room.send({
                "type": "round_num",
                "round_num": n,
            })

            # Round Start
            await room.broadcast({
                "type": "state",
                "state": "ROUNDSTART"
                })
            video = videos[n-1]
            await room.send({
                "type": "video",
                "id": video["id"],
                "start_time": video["start_time"]
                })
            await asyncio.sleep(20)

            # Collect answers
            await room.broadcast({
                "type": "state",
                "state": "ROUNDCOLLECT"
                })
            try:
                await asyncio.wait_for(wait_for_answers(room), timeout=30)
            except TimeoutError:
                pass

            # Compute scores
            compute_scores(room)

            # Round end
            await room.update_players()
            await room.broadcast({
                "type": "state",
                "state": "ROUNDEND"
                })
            await asyncio.sleep(30)


        await room.broadcast({
            "type": "state",
            "state": "GAMEEND"
            })

    except asyncio.CancelledError:
        raise
    finally:
        db.cur.close()
        db.con.close()
        room.game = None


def compute_scores(room):
    pass


async def wait_for_answers(room):
    try:
        with Sub(room.messages) as queue:
            while True:
                try:
                    message = await queue.get()
                    t = message["type"]

                    if t == "answer":
                        name = message["name"]
                        room.players[name].answer = message["answer"]
                        await room.update_players()

                    if all(player.answer is not None for player in room.players.values()):
                        break
                except KeyError:
                    print("No key")

        print("All answers")
    except CancelledError:
        print("oops")
    finally:
        return

