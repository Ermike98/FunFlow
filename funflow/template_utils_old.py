import re
from collections import defaultdict
import itertools


def create_template_pattern_string(templates, layer_input: str):
    template_pattern_string = layer_input
    for template in templates:
        template_pattern_string = template_pattern_string.replace(template, r"(.+)")

    return "^" + template_pattern_string


def find_actual_input_names(layer_input, state_names):
    template_pattern = r"{.*?}"
    templates = re.findall(template_pattern, layer_input)

    if not templates:
        # There are no templates => the name of the input is equal to layer_input
        if layer_input in state_names:
            return [layer_input], {}
        # Input is not available in the state
        return None, None

    pattern = create_template_pattern_string(templates, layer_input)
    template_values = defaultdict(set)
    actual_names = []

    for name in state_names:
        templates_value = re.findall(pattern, name)

        if templates_value:
            actual_names.append(name)

            if len(templates) > 1:
                templates_value = templates_value[0]

            for value, template in zip(templates_value, templates):
                template_values[template].add(value)

    # Input is not available in the state
    if not actual_names:
        return None, None

    return actual_names, template_values


def replace_templates(name: str, templates: list[str], templates_value: list[str]):
    for template, value in zip(templates, templates_value):
        name = name.replace(template, value)

    return name


def find_and_replace_templates(name: str, templates_values: dict[str, str]) -> str:
    template_pattern = r"{.*?}"
    templates = re.findall(template_pattern, name)

    if not templates:
        return name

    return replace_templates(name, templates, [templates_values[template] for template in templates])


def multi_find_and_replace_templates(names: list[str], templates_value: dict[str, str]) -> list[str]:
    return [find_and_replace_templates(name, templates_value) for name in names]


def replace_multi_templates(names: list[str], template_values: dict[str, set[str] | list[str]]) -> list[str]:
    actual_outputs = []
    template_pattern = r"{.*?}"

    for name in names:
        templates = re.findall(template_pattern, name)

        if not templates:
            actual_outputs.append(name)
            continue

        for templates_value in itertools.product(*[template_values[template] for template in templates]):
            actual_outputs.append(replace_templates(name, templates, templates_value))

    return actual_outputs
