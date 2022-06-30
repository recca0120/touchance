import asyncio
import http
import logging
import signal
from json import dumps
from typing import Set, Optional

import websockets
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.server import WebSocketServerProtocol

from src.websocket.utils import get_query_param, urlsafe_base64_encode


def access_token():
    return ''


class QueryParamProtocol(WebSocketServerProtocol):
    async def process_request(self, path, headers):
        token = get_query_param(path, 'token')
        if token is None or urlsafe_base64_encode(token) != access_token():
            return http.HTTPStatus.UNAUTHORIZED, [], b"Invalid token\n"


class Proxy(object):
    connections: Set[WebSocketServerProtocol]
    __host: str
    __port = 8001
    __token: str
    __client: Optional[WebSocketServerProtocol] = None

    def __init__(self, host: str, token: str):
        self.connections = set()
        self.__host = host
        self.__token = token

    @property
    def connected(self):
        return self.__client is not None and self.__client.closed is False

    async def connect(self) -> WebSocketServerProtocol:
        if self.connected is False:
            self.__client = await websockets.connect('ws://%s:%s?token=%s' % (self.__host, self.__port, self.__token))

        return self.__client

    async def broadcast(self):
        try:
            async for message in await self.connect():
                websockets.broadcast(self.connections, message)
        except (ConnectionClosedError, asyncio.exceptions.TimeoutError) as e:
            logging.error(e)
            await asyncio.sleep(1)
            await self.broadcast()

    async def handle(self, websocket: WebSocketServerProtocol):
        self.connections.add(websocket)
        self.greeting()
        try:
            async for message in websocket:
                if self.connected:
                    await self.__client.send(message)
        finally:
            self.connections.remove(websocket)

    def greeting(self):
        websockets.broadcast(self.connections, dumps({'Reply': 'CONNECTIONS', 'count': len(self.connections)}))


async def main():
    loop = asyncio.get_running_loop()
    stop = asyncio.Future()

    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    host = ''
    token = ''

    proxy = Proxy(host, token)
    loop.create_task(proxy.broadcast())

    async with websockets.serve(proxy.handle, host='', port=8000, create_protocol=QueryParamProtocol):
        await stop


if __name__ == '__main__':
    asyncio.run(main())
