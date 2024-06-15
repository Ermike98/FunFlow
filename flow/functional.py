from typing import Callable
from .layer import Layer


class Functional(Layer):
    def __init__(self, func: Callable, input_type="args", **kwargs):
        super().__init__(input_type=input_type, **kwargs)
        self.__func = func

    def call(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

