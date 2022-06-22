from json import loads
from threading import Lock, Thread

from zmq import Context, REQ, SUB, SUBSCRIBE


class Touchance(object):
    host = '127.0.0.1'
    port = '51237'
    __app_id = 'ZMQ'
    __secret = '8076c9867a372d2a9a814ae710c256e2'
    __context = None
    __locker = None
    __socket = None
    __keep_alive = None
    connection_info = None

    def __init__(self, context: Context = None, locker: Lock = None):
        self.set_context(context).set_locker(locker)

    @property
    def session_key(self):
        return self.__get_info('SessionKey')

    @property
    def sub_port(self):
        return self.__get_info('SubPort')

    def set_context(self, context: Context):
        self.__context = context if context is not None else Context()

        return self

    def set_locker(self, locker: Lock):
        self.__locker = locker if locker is not None else Lock()

        return self

    def connect(self):
        self.__socket = self.create_socket(REQ, self.port)
        self.connection_info = self.__send({
            'Request': 'LOGIN',
            'Param': {'SystemName': self.__app_id, 'ServiceKey': self.__secret}
        })

        return self.connection_info['Success'] == 'OK'

    def disconnect(self):
        info = self.__send({'Request': 'LOGOUT', 'SessionKey': self.session_key})
        if info['Success'] != 'OK':
            return False

        self.connection_info = None

        return True

    def keep_alive(self):
        if self.__keep_alive is not None and self.__keep_alive.is_alive():
            self.__keep_alive.stop()

        self.__keep_alive = KeepAlive(self)
        self.__keep_alive.start()

        return self

    def pong(self, _id: str):
        return self.__send({'Request': 'PONG', 'SessionKey': self.session_key, 'ID': _id})

    def create_socket(self, socket_type: int, port: str):
        socket = self.__context.socket(socket_type)
        socket.connect('tcp://%s:%s' % (self.host, port))

        return socket

    def create_sub_socket(self, socket_type: int):
        return self.create_socket(socket_type, self.sub_port)

    def query_instrument_info(self, quote_symbol: str):
        return self.__send({"Request": "QUERYINSTRUMENTINFO", "SessionKey": self.session_key, "Symbol": quote_symbol})

    def query_all_instrument_info(self, query_type: str):
        """查詢指定類型合約列表.

        Parameters
        ----------
        query_type : str
            期貨：Fut
            期權：Opt
            證券：Fut2
        """

        data = self.__send({"Request": "QUERYALLINSTRUMENT", "SessionKey": self.session_key, "Type": query_type})

        return data

    def query_all_future_info(self):
        return self.query_all_instrument_info('Fut')

    def query_all_option_info(self):
        return self.query_all_instrument_info('Opt')

    def query_all_stock_info(self):
        return self.query_all_instrument_info('Fut2')

    def __lock(self):
        self.__locker.acquire()

    def __unlock(self):
        self.__locker.release()

    def __get_info(self, key: str):
        return self.connection_info[key] if key in self.connection_info else None

    def __send(self, params: dict):
        self.__lock()
        self.__socket.send_json(params)
        message = self.__socket.recv().decode('utf-8').rstrip('\x00')
        self.__unlock()
        data = loads(message)
        if 'Success' in data and data['Success'] == 'Fail' and 'ErrMsg' in data:
            raise RuntimeError(data['ErrMsg'])

        return data


class KeepAlive(Thread):
    __stop = False

    def __init__(self, api: Touchance):
        super().__init__()
        self.__api = api

    def stop(self):
        self.__stop = True

    def run(self):
        socket = self.__api.create_sub_socket(SUB)
        socket.setsockopt_string(SUBSCRIBE, '')

        while True:
            message = socket.recv().decode('utf-8')

            if self.__stop is True or 'stop' in message:
                break

            if '{"DataType":"PING"}' not in message:
                continue

            self.__api.pong('TC')


class QuoteAPI(Touchance):
    port = '51237'


class TradeAPI(Touchance):
    port = '51207'
