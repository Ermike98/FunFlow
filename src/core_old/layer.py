from typing import Self, Any
from ..utils import (rename_dict_keys,
                     rename_names,
                     concat_list_without_duplicates,
                     check_expected_vs_actual_names)


class Layer:
    _id = 0

    def __init__(self,
                 name: str = None,
                 inputs: str | Self | list[str | Self] = None,
                 output_names: str | list[str] | bool = None,
                 rename_outputs: dict[str, str] = None,
                 rename_inputs: dict[str, str] = None,
                 filter_outputs: bool = False,
                 debug: bool = False
                 ):
        Layer._id = Layer._id + 1
        self.name = name if name is not None else f"{self.__class__.__name__}: {Layer._id}"

        self.__inputs = []
        self.__input_names = []
        self.__input_layers = []
        self.__input_arguments = []
        if inputs is not None:
            self._add_inputs(inputs)

        self.__input_names_map = {}
        if rename_inputs is not None:
            self.rename_inputs(rename_inputs)

        self._output_names = []
        if hasattr(output_names, '__iter__'):
            self._add_outputs(output_names)
        elif output_names is True:
            self._output_names = self.__input_names

        self.__output_names_map = {}
        if rename_outputs is not None:
            self.rename_outputs(rename_outputs)

        self.__filter_outputs = filter_outputs
        self.__debug = debug

    @property
    def inputs(self) -> list[str]:
        return self.__inputs

    @property
    def outputs(self) -> list[str]:
        return rename_names(self._output_names, self.__output_names_map)

    def call(self, **kwargs) -> dict:
        return kwargs

    def fit(self, inputs: dict, targets: dict) -> Self:
        return Self

    def predict(self, inputs: dict) -> dict:
        return self(**inputs)

    def rename_inputs(self, _map: dict[str, str]) -> Self:
        self.__input_names_map.update(_map)
        return self

    def rename_outputs(self, _map: dict[str, str]) -> Self:
        self.__output_names_map.update(_map)
        return self

    def debug(self, debug: bool = None) -> bool:
        if debug is not None:
            self.__debug = debug
        return self.__debug

    def get_parent_layers(self) -> list[Self]:
        return self.__input_layers

    def get_input_arguments(self) -> list[str]:
        return self.__input_arguments

    def __call__(self, *args, **kwargs) -> dict[str, Any] | tuple[Any] | list[Any] | Any:
        if self.debug():
            print(f"Executing layer: {self.name}")

        # print('Wrapper:', kwargs)
        for arg in args:
            if isinstance(arg, dict):
                kwargs.update(arg)
            elif hasattr(arg, '__iter__'):
                for elem in arg:
                    if isinstance(elem, dict):
                        kwargs.update(elem)

        if self.debug():
            print('kwargs:', kwargs)

        self.__check_inputs_received(kwargs.keys())
        renamed_inputs = rename_dict_keys(kwargs, self.__input_names_map)

        if self.debug():
            print('renamed_inputs:', renamed_inputs)

        outputs = self.call(**renamed_inputs)

        if self.debug():
            print('outputs:', outputs)

        self.__check_outputs_names(outputs.keys())
        renamed_output = rename_dict_keys(outputs, self.__output_names_map)

        if self.debug():
            print('renamed_output:', renamed_output)

        if not self.__filter_outputs:
            return renamed_output

        renamed_output_names = rename_names(self._output_names, self.__output_names_map)
        filtered_output = {key: value for key, value in renamed_output.items() if key in renamed_output_names}

        if self.debug():
            print('filtered_output:', filtered_output)

        return filtered_output

    def __getitem__(self, items: str | list[str]):
        return layers.Select(input_layer=self, selected_items=items, debug=self.debug())

    def _add_outputs(self, outputs: str | list[str]) -> Self:
        if isinstance(outputs, str):
            outputs = [outputs]
        self._output_names = concat_list_without_duplicates(self._output_names, outputs, object_name='output')
        return self

    def _add_inputs(self, inputs: str | Self | list[str | Self], *args, **kwargs) -> Self:
        if isinstance(inputs, list):
            for _input in inputs:
                self._add_inputs(_input)
            return self

        if isinstance(inputs, str):
            self.__add_input(inputs)
            self.__add_input_names(inputs)
            self.__input_arguments.append(inputs)
        elif isinstance(inputs, Layer):
            self.__add_input(inputs.name)
            self.__add_input_names(inputs.outputs)
            self.__input_layers.append(inputs)

        return self

    def __add_input(self, new_input: str):
        self.__inputs = concat_list_without_duplicates(self.__inputs, [new_input], object_name='input')

    def __add_input_names(self, new_input_names: str | list[str]):
        if isinstance(new_input_names, str):
            new_input_names = [new_input_names]
        self.__input_names = concat_list_without_duplicates(self.__input_names, new_input_names,
                                                            object_name='input name')

    def __check_inputs_received(self, input_names_received):
        check_expected_vs_actual_names(self.__input_names, input_names_received,
                                       object_name='inputs', debug=self.debug())

    def __check_outputs_names(self, output_names_received):
        check_expected_vs_actual_names(self._output_names, output_names_received,
                                       object_name='outputs', debug=self.debug())
