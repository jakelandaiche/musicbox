import json
import asyncio
from data import get_video
from utils import Sub

async def start_game(room, N):
    player_data = {player.name: PlayerData(player) for player in room.players.values()}

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
            scores = compute_scores(player_data, video["id"])
            # do something with scores

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


class PlayerData:
    def __init__(self, player):
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
    scores = []
    for player in player_data.values():
        if player.answer is not None:
            player.score = len(player.answer)

            scores.append({
                "id": video_id,
                "label": player.answer,
                "score": player.score
                })

        else:
            player.score = 0
        player.total = player.total + player.score 

    return scores



async def all_submit(room, player_data):
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


