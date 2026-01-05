from funflow import GridMap, Model, Template, Tag, NoTagFilter
import math

# 1. Understanding Tag-based Routing with GridMap
# When we want a single layer to process multiple tagged inputs 
# INDEPENDENTLY, we use GridMap. 
# GridMap automatically iterates over all possible combinations of 
# matched tags and runs the function for each combination.

# A simple processing function.
def processor_func(x):
    return x**2

# 2. Define the GridMap Layer
# We use explicit Template objects with NoTagFilter.
# GridMap will find all values for 'data' with an 'id' tag and run 
# processor_func for each one.

templated_layer = GridMap(
    processor_func,
    inputs=[Template("data", filters=[NoTagFilter("id")])],
    outputs=[Template("result", filters=[NoTagFilter("id")])],
    name="DynamicProcessor"
)

# 3. Create the Model
model = Model([templated_layer])

# 4. Run the model with multiple tagged inputs
if __name__ == "__main__":
    print("--- Running Tag Templating Example with GridMap ---")
    
    inputs = {
        "data, id:dataset_A": 10,
        "data, id:dataset_B": 20
    }
    
    result = model(**inputs)
    
    print("\nInputs Provided:")
    for k, v in inputs.items():
        print(f"  {k} = {v}")
        
    print("\nResults Produced:")
    for k, v in result.items():
        if "result" in k:
            print(f"  {k} = {v}")

    # Expected output:
    # result, id:dataset_A = 100
    # result, id:dataset_B = 400
