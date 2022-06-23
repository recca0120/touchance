import os
from unittest.mock import MagicMock

import pytest
from zmq import REQ

from src.event_manager import EventManager
from src.touchance import QuoteAPI


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
    context.socket.call_args_list[0].assert_called_with(REQ)
    socket.connect.assert_called_once_with('tcp://127.0.0.1:51237')
    socket.send_json.assert_called_once_with(login_params)
    assert locker.release.called


def test_disconnect(mock_quote_api, socket, locker):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply":"LOGOUT","Success":"OK"}\x00']

    assert locker.acquire.called
    assert quote_api.disconnect()
    assert locker.release.called


def test_query_all_instrument_info(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    message = open(os.path.join(os.path.dirname(__file__), 'fixtures/query_all_instrument.txt'), 'rb').read()
    socket.recv.reset_mock()
    socket.recv.side_effect = [message]

    info = quote_api.query_all_instrument('Fut')
    assert info['Success'] == 'OK'

    socket.send_json.assert_called_with({
        'Request': 'QUERYALLINSTRUMENT',
        'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Type': 'Fut'
    })


def test_query_instrument_info(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    message = b'{"Reply":"QUERYINSTRUMENTINFO","Success":"OK","Info":{"TC.F.TWF":{"Duration":"ROD;IOC;FOK;","EXG.SIM":"TWF","EXG.TC3":"TWF","EXGName.CHS":"\xe5\x8f\xb0\xe6\xb9\xbe\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","EXGName.CHT":"\xe5\x8f\xb0\xe7\x81\xa3\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","OpenCloseTime":"00:45~05:45","OrderType":"MARKET;LIMIT;MWP;","OrderTypeMX":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","OrderTypeMX.TC":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","Position":"A;O;C;","ResetTime":"23:30","Symbol.SS2":"I.F.TWF","TimeZone":"Asia/Shanghai"},"TC.F.TWF.FITX":{"Currency":"TWD","Denominator":"1","Denominator.ML":"1","Denominator.yuanta":"1","Duration":"ROD;IOC;FOK;","EXG":"TWF","EXG.Entrust":"TWF","EXG.ITS":"TWF","EXG.ITS_KGI":"TWF","EXG.ITS_TW":"TWF","EXG.ML":"TWF","EXG.PATS":"TWF","EXG.SIM":"TWF","EXG.TC3":"TWF","EXG.dcn":"TWF","EXG.mdc":"TAIFEX","EXG.mo":"TWF","EXG.yuanta":"TAIFEX","EXGName.CHS":"\xe5\x8f\xb0\xe6\xb9\xbe\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","EXGName.CHT":"\xe5\x8f\xb0\xe7\x81\xa3\xe6\x9c\x9f\xe4\xba\xa4\xe6\x89\x80","Group.CHS":"\xe6\x8c\x87\xe6\x95\xb0","Group.CHT":"\xe6\x8c\x87\xe6\x95\xb8","Group.ENG":"Equities","I3_TickSize":"1","Multiplier.CTP":"1","Multiplier.GQ2":"1","Multiplier.GTS":"1","Multiplier.ML":"1","Multiplier.yuanta":"1","Name.CHS":"\xe5\x8f\xb0\xe6\x8c\x87","Name.CHT":"\xe8\x87\xba\xe6\x8c\x87","Name.ENG":"TAIEX Futures","OpenCloseTime":"00:45~05:45;07:00~21:00","OrderType":"MARKET;LIMIT;MWP;","OrderTypeMX":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","OrderTypeMX.TC":"MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;","Position":"A;O;C;","ResetTime":"06:50","SettlementTime":"05:30","ShowDeno":"1","ShowDeno.Entrust":"1","ShowDeno.concords":"1","ShowDeno.dcn":"1","ShowDeno.kgi":"1","ShowDeno.pfcf":"1","ShowDeno.tw":"1","ShowDeno.wlf":"1","ShowMulti":"1","ShowMulti.Entrust":"1","ShowMulti.concords":"1","ShowMulti.dcn":"1","ShowMulti.kgi":"1","ShowMulti.pfcf":"1","ShowMulti.tw":"1","ShowMulti.wlf":"1","Symbol":"FITX","Symbol.Entrust":"FITX","Symbol.GQ2":"ICE.TWF.FITX","Symbol.ITS":"FITX","Symbol.ITS_KGI":"FITX","Symbol.ITS_TW":"FITX","Symbol.ML":"FITX","Symbol.PATS":"FITX","Symbol.SIM":"FITX","Symbol.SS2":"I.F.TWF.FITX","Symbol.TC3":"ICE.TWF.FITX","Symbol.TCDATA":"ICE.TWF.FITX","Symbol.dcn":"FITX","Symbol.mdc":"TXF","Symbol.mo":"TXF","Symbol.yuanta":"TXF","TickSize":"1","TickSize.Underlying":"0.01","TicksPerPoint":"1","TimeZone":"Asia/Shanghai","Underlying.OpenCloseTime":"01:00~05:30","Weight":"200","lotLimitDay":"10","lotLimitNight":"5","pinyin":"tz"}}}\x00'
    socket.recv.reset_mock()
    socket.recv.side_effect = [message]

    info = quote_api.query_instrument_info('TC.F.TWF.FITX.HOT')

    assert info['Success'] == 'OK'
    assert info['Info']['TC.F.TWF.FITX']['Name.CHT'] == '臺指'

    socket.send_json.assert_called_with({
        'Request': 'QUERYINSTRUMENTINFO',
        'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Symbol': 'TC.F.TWF.FITX.HOT'
    })


def test_subscribe_quote(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply": "SUBQUOTE", "Success": "OK"}\x00']

    symbol = 'TC.F.TWF.FITX.HOT'

    assert quote_api.subscribe_quote(symbol)
    socket.send_json.assert_called_with({
        'Request': 'SUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'Symbol': symbol, 'SubDataType': 'REALTIME'},
    })


def test_unsubscribe_quote(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply": "UNSUBQUOTE", "Success": "OK"}\x00']

    symbol = 'TC.F.TWF.FITX.HOT'

    assert quote_api.unsubscribe_quote(symbol)
    socket.send_json.assert_called_with({
        'Request': 'UNSUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'Symbol': symbol, 'SubDataType': 'REALTIME'},
    })


def test_subscribe_greeks(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply": "SUBQUOTE", "Success": "OK"}\x00']

    symbol = 'TC.F.TWF.FITX.HOT'

    assert quote_api.subscribe_greeks(symbol)
    socket.send_json.assert_called_with({
        'Request': 'SUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'Symbol': symbol, 'SubDataType': 'GREEKS', 'GreeksType': 'REAL'},
    })


def test_unsubscribe_greeks(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply": "UNSUBQUOTE", "Success": "OK"}\x00']

    symbol = 'TC.F.TWF.FITX.HOT'

    assert quote_api.unsubscribe_greeks(symbol)
    socket.send_json.assert_called_with({
        'Request': 'UNSUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'Symbol': symbol, 'SubDataType': 'GREEKS', 'GreeksType': 'REAL'},
    })


def test_subscribe_history_1k(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply": "SUBQUOTE", "Success": "OK"}\x00']

    symbol = 'TC.F.TWF.FITX.HOT'
    data_type = '1K'
    start_time = '2021030100'
    end_time = '2021031700'

    assert quote_api.subscribe_history(symbol, data_type, start_time, end_time)
    socket.send_json.assert_called_with({
        'Request': 'SUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'Symbol': symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time},
    })


def test_unsubscribe_history_1k(mock_quote_api, socket):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply": "UNSUBQUOTE", "Success": "OK"}\x00']

    symbol = 'TC.F.TWF.FITX.HOT'
    data_type = '1K'
    start_time = '2021030100'
    end_time = '2021031700'

    assert quote_api.unsubscribe_history(symbol, data_type, start_time, end_time)
    socket.send_json.assert_called_with({
        'Request': 'UNSUBQUOTE', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'Symbol': symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time},
    })


def test_get_history_1k(mock_quote_api, socket, emitter):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = open(
        os.path.join(os.path.dirname(__file__), 'fixtures/history-1k.txt'), 'rb'
    ).read().splitlines()

    message = b'TC.F.TWF.FITX.HOT:{"DataType":"1K","StartTime":"2021030100","EndTime":"2021031700",' \
              b'"Symbol":"TC.F.TWF.FITX.HOT","Status":"Ready"}\x00'

    emitter.emit('RECV_MESSAGE', message)

    symbol = 'TC.F.TWF.FITX.HOT'
    data_type = '1K'
    start_time = '2021030100'
    end_time = '2021031700'

    send_json: MagicMock = socket.send_json
    qry_index = send_json.call_args[0][0]['Param']['QryIndex']
    send_json.assert_called_with({
        'Request': 'GETHISDATA',
        'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {
            'Symbol': symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time,
            'QryIndex': qry_index
        }
    })


def test_pong(mock_quote_api, socket, emitter):
    quote_api = mock_quote_api
    quote_api.connect()

    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply":"PONG","Success":"OK"}\x00']

    emitter.emit('RECV_MESSAGE', b'PING:{"DataType":"PING"}\x00')
    socket.send_json.assert_called_with({"Request": "PONG", "SessionKey": quote_api.session_key, "ID": 'TC'})


def test_keep_alive_pong(mock_quote_api, socket, sub_socket):
    quote_api = mock_quote_api
    quote_api.connect()

    sub_socket.recv.reset_mock()
    sub_socket.recv.side_effect = [b'PING:{"DataType":"PING"}\x00', b'__pytest_stop__\x00']
    socket.recv.reset_mock()
    socket.recv.side_effect = [b'{"Reply":"PONG","Success":"OK"}\x00']

    quote_api.keep_alive()

    subscriber = quote_api.get_subscriber()
    subscriber.stop()

    socket.send_json.assert_called_with({"Request": "PONG", "SessionKey": quote_api.session_key, "ID": 'TC'})


def test_keep_alive_get_history_1k(mock_quote_api, socket, sub_socket):
    quote_api = mock_quote_api
    quote_api.connect()

    sub_socket.recv.side_effect = [
        b'TC.F.TWF.FITX.HOT:{"DataType":"1K","StartTime":"2021030100","EndTime":"2021031700","Symbol":"TC.F.TWF.FITX.HOT","Status":"Ready"}\x00',
        b'__pytest_stop__\x00'
    ]

    socket.recv.reset_mock()
    socket.recv.side_effect = open(
        os.path.join(os.path.dirname(__file__), 'fixtures/history-1k.txt'), 'rb'
    ).read().splitlines()

    quote_api.keep_alive()

    symbol = 'TC.F.TWF.FITX.HOT'
    data_type = '1K'
    start_time = '2021030100'
    end_time = '2021031700'

    send_json: MagicMock = socket.send_json
    qry_index = send_json.call_args_list[len(send_json.call_args_list) - 1].args[0]['Param'].get('QryIndex')
    send_json.assert_called_with({
        'Request': 'GETHISDATA', 'SessionKey': '777d79aadfaff06597919a9ce30f8b46',
        'Param': {'Symbol': symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time,
                  'QryIndex': qry_index
                  }
    })


@pytest.fixture()
def emitter():
    return EventManager()


@pytest.fixture()
def quote_api():
    return QuoteAPI()


@pytest.fixture()
def mock_quote_api(context, locker, emitter):
    return QuoteAPI(context, locker, emitter)


@pytest.fixture()
def socket():
    socket = MagicMock()
    socket.connect = MagicMock()
    socket.send_json = MagicMock()
    message = b'{"Reply":"LOGIN","Success":"OK","SessionKey":"777d79aadfaff06597919a9ce30f8b46","SubPort":"50994"}\x00'
    socket.recv = MagicMock(side_effect=[message])

    return socket


@pytest.fixture()
def sub_socket():
    socket = MagicMock()
    socket.connect = MagicMock()
    socket.send_json = MagicMock()
    socket.recv = MagicMock(side_effect=[b'__pytest_stop__'])

    return socket


@pytest.fixture()
def context(socket, sub_socket):
    context = MagicMock()
    context.socket = MagicMock(side_effect=[socket, sub_socket])

    return context


@pytest.fixture()
def locker():
    locker = MagicMock()
    locker.acquire = MagicMock()
    locker.release = MagicMock()

    return locker
