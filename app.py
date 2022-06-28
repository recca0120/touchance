import asyncio

from src.websocket.websocket_handler import websocket_serve

if __name__ == '__main__':
    asyncio.run(websocket_serve(add_signal_handler=True))
