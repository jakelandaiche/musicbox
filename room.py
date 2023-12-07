import json
import asyncio
import websockets
from bidict import bidict

from player import Player
from game import Game
from utils import Hub, Sub

ROOMS = bidict()

class Room:
    """ room """

    def __init__(self, websocket):
        print("Room created")
        self.messages = Hub()
