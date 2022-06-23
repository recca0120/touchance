import re
from json import loads
from threading import Lock, Thread
from typing import Callable

from zmq import Context, REQ, SUB, SUBSCRIBE

from src.event_manager import EventManager


def decode_message(message: bytes, clean_prefix=False):
    message = message.decode('utf-8').rstrip('\x00')
    if clean_prefix is True:
        index = re.search(':', message).span()[1]
        message = message[index:]

    return loads(message)


class Touchance(object):
    host = '127.0.0.1'
    port = '51237'
    _emitter = EventManager()
    __app_id = 'ZMQ'
    __secret = '8076c9867a372d2a9a814ae710c256e2'
    __context = None
    __locker = None
    __socket = None
    __subscriber = None
    __keep_alive = None
    __connection_info = {}

    def __init__(self, context: Context = None, locker: Lock = None, keep_alive=True):
        self.set_context(context).set_locker(locker)
        self.__keep_alive = keep_alive
        self._emitter.on('message', lambda message: self._receive(decode_message(message, True)))

    @property
    def session_key(self):
        return self.__get_info('SessionKey')

    @property
    def sub_port(self):
        return self.__get_info('SubPort')

    @property
    def is_connected(self):
        return self.__get_info('Reply') == 'LOGIN' and self.__get_info('Success') == 'OK'

    def set_context(self, context: Context):
        self.__context = context if context is not None else Context()

        return self

    def set_locker(self, locker: Lock):
        self.__locker = locker if locker is not None else Lock()

        return self

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

        if self.__subscriber is not None:
            self.__subscriber.stop()

        return True

    def keep_alive(self):
        if self.is_connected is True:
            self.__subscriber = Subscriber(self.__create_sub_socket(), self._emitter)
            self.__subscriber.start()

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
        data_type = result['DataType']

        self._emitter.emit(data_type, result)

        if data_type == 'PING':
            self.pong('TC')

    def _send(self, params: dict):
        self.__lock()
        self.__socket.send_json(params)
        recv = self.__socket.recv()
        self.__unlock()
        data = decode_message(recv)

        if 'Success' in data and data['Success'] != 'OK' and 'ErrMsg' in data:
            raise RuntimeError(data['ErrMsg'])

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
            message = recv.decode('utf-8')

            if self.__stop is True or 'stop' in message:
                break

            self.__emitter.emit('message', recv)


class QuoteAPI(Touchance):
    port = '51237'

    def subscribe_quote(self, quote_symbol: str):
        info = self._send({'Request': 'SUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'REALTIME'
        }})

        return info['Success'] == 'OK'

    def unsubscribe_quote(self, quote_symbol: str):
        info = self._send({'Request': 'UNSUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'REALTIME'
        }})

        return info['Success'] == 'OK'

    def subscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        info = self._send({'Request': 'SUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        }})

        return info['Success'] == 'OK'

    def unsubscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        info = self._send({'Request': 'UNSUBQUOTE', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        }})

        return info['Success'] == 'OK'


class TradeAPI(Touchance):
    port = '51207'
