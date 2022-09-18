from json import loads, JSONDecodeError, dumps

import websockets
from websockets.legacy.server import WebSocketServerProtocol

from src.quant_bridge import QuoteAPI


def access_token():
    return ''


class WebsocketHandler:
    connections: set
    __websocket: WebSocketServerProtocol
    __quote_api: QuoteAPI

    def __init__(self, quote_api: QuoteAPI):
        self.connections = set()
        self.__quote_api = quote_api

    def add(self, websocket: WebSocketServerProtocol):
        self.connections.add(websocket)
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
            print(str(e))

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
