import itertools
import warnings
from abc import abstractmethod, ABC
from collections import defaultdict
from typing import Any, Dict, Optional, Self
from .template_utils import find_actual_input_names, replace_multi_templates, create_tag_to_inputs_mapping
from .templates import Template, TemplateValue
from pprint import pprint


# TODO: Implement input as list of layers, where all the outputs of the provided layers are taken in input

class Layer:
    """
    Abstract base class for all layers.
    """
    _id = 0

    def __init__(self,
                 name: str = None,
                 inputs: str | Template | list[Template | str] = None,
                 outputs: str | Template | list[Template | str] = None,
                 input_type: str = "kwargs",
                 output_type: str = "auto",
                 call_type: str = "auto",
                 debug: bool = False
                 ):
        """

        :param name: Name of the layer.
        :param inputs:
        :param outputs:
        :param input_type:
        :param output_type:
        :param call_type:
        :param debug:
        """
        Layer._id = Layer._id + 1
        self.name = name if name is not None else f"{self.__class__.__name__}: {Layer._id}"
        self.__id = Layer._id

        if inputs is not None:
            if not isinstance(inputs, list):
                inputs = [inputs]
            self._inputs: list[Template] = [_input if isinstance(_input, Template) else Template(_input)
                                            for _input in inputs]
        else:
            self._inputs: list[Template] = []

        # self._outputs = [outputs] if isinstance(outputs, str) else outputs
        if outputs is not None:
            if not isinstance(outputs, list):
                outputs = [outputs]
            self._outputs: list[Template] = [_output if isinstance(_output, Template) else Template(_output)
                                             for _output in outputs]
        else:
            self._outputs: list[Template] = []

        assert input_type in ["args", "kwargs"], \
            f"Allowed input types are 'args' and 'kwargs', but got {input_type}"
        self.__input_type = input_type

        assert output_type in ["auto", "raw", "tuple", "dict"], \
            f"Allowed output types are 'auto', 'raw', 'tuple' and 'dict', but got {output_type}"
        self.__output_type = output_type

        assert call_type in ["auto", "args", "kwargs", "tuple", "dict"], \
            f"Allowed call types are 'auto', 'args', 'kwargs', 'tuple', 'dict' but got {call_type}"
        self.__call_type = call_type

        self._template_values = dict()
        self.__predecessors = []
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
            kwargs = dict(zip(self._inputs, args))

        kwargs = {str(TemplateValue(key)): value for key, value in kwargs.items()}

        # if self.actual_inputs is None or self.__actual_inputs is None:
        #     warnings.warn("You are calling a Layer that has not been initialized yet.", RuntimeWarning)

        user_inputs = kwargs.copy()
        user_inputs.update({name: value for name, value in zip(self._inputs, args)})
        self.init(user_inputs)

        actual_input_names_str = list(map(str, self.actual_inputs))
        actual_output_names_str = list(map(str, self.actual_outputs))

        # assert actual_input_names_str is not None, f"The inputs provided do not match the expected input names"

        results = None
        match self.__call_type:
            case "auto":
                results = self.call(*args, **kwargs)
            case "kwargs":
                results = self.call(**kwargs)
            case "dict":
                results = self.call(kwargs)
            case "args":
                args = (kwargs[input_name] for input_name in actual_input_names_str)
                results = self.call(*args)
            case "tuple":
                args = (kwargs[input_name] for input_name in actual_input_names_str)
                results = self.call(args)

        if self.__output_type == "dict":
            assert isinstance(results, dict), f'Output type set to "dict" but the result is of type {type(results)}'

            if not self.outputs:
                return results

            return {key: value
                    for key, value in results.items()
                    for output_templ in self._outputs
                    if output_templ.match(key)}

        if ((not hasattr(results, "__len__") or len(results) != len(actual_output_names_str))
                and (self.__output_type == "raw" or self.__output_type == "auto")):
            results = (results,)

        assert len(results) == len(actual_output_names_str), \
            f"Expected {len(actual_output_names_str)} outputs, got {len(results)}"

        outputs = dict(zip(map(str, actual_output_names_str), results))

        if self.__debug:
            print(f"- Output: {outputs}")
            print(f"- End Processing {self.name}")

        return outputs

    def _get_actual_outputs(self, state: dict) -> list[TemplateValue] | None:
        actual_outputs = []

        input_template_values = list(map(TemplateValue, state.keys()))
        tag_to_inputs = create_tag_to_inputs_mapping(input_template_values)

        for output_template in self.outputs:
            tag_filters = output_template.tag_filters

            for input_templates_values in itertools.product(*[tag_to_inputs[tag_flt.name] for tag_flt in tag_filters]):
                # print(input_templates_values)
                tags = sum([value.tags for value in input_templates_values], [])
                output_template_value = output_template.instantiate(tags)

                if output_template_value is not None:
                    actual_outputs.append(output_template_value)

        return actual_outputs

    def init(self, state: dict[str, Any], state_producers: dict[str, list[Self]] | None = None) -> Self:
        if state_producers is None:
            state_producers = {key: [] for key in state.keys()}

        actual_inputs = []

        # template_values = dict()
        for input_template in self._inputs:
            actual_input_names = find_actual_input_names(input_template, list(state_producers.keys()))

            if actual_input_names is None:
                return self

            # template_values.update(template_values_input)

            actual_input_names = filter(lambda name: self not in state_producers[name], actual_input_names)

            actual_inputs.extend(actual_input_names)

        # self._template_values = template_values
        self.__predecessors = self.__get_node_predecessors(actual_inputs, state_producers)
        self.__actual_inputs = list(map(TemplateValue, actual_inputs))
        self.__actual_outputs = self._get_actual_outputs(state)

        return self

    def __get_node_predecessors(self, actual_input_names: list[str], state_producers: dict):
        if actual_input_names is None:
            return []

        predecessors_set = set()

        for actual_name in actual_input_names:
            predecessors_set.update(state_producers[actual_name])

        # return [predecessor for predecessor in predecessors_set if predecessor is not None and predecessor != self]
        return [predecessor for predecessor in predecessors_set if predecessor != self]

    @property
    def inputs(self) -> list[Template]:
        return self._inputs

    @property
    def outputs(self) -> list[Template]:
        return self._outputs

    @property
    def actual_inputs(self) -> list[TemplateValue]:
        return self.__actual_inputs

    @property
    def actual_outputs(self) -> list[TemplateValue]:
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
