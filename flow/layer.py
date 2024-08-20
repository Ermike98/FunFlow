import warnings
from abc import abstractmethod, ABC
from typing import Any, Dict, Optional, Self
from .template_utils import find_actual_input_names, find_actual_output_names


# TODO: Implement input as list of layers, where all the outputs of the provided layers are taken in input

class Layer:
    _id = 0

    def __init__(self,
                 name: str = None,
                 inputs: str | list[str] = None,
                 outputs: str | list[str] = None,
                 input_type: Optional[str] = "kwargs",
                 output_type: Optional[str] = "auto",
                 call_type: Optional[str] = "auto",
                 debug: bool = False
                 ):
        Layer._id = Layer._id + 1
        self.name = name if name is not None else f"{self.__class__.__name__}: {Layer._id}"
        self.__id = Layer._id

        if inputs is not None:
            self._input_names = [inputs] if isinstance(inputs, str) else inputs
        else:
            self._input_names = []

        if outputs is not None:
            self._output_names = [outputs] if isinstance(outputs, str) else outputs
        else:
            self._output_names = []

        assert input_type in ["args", "kwargs"], \
            f"Allowed input types are 'args' and 'kwargs', but got {input_type}"
        self.__input_type = input_type

        assert output_type in ["auto", "raw", "tuple", "dict"], \
            f"Allowed output types are 'auto', 'raw', 'tuple' and 'dict', but got {output_type}"
        self.__output_type = output_type

        assert call_type in ["auto", "args", "kwargs", "tuple", "dict"], \
            f"Allowed call types are 'auto', 'args', 'kwargs', 'tuple', 'dict' but got {call_type}"
        self.__call_type = call_type

        self.__predecessors = []
        self.__template_values = dict()
        self.__actual_outputs = None
        self.__actual_inputs = None

        self.__debug = debug

    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def __call__(self, *args, **kwargs: Any) -> Dict:
        if self.__debug:
            print(f"Executing layer: {self.name}")
            print(f"- Input: {kwargs}")
            print(f"- Processing...")

        if self.__input_type == "args" and self.__call_type != "auto":
            kwargs = dict(zip(self._input_names, args))

        if self.actual_inputs is None or self.__actual_inputs is None:
            warnings.warn("You are calling a Layer that has not been initialized yet.", RuntimeWarning)
            user_inputs = kwargs.copy()
            user_inputs.update({name: value for name, value in zip(self._input_names, args)})
            self.init(user_inputs)

        actual_input_names = self.actual_inputs
        actual_output_names = self.actual_outputs

        # assert actual_input_names is not None, f"The inputs provided do not match the expected input names"

        results = None
        match self.__call_type:
            case "auto":
                results = self.call(*args, **kwargs)
            case "kwargs":
                results = self.call(**kwargs)
            case "dict":
                results = self.call(kwargs)
            case "args":
                args = (kwargs[input_name] for input_name in actual_input_names)
                results = self.call(*args)
            case "tuple":
                args = (kwargs[input_name] for input_name in actual_input_names)
                results = self.call(args)

        if not actual_output_names:
            return dict()

        if ((not hasattr(results, "__len__") or len(results) != len(actual_output_names))
                and (self.__output_type == "raw" or self.__output_type == "auto")):
            results = (results,)

        if self.__output_type == "dict" and isinstance(results, dict):
            results = {results[output_name] for output_name in actual_output_names}

        assert len(results) == len(actual_output_names), \
            f"Expected {len(actual_output_names)} outputs, got {len(results)}"

        outputs = dict(zip(actual_output_names, results))

        if self.__debug:
            print(f"- Output: {outputs}")
            print(f"- End Processing {self.name}")

        return outputs

    def _get_actual_output_names(self, state: dict, template_values: dict[str, Any]) -> list[str]:
        actual_outputs = find_actual_output_names(self.outputs, template_values)
        return actual_outputs

    def init(self, state: dict, state_producers: dict[str, Self | None] = None) -> Self:
        if state_producers is None:
            state_producers = {key: [None] for key in state.keys()}

        actual_inputs = []

        template_values = dict()
        for input_name in self._input_names:
            actual_input_names, template_values_input = find_actual_input_names(input_name, state_producers.keys())

            if actual_input_names is None:
                return [], []

            template_values.update(template_values_input)

            actual_input_names = [actual_name for actual_name in actual_input_names if
                                  state_producers[actual_name] is not None and self not in state_producers[actual_name]]

            actual_inputs.extend(actual_input_names)

        self.__template_values = template_values
        self.__predecessors = self.__get_node_predecessors(actual_inputs, state_producers)
        self.__actual_inputs = actual_inputs
        self.__actual_outputs = self._get_actual_output_names(state, template_values)

        return self

    def __get_node_predecessors(self, actual_input_names: list[str], state_producers: dict):
        if actual_input_names is None:
            return []

        predecessors_set = set()

        for actual_name in actual_input_names:
            predecessors_set.update(state_producers[actual_name])

        return [predecessor for predecessor in predecessors_set if predecessor is not None and predecessor != self]

    @property
    def inputs(self) -> list[str]:
        return self._input_names

    @property
    def outputs(self) -> list[str]:
        return self._output_names

    @property
    def actual_inputs(self) -> list[str]:
        return self.__actual_inputs

    @property
    def actual_outputs(self) -> list[str]:
        return self.__actual_outputs

    @property
    def predecessors(self) -> list[Self]:
        return self.__predecessors

    def debug(self, debug: bool = None) -> bool:
        if debug is not None:
            self.__debug = debug
        return self.__debug

    def __repr__(self):
        return (f"{self.__class__.__name__} {self.name}, \n"
                f"- Inputs: {self.inputs} -> {self.__actual_inputs}, \n"
                f"- Outputs: {self.outputs} -> {self.__actual_outputs} \n"
                f"- Predecessors: {[l.name for l in self.predecessors]}")
