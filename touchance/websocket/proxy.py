import asyncio
import logging
from asyncio import Task, AbstractEventLoop
from json import dumps
from typing import Set, Optional, Union

import websockets
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.server import WebSocketServerProtocol

from touchance.websocket.query_param_protocol import QueryParamProtocol


class Proxy(object):
    connections: Set[WebSocketServerProtocol]
    __server_token: str
    __server_port: int
    __server_host: str
    __client: Optional[WebSocketServerProtocol] = None

    def __init__(self, server_token: str, server_host: str, server_port: Union[str, int] = 8001,
                 logger: Optional[logging.Logger] = None):
        self.connections = set()
        self.__server_token = server_token
        self.__server_host = server_host
        self.__server_port = server_port
        self._logger = logger if logger is not None else logging

    @property
    def connected(self):
        return self.__client is not None and self.__client.closed is False

    async def connect(self) -> WebSocketServerProtocol:
        if self.connected is False:
            uri = 'ws://%s:%s?token=%s' % (self.__server_host, self.__server_port, self.__server_token)
            self.__client = await websockets.connect(uri)

        return self.__client

    async def broadcast(self):
        try:
            async for message in await self.connect():
                websockets.broadcast(self.connections, message)
        except (ConnectionClosedError, asyncio.exceptions.TimeoutError) as e:
            self._logger.error(e)
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


async def start_proxy(
        loop: AbstractEventLoop,
        server_token: str,
        server_host: str,
        server_port=8001,
        proxy_port=8000,
        logger: Optional[logging.Logger] = None,
):
    stop = loop.create_future()
    logger = logger if logger is not None else logging

    proxy = Proxy(server_token=server_token, server_host=server_host, server_port=server_port, logger=logger)
    task = loop.create_task(proxy.broadcast())

    try:
        async with websockets.serve(
                proxy.handle,
                host='',
                port=proxy_port,
                extra_headers={'type': 'proxy'},
                create_protocol=QueryParamProtocol
        ):
            await stop
    finally:
        task.cancel()


def __start_proxy(
        server_token: str,
        server_host: str,
        server_port: Union[str, int] = 8000,
        proxy_port: Union[str, int] = 8001,
        logger: Optional[logging.Logger] = None
):
    loop = asyncio.get_event_loop()
    task: Optional[Task] = None

    try:
        task = asyncio.ensure_future(start_proxy(
            loop=loop,
            logger=logger,
            server_token=server_token,
            server_host=server_host,
            server_port=server_port,
            proxy_port=proxy_port,
        ))
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        loop.run_forever()
        task.exception()
    finally:
        loop.close()
