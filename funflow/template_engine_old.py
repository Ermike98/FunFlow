from .layer import Layer
from .template_utils import *
import networkx as nx


def is_any_in_input(input_names: list[str], other_names: list[str]) -> bool:
    for input_name in input_names:

        actual_input_names = find_actual_input_names(input_name, other_names)[0]
        if actual_input_names is not None:
            # print(f"input_name: {input_name}, actual_names: {actual_input_names}")
            return True

    return False


def all_node_predecessor_are_ordered(node_actual_outputs: list[str], ordered: list[Layer]):
    if node_actual_outputs is None:
        return False

    # this is true if none of node.actual_outputs is taken in input by any of the ordered nodes
    for ordered_node in ordered:
        if is_any_in_input(ordered_node.inputs, node_actual_outputs):
            return False
    return True


def find_node_successor(node: Layer, node_actual_outputs: list[str], ordered: list[Layer]):
    return [ordered_node for ordered_node in ordered
            if node != ordered_node and is_any_in_input(ordered_node.inputs, node_actual_outputs)]


def process_node(node: Layer,
                 ordered: list[Layer],
                 quarantined: list[Layer],
                 processing: list[Layer],
                 state_producers: dict,
                 user_inputs: dict
                 ):
    node.init(user_inputs, state_producers)

    actual_outputs = node.actual_outputs
    actual_inputs = node.actual_inputs
    # predecessors = node.predecessors

    # print("\nStart Processing Node:", node)
    # print(f"Predecessor: {list(map(lambda x: x.name, predecessors))}")
    # print(f"Ordered: {list(map(lambda x: x.name, ordered))}")
    # print(f"Quarantined: {list(map(lambda x: x.name, quarantined))}")

    if node in quarantined:
        raise Exception(
            # f"Cyclical graph detected! Nodes involved: {dict(zip(map(lambda x: x.name, quarantined), quarantined))}")
            f"Cyclical graph detected! Nodes involved: {list(map(lambda x: x.name, quarantined))}")

    if actual_inputs is not None:

        for actual_name in actual_outputs:
            if node not in state_producers[actual_name]:
                state_producers[actual_name].append(node)

        successors = find_node_successor(node, actual_outputs, ordered)

        # print(f"Successors: {list(map(lambda x: x.name, successors))}")  # DEBUG
        ordered.append(node)

        if successors:
            quarantined.append(node)
            # processing.extend(successors)  # extend without duplicates

            for successor in successors:
                ordered.remove(successor)

            for successor in successors:
                process_node(successor, ordered, quarantined, processing, state_producers, user_inputs)

            quarantined.remove(node)

        return True

    return False


def create_graph(layers: list[Layer], user_inputs: dict) -> tuple[list[list[Layer]], dict[str, list[Layer]]]:
    state_producers = defaultdict(list)  # state[actual_input_name] => list of producers

    for _input in user_inputs.keys():
        state_producers[_input] = []

    nodes = layers.copy()
    processing = nodes
    ordered = []
    quarantined = []

    while nodes:
        node = nodes.pop(0)

        result_processing = process_node(node, ordered, quarantined, processing, state_producers, user_inputs)

        if not result_processing:
            nodes.append(node)

    layered = ordered_to_leveled(ordered)

    return layered, state_producers


def ordered_to_leveled(ordered: list[Layer]) -> list[list[Layer]]:
    result = []

    current_level_layers = []
    already_included = []
    remaining = ordered.copy()

    while remaining:

        # print(len(remaining))  # DEBUG

        for layer in remaining.copy():
            if ((not any(map(lambda p: p in current_level_layers, layer.predecessors))) and
                    all(map(lambda p: p in already_included, layer.predecessors))):
                # print(layer)

                current_level_layers.append(layer)
                already_included.append(layer)
                remaining.remove(layer)

        result.append(current_level_layers)
        current_level_layers = []

    return result


def topological_order_to_nx(topological_order: list[list[Layer]]) -> nx.DiGraph:
    # PLOT VARIABLE WITH LAYERS AS EDGES
    ordered = sum(topological_order, [])
    layer = 1

    G = nx.DiGraph()

    included_layer = []
    included_graph = []
    remaining = ordered.copy()
    values_included = set()

    while remaining:
        # print(len(remaining))

        for node in remaining.copy():
            if ((not any(map(lambda p: p in included_layer, node.predecessors))) and
                    all(map(lambda p: p in included_graph, node.predecessors))):
                # print(node)

                included_layer.append(node)
                included_graph.append(node)
                remaining.remove(node)
                G.add_nodes_from([node.name.replace(" ", "\n")], layer=layer, color="lightblue")

                G.add_nodes_from([out.replace(" ", "\n") for out in node.actual_outputs if out not in values_included],
                                 layer=layer + 1,
                                 color="orange")
                G.add_nodes_from([inp.replace(" ", "\n") for inp in node.actual_inputs if inp not in values_included],
                                 layer=layer - 1,
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

    return G
