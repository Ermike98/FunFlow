from layer import Layer


class Select(Layer):
    def __init__(self,
                 input_layer: Layer,
                 selected_items: str | list[str],
                 debug: bool = False):
        super().__init__(
            inputs=input_layer,
            output_names=selected_items,
            debug=debug
        )
        selected_items_ = [selected_items] if isinstance(selected_items, str) else selected_items
        self.name = self.name.replace('Select', f'Select{list(selected_items_)}')

    def call(self, **kwargs) -> dict:
        return {name: kwargs[name] for name in self._output_names}
