import asyncio

import websockets

MEMBERS = set()


async def handler(websocket):
    async for message in websocket:
        sender = message["user"]
        if sender not in MEMBERS:
            MEMBERS.add(sender)
        websocket.send(message)


async def main():
    async with websockets.serve(handler, "", 8080):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
