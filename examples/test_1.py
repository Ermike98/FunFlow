from funflow import Layer, create_graph, topological_order_to_nx
from pprint import pprint
import networkx as nx

layers = [
    Layer("Split", ["{a}:{b}", "{b}:{a}"],
          ["{a}_{b}", ]),
]

user_inputs = {"A:B": 0, "B:A": 1}

topological_order, state_producer = create_graph(layers, user_inputs)

print("Topological Order:", topological_order)

ordered = sum(topological_order, [])

print("\nFINAL STATE PRODUCERS:\n")
pprint({key: [node.name for node in value] for key, value in state_producer.items()})

print("\nFINAL ORDER:\n")
for node in ordered:
    print(node)

G = topological_order_to_nx(topological_order)
A = nx.nx_agraph.to_agraph(G)
A.draw("graph_graphviz.pdf", prog="dot")