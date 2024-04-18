# from src_old import Layer, Functional
from flow import Functional, Model, Layer
from pprint import pprint

def f(x):
    # print("x:", x)
    return f"f-x:({x})", f"f-x:({x})", f"f-x:({x})"


def g(un):
    # print("un:", un)
    return f"g-un:({un})"


def h(x, dos):
    return f"h-x:({x})", f"h-dos:({dos})"


def f_kwargs(**kwargs):
    # print(kwargs)
    return f"kwargs "




# layer = Functional(f, debug=True, outputs=['output'], inputs="x", raw_inputs=False)
layer2 = Functional(f, debug=True, outputs=['un', 'dos', 'tres'], inputs="x")
# layer3 = Functional(g, debug=True, outputs=['un-un'], inputs='un')
# layer4 = Functional(h, debug=True, outputs=['xx', "xdos"], inputs=['x', 'dos'])
layer5 = Functional(f_kwargs, debug=True, outputs=['kwd'], inputs=['x', 'dos', 'un'])
model = Model([layer2, layer5], debug=True, outputs=['x', 'un', 'kwd'])

pprint(model(x=10))
# layer = Functional(lambda x: x)
# print(layer(10))
# print(layer(10))
