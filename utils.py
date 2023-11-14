import websockets
import json

async def websocket_pusher(websocket, queue):
    """ 
    Coroutine that redirects all websocket messages to another queue 
    Sends a CONNECTION_CLOSED message if the websocket is closed
    """
    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosed:
            message = {
                "type": "conn_close",
                "ws_id": websocket.id
            }
            await queue.put(message)
            break

        message = json.loads(message)
        message["ws_id"] = websocket.id

        await queue.put(message)


