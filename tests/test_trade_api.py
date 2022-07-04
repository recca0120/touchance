import asyncio
from unittest.mock import MagicMock, AsyncMock

import pytest
from pyee.asyncio import AsyncIOEventEmitter

from touchance.trade_api import TradeAPI


@pytest.mark.asyncio
async def test_get_accounts(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"DataType": "ACCOUNTS", "Success": "OK", "Accounts": [{"BrokerID": "123456", "Account": "XXX", "UserName": "XXX", "AccountName": "XXX"}, {"BrokerID": "123456", "Account": "XXX", "UserName": "XXX", "AccountName": "XXX"}]}\x00'
    ]

    result = await trade_api.get_accounts()

    assert result['DataType'] == 'ACCOUNTS'
    socket.send_json.assert_called_with({'Request': 'ACCOUNTS', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46'})


@pytest.mark.asyncio
async def test_restore_report(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "RESTOREREPORT", "Success": "OK", "Orders": [{"ReportID": "123456", "Account": "XXX", "BrokerID": "XXX", "Symbol": "XXX", "Side": "n", "QryIndex": "n"}, {"ReportID": "123456", "Account": "XXX", "BrokerID": "XXX", "Symbol": "XXX", "Side": "n", "QryIndex": "n"}]}\x00'
    ]

    result = await trade_api.restore_report(0)

    assert result['Reply'] == 'RESTOREREPORT'
    socket.send_json.assert_called_with(
        {'Request': 'RESTOREREPORT', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46', 'QryIndex': 0}
    )


@pytest.mark.asyncio
async def test_new_order(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "NEWORDER", "Success": "OK"}\x00'
    ]

    param = {
        "Symbol": "TC.F.TWF.FITX.HOT",
        "BrokerID": '123456',
        "Account": 'XXX',
        "Price": "15000",
        "TimeInForce": "1",
        "Side": "1",
        "OrderType": "2",
        "OrderQty": "1",
        "PositionEffect": "0"
    }
    result = await trade_api.new_order(param)

    assert result['Reply'] == 'NEWORDER'
    socket.send_json.assert_called_with({
        'Request': 'NEWORDER', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46', 'Param': param
    })


@pytest.mark.asyncio
async def test_new_order_with_err_code(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "NEWORDER", "Success": "Fail", "ErrCode": "-10"}\x00'
    ]
    param = {
        "Symbol": "TC.F.TWF.FITX.HOT",
        "BrokerID": '123456',
        "Account": 'XXX',
        "Price": "15000",
        "TimeInForce": "1",
        "Side": "1",
        "OrderType": "2",
        "OrderQty": "1",
        "PositionEffect": "0"
    }

    with pytest.raises(Exception) as e:
        await trade_api.new_order(param)

    assert e.value.code == '-10'
    assert str(e.value) == 'Unknown Error'


@pytest.mark.asyncio
async def test_replace_order(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "REPLACEORDER", "Success": "OK", "ReportID": "123456"}\x00'
    ]

    param = {
        "ReportID": "123456",
        "ReplaceExecType": "n",
        "OrderQty": "n",
        "Price": "xxxxx",
        "StopPrice": "xxxxx",
    }
    result = await trade_api.replace_order(param)

    assert result['Reply'] == 'REPLACEORDER'
    socket.send_json.assert_called_with({
        'Request': 'REPLACEORDER', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46', 'Param': param
    })


@pytest.mark.asyncio
async def test_cancel_order(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "CANCELORDER", "Success": "OK", "ReportID": "123456"}\x00'
    ]

    param = {
        "ReportID": "123456",
    }
    result = await trade_api.cancel_order(param)

    assert result['Reply'] == 'CANCELORDER'
    socket.send_json.assert_called_with({
        'Request': 'CANCELORDER', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46', 'Param': param
    })


@pytest.mark.asyncio
async def test_margins(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "MARGINS", "Success": "OK", "Margins": [{"BrokerID": "XXX", "Account": "XXX", "TransactDate": "n", "TransactTime": "n", "BeginningBalance": "XXX", "Commissions": "XXX"}, {"BrokerID": "XXX", "Account": "XXX", "TransactDate": "n", "TransactTime": "n", "BeginningBalance": "XXX", "Commissions": "XXX"}]}'
    ]

    result = await trade_api.margins('XXXXXXXXX')

    assert result['Reply'] == 'MARGINS'
    socket.send_json.assert_called_with({
        'Request': 'MARGINS', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46', 'AccountMask': 'XXXXXXXXX'
    })


@pytest.mark.asyncio
async def test_positions(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "POSITIONS", "Success": "OK", "Positions": [{"BrokerID": "XXX", "Account": "XXX", "TransactDate": "n", "TransactTime": "n", "Quantity": "n", "SumLongQty": "n", "SumShortQty": "n", "QryIndex": "n"}, {"BrokerID": "XXX", "Account": "XXX", "TransactDate": "n", "TransactTime": "n", "Quantity": "n", "SumLongQty": "n", "SumShortQty": "n", "QryIndex": "n"}]}'
    ]

    result = await trade_api.positions('XXXXXXXXX', 0)

    assert result['Reply'] == 'POSITIONS'
    socket.send_json.assert_called_with({
        'Request': 'POSITIONS', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46', 'AccountMask': 'XXXXXXXXX',
        'QryIndex': 0
    })


@pytest.mark.asyncio
async def test_restore_fill_report(mock_trade_api: TradeAPI, socket):
    trade_api = mock_trade_api
    await trade_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [
        b'{"Reply": "RESTOREFILLREPORT", "Success": "OK", "Orders": [{"ReportID": "123456", "Account": "XXX", "BrokerID": "XXX", "Symbol": "XXX", "Side": "n", "QryIndex": "n"}, {"ReportID": "123456", "Account": "XXX", "BrokerID": "XXX", "Symbol": "XXX", "Side": "n", "QryIndex": "n"}]}'
    ]

    result = await trade_api.restore_fill_report(0)

    assert result['Reply'] == 'RESTOREFILLREPORT'
    socket.send_json.assert_called_with(
        {'Request': 'RESTOREFILLREPORT', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46', 'QryIndex': 0}
    )


@pytest.fixture()
def emitter():
    return AsyncIOEventEmitter(loop=asyncio.get_event_loop())


@pytest.fixture()
def trade_api():
    return TradeAPI()


@pytest.fixture()
def mock_trade_api(context, locker, emitter):
    return TradeAPI(context, locker, emitter, asyncio.get_event_loop())


@pytest.fixture()
def socket():
    socket = MagicMock()
    socket.connect = MagicMock()
    socket.send_json = MagicMock()
    message = b'{"Reply":"LOGIN","Success":"OK","SessionKey":"777d79aadfaff06597919a9ce30f8b46","SubPort":"50994"}\x00'
    socket.recv = AsyncMock(side_effect=[message])

    return socket


@pytest.fixture()
def sub_socket():
    socket = MagicMock()
    socket.connect = MagicMock()
    socket.send_json = MagicMock()
    socket.recv = AsyncMock(side_effect=[b'__pytest_stop__\x00'])

    return socket


@pytest.fixture()
def context(socket, sub_socket):
    context = MagicMock()
    context.socket = MagicMock(side_effect=[socket, sub_socket])

    return context


@pytest.fixture()
def locker():
    locker = MagicMock()
    locker.acquire = AsyncMock()
    locker.release = MagicMock()

    return locker
