from typing import Callable
from .layer import Layer


class Functional(Layer):
    def __init__(self, func: Callable, **kwargs):
        super().__init__(**kwargs)
        self.__func = func

    def call(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

