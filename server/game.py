import asyncio
import math
from dataclasses import replace
from asyncio import CancelledError
from data import get_videos
from database import Database
from similarity import Similarity
import re

from .player import Player
from .utils import Sub
from .room import Room


async def fake_game(room: Room):
    print("fake game")

    fake_players = [replace(player) for player in room.players.values()]
    fake_answers = [
        "This is a song about a woman being happy that she is young and succesful.",
        "Chill pop song with an interesting out of tune horns.",
        "A woman singing in a low, repetitive, quiet voice about being successful. The song has a moderately fast tempo and features detuned horns.",
        "ARIANA GRANDE",
        "The track unfolds as a vibrant sonic tapestry, blending pulsating beats with the artist's vocals. Its buoyant energy and uplifting lyrics create a musical journey that encapsulates the essence of triumph and accomplishment by repeating the word successful.",
        "A successful woman",
        "A womans singing over minimal arrangement",
        "uhh",
    ]

    async def update_fake_players():
        objs = [player.to_obj() for player in fake_players]
        await room.send({"type": "players", "players": objs})

    for player in fake_players:
        player.answer = None
        player.total = 0
        player.score = 0
        player.color_list = []

    # Round Start
    await room.broadcast({"type": "state", "state": "FAKEROUNDSTART"})
    await update_fake_players()
    await room.send({"type": "video", "id": "_IvArrFhcp0", "start_time": 52})
    await asyncio.sleep(20)

    # Collect
    await room.broadcast({"type": "state", "state": "FAKEROUNDCOLLECT"})
    # Input fake answers at timed intervals
    for player, answer in zip(fake_players, fake_answers):
        await asyncio.sleep(1)
        player.answer = answer
        await update_fake_players()
    await asyncio.sleep(1)

    # Compute scores
    try:
        compute_scores(fake_players)
    except Exception as e:
        print("Error computing scores")
        print(e)

    # Round End
    await update_fake_players()
    await room.broadcast({"type": "state", "state": "FAKEROUNDEND"})
    await asyncio.sleep(20)

    # Round End 2
    await update_fake_players()
    await room.broadcast({"type": "state", "state": "FAKEROUNDEND2"})
    await asyncio.sleep(10)


async def game_task(room: Room, N=5, tutorial=True):
    print(f"Starting game with {room.dataset} and {N} rounds")
    try:
        db = Database()
        game_id = db.create_game()
    except Exception as e:
        print("Database error")
        print(e)
        return

    try:
        videos = get_videos(N=N, dataset=room.dataset)
    except Exception as e:
        print("Error retrieving videos")
        print(e)
        return

    try:
        # Init
        for player in room.players.values():
            try:
                player.db_id = db.create_player(player.name, game_id)
            except Exception as e:
                print("Database error")
                print(e)
            player.answer = None
            player.total = 0
            player.score = 0
            player.color_list = []
        await room.update_players()

        # Game Start
        await room.broadcast({"type": "state", "state": "GAMESTART"})
        await asyncio.sleep(15)

        if tutorial:
            await fake_game(room)

        for n in range(1, N + 1):
            # Reset scores
            for player in room.players.values():
                player.clear()
            await room.update_players()

            # Update round number
            await room.send(
                {
                    "type": "round_num",
                    "round_num": n,
                }
            )
            # Round Start
            await room.broadcast({"type": "state", "state": "ROUNDSTART"})
            video = videos[n - 1]
            await room.send(
                {"type": "video", "id": video["id"], "start_time": video["start_time"]}
            )
            await asyncio.sleep(20)

            # Collect answers
            await room.broadcast({"type": "state", "state": "ROUNDCOLLECT"})
            try:
                await asyncio.wait_for(wait_for_answers(room), timeout=30)
            except TimeoutError:
                pass

            # Compute scores
            try:
                compute_scores(list(room.players.values()))
            except Exception as e:
                print("Error computing scores")
                print(e)

            try:
                for player in room.players.values():
                    db.write_answer(player, n, video["id"])
            except Exception as e:
                print("Error writing to database")
                print(e)

            # Round end await room.update_players()
            await room.broadcast({"type": "state", "state": "ROUNDEND"})
            await asyncio.sleep(30)

        await room.broadcast(
            {
                "type": "player_stats",
                "player_stats": [p.to_obj() for p in room.players.values()],
            }
        )

        await room.broadcast({"type": "state", "state": "GAMEEND"})

    except asyncio.CancelledError:
        print("Game cancelled")
        raise
    except Exception as e:
        print("Error in game")
        print(e)
    finally:
        db.cur.close()
        db.con.close()
        room.game = None


sim_checker = Similarity()

common_words = ["the", "and", "that", "have", "for", "not", "with", "music"]


def compute_scores(players: list[Player]):
    with_answers = [player for player in players if player.answer is not None]
    sim_scores = sim_checker.sim_scores([player.answer for player in with_answers])
    colors: dict[str, int] = {"the": 0}

    for i in range(len(with_answers)):
        player = with_answers[i]
        score = math.floor(sim_scores[i] * 1000)
        mult = 0

        split_answers = []
        for j in range(len(with_answers)):
            if j != i:
                split_answers.extend(
                    with_answers[j].answer.strip(".;,\n\t").lower().split()
                )

        # get words
        answer_l = player.answer.strip(".;,\n\t").lower().split()
        answer_s = set()
        matches = 0

        for word in answer_l:
            player.word_count += 1
            player.unique_words.add(word)
            length = len(word)
            player.word_len += length
            if length > 2 and word not in common_words:
                # more points for words in common with others
                if word in split_answers:
                    if word not in answer_s:
                        # increase multiplier for each unique uncommon word
                        if mult < 10:
                            mult += 1
                        matches += 1
                    # keep track of what words have been matching and assign each a number
                    if word not in colors:
                        colors[word] = max(colors.values()) + 1
                    player.color_list.append(colors[word])
                else:
                    player.color_list.append(0)
                answer_s.add(word)
            else:
                player.color_list.append(0)

        final_mult = matches / 10 * 0.35
        player.score = int((score + matches ^ 2) * (1 + final_mult))
        player.total += player.score
        player.score_info = {
            "bonus": f"{final_mult:0.3f}%",
            "similarity": score,
            "matches": matches**2,
        }


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

                    if all(
                        player.answer is not None for player in room.players.values()
                    ):
                        break
                except KeyError:
                    print("No key")

        print("Received all answers")
    except CancelledError:
        print("Did not receive all answers")
    finally:
        return
