import asyncio

from src.websocket.server import serve

if __name__ == '__main__':
    asyncio.run(serve())
