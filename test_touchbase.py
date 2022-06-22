from unittest.mock import MagicMock

import pytest
from zmq import REQ

from touchance import QuoteAPI


def test_connect(mock_quote_api, context, locker, socket):
    quote_api = mock_quote_api
    login_params = {
        'Request': 'LOGIN',
        'Param': {'SystemName': 'ZMQ', 'ServiceKey': '8076c9867a372d2a9a814ae710c256e2'}
    }

    assert quote_api.connect()
    assert quote_api.session_key == '777d79aadfaff06597919a9ce30f8b46'
    assert quote_api.sub_port == '50994'

    assert locker.acquire.called
    context.socket.assert_called_once_with(REQ)
    socket.connect.assert_called_once_with('tcp://127.0.0.1:51237')
    socket.send_json.assert_called_once_with(login_params)
    assert locker.release.called


def test_disconnect(mock_quote_api, socket, locker):
    quote_api = mock_quote_api
    quote_api.connect()

    recv: MagicMock = socket.recv
    recv.reset_mock()
    recv.return_value = b'{"Reply":"LOGOUT","Success":"OK"}\x00'

    assert locker.acquire.called
    assert quote_api.disconnect()
    assert locker.release.called


def test_query_instrument_info(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    message = b'{"Reply":"QUERYINSTRUMENTINFO","Success":"OK","Info":{"TC.F.TWF":{"Duration":"ROD;IOC;FOK;","EXG.SIM":"TWF","EXG.TC3":"TWF","EXGName.CHS":"\xe5\x8f\xb0\xe6\xb9\xbe\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","EXGName.CHT":"\xe5\x8f\xb0\xe7\x81\xa3\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","OpenCloseTime":"00:45~05:45","OrderType":"MARKET;LIMIT;MWP;","OrderTypeMX":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","OrderTypeMX.TC":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","Position":"A;O;C;","ResetTime":"23:30","Symbol.SS2":"I.F.TWF","TimeZone":"Asia/Shanghai"},"TC.F.TWF.FITX":{"Currency":"TWD","Denominator":"1","Denominator.ML":"1","Denominator.yuanta":"1","Duration":"ROD;IOC;FOK;","EXG":"TWF","EXG.Entrust":"TWF","EXG.ITS":"TWF","EXG.ITS_KGI":"TWF","EXG.ITS_TW":"TWF","EXG.ML":"TWF","EXG.PATS":"TWF","EXG.SIM":"TWF","EXG.TC3":"TWF","EXG.dcn":"TWF","EXG.mdc":"TAIFEX","EXG.mo":"TWF","EXG.yuanta":"TAIFEX","EXGName.CHS":"\xe5\x8f\xb0\xe6\xb9\xbe\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","EXGName.CHT":"\xe5\x8f\xb0\xe7\x81\xa3\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","Group.CHS":"\xe6\x8c\x87\xe6\x95\xb0","Group.CHT":"\xe6\x8c\x87\xe6\x95\xb8","Group.ENG":"Equities","I3_TickSize":"1","Multiplier.CTP":"1","Multiplier.GQ2":"1","Multiplier.GTS":"1","Multiplier.ML":"1","Multiplier.yuanta":"1","Name.CHS":"\xe5\x8f\xb0\xe6\x8c\x87","Name.CHT":"\xe8\x87\xba\xe6\x8c\x87","Name.ENG":"TAIEX Futures","OpenCloseTime":"00:45~05:45;07:00~21:00","OrderType":"MARKET;LIMIT;MWP;","OrderTypeMX":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","OrderTypeMX.TC":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","Position":"A;O;C;","ResetTime":"06:50","SettlementTime":"05:30","ShowDeno":"1","ShowDeno.Entrust":"1","ShowDeno.concords":"1","ShowDeno.dcn":"1","ShowDeno.kgi":"1","ShowDeno.pfcf":"1","ShowDeno.tw":"1","ShowDeno.wlf":"1","ShowMulti":"1","ShowMulti.Entrust":"1","ShowMulti.concords":"1","ShowMulti.dcn":"1","ShowMulti.kgi":"1","ShowMulti.pfcf":"1","ShowMulti.tw":"1","ShowMulti.wlf":"1","Symbol":"FITX","Symbol.Entrust":"FITX","Symbol.GQ2":"ICE.TWF.FITX","Symbol.ITS":"FITX","Symbol.ITS_KGI":"FITX","Symbol.ITS_TW":"FITX","Symbol.ML":"FITX","Symbol.PATS":"FITX","Symbol.SIM":"FITX","Symbol.SS2":"I.F.TWF.FITX","Symbol.TC3":"ICE.TWF.FITX","Symbol.TCDATA":"ICE.TWF.FITX","Symbol.dcn":"FITX","Symbol.mdc":"TXF","Symbol.mo":"TXF","Symbol.yuanta":"TXF","TickSize":"1","TickSize.Underlying":"0.01","TicksPerPoint":"1","TimeZone":"Asia/Shanghai","Underlying.OpenCloseTime":"01:00~05:30","Weight":"200","lotLimitDay":"10","lotLimitNight":"5","pinyin":"tz"}}}\x00'
    socket.recv.reset_mock()
    socket.recv.return_value = message

    info = quote_api.query_instrument_info('TC.F.TWF.FITX.HOT')

    assert info['Success'] == 'OK'
    assert info['Info']['TC.F.TWF.FITX']['Name.CHT'] == '臺指'


def test_keep_alive(mock_quote_api, context, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    recv: MagicMock = socket.recv
    recv.reset_mock()
    recv.side_effect = [
        b'PING:{"DataType":"PING"}\x00',
        b'{"Reply":"PONG","Success":"OK"}\x00',
        b'stop\x00'
    ]

    quote_api.keep_alive()

    socket.send_json.assert_called_with({"Request": "PONG", "SessionKey": quote_api.session_key, "ID": 'TC'})


def test_subscribe(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.return_value = b'{"Reply": "SUBQUOTE", "Success": "OK"}\x00'

    symbol = 'TC.F.TWF.FITX.HOT'

    assert quote_api.subscribe_quote(symbol)
    socket.send_json.assert_called_with({
        'Request': 'SUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'SubDataType': 'REALTIME', 'Symbol': 'TC.F.TWF.FITX.HOT'},
    })


def test_unsubscribe(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.return_value = b'{"Reply": "UNSUBQUOTE", "Success": "OK"}\x00'

    symbol = 'TC.F.TWF.FITX.HOT'

    assert quote_api.unsubscribe_quote(symbol)
    socket.send_json.assert_called_with({
        'Request': 'UNSUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'SubDataType': 'REALTIME', 'Symbol': 'TC.F.TWF.FITX.HOT'},
    })


@pytest.fixture()
def quote_api():
    quote_api = QuoteAPI(keep_alive=False)

    return quote_api


@pytest.fixture()
def mock_quote_api(context, locker):
    api = QuoteAPI(keep_alive=False)
    api.set_context(context)
    api.set_locker(locker)

    return api


@pytest.fixture()
def socket():
    socket = MagicMock()
    socket.connect = MagicMock()
    socket.send_json = MagicMock()
    message = b'{"Reply":"LOGIN","Success":"OK","SessionKey":"777d79aadfaff06597919a9ce30f8b46","SubPort":"50994"}\x00'
    socket.recv = MagicMock(return_value=message)

    return socket


@pytest.fixture()
def context(socket):
    context = MagicMock()
    context.socket = MagicMock(return_value=socket)

    return context


@pytest.fixture()
def locker():
    locker = MagicMock()
    locker.acquire = MagicMock()
    locker.release = MagicMock()

    return locker
