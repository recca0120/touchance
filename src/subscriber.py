from threading import Thread

from src.event_manager import EventManager


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
