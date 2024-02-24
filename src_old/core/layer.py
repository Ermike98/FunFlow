from typing import Any
from abc import abstractmethod


class Layer:
    _id = 0

    def __init__(self,
                 name: str = None,
                 debug: bool = False
                 ):
        Layer._id = Layer._id + 1
        self.name = name if name is not None else f"{self.__class__.__name__}: {Layer._id}"
        self.__id = Layer._id

        self.__debug = debug

    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> Any:
        return args, kwargs

    def __call__(self, *args, **kwargs) -> Any:
        if self.debug():
            print(f"Executing layer: {self.name}")
            print(f"Input: {args}, {kwargs}")
            print(f"Processing...")

        output = self.call(*args, **kwargs)

        if self.debug():
            print(f"Output: {output}")

        return output

    def debug(self, debug: bool = None) -> bool:
        if debug is not None:
            self.__debug = debug
        return self.__debug
