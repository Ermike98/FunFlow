from typing import Callable
from .layer import Layer
from .templates import Template


class Functional(Layer):
    def __init__(self,
                 func: Callable,
                 inputs: str | Template | list[Template | str] = None,
                 outputs: str | Template | list[Template | str] = None,
                 call_type: str = "args",
                 **kwargs):
        super().__init__(inputs=inputs, outputs=outputs, call_type=call_type, **kwargs)
        self.__func = func

    def call(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

