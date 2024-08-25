from flow import Functional, Model
from pprint import pprint

def f(label="", **kwargs):
    return {f"{label} {key}": f"{label} - {value}" for key, value in kwargs.items()}

f_layer = Functional(lambda **kwargs: f("Country", **kwargs), inputs=["{name}"], outputs=["Country {name}"], output_type="dict")

layers = [
    Functional(lambda **kwargs: f("Country", **kwargs), inputs=["{name}"], outputs=["Country {name}"], output_type="dict"),
]

model = Model(layers, inputs=["{name}"], outputs=["Country {name}"])

user_inputs = {"US - Bond": "US - Bond", "US - SP500": "US - SP500"}

result = model(**user_inputs)
# result = f_layer(**user_inputs)
pprint(result)
