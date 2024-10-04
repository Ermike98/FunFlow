import re
from collections import defaultdict
import itertools

from .templates import Template, TemplateValue


def find_actual_input_names(input_template: Template, state_names: list[str]) -> list[str] | None:
    actual_names = [name for name in state_names if input_template.match(name)]

    # No state name matches the template
    if not actual_names:
        return None

    return actual_names


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


def create_tag_to_inputs_mapping(input_template_values: list[TemplateValue]) -> dict[str, set[TemplateValue]]:
    tag_to_inputs = defaultdict(set)
    for input_templ in input_template_values:
        for tag in input_templ.tags:
            tag_to_inputs[tag.name].add(input_templ)

    return tag_to_inputs


def create_name_to_inputs_mapping(input_template_values: list[TemplateValue]) -> dict[str, set[TemplateValue]]:
    name_to_inputs = defaultdict(set)
    for input_templ in input_template_values:
        name_to_inputs[input_templ.name].add(input_templ)

    return name_to_inputs
