import asyncio
import signal

import websockets

from src.quant_bridge import QuoteAPI
from src.websocket.websocket_handler import WebsocketHandler
from src.websocket.query_param_protocol import QueryParamProtocol


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    quote_api = QuoteAPI()
    await quote_api.connect()
    print(quote_api.sub_port)
    quote_api.serve()

    handler = WebsocketHandler(quote_api)
    quote_api.on('PING', handler.broadcast)
    quote_api.on('REALTIME', handler.broadcast)

    async with websockets.serve(handler.handle, host='', port=8000, create_protocol=QueryParamProtocol):
        await stop


if __name__ == '__main__':
    asyncio.run(main())
