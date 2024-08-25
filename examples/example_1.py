from funflow import Layer, create_graph, topological_order_to_nx
from pprint import pprint
import networkx as nx

layers = [
    Layer("Split", ["X country:{id}", "y country:{id}"],
          ["X_{id} train", "X_{id} test", "y_{id} train", "y_{id} test"]),

    Layer("Fit Laplacian 1", ["y_{id} train"], ["L method:identity"]),
    Layer("Fit Laplacian 2", ["y_{id} train", "n_L_corr: {n}"], ["L method:corr_{n}"]),
    Layer("Fit Laplacian 3", ["y_{id} train"], ["L method:opt"]),
    Layer("Fit Laplacian 4", ["L method:{method}"], ["L method:ensemble"]),

    Layer("Fit ML1", ["X_{id} train", "y_{id} train"], ["model1 {id}"]),
    Layer("Fit ML2", ["X_{id} train", "y_{id} train"], ["model2 {id}"]),

    Layer("Pred ML1", ["model1 {id}", "X_{id} test"], ["y_{id} pred model1"]),
    Layer("Pred ML2", ["model2 {id}", "X_{id} test"], ["y_{id} pred model2"]),

    Layer("Combine Y Test", ["y_{id} test"], ["y_test"]),
    Layer("Combine Y Pred1", ["y_{id} pred model1"], ["y pred model1"]),
    Layer("Combine Y Pred2", ["y_{id} pred model2"], ["y pred model2"]),

    Layer("Compute Residuals Test", ["y_test", "L method:{method}"], ["res Laplacian:{method} Model:none"]),
    Layer("Compute Residuals Pred1", ["y pred model1", "L method:{method}"], ["res Laplacian:{method} Model:model1"]),
    Layer("Compute Residuals Pred2", ["y pred model2", "L method:{method}"], ["res Laplacian:{method} Model:model2"]),

    Layer("Combine Residuals ML", ["res Laplacian:{method} Model:model1", "res Laplacian:{method} Model:model2"],
          ["res Laplacian:{method} Model:models12_combined"]),
    Layer("Combine Residuals Ensemble",
          ["res Laplacian:{lapl_method} Model:none", "res Laplacian:{method} Model:model1",
           "res Laplacian:{method} Model:model2"],
          ["res Laplacian:{lapl_method} Model:ensemble"]),

    Layer("Trading Strategy", ["res Laplacian:{lapl_method} Model:{pred_method}"],
          ["signal Laplacian:{lapl_method} Model:{pred_method}"]),

    Layer("Compute Returns", ["y_test", "signal Laplacian:{lapl_method} Model:{pred_method}"],
          ["returns Laplacian:{lapl_method} Model:{pred_method}"]),

    # Layer("Analytics", ["returns Laplacian:{lapl_method} Model:{pred_method}"],
    #      ["PerformanceReport Laplacian:{lapl_method} Model:{pred_method}"])
]

user_inputs = {"X country:DE": 1, "y country:DE": 1, "X country:IT": 1, "y country:IT": 1, "n_L_corr: 10": 10,
               "n_L_corr: 50": 50}

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