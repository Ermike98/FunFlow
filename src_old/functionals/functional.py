from ..core import Layer
from typing import Callable, Self


class Functional(Layer):
    def __init__(self,
                 func: Callable,
                 name: str = None,
                 debug: bool = False):
        super().__init__(
            name=name if name is not None else func.__name__,
            debug=debug
        )
        self.__func = func

    def call(self, *args, **kwargs) -> dict:
        return self.__func(*args, **kwargs)
