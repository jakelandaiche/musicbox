import asyncio
import websockets
import json

connections = set()

async def handler(websocket):
    async for message in websocket:
        message = json.loads(message);
        if websocket not in connections:
            connections.add(websocket)

        out = json.dumps(message)
        websockets.broadcast(connections, out);
        continue

async def main():
    async with websockets.serve(handler, "", 8080):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
