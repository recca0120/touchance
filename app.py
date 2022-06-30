import asyncio

from touchance.websocket.server import serve

if __name__ == '__main__':
    asyncio.run(serve())
