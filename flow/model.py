from typing import Any, Self
from .template_engine import get_layer_inputs
from .layer import Layer


class Model(Layer):
    def __init__(self,
                 layers: Layer | list[Layer] = None,
                 name: str = None,
                 inputs: list[str] = None,
                 outputs: list[str] = None,
                 debug: bool = False
                 ):
        super().__init__(
            name=name,
            inputs=inputs,
            outputs=outputs,
            debug=debug,
            # input_type=None,
            # output_type=None
        )

        if isinstance(layers, Layer):
            layers = [layers]

        self._layers = layers if layers is not None else []
        self._state = dict()

    def add_layer(self, layer: Layer) -> Self:
        self._layers.append(layer)
        self._update_io_names()
        return self

    def call(self, **kwargs: Any) -> Any:
        state = dict()
        state.update(kwargs)
        layers_queue = list(self._layers)
        flag = True

        while layers_queue:
            for layer in layers_queue:
                actual_layer_inputs = get_layer_inputs(layer, state.keys())

                if actual_layer_inputs is None:
                    continue

                layers_queue.remove(layer)
                layer_inputs = {name: state[name] for name in actual_layer_inputs}
                layer_outputs = layer(**layer_inputs)
                state.update(layer_outputs)
                flag = False

            if flag:
                raise Exception("Error: no computation performed, layers are not connected")

            flag = True

        if self._output_names is None:
            return state

        return tuple(state[name] for name in self._output_names)
        # return {name: state[name] for name in self._output_names}

    # State keys, template inputs => actual inputs (subset of state keys), actual outputs || empty tuple if state does not contain all the variables needed

    def _update_io_names(self) -> Self:
        input_names_list = []
        output_names_list = []

        for layer in self._layers:
            input_names_list.append(layer.inputs)
            output_names_list.append(layer.outputs)

        self._input_names = list(dict.fromkeys(sum(input_names_list, [])))
        self._output_names = list(dict.fromkeys(sum(output_names_list, [])))

        return self
