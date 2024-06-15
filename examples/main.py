from flow import Functional, Model, Layer
from pprint import pprint


def f(**kwargs):
    print(kwargs.keys())
    return None


load_X = Functional(f, debug=True, outputs=['X_train'], inputs=[])
load_y = Functional(f, debug=True, outputs=['y_train'], inputs=[])

# transform = Functional(f, debug=True, outputs=['X_train_norm'], inputs=['X_train'])
model = Model([load_X, load_y], debug=True, outputs=['x', 'un', 'kwd'])

result = model(x=10)
pprint()
# layer = Functional(lambda x: x)
# print(layer(10))
# print(layer(10))
