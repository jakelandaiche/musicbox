import json
import asyncio
import math

from data import get_video
from utils import Sub
from database import Database
from similarity import Similarity

sim_checker = Similarity()

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

async def start_game(room, N):
    db = Database()
    game_id = db.create_game()

    player_data = {player.name: \
            PlayerData(player, db.create_player(player.name, game_id)) \
            for player in room.players.values() }

    async with room.lock:
        await room.websocket.send(json.dumps({
            "type": "player_data",
            "player_data": [p.to_obj() for p in player_data.values()]
            }))

        # Game Start
        await room.broadcast(json.dumps({
            "type": "state",
            "state": "GAMESTART"
            }))
        await asyncio.sleep(15)

        for n in range(1, N+1):
            await room.websocket.send(json.dumps({
                "type": "round_num",
                "round_num": n,
            }))

            # Round Start
            await room.broadcast(json.dumps({
                "type": "state",
                "state": "ROUNDSTART"
                }))
            video = get_video()
            await room.websocket.send(json.dumps({
                "type": "video",
                "id": video["id"],
                "start_time": video["start_time"]
                }))
            await asyncio.sleep(20)

            # Round Collect
            for p in player_data.values():
                p.clear()
            await room.websocket.send(json.dumps({
                "type": "player_data",
                "player_data": [p.to_obj() for p in player_data.values()]
                }))
            await room.broadcast(json.dumps({
                "type": "state",
                "state": "ROUNDCOLLECT"
                }))
            await all_submit_or(room, player_data, 30)
            compute_scores(player_data, video["id"])

            for player in player_data.values():
                db.write_answer(player, n)
                    

            await room.websocket.send(json.dumps({
                "type": "player_data",
                "player_data": [p.to_obj() for p in player_data.values()]
                }))



            # Round End 
            await room.broadcast(json.dumps({
                "type": "state",
                "state": "ROUNDEND"
                }))
            await asyncio.sleep(30)


        await room.broadcast(json.dumps({
            "type": "state",
            "state": "GAMEEND"
            }))

        db.cur.close()
        db.con.close()


class PlayerData:
    """ 
    this a separate class because... 
    i have no good reason i just didnt find the time to factor 
    this back into Player
    """
    def __init__(self, player, db_id):
        self.db_id = db_id 
        self.name = player.name
        self.color = player.color
        self.answer = None
        self.total = 0
        self.score = 0

    def clear(self):
        self.answer = None
        self.score = 0

    def to_obj(self):
        return {
                "name": self.name,
                "color": self.color,
                "answer": self.answer,
                "total": self.total,
                "score": self.score,
                }


def compute_scores(player_data, video_id):
    with_answers = [player for player in player_data.values() if player.answer is not None]
    sim_scores = sim_checker.sim_scores([player.answer for player in with_answers])

    for i in range(len(with_answers)):
        player = with_answers[i]
        score = math.floor(sim_scores[i] * 500)
        mult = 0

        # get words
        answer_l = player.answer \
                .replace(".","") \
                .replace(",","") \
                .split(" ")
        answer_s = set(answer_l)

        matches = 0

        for word in answer_s:
            if word not in common_words:
                # increase multiplier for each uncommon word
                if mult < 20:
                    mult += 1

                # more points for words in common with others
                for other in with_answers:
                    if other is not player:
                        matches += 1 if other.answer.count(word) else 0

        player.score = score + matches * mult
        player.total = player.total + player.score




async def all_submit(room, player_data):
    """ returns when all players have submitted """ 
    with Sub(room.messages) as queue:
        try:
            while True:
                message = await queue.get()
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
    return


async def all_submit_or(room, player_data, T):
    try:
        await asyncio.wait_for(all_submit(room, player_data), timeout=T)
    except asyncio.TimeoutError:
        return


