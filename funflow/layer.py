import itertools
from abc import abstractmethod, ABC
from typing import Any, Dict, Self
from .template_utils import find_actual_input_names, create_tag_to_inputs_mapping
from .templates import Template, TemplateValue


# TODO: Implement input as list of layers, where all the outputs of the provided layers are taken in input

class Layer(ABC):
    """
    Abstract base class for all layers in a FunFlow pipeline.
    A layer defines a transformation from inputs to outputs.
    """
    _id_counter = 0

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
        Initialize a Layer.

        :param name: Unique name for the layer. If None, it's auto-generated.
        :param inputs: Input names or templates required by this layer.
        :param outputs: Output names or templates produced by this layer.

        :param input_type: Defines how the layer instance receives inputs when called.
            - "kwargs": Inputs are passed via keyword arguments (default).
            - "args": Inputs are passed via positional arguments.

        :param call_type: Defines how the internal `call` method is invoked.
            - "auto": Tries passing inputs as keyword arguments first; falls back to positional.
            - "kwargs": Passes inputs as individual keyword arguments (`call(**kwargs)`).
            - "args": Passes inputs as individual positional arguments in the order defined 
              by `actual_inputs` (`call(*args)`).
            - "dict": Passes all inputs as a single dictionary argument (`call(data_dict)`).
            - "tuple": Passes all inputs as a single tuple argument (`call(data_tuple)`).

        :param output_type: Defines how the internal `call` method's return value is processed.
            - "auto": Automatically detects if the output is a dictionary, tuple, or single value 
              and maps it to defined outputs.
            - "dict": Expects a dictionary where keys match output names.
            - "tuple": Expects a tuple where elements match defined outputs in order.
            - "raw": Similar to 'auto', but treats non-dict outputs as a single raw value or 
              wraps them in a tuple for mapping.

        :param debug: If True, enables execution logging for this layer.
        """
        self._name = name or self.__class__.__name__
        self._id = Layer._id_counter
        Layer._id_counter += 1

        if isinstance(inputs, str) or isinstance(inputs, Template):
            inputs = [inputs]
        elif inputs is None:
            inputs = []
        self._inputs = [Template(i) if isinstance(i, str) else i for i in inputs]

        if isinstance(outputs, str) or isinstance(outputs, Template):
            outputs = [outputs]
        elif outputs is None:
            outputs = []
        self._outputs = [Template(o) if isinstance(o, str) else o for o in outputs]

        assert input_type in ["args", "kwargs"], \
            f"Allowed input types are 'args' and 'kwargs', but got {input_type}"
        self._input_type = input_type

        assert output_type in ["auto", "raw", "tuple", "dict"], \
            f"Allowed output types are 'auto', 'raw', 'tuple' and 'dict', but got {output_type}"
        self._output_type = output_type

        assert call_type in ["auto", "args", "kwargs", "tuple", "dict"], \
            f"Allowed call types are 'auto', 'args', 'kwargs', 'tuple', 'dict' but got {call_type}"
        self._call_type = call_type

        # These are set during initialization of the model
        self._actual_inputs: list[TemplateValue] = []
        self._actual_outputs: list[TemplateValue] = []
        self._predecessors: list[Self] = []

        self._debug = debug

    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> Any:
        """
        Perform the layer's transformation.
        Should be implemented by subclasses.
        """
        pass

    def __call__(self, *args, **kwargs: Any) -> Dict:
        """
        Execute the layer. Handles input/output mapping and debug logging.
        """
        if self._debug:
            print(f"Executing layer: {self._name}")
            print(f"- Input: {kwargs}")
            print(f"- Processing...")

        # Standardize kwargs keys to strings
        processed_kwargs = {str(TemplateValue(str(k))): v for k, v in kwargs.items()}

        if self._input_type == "args":
            for i, arg_val in enumerate(args):
                if i < len(self._inputs):
                    processed_kwargs[str(self._inputs[i])] = arg_val

        # Create state context for init
        state = processed_kwargs.copy()
        for i, arg_val in enumerate(args):
            if i < len(self._inputs):
                state[str(self._inputs[i])] = arg_val

        self.init(state)

        actual_input_names_str = list(map(str, self._actual_inputs))
        actual_output_names_str = list(map(str, self._actual_outputs))

        results = None
        match self._call_type:
            case "auto":
                if processed_kwargs:
                    results = self.call(**processed_kwargs)
                else:
                    results = self.call(*args)
            case "kwargs":
                results = self.call(**processed_kwargs)
            case "dict":
                results = self.call(processed_kwargs)
            case "args":
                call_args = [processed_kwargs[name] for name in actual_input_names_str]
                results = self.call(*call_args)
            case "tuple":
                call_args = tuple(processed_kwargs[name] for name in actual_input_names_str)
                results = self.call(call_args)

        if self._output_type == "dict":
            assert isinstance(results, dict), f'Output type set to "dict" but the result is of type {type(results)}'

            if not self._outputs:
                return results

            return {key: value
                    for key, value in results.items()
                    for output_templ in self._outputs
                    if output_templ.match(key)}

        if ((not hasattr(results, "__len__") or len(results) != len(actual_output_names_str))
                and (self._output_type == "raw" or self._output_type == "auto")):
            results = (results,)

        assert len(results) == len(actual_output_names_str), \
            f"Expected {len(actual_output_names_str)} outputs, got {len(results)}"

        outputs = dict(zip(actual_output_names_str, results))

        if self._debug:
            print(f"- Output: {outputs}")
            print(f"- End Processing {self._name}")

        return outputs

    def _get_actual_outputs(self, state: dict) -> list[TemplateValue] | None:
        """Determines the actual output names based on current state tags."""
        actual_outputs = []

        input_template_values = [TemplateValue(str(k)) for k in state.keys()]
        tag_to_inputs = create_tag_to_inputs_mapping(input_template_values)

        for output_template in self._outputs:
            tag_filters = output_template.tag_filters

            for input_templates_values in itertools.product(*[tag_to_inputs[tag_flt.name] for tag_flt in tag_filters]):
                tags = sum([value.tags for value in input_templates_values], [])
                output_template_value = output_template.instantiate(tags)

                if output_template_value is not None:
                    actual_outputs.append(output_template_value)

        return actual_outputs

    def init(self, state: dict[str, Any], state_producers: dict[str, list[Self]] | None = None) -> Self:
        """Initializes actual inputs and outputs based on context."""
        if state_producers is None:
            state_producers = {key: [] for key in state.keys()}

        actual_inputs = []

        for input_template in self._inputs:
            actual_input_names = find_actual_input_names(input_template, list(state_producers.keys()))

            if actual_input_names is None:
                return self

            actual_input_names = filter(lambda name: self not in state_producers[name], actual_input_names)

            actual_inputs.extend(actual_input_names)

        self._predecessors = self.__get_node_predecessors(actual_inputs, state_producers)
        self._actual_inputs = [TemplateValue(n) for n in actual_inputs]
        self._actual_outputs = self._get_actual_outputs(state)

        return self

    def __get_node_predecessors(self, actual_input_names: list[str], state_producers: dict):
        if actual_input_names is None:
            return []

        predecessors_set = set()

        for actual_name in actual_input_names:
            predecessors_set.update(state_producers[actual_name])

        return [predecessor for predecessor in predecessors_set if predecessor != self]

    @property
    def name(self) -> str:
        """The name of the layer."""
        return self._name

    @property
    def id(self) -> int:
        """The unique ID of the layer."""
        return self._id

    @property
    def inputs(self) -> list[Template]:
        """The input templates defined for this layer."""
        return self._inputs

    @property
    def outputs(self) -> list[Template]:
        """The output templates defined for this layer."""
        return self._outputs

    @property
    def actual_inputs(self) -> list[TemplateValue]:
        """The specific input/output variables that matched the input templates."""
        return self._actual_inputs

    @property
    def actual_outputs(self) -> list[TemplateValue]:
        """The specific input/output variables this layer will produce."""
        return self._actual_outputs

    @property
    def predecessors(self) -> list[Self]:
        """Other layers that must execute before this one."""
        return self._predecessors

    def debug(self, debug: bool = None) -> bool:
        """Enables or disables debug mode."""
        if debug is not None:
            self._debug = debug
        return self._debug

    def __repr__(self):
        return (f"{self.__class__.__name__} {self._name}, \n"
                f"- Inputs: {self._inputs} -> {self._actual_inputs}, \n"
                f"- Outputs: {self._outputs} -> {self._actual_outputs} \n"
                f"- Predecessors: {[l.name for l in self._predecessors]}")
