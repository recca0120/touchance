from threading import Thread
from typing import Callable


class EventManager(object):
    def __init__(self):
        self.__listeners = {}

    def on(self, event_name: str, func: Callable):
        if event_name not in self.__listeners:
            self.__listeners[event_name] = []

        self.__listeners[event_name].append(func)

    def has(self, event_name: str):
        return event_name in self.__listeners

    def emit(self, event_name: str, *args, **kwargs):
        if self.has(event_name) is True:
            for func in self.__listeners[event_name]:
                Thread(target=func, args=args, kwargs=kwargs).start()
                # func(*args, **kwargs)
