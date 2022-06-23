import re
from json import loads
from threading import Lock, Thread
from typing import Callable

from zmq import Context, REQ, SUB, SUBSCRIBE

from src.event_manager import EventManager


def decode_message(raw_message: bytes, clean_prefix=False):
    # with open('history-1k.txt', 'ab') as fp:
    #     fp.write(raw_message)
    #     fp.write("\n".encode())
    message = raw_message.decode('utf-8').rstrip('\x00')
    if clean_prefix is True:
        index = re.search(':', message).span()[1]
        message = message[index:]

    return loads(message)


class Touchance(object):
    host = '127.0.0.1'
    port = '51237'
    _emitter = None
    __app_id = 'ZMQ'
    __secret = '8076c9867a372d2a9a814ae710c256e2'
    __context = None
    __locker = None
    __socket = None
    __sub_socket = None
    _subscriber = None
    __keep_alive = None
    __connection_info = {}

    def __init__(self,
                 context: Context = Context(),
                 locker: Lock = Lock(),
                 emitter: EventManager = EventManager(),
                 keep_alive=True):
        self.__context = context
        self.__locker = locker
        self._emitter = emitter
        self.__keep_alive = keep_alive
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

    def get_subscriber(self):
        return self._subscriber

    def connect(self):
        self.__socket = self.__create_socket(REQ, self.port)
        self.__connection_info = self._send({
            'Request': 'LOGIN',
            'Param': {'SystemName': self.__app_id, 'ServiceKey': self.__secret}
        })

        if self.is_connected is True and self.__keep_alive is True:
            self.keep_alive()

        return self.is_connected

    def disconnect(self):
        self.__connection_info = self._send({'Request': 'LOGOUT', 'SessionKey': self.session_key})

        if self._subscriber is not None:
            self._subscriber.stop()

        return True

    def keep_alive(self):
        if self.is_connected is True and self.__sub_socket is None:
            self.__sub_socket = self.__create_sub_socket()

        if self._subscriber is not None:
            self._subscriber.stop()

        if self.__sub_socket is not None:
            self._subscriber = Subscriber(self.__sub_socket, self._emitter)

        self._subscriber.start()

        return self

    def pong(self, _id: str):
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
        return self.__connection_info[key] if key in self.__connection_info else None


class Subscriber(Thread):
    __stop = False

    def __init__(self, socket, emitter: EventManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__socket = socket
        self.__emitter = emitter

    def stop(self):
        self.__stop = True

    def run(self):
        while True:
            recv = self.__socket.recv()

            if self.__stop is True or '__pytest_stop__' in recv.decode():
                break

            self.__emitter.emit('RECV_MESSAGE', recv)


class QuoteAPI(Touchance):
    port = '51237'

    def subscribe_quote(self, quote_symbol: str):
        info = self._send({'Request': 'SUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'REALTIME'
        }})

        return info.get('Reply') == 'SUBQUOTE' and info.get('Success') == 'OK'

    def unsubscribe_quote(self, quote_symbol: str):
        info = self._send({'Request': 'UNSUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'REALTIME'
        }})

        return info.get('Reply') == 'UNSUBQUOTE' and info.get('Success') == 'OK'

    def subscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        info = self._send({'Request': 'SUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        }})

        return info.get('Reply') == 'SUBQUOTE' and info.get('Success') == 'OK'

    def unsubscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        info = self._send({'Request': 'UNSUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        }})

        return info.get('Reply') == 'UNSUBQUOTE' and info.get('Success') == 'OK'

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
        info = self._send({'Request': 'SUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time
        }})

        return info.get('Reply') == 'SUBQUOTE' and info.get('Success') == 'OK'

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
        info = self._send({'Request': 'UNSUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time
        }})

        return info.get('Reply') == 'UNSUBQUOTE' and info.get('Success') == 'OK'

    def get_history(self, quote_symbol: str, data_type: str, start_time: str, end_time: str, qry_index):
        return self._send({'Request': 'GETHISDATA', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time,
            'QryIndex': qry_index
        }}, True)

    def _receive(self, result: dict):
        super()._receive(result)

        if result.get('Status') == 'Ready':
            for history in self.__get_histories(result):
                self._emitter.emit('HISTORY', history, result)

    def __get_histories(self, result):
        qry_index = ""
        try:
            while True:
                data = self.get_history(
                    result.get('Symbol'),
                    result.get('DataType'),
                    result.get('StartTime'),
                    result.get('EndTime'),
                    qry_index
                )
                histories = data.get('HisData')

                if len(histories) == 0:
                    break

                for history in histories:
                    yield history

                qry_index = histories[-1].get('QryIndex')
        except StopIteration:
            pass


class TradeAPI(Touchance):
    port = '51207'
