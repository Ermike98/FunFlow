from ..core_old import Layer
from typing import Callable, Self


class Functional(Layer):
    def __init__(self,
                 func: Callable,
                 inputs: str | Self | list[str | Self] = None,
                 output_names: str | list[str] = None,
                 raw: bool = True,
                 unpack_inputs: bool = False,
                 debug: bool = False):
        super().__init__(
            inputs=inputs,
            output_names=output_names if raw is True else None,
            debug=debug
        )
        self.__func = func
        self.__raw = raw
        self.__unpack_inputs = unpack_inputs

    def call(self, **kwargs) -> dict:
        if self.__unpack_inputs:
            result = self.__func(**kwargs)
        else:
            result = self.__func(kwargs)

        if not self.__raw:
            return result

        if len(self._output_names) == 1:
            result = [result]

        return dict(zip(self._output_names, result))
