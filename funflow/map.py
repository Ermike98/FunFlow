import itertools
from typing import Callable
from .layer import Layer
from .template_utils import replace_multi_templates, create_name_to_inputs_mapping
from .templates import Template, TemplateValue


class Map(Layer):
    def __init__(self,
                 func: Callable,
                 inputs: str | list[str] | Template | list[Template] = None,
                 outputs: str | list[str] | Template | list[Template] = None,
                 map_over: list[str] = None,
                 func_input_type: str = 'args',
                 func_output_type: str = 'tuple',
                 **kwargs):
        super().__init__(inputs=inputs, outputs=outputs, **kwargs, output_type="dict", call_type="kwargs")
        self.__func = func
        self.__map_over = map_over  # TODO - Add warning if name in map_over is not present in input_names/templates
        self.__func_input_type = func_input_type
        self.__func_output_type = func_output_type

    def __get_map_over(self, tags):
        pass

    def call(self, **kwargs):
        input_template_values = list(map(TemplateValue, kwargs.keys()))
        name_to_template_values = create_name_to_inputs_mapping(input_template_values)

        if self.__map_over is not None:
            for input_name in self.__map_over:
                assert input_name in name_to_template_values, (
                    f"Trying to map over template {input_name} but {input_name} is "
                    f"not in the input templates: {list(name_to_template_values.keys())}")
            map_over = self.__map_over
        else:
            map_over = name_to_template_values.keys()

        excluded_templates = [template for template in self._template_values if template not in map_over]

        result = dict()

        for values in itertools.product(*[self._template_values[template] for template in map_over]):
            template_values_dict = dict(zip(map_over, map(lambda x: [x], values)))
            template_values_dict.update({template: self._template_values[template] for template in excluded_templates})

            input_names = replace_multi_templates(self.inputs, template_values_dict)

            if self.__func_input_type == "args":
                outputs = self.__func(*(kwargs[input_name] for input_name in input_names))
            else:  # self.__func_input_type == "kwargs"
                outputs = self.__func(**{input_name: kwargs[input_name] for input_name in input_names})

            output_names = replace_multi_templates(self.outputs, template_values_dict)

            if len(output_names) == 1 and self.__func_output_type == "tuple":
                outputs = [outputs]

            if outputs is not None:

                if self.__func_output_type == "tuple":
                    result.update(dict(zip(output_names, outputs)))
                elif self.__func_output_type == "dict":
                    result.update({output_name: outputs[output_name] for output_name in output_names})

        return result
        # self.__func(**kwargs)
