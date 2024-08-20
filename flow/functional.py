from typing import Callable
from .layer import Layer


class Functional(Layer):
    def __init__(self,
                 func: Callable,
                 inputs: list[str] = None,
                 outputs: list[str] = None,
                 **kwargs):
        super().__init__(inputs=inputs, outputs=outputs, **kwargs)
        self.__func = func

    def call(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

