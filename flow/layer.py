from abc import abstractmethod
from pprint import pprint
from typing import Any, Dict, Optional


class Layer:
    _id = 0

    def __init__(self,
                 name: str = None,
                 inputs: str | list[str] = None,
                 outputs: str | list[str] = None,
                 input_type: Optional[str] = "kwargs",
                 output_type: Optional[str] = "auto",
                 debug: bool = False
                 ):
        Layer._id = Layer._id + 1
        self.name = name if name is not None else f"{self.__class__.__name__}: {Layer._id}"
        self.__id = Layer._id

        if inputs is not None:
            self._input_names = [inputs] if isinstance(inputs, str) else inputs
        else:
            self._input_names = []

        self._output_names = [outputs] if isinstance(outputs, str) else outputs

        assert output_type == "auto", f"Allowed output types are 'auto', but got {output_type}"
        self.__output_type = output_type

        assert input_type == "args" or input_type == "kwargs", f"Allowed input types are 'args' and 'kwargs', but got {input_type}"
        self.__input_type = input_type

        self.__debug = debug

    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def __call__(self, *args, **kwargs: Any) -> Dict:
        if self.__debug:
            print(f"Executing layer: {self.name}")
            print(f"- Input: {kwargs}")
            print(f"- Processing...")

        if self.__input_type == "args":
            args = (kwargs[input_name] for input_name in self._input_names)
            results = self.call(*args)
        else:
            results = self.call(**kwargs)

        # call_arg = args
        # if kwargs:
        #     call_arg = call_arg + (kwargs, )

        # results = self.call(*args, **kwargs) if not self.__raw_inputs else self.call(call_arg)

        if not self._output_names:
            return dict()

        if not hasattr(results, "__len__") or len(results) != len(self._output_names):
            results = (results,)

        assert len(results) == len(self._output_names), f"Expected {len(self._output_names)} outputs, got {len(results)}"
        outputs = dict(zip(self._output_names, results))

        if self.__debug:
            print(f"- Output: {outputs}")
            print(f"- End Processing {self.name}")

        return outputs

    @property
    def inputs(self) -> list[str]:
        return self._input_names

    @property
    def outputs(self) -> list[str]:
        return self._output_names

    def debug(self, debug: bool = None) -> bool:
        if debug is not None:
            self.__debug = debug
        return self.__debug
