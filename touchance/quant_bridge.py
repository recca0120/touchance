import asyncio
import logging
import re
from abc import ABC
from asyncio import Task, AbstractEventLoop, Lock
from json import loads, JSONDecodeError
from typing import Callable, Optional

from pyee.asyncio import AsyncIOEventEmitter
from zmq import REQ, SUB, SUBSCRIBE
from zmq.asyncio import Context, Socket

from touchance.exceptions import SessionIllegalException, SubscribeException, NewOrderException


class TCore(ABC):
    host = '127.0.0.1'
    port = '51237'
    _emitter: AsyncIOEventEmitter
    _logger: logging.Logger
    __app_id = 'ZMQ'
    __secret = '8076c9867a372d2a9a814ae710c256e2'
    __context: Context
    __locker: Lock
    __socket: Optional[Socket] = None
    __sub_socket: Optional[Socket] = None
    __serve_task: Optional[Task] = None
    __connection_info: Optional[dict] = None

    def __init__(self,
                 context: Optional[Context] = None,
                 locker: Optional[Lock] = None,
                 emitter: Optional[AsyncIOEventEmitter] = None,
                 event_loop: Optional[AbstractEventLoop] = None,
                 logger: Optional[logging.Logger] = None):
        self.__context = context if context is not None else Context()
        self.__locker = locker if locker is not None else Lock()
        self.__event_loop = event_loop if event_loop is not None else asyncio.get_event_loop()
        self._logger = logger if logger is not None else logging.getLogger()

        self._emitter = emitter if emitter is not None else AsyncIOEventEmitter(self.__event_loop)

        async def recv_message(message):
            self._emitter.on('MESSAGE', message)

            return await self._receive(self.__decode_message(message))

        self._emitter.on('RECV_MESSAGE', recv_message)

    @property
    def session_key(self):
        return self.__get_info('SessionKey')

    @property
    def sub_port(self):
        return self.__get_info('SubPort')

    @property
    def is_connected(self):
        return self.__get_info('Reply') == 'LOGIN' and self.__get_info('Success') == 'OK'

    async def connect(self):
        self.__socket = self.__create_socket(REQ, self.port)
        self.__connection_info = await self._send({
            'Request': 'LOGIN',
            'Param': {'SystemName': self.__app_id, 'ServiceKey': self.__secret}
        })
        self._logger.info('QuoteAPI SubPort: %s', self.sub_port)

        return self.is_connected

    async def disconnect(self):
        self.__connection_info = await self._send({'Request': 'LOGOUT', 'SessionKey': self.session_key})

        if self.__serve_task is not None:
            self.__serve_task.cancel()
            self.__serve_task = None

        return True

    def serve(self):
        if self.is_connected is True and self.__sub_socket is None:
            self.__sub_socket = self.__create_sub_socket()

        if self.__serve_task is not None:
            self.__serve_task.cancel()
            self.__serve_task = None

        self.__serve_task = self.__event_loop.create_task(self.__sub())

        return self.__serve_task

    async def __sub(self):
        while True:
            recv = await self.__sub_socket.recv()

            if '__pytest_stop__' in recv.decode():
                break

            self._emitter.emit('RECV_MESSAGE', recv)

    async def pong(self, _id=''):
        return await self._send({'Request': 'PONG', 'SessionKey': self.session_key, 'ID': _id})

    async def query_instrument_info(self, quote_symbol: str):
        return await self._send(
            {'Request': 'QUERYINSTRUMENTINFO', 'SessionKey': self.session_key, 'Symbol': quote_symbol})

    async def query_all_instrument(self, query_type: str):
        """查詢指定類型合約列表.

        Parameters
        ----------
        query_type : str
            期貨：Fut
            期權：Opt
            證券：Fut2
        """

        return await self._send({'Request': 'QUERYALLINSTRUMENT', 'SessionKey': self.session_key, 'Type': query_type})

    async def query_all_future(self):
        return await self.query_all_instrument('Fut')

    async def query_all_option(self):
        return await self.query_all_instrument('Opt')

    async def query_all_stock(self):
        return await self.query_all_instrument('Fut2')

    def on(self, event_name: str, func: Callable):
        self._emitter.on(event_name.upper(), func)

    async def _receive(self, result: dict):
        data_type = result.get('DataType')
        self._emitter.emit(data_type, result)

        if data_type == 'PING':
            self.__event_loop.create_task(self.pong('TC'))

    async def _send(self, params: dict):
        await self.__lock()
        self.__socket.send_json(params)
        recv = await self.__socket.recv()
        self.__unlock()
        data: dict = self.__decode_message(recv)

        if 'Success' in data and data.get('Success') != 'OK':
            self._logger.error(data)
            request = params.get('Request')

            if request == 'NEWORDER' and 'ErrCode' in data:
                raise NewOrderException(data.get('ErrCode'))

            if 'ErrMsg' in data:
                err_msg = data.get('ErrMsg')

                if 'the Session is illegal' in err_msg:
                    raise SessionIllegalException(err_msg)

                if request in 'SUBQUOTE':
                    raise SubscribeException(err_msg)

                raise RuntimeError(err_msg)

        return data

    def __create_socket(self, socket_type: int, port: str):
        socket = self.__context.socket(socket_type)
        socket.connect('tcp://%s:%s' % (self.host, port))

        return socket

    def __create_sub_socket(self):
        socket = self.__create_socket(SUB, self.sub_port)
        socket.setsockopt_string(SUBSCRIBE, '')

        return socket

    async def __lock(self):
        await self.__locker.acquire()

    def __unlock(self):
        self.__locker.release()

    def __get_info(self, key: str):
        return self.__connection_info.get(key) if self.__connection_info is not None else None

    def __decode_message(self, raw_message: bytes):
        # with open('history-1k.txt', 'ab') as fp:
        #     fp.write(raw_message)
        #     fp.write("\n".encode())
        message = raw_message.decode('utf-8').rstrip('\x00')
        matched = re.match(r'(^[\w\d.]+:){', message)
        if matched is not None:
            index = len(matched.group(1))
            message = message[index:]

        try:
            return loads(message)
        except JSONDecodeError:
            self._logger.error(raw_message)
            return {}
