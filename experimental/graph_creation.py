import re
from collections import defaultdict
import itertools
from typing import List
from dataclasses import dataclass, field
import networkx as nx
from matplotlib import pyplot as plt


def create_template_pattern_string(templates, layer_input: str):
    template_pattern_string = layer_input
    for template in templates:
        template_pattern_string = template_pattern_string.replace(template, r"(.+)")

    return template_pattern_string


def find_actual_input_names(layer_input, state_names):
    # print(f"find_actual_input_names: layer_input={layer_input}, state_names={state_names}")
    template_pattern = r"{.*?}"
    templates = re.findall(template_pattern, layer_input)
    # print("Templates: ", templates)
    if not templates:
        # There are no templates => the name of the input is equal to layer_input
        if layer_input in state_names:
            return [layer_input], None
        # Input is not available in the state
        return None, None

    pattern = create_template_pattern_string(templates, layer_input)
    template_values = defaultdict(set)
    actual_names = []

    for name in state_names:
        # print(f"re.findall({pattern}, {name}): {re.findall(pattern, name)}")
        templates_value = re.findall(pattern, name)
        if templates_value:
            actual_names.append(name)

            for value, template in zip(templates_value[0], templates):
                template_values[template].add(value)

    # Input is not available in the state
    if not actual_names:
        return None, None

    return actual_names, template_values


def replace_templates(name, templates, templates_value):
    for template, value in zip(templates, templates_value):
        name = name.replace(template, value)

    return name


def find_actual_output_names(layer_outputs, template_values):
    actual_outputs = []
    template_pattern = r"{.*?}"

    for layer_output in layer_outputs:
        templates = re.findall(template_pattern, layer_output)
        if not templates:
            actual_outputs.append(layer_output)
            continue

        for templates_value in itertools.product(*[template_values[template] for template in templates]):
            actual_outputs.append(replace_templates(layer_output, templates, templates_value))

    return actual_outputs


@dataclass
class Node:
    name: str
    inputs: List
    outputs: List
    actual_inputs: List | None = None
    actual_outputs: List | None = None
    predecessors: List = field(default_factory=list)

    # def __init__(self, name, inputs, outputs, actual_inputs=None, actual_outputs=None, predecessors=None, ):
    #     self.name = name
    #     self.inputs = inputs
    #     self.outputs = outputs
    #     self.actual_inputs = actual_inputs
    #     self.actual_outputs = actual_outputs
    #     self.predecessors = predecessors if predecessors is not None else []

    def update_actuals(self, state_producer):
        actual_inputs = []
        actual_outputs = []
        predecessors_set = set()

        for input_name in self.inputs:
            actual_names, template_values = find_actual_input_names(input_name, state_producer.keys())

            if actual_names is None:
                self.actual_inputs = None
                self.actual_outputs = None
                self.predecessors = []

                return

            actual_names = [actual_name for actual_name in actual_names if self not in state_producer[actual_name]]

            actual_inputs.extend(actual_names)
            actual_outputs.extend(find_actual_output_names(self.outputs, template_values))

            for actual_name in actual_names:
                predecessors_set.update(state_producer[actual_name])

        self.actual_inputs = actual_inputs
        self.actual_outputs = actual_outputs
        self.predecessors = [predecessor for predecessor in predecessors_set if predecessor != self]

    def __hash__(self):
        return hash(self.name)


def is_any_in_input(input_names, other_names):
    for input_name in input_names:
        actual_input_names = find_actual_input_names(input_name, other_names)[0]
        if actual_input_names is not None:
            return True
    return False
    # return any(map(lambda x: find_actual_input_names(x, other_names)[0] is not None, input_names))


def all_node_predecessor_are_ordered(node: Node, ordered: List[Node]):
    if node.actual_outputs is None:
        return False

    # this is true if none of node.actual_outputs is taken in input by any of the ordered nodes
    for ordered_node in ordered:
        if is_any_in_input(ordered_node.inputs, node.actual_outputs):
            return False
    return True


def find_node_successor(node, ordered):
    return [ordered_node for ordered_node in ordered if node != ordered_node and is_any_in_input(ordered_node.inputs, node.actual_outputs)]


def process_node(node, ordered, quarantined, processing, state_producer):
    node.update_actuals(state_producer)

    print("\nStart Procssing Node:", node)
    print(f"Predecessor: {list(map(lambda x: x.name, node.predecessors))}")
    # print(
    #     f"Node: {node.name}, Inputs: {node.inputs}, Actual Inputs: {node.actual_inputs}, Outputs: {node.outputs}, Actual Outputs: {node.actual_outputs}")
    print(f"Ordered: {list(map(lambda x: x.name, ordered))}")
    print(f"Quarantined: {list(map(lambda x: x.name, quarantined))}")
    # print(f"Processing: {list(map(lambda x: x.name, processing))}")
    # print(f"State Producer:")
    # for name, predecessors_list in state_producer.items():
    #     print(f"Input Name: {name}, Producer Names: {list(map(lambda x: x.name, predecessors_list))}")

    if node in quarantined:
        raise Exception(
            # f"Cyclical graph detected! Nodes involved: {dict(zip(map(lambda x: x.name, quarantined), quarantined))}")
            f"Cyclical graph detected! Nodes involved: {list(map(lambda x: x.name, quarantined))}")

    if node.actual_inputs is not None:

        for actual_name in node.actual_outputs:
            if node not in state_producer[actual_name]:
                state_producer[actual_name].append(node)

        successors = find_node_successor(node, ordered)
        print(f"Successors: {list(map(lambda x: x.name, successors))}")
        ordered.append(node)

        if successors:
            quarantined.append(node)
            # processing.extend(successors)  # extend without duplicates

            for successor in successors:
                ordered.remove(successor)

            for successor in successors:
                process_node(successor, ordered, quarantined, processing, state_producer)

            quarantined.remove(node)

        return True

    return False


nodes = [
    Node("A", ["x"], ["y"]),
    Node("B", ["w"], ["z_1"]),
    Node("C", ["y"], ["w"]),
    Node("D", ["w", "y"], ["z_2"]),
    Node("E", ["z_{id}"], ["z_3"]),
    Node("F", ["z_{id}"], ["p_{id}"])
]

# nodes = [
#     Node("C", ["z"], ["y"]),
#     Node("B", ["y"], ["x"]),
#     Node("A", ["x"], ["z"]),
# ]

user_inputs = {"x": 10}

state_producer = defaultdict(list)  # state[actual_input_name] => list of producers

for _input in user_inputs.keys():
    state_producer[_input] = []

processing = nodes
ordered = []
quarantined = []

i = 0
while nodes:
    node = nodes.pop(0)
    # nodes.append(node)
    print("\n")
    result_processing = process_node(node, ordered, quarantined, processing, state_producer)
    print(f"Result processing node: {node.name} is: {result_processing}")
    print(f"Node: {node}")

    if not result_processing:
        nodes.append(node)

    print("Ordered Nodes:")
    for node in ordered:
        print(node)

print(state_producer)

for node in ordered:
    print(node)

edges = []

for node in ordered:
    for predecessor in node.predecessors:
        edges.append((predecessor.name, node.name))

G = nx.from_edgelist(edges, create_using=nx.DiGraph)
# top = nx.bipartite.sets(G)[0]
# pos = nx.multipartite_layout(G)
nx.draw(G, with_labels=True)


plt.show()