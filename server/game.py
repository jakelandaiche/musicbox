import json
import asyncio
from asyncio import CancelledError

from data import get_video
from database import Database

from .utils import Sub 
from .room import Room

common_words = [
    "the",
    "be",
    "to",
    "of",
    "and",
    "a",
    "in",
    "that",
    "have",
    "it",
    "for",
    "not",
    "on",
    "with",
    "as",
    "at",
]


async def game_task(room: Room, N: int):
    db = Database()
    game_id = db.create_game()

    videos = [get_video() for _ in range(N)]

    try:
        await room.update_players()

        # Game Start
        await room.broadcast({
            "type": "state",
            "state": "GAMESTART"
            })
        await asyncio.sleep(15)

        for n in range(1, N+1):
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

            for p in room.players.values():
                p.info["answer"] = None
                p.info["score"] = 0


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


def compute_scores(player_data, video_id):
    with_answers = [player for player in player_data.values() if player.answer is not None]

    for player in with_answers:
        score = 0
        mult = 10
        
        # get words
        answer_l = player.answer \
                .replace(".","") \
                .replace(",","") \
                .split(" ")
        answer_s = set(answer_l)

        for word in answer_s:
            if word not in common_words:
                # increase multiplier for each uncommon word
                if mult < 20:
                    mult += 1

                # more points for words in common with others
                for other in with_answers:
                    if other is not player:
                        score += 1 if other.answer.count(word) else 0

        player.info["score"] = score * mult
        player.info["total"] = player.total + player.score




async def all_submit(room, player_data):
    """ returns when all players have submitted """ 
    try:
        with Sub(room.messages) as messages:
            async for message in messages:
                if message["type"] == "answer":
                    name = message["player"].name
                    player_data[name].answer = message["answer"]
                    await room.websocket.send(json.dumps({
                        "type": "player_data",
                        "player_data": [p.to_obj() for p in player_data.values()]
                        }))

                if all(p.answer is not None for p in player_data.values()):
                   break 
    except asyncio.CancelledError:
        raise


async def all_submit_or(room, player_data, T):
    try:
        await asyncio.wait_for(all_submit(room, player_data), timeout=T)
    except asyncio.TimeoutError:
        return
