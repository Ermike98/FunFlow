import itertools
from typing import Callable
from .layer import Layer
from .template_utils import replace_multi_templates


class Map(Layer):
    def __init__(self,
                 func: Callable,
                 inputs: list[str] = None,
                 outputs: list[str] = None,
                 map_over: list[str] = None,
                 **kwargs):
        super().__init__(inputs=inputs, outputs=outputs, **kwargs, output_type="dict")
        self.__func = func
        self.__map_over = map_over

    def call(self, **kwargs):
        if self.__map_over is not None:
            for template in self.__map_over:
                assert template in self._template_values, (f"Trying to map over template {template} but {template} is "
                                                           f"not in the input templates: {list(self._template_values.keys())}")
            map_over = self.__map_over
        else:
            map_over = self._template_values.keys()

        excluded_templates = [template for template in self._template_values if template not in map_over]

        result = dict()

        for values in itertools.product(*[self._template_values[template] for template in map_over]):
            template_values_dict = dict(zip(map_over, map(lambda x: [x], values)))
            template_values_dict.update({template: self._template_values[template] for template in excluded_templates})

            input_names = replace_multi_templates(self.inputs, template_values_dict)
            outputs = self.__func(*(kwargs[input_name] for input_name in input_names))
            output_names = replace_multi_templates(self.outputs, template_values_dict)

            if len(output_names) == 1:
                outputs = [outputs]

            result.update(dict(zip(output_names, outputs)))

        return result
        # self.__func(**kwargs)
