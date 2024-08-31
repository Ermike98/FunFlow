from .layer import Layer


class Rename(Layer):
    def __init__(self,
                 mapping: dict[str, str],
                 **kwargs):
        super().__init__(inputs=list(mapping.keys()), outputs=list(mapping.values()),
                         input_type="kwargs", output_type="dict", **kwargs)
        self.mapping = mapping

    def call(self, **kwargs):
        return {output_name: kwargs[input_name] for input_name, output_name in self.mapping.items()}

