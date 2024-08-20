import time

from flow import Functional

# layer = Functional(lambda x, y: x + y, inputs=["x", "y"], outputs=["z"], input_type='args')
layer = Functional(lambda *args: " ".join(args), outputs=["z"])

# user_inputs = {"x": "Test", "y": " Functional"}
user_inputs = "Test", "Functional"
result = layer(*user_inputs)

print("Call without init")
print("result: ", result)
print(layer)

