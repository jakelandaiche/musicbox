import asyncio
import websockets
import argparse

# move rooms into server class
from bidict import bidict

from ws_handler import ws_handler


class Server:

    def __init__(self):
        self.parse_args()

    def parse_args(self):
        parser = argparse.ArgumentParser(
            prog="MusicBox",
        )
        parser.add_argument("--host", default="localhost")
        parser.add_argument("--port", default=8080)
        parser.add_argument("--file", default="filtered.csv")
        args = parser.parse_args()
        self.host = args.host
        self.port = args.port

    async def start(self):
        print(f"Listening on {self.host}:{self.port}")
        async with websockets.serve(ws_handler, self.host, self.port):
            await asyncio.Future()



if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start())