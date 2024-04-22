from pprint import pprint

from flow import Functional, Model

def template_add(**kwargs):
    print("template_add kwargs:", kwargs)
    return sum(kwargs.values())

def template_x_minus_y(**kwargs):
    print("template_x_minus_y kwargs:", kwargs)
    xs = [val for key, val in kwargs.items() if key.startswith('x')]
    ys = [val for key, val in kwargs.items() if key.startswith('y')]
    return sum(xs), sum(ys), sum(xs) - sum(ys)

f_add = Functional(template_add, inputs=["x_{id}"], outputs="sum", debug=True)
f_x_minus_y = Functional(template_x_minus_y, inputs=["x_{id}", "y_{id}"], outputs=["sum_x", "sum_y", "x_minus_y"], debug=True)
model = Model([f_add, f_x_minus_y], debug=True, outputs=["sum", "sum_x", "sum_y", "x_minus_y"])


model(x_1=1, x_2=2, x_3=3, x_9=9, y_1=2, y_2=2, y_3=2)

