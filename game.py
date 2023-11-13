import asyncio
import json
import random

from data import get_videos

def decide_winner(answers):
    return random.choice(answers)

class Game:
    def __init__(self, room, N):
        self.state = "START"
        self.room = room
        self.N = N

    async def run(self):
        # game explanation
        self.room.room_text = f"<h3>MusicBox</h3>" + "Welcome to MusicBox. The game will start soon"
        await self.room.update_frontend()
        await self.room.set_countdown(15)
        await asyncio.sleep(17)
        
        for i in range(self.N):
            # play audio
            for player in self.room.players.values():
                player.answer = ""
            self.room.show_answers = False 
            video = get_videos()[0]
            msg = {"type": "video", "id": video["id"], "start_time": video["start_time"]}
            await self.room.websocket.send(json.dumps(msg))

            self.room.room_text = f"<h3>Round {i+1}</h3>" + "Listen to this audio carefully"
            await self.room.update_frontend()
            await self.room.set_countdown(15)
            await asyncio.sleep(17)

            # collect answers
            self.room.room_text = f"<h3>Round {i+1}</h3>" + "Put down your answers"
            await self.room.update_frontend()
            await self.room.set_countdown(30)
            await asyncio.sleep(32)


            # round end
            answers = [player.answer for player in self.room.players.values()]
            print(f"results for {video['id']}")
            print(answers)
            self.room.room_text = f"<h3>Round {i+1}</h3>" + "The answers revealed"
            self.room.show_answers = True
            await self.room.update_frontend()
            await self.room.set_countdown(15)
            await asyncio.sleep(17)



        self.room.room_text = "The game is over. Thanks for playing"
        await self.room.update_frontend()
