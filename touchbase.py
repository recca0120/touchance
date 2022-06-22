from json import loads
from threading import Lock

from zmq import Context, REQ


class Touchbase(object):
    host = '127.0.0.1'
    __app_id = 'ZMQ'
    __secret = '8076c9867a372d2a9a814ae710c256e2'
    __context = None
    __locker = None
    __socket = None
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
        self.__socket = self.__context.socket(REQ)
        self.__socket.connect('tcp://%s:%s' % (self.host, 51237))
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

    def queryAllFutureInfo(self):
        return self.query_all_instrument_info('Fut')

    def queryAllOptionInfo(self):
        return self.query_all_instrument_info('Opt')

    def queryAllStockInfo(self):
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
        self.__unlock()
        message = self.__socket.recv()
        data = loads(message[:-1])

        if data['Success'] == 'Fail':
            raise RuntimeError(data['ErrMsg'])

        return data
