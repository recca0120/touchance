import os
from json import loads, dumps
from unittest.mock import MagicMock, AsyncMock

import pytest
from websockets.legacy.server import WebSocketServerProtocol

from src.quant_bridge import QuoteAPI
from src.websocket.server import Server


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


@pytest.mark.asyncio
async def test_execute_queryallinstrument(handler: Server, websocket: MagicMock, quote_api: MagicMock):
    message = '{"Request": "QUERYALLINSTRUMENT", "Type": "Fut"}'

    quote_api.query_all_instrument.return_value = get_fixture('query_all_instrument.txt')

    await handler.execute(websocket, message)

    info: AsyncMock = quote_api.query_all_instrument
    info.assert_called_once_with('Fut')
    send: AsyncMock = websocket.send
    send.assert_called_once_with(dumps(quote_api.query_all_instrument.return_value))


@pytest.mark.asyncio
async def test_query_instrument_info(handler: Server, websocket: MagicMock, quote_api: MagicMock):
    message = '{"Request": "QUERYINSTRUMENTINFO", "Symbol": "TC.F.TWF.FITX.HOT"}'

    quote_api.query_instrument_info.return_value = get_fixture('query_instrument_info.txt')

    await handler.execute(websocket, message)

    info: AsyncMock = quote_api.query_instrument_info
    info.assert_called_once_with('TC.F.TWF.FITX.HOT')
    send: AsyncMock = websocket.send
    send.assert_called_once_with(dumps(quote_api.query_instrument_info.return_value))


@pytest.mark.asyncio
async def test_subquote_realtime(handler: Server, websocket: MagicMock, quote_api: MagicMock):
    message = '{"Request": "SUBQUOTE", "Param": {"Symbol": "TC.F.TWF.FITX.HOT", "SubDataType": "REALTIME"}}'
    # message = '{"Request": "SUBQUOTE", "Param": {"Symbol": "TC.F.CBOT.YM.202209", "SubDataType": "REALTIME"}}'

    quote_api.subscribe.return_value = True

    await handler.execute(websocket, message)

    subscribe: AsyncMock = quote_api.subscribe
    subscribe.assert_called_once_with('SUBQUOTE', {'Symbol': 'TC.F.TWF.FITX.HOT', 'SubDataType': 'REALTIME'})
    send: AsyncMock = websocket.send
    send.assert_called_once_with('{"Reply": "SUBQUOTE", "Success": "OK"}')


@pytest.mark.asyncio
async def test_unsubquote_realtime(handler: Server, websocket: MagicMock, quote_api: MagicMock):
    message = '{"Request": "UNSUBQUOTE", "Param": {"Symbol": "TC.F.TWF.FITX.HOT", "SubDataType": "REALTIME"}}'
    # message = '{"Request": "UNSUBQUOTE", "Param": {"Symbol": "TC.F.CBOT.YM.202209", "SubDataType": "REALTIME"}}'

    quote_api.subscribe.return_value = True

    await handler.execute(websocket, message)

    subscribe: AsyncMock = quote_api.subscribe
    subscribe.assert_called_once_with('UNSUBQUOTE', {'Symbol': 'TC.F.TWF.FITX.HOT', 'SubDataType': 'REALTIME'})
    send: AsyncMock = websocket.send
    send.assert_called_once_with('{"Reply": "UNSUBQUOTE", "Success": "OK"}')


@pytest.mark.asyncio
async def test_unsubquote_realtime(handler: Server, websocket: MagicMock, quote_api: MagicMock):
    message = '{"Request": "GETHISDATA", "Param": {"Symbol": "TC.F.TWF.FITX.HOT", "SubDataType": "1K", "StartTime": "2021030100", "EndTime": "2021031700"}}'
    # message = '{"Request": "GETHISDATA", "Param": {"Symbol": "TC.F.TWF.FITX.HOT", "SubDataType": "TICKS", "StartTime": "2022062700", "EndTime": "2022062723"}}'

    quote_api.get_histories.return_value = AsyncIterator([{"DataType": "1K", "HisData": [
        {"Date": "20210302", "Time": "4600", "UpTick": "971", "UpVolume": "2992", "DownTick": "910",
         "DownVolume": "1632", "UnchVolume": "0", "Open": "16249", "High": "16277", "Low": "16245",
         "Close": "16254",
         "Volume": "4624", "OI": "0", "QryIndex": "1"},
    ]}])

    await handler.execute(websocket, message)

    get_histories: AsyncMock = quote_api.get_histories
    get_histories.assert_called_once_with('TC.F.TWF.FITX.HOT', '1K', '2021030100', '2021031700')
    send: AsyncMock = websocket.send
    send.assert_called()


def get_fixture(file: str):
    fixture = open(os.path.realpath(os.path.join(os.path.dirname(__file__), '../fixtures/' + file)), 'rb').read()

    return loads(fixture[:-1].decode())


@pytest.fixture
def websocket():
    return MagicMock(spec=WebSocketServerProtocol)


@pytest.fixture
def quote_api():
    return MagicMock(spec=QuoteAPI)
    pass


@pytest.fixture
def handler(quote_api: QuoteAPI):
    return Server(quote_api)
    pass
