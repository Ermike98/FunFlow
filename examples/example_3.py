from funflow import Functional, Model

layers = [
    Functional(lambda x: x * 2, inputs=["x"], outputs=["y"]),
    Functional(lambda x, y: (x * 2 / y) == 1, inputs=["x", "y"], outputs=["test_ratio"]),
    Functional(lambda y: f"y: {y}", inputs=["y"], outputs=["description y"]),
    Functional(lambda x: f"x: {x}", inputs=["x"], outputs=["description y"]),
]

model = Model(layers, inputs=["x"])

result = model(x=10)
print(result)

