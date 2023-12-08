import json
import asyncio
from data import get_video
from utils import Sub

async def start_game(room, N):
    player_data = {player.name: PlayerData(player) for player in room.players.values()}

    async with room.lock:
        # Game Start
        await room.broadcast(json.dumps({
            "type": "state",
            "state": "GAMESTART"
            }))
        await asyncio.sleep(2)


        for n in range(1, N+1):
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
            await asyncio.sleep(2)

            # Round Collect
            await room.broadcast(json.dumps({
                "type": "state",
                "state": "ROUNDCOLLECT"
                }))
            await all_submit_or(room, player_data, 30)
            scores = compute_scores(player_data)

            # Round End 
            await room.broadcast(json.dumps({
                "type": "state",
                "state": "ROUNDEND"
                }))
            await asyncio.sleep(2)


        await room.broadcast(json.dumps({
            "type": "state",
            "state": "GAMEEND"
            }))
        await asyncio.sleep(room, 2)

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
                "answer": self.answer,
                "total": self.total,
                "score": self.score,
                }

def compute_scores(player_data):
    pass

async def all_submit(room, player_data):
    with Sub(room.messages) as queue:
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
    return


async def all_submit_or(room, player_data, T):
    await asyncio.wait_for(all_submit(room, player_data), timeout=T)


