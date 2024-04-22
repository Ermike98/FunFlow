from .layer import Layer
import re


def get_layer_inputs(layer: Layer, state_names):
    layer_inputs = layer.inputs
    engine = TemplateEngine(state_names)
    actual_layer_inputs = []
    for layer_input in layer_inputs:
        actual_inputs = engine.find_matches(layer_input)
        # print(f"Layer Inputs: {layer_input}, Actual Inputs: {actual_inputs}")
        if actual_inputs is None:
            return None

        actual_layer_inputs.extend(actual_inputs)

    return actual_layer_inputs


def create_template_pattern_string(templates, layer_input: str):
    template_pattern_string = layer_input
    for template in templates:
        template_pattern_string = template_pattern_string.replace(template, r"(.+)")

    return template_pattern_string


class TemplateEngine:

    def __init__(self, state_names: list[str]):
        self.state_names = state_names
        self.template_maps = dict()

    def find_matches(self, layer_input) -> list | None:
        template_pattern = r"{.*?}"
        templates = re.findall(template_pattern, layer_input)
        # print("Templates: ", templates)
        if not templates:
            # There are no templates => the name of the input is equal to layer_input
            if layer_input in self.state_names:
                return [layer_input]
            # Input is not available in the state
            return None

        pattern = create_template_pattern_string(templates, layer_input)
        # print("Pattern: ", pattern)
        matches = []
        for name in self.state_names:
            # print(f"re.match({pattern}, {name}): {re.match(pattern, name)}")
            if re.match(pattern, name) is not None:
                matches.append(name)

        # Input is not available in the state
        if not matches:
            return None

        return matches

    # def convert(self, layer_names: list[str]):
    #     concrete_names = []
    #
    #     for layer_name in layer_names:
    #         if layer_name.count("$") < 2:
    #             concrete_names.append(layer_name)
    #             continue
