import re
from collections import defaultdict
import itertools
from pprint import pprint
from typing import List
from dataclasses import dataclass, field
import networkx as nx
from matplotlib import pyplot as plt


def create_template_pattern_string(templates, layer_input: str):
    template_pattern_string = layer_input
    for template in templates:
        template_pattern_string = template_pattern_string.replace(template, r"(.+)")

    return "^" + template_pattern_string


def find_actual_input_names(layer_input, state_names):
    # print(f"find_actual_input_names) layer_input:{layer_input}, state_names:{state_names}")
    template_pattern = r"{.*?}"
    templates = re.findall(template_pattern, layer_input)
    # print("Templates: ", templates)
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
        # print(f"re.findall({pattern}, {name}): {re.findall(pattern, name)}")
        templates_value = re.findall(pattern, name)
        # print(f"find_actual_input_names) templates: {templates}, templates_value: {templates_value}, pattern: {pattern}, name: {name}")
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


def replace_templates(name, templates, templates_value):
    for template, value in zip(templates, templates_value):
        name = name.replace(template, value)

    return name


def find_actual_output_names(layer_outputs, template_values):
    actual_outputs = []
    template_pattern = r"{.*?}"

    for layer_output in layer_outputs:
        templates = re.findall(template_pattern, layer_output)

        # print(f"replace_multi_templates) layer_outputs: {layer_outputs}, template_values: {template_values}, templates: {templates}")

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

    def update_actuals(self, state_producer):
        actual_inputs = []
        actual_outputs = []
        predecessors_set = set()

        template_values = dict()
        for input_name in self.inputs:
            actual_input_names, template_values_input = find_actual_input_names(input_name, state_producer.keys())

            print(
                f"input_name: {input_name}, actual_names: {actual_input_names}, template_values: {template_values}, template_values_input: {template_values_input}")

            if actual_input_names is None:
                self.actual_inputs = None
                self.actual_outputs = None
                self.predecessors = []

                return

            template_values.update(template_values_input)

            actual_input_names = [actual_name for actual_name in actual_input_names if
                                  self not in state_producer[actual_name]]

            actual_inputs.extend(actual_input_names)

            for actual_name in actual_input_names:
                predecessors_set.update(state_producer[actual_name])

        # actual_outputs.extend(replace_multi_templates(self.outputs, template_values))

        self.actual_inputs = actual_inputs
        self.actual_outputs = find_actual_output_names(self.outputs, template_values)
        self.predecessors = [predecessor for predecessor in predecessors_set if predecessor != self]

    def __hash__(self):
        return hash(self.name)


def is_any_in_input(input_names, other_names):
    for input_name in input_names:

        actual_input_names = find_actual_input_names(input_name, other_names)[0]
        if actual_input_names is not None:
            print(f"input_name: {input_name}, actual_names: {actual_input_names}")
            # return True
    return False


def all_node_predecessor_are_ordered(node: Node, ordered: List[Node]):
    if node.actual_outputs is None:
        return False

    # this is true if none of node.actual_outputs is taken in input by any of the ordered nodes
    for ordered_node in ordered:
        if is_any_in_input(ordered_node.inputs, node.actual_outputs):
            return False
    return True


def find_node_successor(node, ordered):
    return [ordered_node for ordered_node in ordered if
            node != ordered_node and is_any_in_input(ordered_node.inputs, node.actual_outputs)]


def process_node(node, ordered, quarantined, processing, state_producer):
    node.update_actuals(state_producer)

    print("\nStart Procssing Node:", node)
    print(f"Predecessor: {list(map(lambda x: x.name, node.predecessors))}")
    print(f"Ordered: {list(map(lambda x: x.name, ordered))}")
    print(f"Quarantined: {list(map(lambda x: x.name, quarantined))}")

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


def create_graph(nodes, user_inputs):
    state_producer = defaultdict(list)  # state[actual_input_name] => list of producers

    for _input in user_inputs.keys():
        state_producer[_input] = []

    processing = nodes
    ordered = []
    quarantined = []

    i = 0
    while nodes:
        node = nodes.pop(0)

        print(f"\n\nNode: {node}")
        #print("\n")
        result_processing = process_node(node, ordered, quarantined, processing, state_producer)
        # print(f"Result processing node: {node.name} is: {result_processing}")
        # print(f"Node: {node}")

        if not result_processing:
            nodes.append(node)

        # print("Ordered Nodes:")
        # for node in ordered:
        #     print(node)

    return ordered, state_producer


nodes = [
    Node("Split", ["X country:{id}", "y country:{id}"], ["X_{id} train", "X_{id} test", "y_{id} train", "y_{id} test"]),

    Node("Fit Laplacian 1", ["y_{id} train"], ["L method:identity"]),
    Node("Fit Laplacian 2", ["y_{id} train", "n_L_corr: {n}"], ["L method:corr_{n}"]),
    Node("Fit Laplacian 3", ["y_{id} train"], ["L method:opt"]),
    Node("Fit Laplacian 4", ["L method:{method}"], ["L method:ensemble"]),

    Node("Fit ML1", ["X_{id} train", "y_{id} train"], ["model1 {id}"]),
    Node("Fit ML2", ["X_{id} train", "y_{id} train"], ["model2 {id}"]),

    Node("Pred ML1", ["model1 {id}", "X_{id} test"], ["y_{id} pred model1"]),
    Node("Pred ML2", ["model2 {id}", "X_{id} test"], ["y_{id} pred model2"]),

    Node("Combine Y Test",  ["y_{id} test"], ["y_test"]),
    Node("Combine Y Pred1", ["y_{id} pred model1"], ["y pred model1"]),
    Node("Combine Y Pred2", ["y_{id} pred model2"], ["y pred model2"]),

    Node("Compute Residuals Test", ["y_test", "L method:{method}"], ["res Laplacian:{method} Model:none"]),
    Node("Compute Residuals Pred1", ["y pred model1", "L method:{method}"], ["res Laplacian:{method} Model:model1"]),
    Node("Compute Residuals Pred2", ["y pred model2", "L method:{method}"], ["res Laplacian:{method} Model:model2"]),

    Node("Combine Residuals ML", ["res Laplacian:{method} Model:model1", "res Laplacian:{method} Model:model2"],
         ["res Laplacian:{method} Model:models12_combined"]),
    Node("Combine Residuals Ensemble",
         ["res Laplacian:{lapl_method} Model:none", "res Laplacian:{method} Model:model1", "res Laplacian:{method} Model:model2"],
         ["res Laplacian:{lapl_method} Model:ensamble"]),

    Node("Trading Strategy", ["res Laplacian:{lapl_method} Model:{pred_method}"],
         ["signal Laplacian:{lapl_method} Model:{pred_method}"]),

    Node("Compute Returns", ["y_test", "signal Laplacian:{lapl_method} Model:{pred_method}"],
         ["returns Laplacian:{lapl_method} Model:{pred_method}"]),
    # Node("Analytics", ["returns Laplacian:{lapl_method} Model:{pred_method}"],
    #      ["PerformanceReport Laplacian:{lapl_method} Model:{pred_method}"])
]

user_inputs = {"X country:DE": 1, "y country:DE": 1, "X country:IT": 1, "y country:IT": 1, "n_L_corr: 10": 10, "n_L_corr: 50": 50}

# nodes = [
#     Node("E", ["z_{id}"], ["z_3"]),
#     Node("B", ["w"], ["z_1"]),
#     Node("F", ["z_{id}"], ["p_{id}"]),
#     Node("A", ["x"], ["y"]),
#     Node("D", ["w", "y"], ["z_2"]),
#     Node("C", ["y"], ["w"]),
# ]

# user_inputs = {"x": 1}

# nodes = [
#     Node("C", ["z"], ["y"]),
#     Node("B", ["y"], ["x"]),
#     Node("A", ["x"], ["z"]),
# ]

ordered, state_producer = create_graph(nodes, user_inputs)

print("\nFINAL STATE PRODUCERS:\n")
pprint({key: [node.name for node in value] for key, value in state_producer.items()})

print("\nFINAL ORDER:\n")
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

# PLOT VARIABLE WITH LAYERS AS EDGES

layer = 1

G = nx.DiGraph()

included_layer = []
included_graph = []
remaining = ordered.copy()
values_included = set()

while remaining:
    print(len(remaining))

    for node in remaining.copy():
        if ((not any(map(lambda p: p in included_layer, node.predecessors))) and
                all(map(lambda p: p in included_graph, node.predecessors))):
            print(node)

            included_layer.append(node)
            included_graph.append(node)
            remaining.remove(node)
            G.add_nodes_from([node.name.replace(" ", "\n")], layer=layer, color="lightblue")

            G.add_nodes_from([out.replace(" ", "\n") for out in node.actual_outputs if out not in values_included], layer=layer + 1,
                             color="orange")
            G.add_nodes_from([inp.replace(" ", "\n") for inp in node.actual_inputs if inp not in values_included], layer=layer - 1,
                             color="orange")

            values_included.update(node.actual_outputs)
            values_included.update(node.actual_inputs)

            G.add_edges_from(
                zip([node.name.replace(" ", "\n")] * len(node.actual_outputs),
                    map(lambda x: x.replace(" ", "\n"), node.actual_outputs)),
                layer=layer + 1)
            G.add_edges_from(
                zip(map(lambda x: x.replace(" ", "\n"), node.actual_inputs),
                    [node.name.replace(" ", "\n")] * len(node.actual_inputs)),
                layer=layer - 1)

    layer += 2
    included_layer = []

A = nx.nx_agraph.to_agraph(G)
A.draw("graph_graphviz.pdf", prog="dot")

colors = [data["color"] for v, data in G.nodes(data=True)]
plt.figure(figsize=(75, 50))
pos = nx.multipartite_layout(G, subset_key="layer")
nx.draw(G, pos, with_labels=True, node_color=colors, node_size=10000, font_size=20, edge_color='grey')
plt.savefig("graph.pdf")
plt.show()

# named_edges = dict()
#
# for node in ordered:
#     for output_name in node.outputs:
#         named_edges[(node.name, output_name)] = node.name
#
#     for input_name in node.inputs:
#         named_edges[(input_name, node.name)] = node.name
#
# G = nx.from_edgelist(named_edges.keys(), create_using=nx.DiGraph)
#
# # pos = nx.kamada_kawai_layout(G)
# plt.figure(figsize=(15, 15))
# nx.draw(G, with_labels=True)
# # nx.draw_networkx_edge_labels(G, pos, edge_labels=named_edges, font_color='red')
# plt.axis('off')
# plt.show()
#
# for node in ordered:
#     node.predecessors = []
#
# pprint(ordered)
#