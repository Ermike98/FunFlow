from flow import Map

map_layer = Map(lambda string, n: string * n, inputs=["String {id}", "N {n}"], outputs=["{id}*{n}"])

user_inputs = {
    "String 1": 1,
    "String '1'": '1',
    "String bla": "bla",
    "N 1": 1,
    "N 3": 3,
}

print(map_layer.init(user_inputs)._template_values)
print(map_layer(**user_inputs))