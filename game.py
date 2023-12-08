import json
import asyncio
from data import get_videos

async def all_submit(room):
    pass

async def all_submit_or(room, T):
    await asyncio.sleep(30)

class GamePlayerData:
    def __init__(self):
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

async def start_game(room, N):
    playerdata = {name: GamePlayerData() for name in room.players.keys()}
    print(playerdata)

    async with room.lock:
        # Game Start
        await room.broadcast(json.dumps({
            "type": "state",
            "state": "GAMESTART"
            }))
        await asyncio.sleep(30)


        for n in range(1, N+1):
            # Round Start
            await room.broadcast(json.dumps({
                "type": "state",
                "state": "ROUNDSTART"
                }))
            await room.websocket.send(json.dumps({

                }))
            await asyncio.sleep(30)

            # Round Collect
            await room.broadcast(json.dumps({
                "type": "state",
                "state": "ROUNDCOLLECT"
                }))
            await all_submit_or(room, 30)

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
        await asyncio.sleep(room, 30)

