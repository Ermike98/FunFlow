import networkx as nx
from layers import Layer
from utils import overlapping_keys_in_dicts
from typing import Self, Any


class Model(Layer):
    def __init__(self,
                 name: str = None,
                 outputs: Layer | list[Layer] = None,
                 rename_outputs: dict[str, str] = None,
                 rename_inputs: dict[str, str] = None,
                 debug: bool = False):
        super().__init__(
            name=name,
            rename_outputs=rename_outputs,
            rename_inputs=rename_inputs,
            debug=debug
        )

        self.__output_layers = []
        if isinstance(outputs, Layer):
            self.__output_layers.append(outputs)
        elif hasattr(outputs, '__iter__'):
            self.__output_layers.extend(outputs)
        else:
            raise ValueError(f'Type of outputs ({type(outputs)}) is not accepted, try with list of Layer instead!')
        for output_layer in self.__output_layers:
            self._add_outputs(output_layer.outputs)

        self.__layers: dict[str, Layer] = dict()
        self.__layers_parents: dict[str, list[str]] = dict()

        self.__create_model_graph()

    @property
    def G(self) -> nx.DiGraph:
        return self.__G

    @property
    def layers(self) -> dict[str, Layer]:
        return self.__layers

    @property
    def output_layers(self):
        return self.__output_layers

    def fit(self, inputs: dict, targets: dict[str | tuple[str, str], Any]) -> Self:
        layers_results: dict[str, dict] = dict()
        common_targets = {key: value for key, value in targets.items() if isinstance(key, str)}

        for layer_name in self.__topological_order:
            if self.debug():
                print(f'Fitting layer {layer_name}')

            layer = self.__layers[layer_name]
            layer_args = (layers_results[parent_name] for parent_name in self.__layers_parents[layer_name])
            layer_kwargs = {arguments: inputs[arguments] for arguments in layer.get_input_arguments()}

            layer_fit_input = layer_kwargs.copy()
            for parent_result in layer_args:
                layer_fit_input.update(parent_result)

            layer_fit_target = common_targets.copy()
            layer_fit_target.update({key[1]: value for key, value in targets.items()
                                     if isinstance(key, tuple) and key[0] == layer.name})

            layer.fit(layer_fit_input, layer_fit_target)
            layers_results[layer_name] = layer(*layer_args, **layer_kwargs)

        return self

    def call(self, **kwargs):
        layers_results: dict[str, dict] = dict()

        for layer_name in self.__topological_order:
            if self.debug():
                print(f'Computing output for {layer_name}')

            layer = self.__layers[layer_name]
            layer_args = (layers_results[parent_name] for parent_name in self.__layers_parents[layer_name])
            layer_kwargs = {arguments: kwargs[arguments] for arguments in layer.get_input_arguments()}
            layers_results[layer_name] = layer(*layer_args, **layer_kwargs)

        result = dict()
        for output_layer in self.__output_layers:
            if self.debug():
                print(f'Current result dictionary: {result}')
                print(f'Merging output of {output_layer.name}')

            output_layer_result = layers_results[output_layer.name]

            overlapping_keys = overlapping_keys_in_dicts(result, output_layer_result)
            if overlapping_keys:
                print(f'Warning: overlapping output keys! Keys {overlapping_keys} have already been used!')

            result.update(output_layer_result)

        return result

    def __create_model_graph(self):
        layers_queue = self.__output_layers.copy()

        input_arguments = set()

        while layers_queue:
            layer = layers_queue.pop(0)

            # Add layer to __layers dictionary
            self.__layers[layer.name] = layer

            # Add layer's argument to model's input arguments
            input_arguments.update(layer.get_input_arguments())

            # Add layer's parent to dict of parents
            layer_parents = layer.get_parent_layers()
            self.__layers_parents[layer.name] = list(map(lambda x: x.name, layer_parents))

            # Add the nodes that have not been visited to the layers_queue
            layers_queue.extend(filter(lambda x: x.name not in self.__layers_parents, layer_parents))

        self._add_inputs(list(input_arguments))

        # Initialise the graph and compute the graph topological order
        self.__G = nx.from_dict_of_lists(self.__layers_parents, nx.DiGraph).reverse(copy=True)
        self.__topological_order = list(nx.topological_sort(self.__G))
