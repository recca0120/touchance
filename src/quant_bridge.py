import re
from abc import ABC
from json import loads
from threading import Lock
from typing import Callable, Optional

from zmq import Context, REQ, SUB, SUBSCRIBE, Socket

from src.event_manager import EventManager
from src.subscriber import Subscriber


def decode_message(raw_message: bytes, clean_prefix=False):
    # with open('history-1k.txt', 'ab') as fp:
    #     fp.write(raw_message)
    #     fp.write("\n".encode())
    message = raw_message.decode('utf-8').rstrip('\x00')
    if clean_prefix is True:
        index = re.search(':', message).span()[1]
        message = message[index:]

    return loads(message)


class TCore(ABC):
    host = '127.0.0.1'
    port = '51237'
    __app_id = 'ZMQ'
    __secret = '8076c9867a372d2a9a814ae710c256e2'
    __socket: Optional[Socket] = None
    __sub_socket: Optional[Socket] = None
    __subscriber: Optional[Subscriber] = None
    __connection_info: Optional[dict] = None

    def __init__(self,
                 context: Context = Context(),
                 locker: Lock = Lock(),
                 emitter: EventManager = EventManager()):
        self.__context = context
        self.__locker = locker

        self._emitter = emitter
        self._emitter.on('RECV_MESSAGE', lambda message: self._receive(decode_message(message, True)))

    @property
    def session_key(self):
        return self.__get_info('SessionKey')

    @property
    def sub_port(self):
        return self.__get_info('SubPort')

    @property
    def is_connected(self):
        return self.__get_info('Reply') == 'LOGIN' and self.__get_info('Success') == 'OK'

    def connect(self):
        self.__socket = self.__create_socket(REQ, self.port)
        self.__connection_info = self._send({
            'Request': 'LOGIN',
            'Param': {'SystemName': self.__app_id, 'ServiceKey': self.__secret}
        })

        return self.is_connected

    def disconnect(self):
        self.__connection_info = self._send({'Request': 'LOGOUT', 'SessionKey': self.session_key})

        if self.__subscriber is not None:
            self.__subscriber.cancel()

        return True

    def handle(self):
        if self.is_connected is True and self.__sub_socket is None:
            self.__sub_socket = self.__create_sub_socket()

        if self.__subscriber is not None:
            self.__subscriber.cancel()

        if self.__sub_socket is not None:
            self.__subscriber = Subscriber(self.__sub_socket, self._emitter)

        self.__subscriber.start()

        return self.__subscriber

    def pong(self, _id=''):
        return self._send({'Request': 'PONG', 'SessionKey': self.session_key, 'ID': _id})

    def query_instrument_info(self, quote_symbol: str):
        return self._send({'Request': 'QUERYINSTRUMENTINFO', 'SessionKey': self.session_key, 'Symbol': quote_symbol})

    def query_all_instrument(self, query_type: str):
        """查詢指定類型合約列表.

        Parameters
        ----------
        query_type : str
            期貨：Fut
            期權：Opt
            證券：Fut2
        """

        return self._send({'Request': 'QUERYALLINSTRUMENT', 'SessionKey': self.session_key, 'Type': query_type})

    def query_all_future(self):
        return self.query_all_instrument('Fut')

    def query_all_option(self):
        return self.query_all_instrument('Opt')

    def query_all_stock(self):
        return self.query_all_instrument('Fut2')

    def on(self, event_name: str, func: Callable):
        self._emitter.on(event_name.upper(), func)

    def _receive(self, result: dict):
        self._emitter.emit('MESSAGE', result)
        data_type = result.get('DataType')
        self._emitter.emit(data_type, result)

        if data_type == 'PING':
            self.pong('TC')

    def _send(self, params: dict, clear_prefix=False):
        self.__lock()
        self.__socket.send_json(params)
        recv = self.__socket.recv()
        self.__unlock()
        data: dict = decode_message(recv, clear_prefix)

        if 'Success' in data and data.get('Success') != 'OK' and 'ErrMsg' in data:
            raise RuntimeError(data.get('ErrMsg'))

        return data

    def __create_socket(self, socket_type: int, port: str):
        socket = self.__context.socket(socket_type)
        socket.connect('tcp://%s:%s' % (self.host, port))

        return socket

    def __create_sub_socket(self):
        socket = self.__create_socket(SUB, self.sub_port)
        socket.setsockopt_string(SUBSCRIBE, '')

        return socket

    def __lock(self):
        self.__locker.acquire()

    def __unlock(self):
        self.__locker.release()

    def __get_info(self, key: str):
        return self.__connection_info.get(key) if self.__connection_info is not None else None


class QuoteAPI(TCore):
    port = '51237'

    def subscribe_quote(self, quote_symbol: str):
        return self.subscribe('SUBQUOTE', {'Symbol': quote_symbol, 'SubDataType': 'REALTIME'})

    def unsubscribe_quote(self, quote_symbol: str):
        return self.subscribe('UNSUBQUOTE', {'Symbol': quote_symbol, 'SubDataType': 'REALTIME'})

    def subscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        return self.subscribe('SUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        })

    def unsubscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        return self.subscribe('UNSUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        })

    def subscribe_history(self, quote_symbol: str, data_type: str, start_time: str, end_time: str):
        """訂閱歷史資料.

        Parameters
        ----------
        quote_symbol: str
        data_type: str
            TICKS, 1K, DK
        start_time: str
        end_time: str
        """
        return self.subscribe('SUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time
        })

    def unsubscribe_history(self, quote_symbol: str, data_type: str, start_time: str, end_time: str):
        """取溑訂閱歷史資料.

        Parameters
        ----------
        quote_symbol: str
        data_type: str
            TICKS, 1K, DK
        start_time: str
        end_time: str
        """
        return self.subscribe('UNSUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time
        })

    def subscribe(self, request: str, param: dict):
        info = self._send({'Request': request, 'SessionKey': self.session_key, 'Param': param})

        return info.get('Reply') == request and info.get('Success') == 'OK'

    def get_history(self, quote_symbol: str, data_type: str, start_time: str, end_time: str, qry_index):
        return self._send({'Request': 'GETHISDATA', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time,
            'QryIndex': qry_index
        }}, True)

    def _receive(self, result: dict):
        super()._receive(result)

        if result.get('Status') == 'Ready':
            generator = self.get_histories(
                result.get('Symbol'), result.get('DataType'), result.get('StartTime'), result.get('EndTime')
            )
            histories = []
            for history in generator:
                self._emitter.emit('HISTORY', history, result)
                histories.append(history)
            self._emitter.emit('HISTORIES', histories, result)

    def get_histories(self, quote_symbol: str, data_type: str, start_time: str, end_time: str):
        qry_index = ''
        while True:
            data = self.get_history(quote_symbol, data_type, start_time, end_time, qry_index)
            histories = data.get('HisData')

            if len(histories) == 0:
                break

            yield from histories

            qry_index = histories[-1].get('QryIndex')


class TradeAPI(TCore):
    port = '51207'
