from typing import Any
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self
from .layer import Layer
from .template_engine import create_graph, topological_order_to_nx


class Model(Layer):
    """
    A Model is a collection of layers from which a working computation graph can be extracted.
    It manages the execution flow and the shared state between layers.
    """

    def __init__(self,
                 layers: Layer | list[Layer] = None,
                 inputs: list[str] = None,
                 outputs: list[str] = None,
                 **kwargs
                 ):
        """
        Initialize a Model.

        :param layers: A single Layer or a list of Layers to include.
        :param inputs: Global required input names for the entire model.
        :param outputs: Expected global output names from the model.
        :param kwargs: Additional arguments passed to the Layer base class.
        """
        super().__init__(
            inputs=inputs,
            outputs=outputs,
            input_type="kwargs",
            output_type="dict",
            **kwargs
        )

        if isinstance(layers, Layer):
            layers = [layers]

        self._layers = layers if layers is not None else []
        # self._state = dict()

    def add_layer(self, layer: Layer) -> Self:
        """
        Add a layer to the model.

        :param layer: The Layer instance to add.
        :return: Self, for chaining.
        """
        self._layers.append(layer)
        return self

    def call(self, **kwargs: Any) -> Any:
        """
        Execute the model's pipeline.
        Calculates the topological order of layers and runs them in sequence.

        :param kwargs: Initial state values (inputs).
        :return: A dictionary containing the final state after all layers execute.
        """
        state = kwargs.copy()

        topological_order, state_producer = create_graph(self._layers, state)

        for layers in topological_order:

            # INFO: this could be parallelized
            for layer in layers:
                actual_input_names = layer.actual_inputs

                layer_inputs = {str(name): state[str(name)] for name in actual_input_names}
                layer_outputs = layer(**layer_inputs)
                state.update(layer_outputs)

        return state

    def create_graph(self, inputs: dict[str, Any]):
        """
        Generate a NetworkX directed graph representation of the pipeline.

        :param inputs: Sample inputs to resolve dynamic templates.
        :return: A networkx.DiGraph object.
        """
        topological_order, state_producer = create_graph(self._layers, inputs)
        G = topological_order_to_nx(topological_order)
        return G