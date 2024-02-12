import asyncio
import argparse
from websockets import serve

from server import ws_handler

parser = argparse.ArgumentParser(
        prog="MusicBox",
        )
parser.add_argument("--host", default="localhost")
parser.add_argument("--port", default=8080)


async def main(host, port):
    async with serve(ws_handler, host, port):
        await asyncio.Future()


if __name__ == "__main__":
    args = parser.parse_args()
    print(f"Listening on {args.host}:{args.port}")

    asyncio.run(main(args.host, args.port))