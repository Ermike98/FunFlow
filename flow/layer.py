from abc import abstractmethod
from typing import Any, Dict


class Layer:
    _id = 0

    def __init__(self,
                 name: str = None,
                 inputs: str | list[str] = None,
                 outputs: str | list[str] = None,
                 raw_inputs: bool = False,
                 raw_outputs: bool = False,
                 debug: bool = False
                 ):
        Layer._id = Layer._id + 1
        self.name = name if name is not None else f"{self.__class__.__name__}: {Layer._id}"
        self.__id = Layer._id

        self._input_names = [inputs] if isinstance(inputs, str) else inputs
        self._output_names = [outputs] if isinstance(outputs, str) else outputs

        self.__raw_inputs = raw_inputs
        self.__raw_outputs = raw_outputs

        self.__debug = debug

    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def __call__(self, *args, **kwargs: Any) -> Dict:
        if self.__debug:
            print(f"Executing layer: {self.name}")
            print(f"{self.name} Input: {kwargs}")
            print(f"Processing...")

        call_arg = args
        if kwargs:
            call_arg = call_arg + (kwargs, )

        results = self.call(*args, **kwargs) if not self.__raw_inputs else self.call(call_arg)

        if self.__raw_outputs or self._output_names is None:
            if self.__debug:
                print(f"{self.name} Output: {results}")
            return results

        if not isinstance(results, tuple):
            results = (results, )

        outputs = dict(zip(self._output_names, results))

        if self.__debug:
            print(f"{self.name} Output: {outputs}")

        return outputs

    @property
    def inputs(self) -> list:
        return self._input_names

    @property
    def outputs(self) -> list:
        return self._output_names

    def debug(self, debug: bool = None) -> bool:
        if debug is not None:
            self.__debug = debug
        return self.__debug
