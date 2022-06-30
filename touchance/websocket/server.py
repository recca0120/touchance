import asyncio
import logging
import sys
from asyncio import Task, AbstractEventLoop
from json import loads, JSONDecodeError, dumps
from typing import Set, Optional, Union

import websockets
from websockets.legacy.server import WebSocketServerProtocol

from touchance.quote_api import QuoteAPI
from touchance.websocket.query_param_protocol import QueryParamProtocol


class Server:
    connections: Set[WebSocketServerProtocol]
    __websocket: WebSocketServerProtocol
    __quote_api: QuoteAPI

    def __init__(self, quote_api: QuoteAPI, logger: Optional[logging.Logger] = None):
        self.connections = set()
        self.__quote_api = quote_api
        self.__logger = logger if logger is not None else logging

    def add(self, websocket: WebSocketServerProtocol):
        self.connections.add(websocket)
        # self.greeting()

    def greeting(self):
        self.broadcast({'Reply': 'CONNECTIONS', 'count': len(self.connections)})

    def remove(self, websocket):
        self.connections.remove(websocket)

    async def execute(self, websocket: WebSocketServerProtocol, message):
        command_list = {
            'QUERYALLINSTRUMENT': 'query_all_instrument',
            'QUERYINSTRUMENTINFO': 'query_instrument_info',
            'SUBQUOTE': 'subscribe',
            'UNSUBQUOTE': 'subscribe',
            'GETHISDATA': 'get_histories'
        }
        try:
            request = loads(message)
            func = command_list.get(request.get('Request'))

            if func is not None:
                await getattr(self, f'_{func}')(websocket, request)
        except JSONDecodeError as e:
            self.__logger.error(e)

    async def handle(self, websocket: WebSocketServerProtocol):
        self.add(websocket)

        try:
            async for message in websocket:
                await self.execute(websocket, message)
        finally:
            self.remove(websocket)

    def broadcast(self, obj):
        websockets.broadcast(self.connections, dumps(obj))

    async def _query_all_instrument(self, websocket: WebSocketServerProtocol, request: dict):
        await websocket.send(dumps(
            await self.__quote_api.query_all_instrument(request.get('Type'))
        ))

    async def _query_instrument_info(self, websocket: WebSocketServerProtocol, request: dict):
        await websocket.send(dumps(
            await self.__quote_api.query_instrument_info(request.get('Symbol'))
        ))

    async def _subscribe(self, websocket: WebSocketServerProtocol, request: dict):
        try:
            successful = await self.__quote_api.subscribe(request.get('Request'), request.get('Param'))
            response = '{"Reply": "%s", "Success": "%s"}' % (request.get('Request'), 'OK' if successful else 'FAIL')
            await websocket.send(response)
        except RuntimeError as e:
            await websocket.send(str(e))

    async def _get_histories(self, websocket: WebSocketServerProtocol, request: dict):
        param = request.get('Param')
        async for data in self.__quote_api.get_histories(
                param.get('Symbol'), param.get('SubDataType'), param.get('StartTime'), param.get('EndTime')
        ):
            await websocket.send(dumps(data))


async def start_server(loop: AbstractEventLoop, logger: logging.Logger, port: Union[str, int] = 8001):
    stop = loop.create_future()

    quote_api = QuoteAPI(event_loop=loop, logger=logger)
    await quote_api.connect()
    quote_api.serve()

    handler = Server(quote_api, logger)
    quote_api.on('PING', handler.broadcast)
    quote_api.on('REALTIME', handler.broadcast)

    try:
        async with websockets.serve(
                handler.handle,
                host='',
                port=port,
                extra_headers={'type': 'server'},
                create_protocol=QueryParamProtocol
        ):
            await stop
    except (asyncio.CancelledError, KeyboardInterrupt):
        sys.exit(0)


def __start_wss_server(logger: Optional[logging.Logger] = None, port: Union[str, int] = 8001):
    loop = asyncio.get_event_loop()
    logger = logger if logger is not None else logging

    task: Optional[Task] = None
    try:
        task = asyncio.ensure_future(start_server(loop=loop, logger=logger, port=port))
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        loop.run_forever()
        task.exception()
    finally:
        loop.close()
