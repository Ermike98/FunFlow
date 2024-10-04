import itertools
from typing import Callable, Any
from .layer import Layer
from .template_utils import replace_multi_templates, create_name_to_inputs_mapping
from .templates import Template, TemplateValue


class GridMap(Layer):
    def __init__(self,
                 func: Callable,
                 inputs: str | list[str] | Template | list[Template] = None,
                 outputs: str | list[str] | Template | list[Template] = None,
                 func_input_type: str = 'args',
                 func_output_type: str = 'tuple',
                 include_tags: bool = False,
                 **kwargs):
        super().__init__(inputs=inputs, outputs=outputs, **kwargs, output_type="dict", call_type="kwargs")
        self.__func = func
        self.__func_input_type = func_input_type
        self.__func_output_type = func_output_type
        self.__include_tags = include_tags

    def call(self, **kwargs: Any):
        kwargs = {str(TemplateValue(name)): value for name, value in kwargs.items()}
        input_template_values = list(map(TemplateValue, kwargs.keys()))
        name_to_template_values = create_name_to_inputs_mapping(input_template_values)

        result = dict()
        for template_values in itertools.product(*[name_to_template_values[input_name.name]
                                                   for input_name in self.inputs]):

            tags = sum(list(map(lambda x: x.tags, template_values)), [])
            output_template_values = [template.instantiate(tags) for template in self.outputs]

            if any(map(lambda x: x is None, output_template_values)):
                # print(f"Not able to instantiate the output template values:"
                #       f"\n- input template values: {template_values}"
                #       f"\n- output templates: {self.outputs}"
                #       f"\n- output template values: {output_template_values}")  # DEBUG
                continue

            if self.__func_input_type == "args":
                func_inputs = (kwargs[str(value)] for value in template_values)
                outputs = self.__func(*func_inputs)
            else:  # self.__func_input_type == "kwargs"
                if self.__include_tags:
                    func_inputs = {str(value): kwargs[str(value)] for value in template_values}
                else:
                    func_inputs = {value.name: kwargs[str(value)] for value in template_values}
                outputs = self.__func(**func_inputs)

            # The function returns None then do not add anything to result
            if outputs is None:
                continue

            if ((not hasattr(outputs, "__len__") or len(outputs) != len(output_template_values))
                    and (self.__func_output_type == "tuple")):
                outputs = (outputs,)

            if self.__func_output_type == "tuple":
                output_dict = {str(templ_value): output_value
                               for templ_value, output_value in zip(output_template_values, outputs)}
            else:  # self.__func_output_type == "dict":
                output_dict = {str(templ_value): outputs[templ_value.name] for templ_value in output_template_values}

            result.update(output_dict)

        return result

    def _get_actual_outputs(self, state: dict[str, Any]) -> list[TemplateValue] | None:
        # state = {str(TemplateValue(name)): value for name, value in state.items()}
        input_template_values = self.actual_inputs
        name_to_template_values = create_name_to_inputs_mapping(input_template_values)

        actual_outputs = []

        for template_values in itertools.product(*[name_to_template_values[input_name.name]
                                                   for input_name in self.inputs]):
            tags = sum(list(map(lambda x: x.tags, template_values)), [])
            output_template_values = [template.instantiate(tags) for template in self.outputs]

            if any(map(lambda x: x is None, output_template_values)):
                continue

            actual_outputs.extend(output_template_values)

        return actual_outputs


